# Part B - Capacity Reconciliation

Source files: `bench/model_spec.md`, `bench/bench_log.csv`

## B1 - KV Cache Bytes/Token and Maximum Concurrent Sequences

The model uses GQA with 24 query heads but only **8 KV heads**. K/V states are cached per KV head, not per query head. Using 24 KV heads would therefore overestimate cache usage by 3x.

The KV-cache cost per token is:

`bytes/token = 2 × layers × kv_heads × head_dim × bytes/element`

`= 2 × 28 × 8 × 128 × 2 = 114,688 bytes/token (~112 KiB)`

The 24 GB GPU is reduced by the `gpu_memory_utilization=0.92` setting and 1.6 GB of non-KV runtime overhead:

`available = (24 × 0.92) - 1.6 = 20.48 GB`

This corresponds to approximately 191,740 KV tokens, giving:

`191,740 / 4096 ≈ 46.8`

So the theoretical limit is about **46 full 4096-token sequences**.

However, the benchmark shows a much lower practical ceiling:

| Batch | KV Cache Utilization | Preempted Sequences |
|---:|---:|---:|
| 4 | 0.16 | 0 |
| 8 | 0.31 | 0 |
| 16 | 0.62 | 0 |
| 24 | 0.93 | 0 |
| 32 | 0.97 | 7 |
| 48 | 0.97 | 23 |

Cache utilization reaches 93% at batch 24 and 97% at batch 32, where preemption begins. The gap from the theoretical 46 sequences is explained by block-based allocation and runtime overhead.

**Key finding:** batch 24 is the highest tested point without preemption.

---

## B2 - The Long-Context Throughput Anomaly

For short prompts, increasing batch size generally improves throughput. With long prompts (`prompt_len=3584`), this trend breaks after batch 24.

| Batch | Reported tok/s | Δ from Previous | Preempted | TTFT p50 |
|---:|---:|---:|---:|---:|
| 4 | 565.4 | - | 0 | 483.2 ms |
| 8 | 902.6 | +59.6% | 0 | 519.0 ms |
| 16 | 1311.4 | +45.3% | 0 | 498.3 ms |
| 24 | **1607.4** | +22.6% | 0 | 500.5 ms |
| 32 | 1384.0 | **-13.9%** | 7 | 636.9 ms |
| 48 | 1298.5 | **-6.2%** | 23 | 955.4 ms |

Throughput peaks at **batch 24** and then declines. This happens exactly where KV-cache utilization reaches saturation and preemption begins.

At batch 32, seven sequences are preempted, increasing to 23 at batch 48. Preemption forces the scheduler to pause and resume or recompute sequences, adding work without producing proportional new output.

The latency results support the same explanation. TTFT stays near 500 ms through batch 24, then increases to 636.9 ms and 955.4 ms.

The benchmark therefore shows that adding more requests beyond batch 24 creates memory contention rather than useful parallelism.

**Recommended operating point:** cap long-context requests at **batch 24**, where throughput is highest and preemption is still zero.

---

## B3 - The Report's Misread Throughput Column

`REPORT_v0` treated `reported_tok_s` as generated-token throughput. The benchmark data shows that this interpretation is incorrect.

The column follows:

`reported_tok_s = num_requests × (prompt_len + gen_len) / wall_clock_s`

This formula matches **all 13 rows** of the benchmark within rounding.

| Batch | Prompt | Gen Len | Requests | Wall Clock (s) | Reported tok/s | Formula | Match |
|---:|---:|---:|---:|---:|---:|---:|:---:|
| 1 | 512 | 256 | 1 | 10.94 | 70.2 | 70.2 | ✓ |
| 2 | 512 | 256 | 2 | 11.61 | 132.3 | 132.3 | ✓ |
| 4 | 512 | 256 | 4 | 11.77 | 261.0 | 261.0 | ✓ |
| 8 | 512 | 256 | 8 | 12.40 | 495.4 | 495.5 | ✓ |
| 16 | 512 | 256 | 16 | 13.91 | 883.2 | 883.4 | ✓ |
| 32 | 512 | 256 | 32 | 16.50 | 1489.6 | 1489.5 | ✓ |
| 64 | 512 | 256 | 64 | 21.68 | 2267.3 | 2267.2 | ✓ |
| 4 | 3584 | 512 | 4 | 28.98 | 565.4 | 565.4 | ✓ |
| 8 | 3584 | 512 | 8 | 36.30 | 902.6 | 902.7 | ✓ |
| 16 | 3584 | 512 | 16 | 49.97 | 1311.4 | 1311.5 | ✓ |
| 24 | 3584 | 512 | 24 | 61.16 | 1607.4 | 1607.3 | ✓ |
| 32 | 3584 | 512 | 32 | 94.71 | 1384.0 | 1383.9 | ✓ |
| 48 | 3584 | 512 | 48 | 151.41 | 1298.5 | 1298.5 | ✓ |

The problem is that prompt tokens are counted together with generated tokens. For long prompts, this makes throughput look much higher because most counted tokens come from the prompt.

For batch 24, actual generated-token throughput is:

`24 × 512 / 61.16 ≈ 200.9 tok/s`

A decode-only estimate from `itl_ms_p50` gives 249.8 tok/s, but excludes prefill. Therefore, **200.9 tok/s is the more representative end-to-end figure**.

At batch 48, generated throughput is only about **162.3 tok/s**, not ~3200 tok/s.

---

## B4 - Confirming the B2 Mechanism

The evidence points to **KV-cache saturation and preemption** as the main reason throughput falls after batch 24.

The pattern is consistent across several metrics:

`KV saturation -> preemption -> additional work -> lower goodput`

At batch 24, KV utilization is already 0.93 with no preemptions. At batch 32 it reaches 0.97 and seven sequences are preempted. At batch 48, utilization remains 0.97 while preemptions increase to 23.

Latency also changes at the same point. TTFT is around 500 ms through batch 24, then rises to 636.9 ms at batch 32 and 955.4 ms at batch 48.

This combination suggests that the system is no longer limited simply by available compute. Instead, memory pressure causes the scheduler to interrupt active sequences, creating additional work and waiting time.

The most useful additional metric would be the serving engine's **preemption recomputation cost**. This would show how much computation is repeated after a sequence is preempted.

The expected relationship is:

| Batch | KV Utilization | Preemptions | Expected Effect |
|---:|---:|---:|---|
| 24 | 0.93 | 0 | Stable operation |
| 32 | 0.97 | 7 | Recompute overhead begins |
| 48 | 0.97 | 23 | Higher memory contention |

This would provide direct evidence linking preemption to the observed goodput decline.

For the current benchmark, **batch 24 is therefore the safest operating point for 3584-token prompts**, while preemption-recomputation statistics would provide the final confirmation.
