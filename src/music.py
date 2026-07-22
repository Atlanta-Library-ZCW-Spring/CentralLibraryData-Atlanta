import json
from pathlib import Path

import pandas as pd


INPUT_FILE = Path("tcc_ceds_music.csv")
OUTPUT_FILE = Path("music_data.json")
MAX_ROWS = 12

REQUIRED_COLUMNS = [
    "artist_name",
    "track_name",
    "genre",
    "release_date",
]


def extract_music_data(input_file, max_rows=None):

    if not input_file.exists():
        raise FileNotFoundError(f"Input file was not found: {input_file}")

    # Read CSV
    music_df = pd.read_csv(input_file, dtype=str)

    # Check required columns
    missing_columns = []

    for column in REQUIRED_COLUMNS:
        if column not in music_df.columns:
            missing_columns.append(column)

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    # Keep only required columns
    music_df = music_df[REQUIRED_COLUMNS]

    # Read only first max_rows rows
    if max_rows is not None:
        music_df = music_df.head(max_rows)

    # Replace missing values with empty strings
    music_df = music_df.fillna("")

    # Remove leading/trailing spaces
    for column in REQUIRED_COLUMNS:
        music_df[column] = music_df[column].str.strip()

    # Convert DataFrame to list of dictionaries
    music_data = music_df.to_dict(orient="records")

    return music_data


def write_json(data, output_file):

    with output_file.open(mode="w", encoding="utf-8") as json_file:

        json.dump(data, json_file, indent=4,ensure_ascii=False)


def main():

    music_data = extract_music_data(input_file=INPUT_FILE, max_rows=MAX_ROWS)

    write_json(data=music_data, output_file=OUTPUT_FILE)

    print("Extraction completed successfully.")
    print(f"Records extracted: {len(music_data)}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()