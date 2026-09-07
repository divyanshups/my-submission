## Key Findings

The two tables above show a major difference between the two tokenizers.

### 1. GPT-2 greatly overestimates Indic token cost

From the `tok_per_parallel_sentence` column shows:

- English: **16.80**
- Hindi: **111.12**, about **6.6x English**
- Malayalam: **247.32**, about **14.7x English**
- Tamil: **224.44**, about **13.4x English**

This happens because GPT-2 is mainly optimized for English and has poor vocabulary coverage for Indic scripts. It breaks Indic text into many smaller tokens.

So these large numbers mainly measure **tokenizer vocabulary coverage**, not the true computational cost of the languages.

### 2. XLM-RoBERTa gives a much more realistic comparison

With `xlm-roberta-base`:

- English: **18.88**
- Hindi: **22.04**, about **1.17x**
- Malayalam: **24.56**, about **1.30x**
- Tamil: **24.44**, about **1.29x**

The gap becomes much smaller because XLM-RoBERTa was designed for multilingual text and has better Indic-script coverage.

### 3. Why use tokens per parallel sentence?

For routing and cost planning, **tokens per parallel sentence** is a useful metric because it compares the tokenization cost of approximately the **same underlying content** across languages.

A parallel sentence expresses the same content in different languages. This makes it fairer than **tokens per word**, since a word is not necessarily an equivalent linguistic unit across languages. Different languages can express the same meaning using different numbers of words.

The results from are:

| Tokenizer | Language | Tok/Word | Tok/Grapheme | Tok/Byte | Tok/Parallel Sentence |
|---|---|---:|---:|---:|---:|
| GPT-2 | English | 1.193 | 0.1915 | 0.1915 | 16.80 |
| GPT-2 | Hindi | 7.311 | 1.8204 | 0.5621 | 111.12 |
| GPT-2 | Malayalam | 24.732 | 4.1413 | 0.9530 | 247.32 |
| GPT-2 | Tamil | 20.859 | 3.3903 | 0.9488 | 224.44 |
| XLM-RoBERTa-base | English | 1.341 | 0.2152 | 0.2152 | 18.88 |
| XLM-RoBERTa-base | Hindi | 1.450 | 0.3611 | 0.1115 | 22.04 |
| XLM-RoBERTa-base | Malayalam | 2.456 | 0.4113 | 0.0946 | 24.56 |
| XLM-RoBERTa-base | Tamil | 2.271 | 0.3692 | 0.1033 | 24.44 |

With XLM-RoBERTa-base, Hindi requires **1.17x**, Malayalam **1.30x**, and Tamil **1.29x** as many tokens as English for approximately the same aligned content.

This makes tokens per parallel sentence more relevant to **LLM inference cost and context-window usage** than tokens per word.

Grapheme- and byte-based metrics should be interpreted separately because scripts have different Unicode and UTF-8 representations.

**Caveat:** these results use only 15 aligned sentences per language, so they should be treated as sample-level estimates rather than universal language costs.
