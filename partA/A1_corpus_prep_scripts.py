"""Multilingual Indic Parallel Dataset Extraction Pipeline.
Source: yash9439/flores200 (Hugging Face)

Extracts and samples random entries from the dataset, according to user specified values for "NUMBER_OF_RECORDS", "LINES_PER_RECORD"
across English, Hindi, Malayalam, and Tamil languages into individual .txt files.
"""

import random
import re
import unicodedata
from typing import List
from datasets import load_dataset

#Dataset configuration
FLORES_REPO = "yash9439/flores200"
FLORES_SPLIT = "dev"

#Language column mappings in FLORES-200
LANGUAGE_CONFIGS = {
    "eng": "eng_Latn",  # English
    "hin": "hin_Deva",  # Hindi
    "mal": "mal_Mlym",  # Malayalam
    "tamil": "tam_Taml",  # Tamil
}

#Pipeline configuration defaults
NUMBER_OF_RECORDS = 5  # Total number of records (samples) to generate
LINES_PER_RECORD = 3  # Number of lines in each record

#Sanitizes text via standardizing Unicode to NFKC, and striping non-semantic invisible codepoints while preserving Devanagari & Dravidian ZWJ/ZWNJ.
def clean_indic_text(text):
    if not text:
        return ""

    #Unicode Normalization (Form KC)
    text = unicodedata.normalize("NFKC", text)

    #Remove zero-width spaces and BOMs
    text = text.replace("\ufeff", "").replace("\u200b", "").replace("\xa0", " ")

    #Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text).strip()
    return text

#Loading the FLORES-200 dataset split using Hugging Face datasets.
def load_flores_split(repo_name, split_name):
    dataset = load_dataset(repo_name, split=split_name)
    print(f"Dataset loaded successfully. Total sentences: {len(dataset)}\n")
    return dataset

#Generating unique random starting line numbers ensuring enough remaining lines for each record.
def generate_random_ln(total_dataset_size, num_records, num_lines):
    max_start_id = total_dataset_size - num_lines + 1

    if max_start_id < 1:
        raise ValueError(
            "Dataset is smaller than the requested number of lines per record."
        )

    if num_records > max_start_id:
        raise ValueError(
            f"Requested {num_records} records, but only {max_start_id} unique starting points exist."
        )

    # Randomly sample unique starting points
    ln = random.sample(range(1, max_start_id + 1), num_records)
    ln.sort()
    return ln

#Extracting N consecutive lines starting from the given line numbers
def extract_n_lines(dataset, lang_column, ln, num_lines):
    start_idx = ln - 1
    total_rows = len(dataset)

    if 0 <= start_idx < total_rows:
        end_idx = min(start_idx + num_lines, total_rows)
        lines = [
            clean_indic_text(dataset[i][lang_column])
            for i in range(start_idx, end_idx)
        ]
        return "\n".join(lines)

    return ""

#Saving records into a .txt file separated by record dividers
def save_list_to_file(data_list, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for idx, text in enumerate(data_list, 1):
            f.write(f"--- RECORD {idx} ---\n")
            f.write(text if text else "[RECORD OUT OF RANGE]")
            f.write("\n\n" + "=" * 50 + "\n\n")

    print(f" Saved: {filename} ({len(data_list)} records)")

#Sampling random line numbers and extracting "num_lines" for each language across "num_records", and writes individual .txt files
def process_flores_records(num_records = 5, num_lines = 10):
    dataset = load_flores_split(FLORES_REPO, FLORES_SPLIT)

    ln = generate_random_ln(len(dataset), num_records, num_lines)
    print(f"Generated {num_records} random starting line numbers: {ln}\n")

    eng_list = []
    hin_list = []
    mal_list = []
    tamil_list = []

    for idx, prid in enumerate(ln, 1):
        print(
            f"--> [Record {idx}/{num_records}] Extracting {num_lines} lines starting at PRID {prid}:"
        )

        eng_text = extract_n_lines(
            dataset, LANGUAGE_CONFIGS["eng"], prid, num_lines
        )
        hin_text = extract_n_lines(
            dataset, LANGUAGE_CONFIGS["hin"], prid, num_lines
        )
        mal_text = extract_n_lines(
            dataset, LANGUAGE_CONFIGS["mal"], prid, num_lines
        )
        tamil_text = extract_n_lines(
            dataset, LANGUAGE_CONFIGS["tamil"], prid, num_lines
        )

        eng_list.append(eng_text)
        hin_list.append(hin_text)
        mal_list.append(mal_text)
        tamil_list.append(tamil_text)

        print(
            f"    - English: {'Done' if eng_text else 'Failed'} | "
            f"Hindi: {'Done' if hin_text else 'Failed'} | "
            f"Malayalam: {'Done' if mal_text else 'Failed'} | "
            f"Tamil: {'Done' if tamil_text else 'Failed'}"
        )

    print("\nWriting language outputs to .txt files...")
    save_list_to_file(eng_list, "eng_output.txt")
    save_list_to_file(hin_list, "hin_output.txt")
    save_list_to_file(mal_list, "mal_output.txt")
    save_list_to_file(tamil_list, "tamil_output.txt")

    return eng_list, hin_list, mal_list, tamil_list


# Execution block
if __name__ == "__main__":
    # Specify the number of records and lines per record here
    eng_list, hin_list, mal_list, tamil_list = process_flores_records(
        num_records=NUMBER_OF_RECORDS, num_lines=LINES_PER_RECORD
    )