# A1: Eval Corpus Documentation

## Source and Rationale

**Source:** FLORES-200 `dev` split, using the `yash9439/flores200` Hugging Face mirror.

FLORES-200 was selected because it provides **parallel, human-translated sentences**. The same sentence is available across languages, making it suitable for fair cross-language tokenization comparisons.

Earlier non-parallel datasets were rejected because they cannot guarantee that the same content is being compared across languages.

## Languages

| Code | Language | Script | Family |
|---|---|---|---|
| `eng` | English | Latin | Germanic |
| `hin` | Hindi | Devanagari | Indo-Aryan |
| `mal` | Malayalam | Malayalam | Dravidian |
| `tam` | Tamil | Tamil | Dravidian |

FLORES language-script mappings: `eng_Latn`, `hin_Deva`, `mal_Mlym`, `tam_Taml`.

## Corpus Size

The intended sample contains:

- **5 records × 3 sentences = 15 sentences per language**, however parameters like,<br>"NUMBER_OF_RECORDS", "LINES_PER_RECORD" can be changed to get more number of sentences.
- Randomly selected from the **997-sentence FLORES-200 dev split**
- Line Numbers used: `[781, 838, 854, 861, 928]`
- Each record contains 3 consecutive sentences

### Known Discrepancy

The audit notebook reports **25 lines** in the saved text files. However, the files also contain record headers and divider lines.

Therefore, **15 is the actual number of FLORES sentences per language**. The 25-line count should not be treated as corpus size.

## Domain

FLORES-200 contains professionally translated content from **Wikinews, Wikijunior, and Wikivoyage**.

The text is mostly clean, formal, general-purpose prose. It does not represent conversational, social-media, code-switched, or highly technical language.

## Preprocessing

Each sentence was cleaned using `clean_indic_text()`:

1. NFKC Unicode normalization
2. Removal of BOM and zero-width spaces
3. NBSP converted to normal spaces
4. Multiple spaces/tabs collapsed
5. Leading and trailing whitespace removed

No lowercasing, punctuation removal, or tokenization was performed at this stage.

## Limitations

This is a **small 25-sentence sample**, so it cannot represent typical language-wide tokenizer behavior. The results should be treated as directional evidence, not stable population statistics.

The corpus is also limited to **four languages and one formal domain**. It does not represent other Indic languages, conversational text, social media, code-switching, or technical domains.

**Main takeaway:** FLORES-200 provides a fair content-controlled comparison, but the sample is too small and narrow to serve as a production-wide benchmark.