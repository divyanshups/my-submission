# AI_USAGE.md

## How AI Helped

AI was used mainly as a reasoning and review assistant during the project.

It helped with:
- Understanding the problem statement clearly and thoroughly thus helping me approach for the solution.
- Reviewing the fertility analysis and identifying potential issues in token counting, whitespace handling, normalization, and aggregation.
- Suggesting experiments to check whether a suspected issue was actually a bug.
- Checking calculations and interpreting benchmark results.
- Structuring the notebook around `hypothesis -> experiment -> result -> revision`.
- Helping explain technical findings clearly and turn them into concise report sections.
- Assisting with code and documentation where appropriate.

## Where AI Misled Me

AI suggestions were not treated as ground truth. Important claims were checked against the actual code, notebook outputs, and benchmark logs.

### Fertility Analysis

The biggest instance where AI misled me was while reviewing `fertility.py`. AI initially classified a **conceptual error as a normal implementation error**, while I was specifically looking for actual implementation errors. This could have led me to modify working code instead of questioning whether the metric definition itself was conceptually correct.

This highlighted the importance of distinguishing between:
- Implementation errors, where the code does not correctly implement the intended metric.
- Conceptual errors, where the metric or interpretation itself is incorrect.

AI also expected a large grapheme-counting difference, but the actual A2 experiment showed code points = 16 and grapheme clusters = 16. Therefore, the expected overcount was not demonstrated by the test, and the implementation was not changed based only on the hypothesis, because the dataset used here, didn't had proper examples.

NFC normalization was also initially treated as suspicious, but there was not enough experimental evidence to classify it as a bug, so it was kept pending further isolation testing.


### Benchmark Throughput

AI initially treated the logged `reported_tok_s` as generated-token throughput. After rechecking the benchmark calculation, it was found to count both prompt and generated tokens. This inflated the apparent throughput for long-prompt workloads.

The analysis was therefore revised to use generated-token goodput for the final interpretation.

## Final Approach

AI was used for hypothesis generation, code review, calculations, interpretation, and documentation, but important claims were verified against actual experiments and outputs.

When AI suggestions and experimental evidence disagreed, the **code, logs, and measured results were treated as authoritative**.