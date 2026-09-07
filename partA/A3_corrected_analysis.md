#Corrected Analysis

**Corpus:** FLORES-200, with 15 aligned sentences each for English, Hindi, Malayalam, and Tamil.  
**Analysis:** Corrected `fertility.py` logic and evaluated the built corpus using two tokenizers: GPT-2 and XLM-RoBERTa.

## Key Findings

The table above shows a major difference between the two tokenizers.

### 1. GPT-2 greatly overestimates Indic token cost

From the `tok/parallel sentence` column:

- English: **17.40**
- Hindi: **124.00**, about **7.1x English**
- Malayalam: **253.28**, about **14.6x English**
- Tamil: **270.08**, about **15.5x English**

This happens because GPT-2 is mainly optimized for English and has poor vocabulary coverage for Indic scripts. It breaks Indic text into many smaller tokens.

So these large numbers mainly measure **tokenizer vocabulary coverage**, not the true computational cost of the languages.

### 2. XLM-RoBERTa gives a much more realistic comparison

With `xlm-roberta-base`:

- English: **19.16**
- Hindi: **24.92**, about **1.30x**
- Malayalam: **26.92**, about **1.40x**
- Tamil: **26.20**, about **1.37x**

The gap becomes much smaller because XLM-RoBERTa was designed for multilingual text and has better Indic-script coverage.

### 3. Why use tokens per parallel sentence?

For routing and cost planning, **tokens per parallel sentence** is a useful metric because it compares the tokenization cost of approximately the **same underlying content** across languages.

A parallel sentence expresses the same content in different languages. This makes it fairer than **tokens per word**, since a word is not necessarily an equivalent linguistic unit across languages. Different languages can express the same meaning using different numbers of words.

The results are:

| Tokenizer | Language | Tok/Word | Tok/Grapheme | Tok/Byte | Tok/Parallel Sentence |
|---|---|---:|---:|---:|---:|
| GPT-2 | English | 1.239 | 0.1908 | 0.1908 | 17.40 |
| GPT-2 | Hindi | 7.561 | 1.9007 | 0.5681 | 124.00 |
| GPT-2 | Malayalam | 23.627 | 4.1037 | 0.9522 | 253.28 |
| GPT-2 | Tamil | 23.444 | 3.5574 | 0.9571 | 270.08 |
| XLM-RoBERTa-base | English | 1.365 | 0.2101 | 0.2101 | 19.16 |
| XLM-RoBERTa-base | Hindi | 1.520 | 0.3820 | 0.1142 | 24.92 |
| XLM-RoBERTa-base | Malayalam | 2.511 | 0.4362 | 0.1012 | 26.92 |
| XLM-RoBERTa-base | Tamil | 2.274 | 0.3451 | 0.0928 | 26.20 |

With XLM-RoBERTa-base, Hindi requires **1.30x**, Malayalam **1.40x**, and Tamil **1.37x** as many tokens as English for approximately the same aligned content.

This makes tokens per parallel sentence more relevant to **LLM inference cost and context-window usage** than tokens per word.

Grapheme- and byte-based metrics should be interpreted separately because scripts have different Unicode and UTF-8 representations.

**Caveat:** these results use only 15 aligned sentences per language, so they should be treated as sample-level estimates rather than universal language costs.

