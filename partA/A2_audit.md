# Audit: fertility.py

## 1. Purpose

The audit checks whether the fertility analysis correctly measures tokenizer efficiency across English, Hindi, Malayalam, and Tamil using GPT-2 and XLM-RoBERTa.

The main A2 issues checked were:

- Lowercasing effects
- Word splitting errors
- Code point vs grapheme counting
- Mean-of-ratios vs pooled calculation
- Incorrect interpretation of compression

## 2. Key Findings

### Fix 1: Lowercasing

The A2 isolation test showed:

| Language | Original tokens | Lowercased tokens |
|---|---:|---:|
| English | 5 | 4 |
| Hindi | 5 | 4 |

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
| Mean of sentence-level ratios | 1.5804 |
| Pooled calculation | 1.2393 |

Relative difference: **27.5%**

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

| Tokenizer         | Lang | Char per Token(Real) | Token per Char (Misleading) |
|-------------------|------|----------------|----------------|
| gpt2              | eng  | 5.044          | 0.1983         |
| gpt2              | hin  | 0.763          | 1.3104         |
| gpt2              | mal  | 0.416          | 2.4015         |
| gpt2              | tam  | 0.418          | 2.3917         |
| xlm-roberta-base  | eng  | 4.645          | 0.2153         |
| xlm-roberta-base  | hin  | 3.647          | 0.2742         |
| xlm-roberta-base  | mal  | 3.635          | 0.2751         |
| xlm-roberta-base  | tam  | 4.080          | 0.2451         |

Therefore, calling `tokens/characters` "compression" can mislead readers into thinking that a lower value is worse, when the opposite is true.

## 3. Likely Decoys

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

| Tokenizer | Language | Fertility (Tok/Word) | Graphemes/Token |
|---|---|---:|---:|
| GPT-2 | English | 1.239 | 5.241 |
| GPT-2 | Hindi | 7.561 | 0.526 |
| GPT-2 | Malayalam | 23.627 | 0.244 |
| GPT-2 | Tamil | 23.444 | 0.281 |
| XLM-RoBERTa-base | English | 1.365 | 4.760 |
| XLM-RoBERTa-base | Hindi | 1.520 | 2.618 |
| XLM-RoBERTa-base | Malayalam | 2.511 | 2.293 |
| XLM-RoBERTa-base | Tamil | 2.274 | 2.898 |

