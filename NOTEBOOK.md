# NOTEBOOK.md

**Format: hypothesis → experiment → result → revision**

## Session 1: `fertility.py` Audit

**Hypothesis:** Check compression, `random.seed()`, NFC, `.lower()`, `.split(" ")`, `len(line)`, and per-line aggregation.

**Key findings:**

1. `.lower()` changes English tokenization; A2 showed Hindi also changed from 24 to 23 tokens.
2. `line.split(" ")` can inflate word counts because repeated spaces create empty strings.
3. `len(line)` counts Unicode code points, not grapheme clusters. 
Grapheme clusters are generally closer to what a user perceives as a single character, especially in Indic scripts where a visible character can consist of multiple Unicode code points.
4. Per-line mean gives short and long sentences equal weight.
5. Word count is not a fair cross-language denominator because Indic words can contain more morphology.
6. NFC was initially treated as a decoy but requires an isolation experiment before being considered proven.

**Conceptual correction:** `tokens/character` is fertility, not compression. Real compression is `characters/token`, where higher is better.

## Session 2: Corpus Preparation

**Hypothesis:** The earlier small ad hoc corpus was not strong enough for cross-language evaluation.

**Action:** Used FLORES-200 `dev` from `yash9439/flores200` because it is parallel, ungated, and parquet-backed. Languages: English, Hindi, Malayalam, and Tamil.

**Result:** The evaluation corpus contains **90 sentence lines per language**, sampled using Line Numbers `[26, 28, 31, 33, 90, 96, 105, 115, 143, 204, 224, 229, 239, 251, 282, 433, 518, 559, 575, 605, 617, 655, 666, 693, 719, 734, 755, 759, 760, 914]`. The source is formal, professionally translated FLORES content from Wikinews, Wikijunior, and Wikivoyage.

Preprocessing uses NFKC, BOM removal, zero-width removals and whitespace normalization.

**Limitation:** The corpus is small and formal, so results are directional and may not represent conversational, code-switched, legal, medical, or other domain-specific text.

## Session 3: Corpus and Normalization Checks

`clean_indic_text()` uses NFKC, while `fertility.py` uses NFC. These are different normalization steps and have not been tested together.

The fertility notebook uses **15 sentence lines per language**. This keeps the parallel-sentence comparison based on the actual evaluation sentences rather than raw file formatting.

## Session 4: A3 Cross-Tokenizer Analysis

**Hypothesis:** Compare GPT-2 and XLM-RoBERTa on the same parallel corpus using multiple denominators.

**Action:** Calculated:

- `tok/word`
- `tok/grapheme`
- `tok/byte`
- `tok/parallel-sentence`

**Result:** GPT-2 fragments Malayalam and Tamil heavily, while XLM-R significantly reduces the gap.


| Tokenizer | Language | Tok / Word | Tok / Grapheme | Tok / Byte | Tok / Parallel Sentence |
|---|---|---:|---:|---:|---:|
| GPT-2 | English | 1.297 | 0.1981 | 0.1980 | 16.83 |
| GPT-2 | Hindi | 7.251 | 1.8140 | 0.5608 | 110.85 |
| GPT-2 | Malayalam | 23.757 | 3.9194 | 0.9441 | 219.51 |
| GPT-2 | Tamil | 22.108 | 3.4001 | 0.9477 | 232.73 |
| XLM-RoBERTa-base | English | 1.445 | 0.2207 | 0.2207 | 18.76 |
| XLM-RoBERTa-base | Hindi | 1.496 | 0.3742 | 0.1157 | 22.87 |
| XLM-RoBERTa-base | Malayalam | 2.647 | 0.4367 | 0.1052 | 24.46 |
| XLM-RoBERTa-base | Tamil | 2.412 | 0.3709 | 0.1034 | 25.39 |


### Denominator Revision

`tok/word` is rejected as the main routing metric because word structure differs across languages.

`tok/byte` is also rejected because Unicode encoding naturally uses more bytes for many Indic scripts.

**Recommended metric:** `tok/parallel-sentence`, because aligned sentences keep the underlying translated content approximately constant.

This requires genuine sentence alignment, not just equal line counts.


### Main Conclusion

GPT-2 has very poor token efficiency for the Indic languages in this corpus:

- Hindi: **6.59x** English
- Malayalam: **13.05x** English
- Tamil: **13.83x** English

XLM-R reduces the gap to:

- Hindi: **1.22x**
- Malayalam: **1.30x**
- Tamil: **1.35x**

Therefore, an Indic-aware multilingual tokenizer is preferable to an English-centric tokenizer for multilingual workloads.

The **1.2x to 1.4x** range should be treated as an initial directional estimate, not a fixed production constant.


## Session 5: Capacity Reconciliation

**KV cache:** Using 8 KV heads gives **114,688 bytes/token** and a theoretical maximum of about **46 concurrent 4096-token sequences**.

**Observed capacity:** Cache utilization reaches 0.93 at batch 24 and 0.97 at batch 32, with preemption beginning at higher batches.

**Throughput:** Scaling is non-linear. Peak throughput is **1607.4 tok/s at batch 24**, then decreases at larger batches as preemptions increase.

**Goodput correction:** The reported ~3200 tok/s figure conflates prompt and generated tokens. Honest batch-24 generated-token throughput is **200.9 tok/s**.

The alternative per-request rate is **249.8 tok/s**, about **24.3% higher**, so it should be treated as an upper bound rather than equivalent goodput.

## Session 6: Localization Decision

**Hypothesis:** If the base model already understands casual language across all six languages, the main issue is elicitation rather than missing model capability. Prompt engineering can therefore be tested before moving to SFT or a dedicated rewriter.

**Decision:** Use **prompt engineering with curated few-shot exemplars**.

The approach assumes:

- The base model already has sufficient understanding of all six languages.
- A 7-8B multilingual model can generate candidates efficiently on the A100.
- Self-consistency can provide an automated quality filter.
- A small set of strong examples can teach the desired casual style.

**Experiment:** Generate 500 candidates per language, apply automated filtering, and select **8 gold exemplars per language** for the final system prompt.

Human review is used for Hindi and Kannada, where native-speaker validation is available. The target is a **naturalness score of ≥4/5** on held-out production-style prompts.

For Tamil, Telugu, Bengali, and Marathi, only automated filtering is used. A self-consistency agreement of **≥70%** is treated as a passing proxy.

**Main caveat:** Four of the six languages have no human validation before launch. Therefore, the automated 70% agreement threshold does not guarantee native-level naturalness.

**Kill criterion:** If Hindi or Kannada scores below **3/5 by Day 10** after applying the exemplars, stop the few-shot approach and move to a small rewriter model or SFT.

**Day-1 experiment:** Start with Hindi, generate 20 responses, apply self-consistency filtering, select the top 5, and have the native reviewer score them the same day.


