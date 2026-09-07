## Key Findings

The two tables above show a major difference between the two tokenizers.

### 1. GPT-2 greatly overestimates Indic token cost

From the `tok_per_parallel_sentence` column shows:

- English: **16.83**
- Hindi: **110.85**, about **6.6x English**
- Malayalam: **219.51**, about **13.0x English**
- Tamil: **232.73**, about **13.8x English**

This happens because GPT-2 is mainly optimized for English and has poor vocabulary coverage for Indic scripts. It breaks Indic text into many smaller tokens.

So these large numbers mainly measure **tokenizer vocabulary coverage**, not the true computational cost of the languages.

### 2. XLM-RoBERTa gives a much more realistic comparison

With `xlm-roberta-base`:

- English: **18.76**
- Hindi: **22.87**, about **1.22x**
- Malayalam: **24.46**, about **1.30x**
- Tamil: **25.39**, about **1.35x**

The gap becomes much smaller because XLM-RoBERTa was designed for multilingual text and has better Indic-script coverage.

### 3. Why use tokens per parallel sentence?

For routing and cost planning, **tokens per parallel sentence** is a useful metric because it compares the tokenization cost of approximately the **same underlying content** across languages.

A parallel sentence expresses the same content in different languages. This makes it fairer than **tokens per word**, since a word is not necessarily an equivalent linguistic unit across languages. Different languages can express the same meaning using different numbers of words.

The results from are:

| Tokenizer | Language | Tok/Word | Tok/Grapheme | Tok/Byte | Tok/Parallel Sentence |
|---|---|---:|---:|---:|---:|
| GPT-2 | English | 1.297 | 0.1981 | 0.1980 | 16.83 |
| GPT-2 | Hindi | 7.251 | 1.8140 | 0.5608 | 110.85 |
| GPT-2 | Malayalam | 23.757 | 3.9194 | 0.9441 | 219.51 |
| GPT-2 | Tamil | 22.108 | 3.4001 | 0.9477 | 232.73 |
| XLM-RoBERTa-base | English | 1.445 | 0.2207 | 0.2207 | 18.76 |
| XLM-RoBERTa-base | Hindi | 1.496 | 0.3742 | 0.1157 | 22.87 |
| XLM-RoBERTa-base | Malayalam | 2.647 | 0.4367 | 0.1052 | 24.46 |
| XLM-RoBERTa-base | Tamil | 2.412 | 0.3709 | 0.1034 | 25.39 |

With XLM-RoBERTa-base, Hindi requires **1.22x**, Malayalam **1.30x**, and Tamil **1.35x** as many tokens as English for approximately the same aligned content.

This makes tokens per parallel sentence more relevant to **LLM inference cost and context-window usage** than tokens per word.

Grapheme- and byte-based metrics should be interpreted separately because scripts have different Unicode and UTF-8 representations.

**Caveat:** these results use only 150 aligned sentences per language, so they should be treated as sample-level estimates rather than universal language costs.
