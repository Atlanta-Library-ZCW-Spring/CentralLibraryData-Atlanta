import ast
import pandas as pd

def parse_list(value):
    """
    Convert a string containing a list of dictionaries
    into a real Python list.

    Invalid or missing values become an empty list.
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
        
def extract_names(items):
    """
    Extract the 'name' value from a list of dictionaries.

    Used for genres and keywords.
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
    Extract the first five cast member names.
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
        if not isinstance(person, dict):
            continue

        if person.get("job") == "Director":
            return person.get("name")

    return ""

movies_df = pd.read_csv("movies_metadata.csv",low_memory=False) # Read the movies metadata CSV file into a pandas DataFrame
credits_df = pd.read_csv("credits.csv")
keywords_df = pd.read_csv("keywords.csv")

movies_df = movies_df[
    [
        "id",
        "title",
        "runtime",
        "genres"
    ]
].copy()
# Create a copy of the DataFrame with selected columns: 'id', 'title', 'runtime', and 'genres'
credits_df = credits_df[
    [
        "id",
        "cast",
        "crew"
    ]
].copy()

keywords_df = keywords_df[
    [
        "id",
        "keywords"
    ]
].copy()

movies_df["id"] = pd.to_numeric(movies_df["id"],errors="coerce")

movies_df["runtime"] = pd.to_numeric(movies_df["runtime"], errors="coerce")

movies_df = movies_df.dropna(subset=["id"])

movies_df["id"] = movies_df["id"].astype(int)

movies_df["title"] = (movies_df["title"].fillna("").astype(str).str.strip())

movies_df = movies_df.drop_duplicates(subset=["id"])


# -----------------------------------
# 4. Clean credits DataFrame
# -----------------------------------

credits_df["id"] = pd.to_numeric(credits_df["id"],errors="coerce")

credits_df = credits_df.dropna(subset=["id"])

credits_df["id"] = credits_df["id"].astype(int)

credits_df = credits_df.drop_duplicates(subset=["id"])


# -----------------------------------
# 5. Clean keywords DataFrame
# -----------------------------------

keywords_df["id"] = pd.to_numeric(keywords_df["id"],errors="coerce")

keywords_df = keywords_df.dropna(subset=["id"])

keywords_df["id"] = keywords_df["id"].astype(int)

keywords_df = keywords_df.drop_duplicates(subset=["id"])

# Join Movies and Credits

final_df = pd.merge(movies_df, credits_df, on="id", how="left")
final_df = pd.merge(final_df, keywords_df, on="id", how="left")
print("Merge completed.")
print("Rows after merge:", len(final_df))

# Check Merge Before Parsing

print("\nColumns after merge:")

print(final_df.columns.tolist())

print("\nFirst five merged records:")

print(
    final_df[
        [
            "id",
            "title",
            "runtime",
            "genres",
            "cast",
            "crew",
            "keywords"
        ]
    ].head())

# Transform: Parse Complex Columns

final_df["genres_parsed"] = final_df["genres"].apply(parse_list)

final_df["cast_parsed"] = final_df["cast"].apply(parse_list)

final_df["crew_parsed"] = final_df["crew"].apply(parse_list)

final_df["keywords_parsed"] = final_df["keywords"].apply(parse_list)

# Transform: Extract Simple Values

final_df["genre_names"] = final_df["genres_parsed"].apply(extract_names)

final_df["top_cast"] = final_df["cast_parsed"].apply(lambda cast_list: extract_top_cast(cast_list,cast_limit=5))

final_df["director"] = final_df["crew_parsed"].apply(extract_director)

final_df["keyword_names"] = final_df["keywords_parsed"].apply(extract_names)

# Create Clean Final Dataframe

clean_df = final_df[
    [
        "id",
        "title",
        "runtime",
        "genre_names",
        "top_cast",
        "director",
        "keyword_names"
    ]
].copy()

# Validate Final Data

print("\nFinal DataFrame columns:")

print(clean_df.columns.tolist())

print("\nFinal row count:", len(clean_df))

print("\nMissing values:")

print(clean_df.isnull().sum())

print(
    "\nDuplicate movie IDs:",
    clean_df["id"].duplicated().sum()
)
# Display Toy Story
toy_story_df = clean_df[clean_df["id"] == 862]

print("\nToy Story parsed record:")

print(toy_story_df.to_string(index=False))

# LOAD: Export Full DATASET

clean_df.to_csv("final_movies.csv",index=False)

clean_df.to_json("final_movies.json",orient="records",indent=4,force_ascii=False)

# Load: Export First 20 Records

first_20_df = clean_df.head(20)

first_20_df.to_json("final_movies_20.json",orient="records",indent=4,force_ascii=False)

# Completion Message

print("\nETL pipeline completed successfully.")

print("Created: final_movies.csv")
print("Created: final_movies.json")
print("Created: final_movies_20.json")
