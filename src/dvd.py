import ast
import os
from pathlib import Path

import pandas as pd
import requests


# ============================================================
# 1. Helper Functions
# ============================================================

def parse_list(value):
    """
    Convert a string containing a list of dictionaries
    into a Python list.
    """
    if pd.isna(value):
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        try:
            parsed_value = ast.literal_eval(value)

            if isinstance(parsed_value, list):
                return parsed_value

        except (ValueError, SyntaxError):
            return []

    return []


def extract_names(items):
    """
    Extract the 'name' value from a list of dictionaries.
    Used for movie genres.
    """
    names = []

    for item in items:
        if isinstance(item, dict):
            name = item.get("name")

            if name:
                names.append(name)

    return names


def extract_top_cast(cast_list, cast_limit=5):
    """
    Extract the first cast-member names,
    up to the specified cast limit.
    """
    cast_names = []

    for person in cast_list[:cast_limit]:
        if isinstance(person, dict):
            name = person.get("name")

            if name:
                cast_names.append(name)

    return cast_names


def extract_director(crew_list):
    """
    Extract the director's name from the crew list.
    """
    for person in crew_list:
        if (
            isinstance(person, dict)
            and person.get("job") == "Director"
        ):
            return person.get("name", "")

    return ""


# ============================================================
# 2. Extract: Read CSV Files
# ============================================================

movies_df = pd.read_csv(
    "movies_metadata.csv",
    low_memory=False
)

credits_df = pd.read_csv("credits.csv")


# ============================================================
# 3. Select Required Columns
# ============================================================

movies_df = movies_df[
    [
        "id",
        "title",
        "runtime",
        "genres"
    ]
].copy()

credits_df = credits_df[
    [
        "id",
        "cast",
        "crew"
    ]
].copy()


# ============================================================
# 4. Clean Movies DataFrame
# ============================================================

movies_df["id"] = pd.to_numeric(
    movies_df["id"],
    errors="coerce"
)

movies_df["runtime"] = pd.to_numeric(
    movies_df["runtime"],
    errors="coerce"
)

# Remove rows without a valid movie ID
movies_df = movies_df.dropna(subset=["id"])

movies_df["id"] = movies_df["id"].astype(int)

movies_df["title"] = (
    movies_df["title"]
    .fillna("")
    .astype(str)
    .str.strip()
)

# Remove duplicate TMDB movie IDs
movies_df = movies_df.drop_duplicates(
    subset=["id"]
)


# ============================================================
# 5. Clean Credits DataFrame
# ============================================================

credits_df["id"] = pd.to_numeric(
    credits_df["id"],
    errors="coerce"
)

credits_df = credits_df.dropna(
    subset=["id"]
)

credits_df["id"] = credits_df["id"].astype(int)

credits_df = credits_df.drop_duplicates(
    subset=["id"]
)


# ============================================================
# 6. Merge Movies and Credits
# ============================================================

final_df = pd.merge(
    movies_df,
    credits_df,
    on="id",
    how="left"
)


# ============================================================
# 7. Parse Complex Columns
# ============================================================

final_df["genres_parsed"] = (
    final_df["genres"].apply(parse_list)
)

final_df["cast_parsed"] = (
    final_df["cast"].apply(parse_list)
)

final_df["crew_parsed"] = (
    final_df["crew"].apply(parse_list)
)


# ============================================================
# 8. Create Simplified Columns
# ============================================================

final_df["genre_names"] = (
    final_df["genres_parsed"].apply(extract_names)
)

final_df["top_cast"] = (
    final_df["cast_parsed"].apply(
        lambda cast_list: extract_top_cast(
            cast_list,
            cast_limit=5
        )
    )
)

final_df["director"] = (
    final_df["crew_parsed"].apply(extract_director)
)


# ============================================================
# 9. Create Clean DataFrame
# ============================================================

clean_df = final_df[
    [
        "id",
        "title",
        "runtime",
        "genre_names",
        "top_cast",
        "director"
    ]
].copy()


# ============================================================
# 10. TMDB API Configuration
# ============================================================

TMDB_TOKEN = os.getenv("TMDB_TOKEN")

if not TMDB_TOKEN:
    raise ValueError(
        "TMDB_TOKEN was not found. "
        "Add it to your environment and restart VS Code."
    )

HEADERS = {
    "Authorization": f"Bearer {TMDB_TOKEN}",
    "accept": "application/json"
}

# Reuse the same connection for multiple requests
session = requests.Session()
session.headers.update(HEADERS)


def get_mpa_rating(tmdb_id):
    """
    Return the first available US MPA certification
    for a movie from the TMDB API.
    """
    url = (
        f"https://api.themoviedb.org/3/movie/"
        f"{tmdb_id}/release_dates"
    )

    try:
        response = session.get(
            url,
            timeout=15
        )

        response.raise_for_status()

    except requests.RequestException as error:
        print(
            f"TMDB request failed for movie "
            f"{tmdb_id}: {error}"
        )
        return ""

    try:
        data = response.json()

    except requests.JSONDecodeError:
        print(
            f"TMDB returned invalid JSON "
            f"for movie {tmdb_id}."
        )
        return ""

    for country in data.get("results", []):
        if country.get("iso_3166_1") == "US":

            for release in country.get(
                "release_dates",
                []
            ):
                rating = (
                    release
                    .get("certification", "")
                    .strip()
                )

                if rating:
                    return rating

    return ""


# ============================================================
# 11. Test the TMDB Function
# ============================================================

# ============================================================
# Process only the first 100 movies
# ============================================================

clean_df = clean_df.head(100).copy()

print(f"Processing {len(clean_df)} movies...")


# ============================================================
# 12. Add MPA Ratings
# ============================================================

# This makes one API request for each movie.
clean_df["mpa_rating"] = (
    clean_df["id"].apply(get_mpa_rating)
)


# Put mpa_rating next to runtime
clean_df = clean_df[
    [
        "id",
        "title",
        "runtime",
        "mpa_rating",
        "genre_names",
        "top_cast",
        "director"
    ]
].copy()

print("\nMPA ratings added to clean_df.")

print(
    clean_df[
        [
            "title",
            "mpa_rating"
        ]
    ].head()
)


# ============================================================
# 13. Validate Final Data
# ============================================================

print("\nFinal DataFrame columns:")
print(clean_df.columns.tolist())

print("\nFinal row count:")
print(len(clean_df))

print("\nMissing values:")
print(clean_df.isnull().sum())

print("\nDuplicate movie IDs:")
print(clean_df["id"].duplicated().sum())

print("\nMPA rating distribution:")

print(
    clean_df["mpa_rating"]
    .replace("", "Not available")
    .value_counts(dropna=False)
)

# ============================================================
# 14. Export Full Dataset as JSON
# ============================================================
# Export the JSON file

clean_df.to_json(
    "final_movies.json",
    orient="records",
    indent=4,
    force_ascii=False
)

print("final_movies.json created successfully!")
