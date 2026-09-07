# Recommendation Memo

## Key Finding

The analysis shows that **tokenizer choice has a much bigger impact than language choice**.

Using the multilingual **xlm-roberta-base** tokenizer, the token cost per equivalent sentence is only slightly higher than English:

- **Hindi: ~1.30x English**
- **Tamil: ~1.37x English**
- **Malayalam: ~1.40x English**

In comparison, **GPT-2** produces much higher token counts for Indic languages:

- **Hindi: ~7.1x English**
- **Tamil: ~15.5x English**
- **Malayalam: ~14.6x English**

This suggests that the large cost difference is mainly caused by **poor Indic vocabulary coverage in GPT-2**, rather than the languages themselves being inherently expensive to process.

## Evidence

| Tokenizer | Language | Tokens / Parallel Sentence | Relative to English |
|---|---|---:|---:|
| GPT-2 | English | 17.40 | 1.00x |
| GPT-2 | Hindi | 124.00 | **7.13x** |
| GPT-2 | Malayalam | 253.28 | **14.55x** |
| GPT-2 | Tamil | 270.08 | **15.52x** |
| XLM-RoBERTa | English | 19.16 | 1.00x |
| XLM-RoBERTa | Hindi | 24.92 | **1.30x** |
| XLM-RoBERTa | Malayalam | 26.92 | **1.40x** |
| XLM-RoBERTa | Tamil | 26.20 | **1.37x** |

## Routing Recommendation

We should **not** use English-focused tokenizers such as GPT-2 for Indic-language traffic.

A multilingual tokenizer such as **xlm-roberta-base** keeps the overhead around **1.3 to 1.4x English**, which is manageable through normal capacity planning.

**Main takeaway: We should choose the right tokenizer instead of creating separate infrastructure for each language.**

## Biggest Caveat

The analysis is based on only **15 FLORES-200 sentences per language**. Production conversations may have different sentence lengths, vocabulary, and writing styles.

Therefore, treat the **1.3 to 1.4x range as an initial estimate**, not a fixed production constant.

## Production Metric

Track **tokens per request for each language** and compare them with English.

If Hindi, Tamil, or Malayalam moves significantly above the expected **~1.3 to 1.4x range**, investigate the serving pipeline for:

- Tokenizer changes
- Vocabulary issues
- Unexpected fallback paths

This makes token efficiency a **live production monitoring signal**.