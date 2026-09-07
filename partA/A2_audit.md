# Audit: fertility.py

## 1. Purpose

The audit checks the potential flaws in the codebase `fertility.py`.

Thereafter, the code has been corrected to measure tokenizers efficiency across English, Hindi, Malayalam, and Tamil using GPT-2 and XLM-RoBERTa.

The main A2 issues checked were:

-Incorrect interpretation of compression
- Lowercasing effects
- Word splitting errors
- Code point vs grapheme counting
- Mean-of-ratios vs pooled calculation

## 2. Key Findings

### Fix 1: Lowercasing

The A2 isolation test showed:

| Language | Original tokens | Lowercased tokens |
|---|---:|---:|
| English | 24 | 23 |
| Hindi | 136 | 136 |

The notebook comment expected no change for Hindi, but the actual output shows a change from 5 to 4 tokens.

Therefore, this should be treated as an observed behavior, not evidence that lowercasing has no effect on Hindi.

### Fix 2: Word Splitting

The A2 test injected an extra space and compared:

- `split(" ")` -> 6 words
- `split()` -> 5 words

This confirms that `split(" ")` can create empty-string tokens when multiple spaces occur.

Using `split()` after whitespace normalization is therefore the correct approach.

### Fix 3: Pooled vs Mean-of-Ratios

This was the strongest numerical finding in A2.

For English:

| Method | Fertility |
|---|---:|
| Mean of sentence-level ratios | 1.5939 |
| Pooled calculation | 1.2599 |

Relative difference: **26.5%**

This confirms that averaging sentence-level fertility ratios can produce a substantially different result from calculating fertility using pooled totals.

The corrected implementation therefore uses `fertility = total_tokens / total_words` instead of averaging sentence-level ratios.

### Fix 4: Compression Metric

This is a **conceptual bug**, with a real code calculation bug.

The code **incorrectly** calculates describing and documenting it as "compression":

`tokens / characters`


It is a fertility-style metric using characters as the denominator. Lower values mean fewer tokens are needed per character, which indicates better token efficiency.

**Real compression** uses the inverse relationship:

`characters / tokens`

or:

`bytes / tokens`

Here, higher values are better because each token represents more content.

Look at the difference here: 


| tokenizer          | lang | char_per_token | token_per_char |
|--------------------|------|----------------|----------------|
| gpt2               | eng  | 5.049          | 0.1981         |
| gpt2               | hin  | 0.771          | 1.2975         |
| gpt2               | mal  | 0.425          | 2.3543         |
| gpt2               | tam  | 0.424          | 2.3606         |
| xlm-roberta-base   | eng  | 4.530          | 0.2207         |
| xlm-roberta-base   | hin  | 3.736          | 0.2677         |
| xlm-roberta-base   | mal  | 3.812          | 0.2623         |
| xlm-roberta-base   | tam  | 3.883          | 0.2575         |



Therefore, calling `tokens/characters` "compression" can mislead readers into thinking that a lower value is worse, when the opposite is true.

## 3. Suspicious Flaws

### `random.seed(1337)` and unused `random`

Nothing else in `fertility.py` calls `random.*`, so the seed has no effect on the current output.

This is dead code and can be removed.

To verify:

`delete random.seed(1337) -> rerun -> compare outputs`

The output should remain byte-identical.

### NFC Normalization

`unicodedata.normalize("NFC", line)` is likely valid rather than a bug.

NFC helps keep equivalent Unicode representations consistent before tokenization.

However, this should be verified experimentally:

`normalization ON vs OFF -> source-mixed sample -> compare token counts`

If the numbers remain similar or NFC reduces representation-related variation, the normalization is behaving as intended.

## 4. Corrected Metric Definitions

### Fertility

`fertility = tokens / words`

Higher fertility means more tokenizer tokens are required per word.

### Tokenization Density

`tokens / grapheme`

This measures how many tokenizer tokens are generated per grapheme.

### Compression

The correct compression direction is:

`graphemes / tokens`

Higher values mean each token represents more grapheme content.

Therefore, `tokens/grapheme` should not be called compression.

## 5. A2 Results


| tokenizer        | lang | n_lines | fertility_tok_per_word | compression_grapheme_per_tok |
|------------------|------|---------|-------------------------|------------------------------|
| gpt2             | eng  | 150     | 1.297                   | 5.049                        |
| gpt2             | hin  | 150     | 7.251                   | 0.551                        |
| gpt2             | mal  | 150     | 23.757                  | 0.255                        |
| gpt2             | tam  | 150     | 22.108                  | 0.294                        |
| xlm-roberta-base | eng  | 150     | 1.445                   | 4.530                        |
| xlm-roberta-base | hin  | 150     | 1.496                   | 2.672                        |
| xlm-roberta-base | mal  | 150     | 2.647                   | 2.290                        |
| xlm-roberta-base | tam  | 150     | 2.412                   | 2.696                        |



