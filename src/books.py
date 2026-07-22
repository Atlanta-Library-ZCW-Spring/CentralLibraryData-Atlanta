import csv
import json
from pathlib import Path


INPUT_FILE = Path("tcc_ceds_music.csv")
OUTPUT_FILE = Path("music_data.json")
MAX_ROWS = 10

REQUIRED_COLUMNS = [
    "artist_name",
    "track_name",
    "genre",
    "release_date",
]


def extract_music_data(input_file, max_rows=None):

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input file was not found: {input_file}"
        )

    music_data = []

    with input_file.open(
        mode="r",
        encoding="utf-8",
        newline=""
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError("The CSV file does not contain a header row.")

        missing_columns = [
            column
            for column in REQUIRED_COLUMNS
            if column not in reader.fieldnames
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        for index, row in enumerate(reader):

            if max_rows is not None and index >= max_rows:
                break

            song = {
                "artist_name": row["artist_name"].strip(),
                "track_name": row["track_name"].strip(),
                "genre": row["genre"].strip(),
                "release_date": row["release_date"].strip(),
            }

            music_data.append(song)

    return music_data


def write_json(
    data: list[dict],
    output_file: Path
) -> None:
    """
    Write extracted data to a JSON file.
    """

    with output_file.open(
        mode="w",
        encoding="utf-8"
    ) as json_file:

        json.dump(
            data,
            json_file,
            indent=4,
            ensure_ascii=False
        )


def main() -> None:
    music_data = extract_music_data(
        input_file=INPUT_FILE,
        max_rows=MAX_ROWS
    )

    write_json(
        data=music_data,
        output_file=OUTPUT_FILE
    )

    print("Extraction completed successfully.")
    print(f"Records extracted: {len(music_data)}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()