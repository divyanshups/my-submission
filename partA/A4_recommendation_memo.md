# Recommendation Memo

## Key Finding

The analysis shows that **tokenizer choice has a much bigger impact than language choice**.

Using the multilingual **xlm-roberta-base** tokenizer, the token cost per equivalent sentence is only slightly higher than English:

- **Hindi: ~1.22x English**
- **Tamil: ~1.35x English**
- **Malayalam: ~1.30x English**

In comparison, **GPT-2** produces much higher token counts for Indic languages:

- **Hindi: ~6.6x English**
- **Tamil: ~13.8x English**
- **Malayalam: ~13.0x English**

This suggests that the large cost difference is mainly caused by **poor Indic vocabulary coverage in GPT-2**, rather than the languages themselves being inherently expensive to process.

## Evidence

| Tokenizer | Language | Tokens / Parallel Sentence | Relative to English |
|---|---|---:|---:|
| GPT-2 | English | 16.83 | 1.00x |
| GPT-2 | Hindi | 110.85 | **6.59x** |
| GPT-2 | Malayalam | 219.51 | **13.05x** |
| GPT-2 | Tamil | 232.73 | **13.83x** |
| XLM-RoBERTa | English | 18.76 | 1.00x |
| XLM-RoBERTa | Hindi | 22.87 | **1.22x** |
| XLM-RoBERTa | Malayalam | 24.46 | **1.30x** |
| XLM-RoBERTa | Tamil | 25.39 | **1.35x** |

## Routing Recommendation

We should **not** use English-focused tokenizers such as GPT-2 for Indic-language traffic.

A multilingual tokenizer such as **xlm-roberta-base** keeps the overhead around **1.2 to 1.4x English**, which is manageable through normal capacity planning.

**Main takeaway: We should choose the right tokenizer instead of creating separate infrastructure for each language.**

## Biggest Caveat

The analysis is based on **150 FLORES-200 sentences per language**. Production conversations may have different sentence lengths, vocabulary, and writing styles.

Therefore, treat the **1.2 to 1.4x range as an initial estimate**, not a fixed production constant.

## Production Metric

Track **tokens per request for each language** and compare them with English.

If Hindi, Tamil, or Malayalam moves significantly above the expected **~1.2 to 1.4x range**, investigate the serving pipeline for:

- Tokenizer changes
- Vocabulary issues
- Unexpected fallback paths

This makes token efficiency a **live production monitoring signal**.
