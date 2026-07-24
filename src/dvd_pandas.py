import json
import os
import requests
import pandas as pd
from pathlib import Path

API_KEY = os.getenv("OMDB_API_KEY")
rating_cache = {}

credit_file = Path("data/movies-archive/credits.csv")
movies_file = Path("data/movies-archive/movies_metadata.csv")
json_file = Path("data/dvdout_panda.json")

def get_movie_rating(imdb_id, api_key):
    if not imdb_id:
        return "Not Rated"

    if imdb_id in rating_cache:
        return rating_cache[imdb_id]

    url = "https://www.omdbapi.com/"
    parameters = {"apikey": api_key, "i": imdb_id}
    try:
        response = requests.get(url, params=parameters, timeout=10)
        response.raise_for_status()
        rating = response.json().get("Rated", "NR")
    except requests.RequestException:
        rating = "NR"

    rating_cache[imdb_id] = rating
    return rating


def get_director(crew_string):
    try:
        crew_list = pd.io.json.ujson_loads(crew_string) if False else __import__("ast").literal_eval(crew_string)
    except (ValueError, SyntaxError):
        return "Unknown"

    for member in crew_list:
        if member.get("job") == "Director":
            return member.get("name")
    return "Unknown"


def get_genres(genres_string):
    try:
        genres_list = __import__("ast").literal_eval(genres_string)
        
        if not isinstance(genres_list, list):
            return "Unknown"
        names = []
        for g in genres_list:
            # each genre item is expected to be a dict with a 'name' key
            if isinstance(g, dict) and "name" in g:
                names.append(str(g["name"]))
        return ", ".join(names) if names else "Unknown"
    except (ValueError, SyntaxError):
        return "Unknown"


if __name__ == "__main__":
    movies_df = pd.read_csv(movies_file, low_memory=False).head(50)
    credits_df = pd.read_csv(credit_file)

    # id columns must match types to merge cleanly
    movies_df["id"] = movies_df["id"].astype(str)
    credits_df["id"] = credits_df["id"].astype(str)

    credits_df["director"] = credits_df["crew"].apply(get_director)

    merged_df = movies_df.merge(
        credits_df[["id", "director"]],
        on="id",
        how="left"
    )

    merged_df["director"] = merged_df["director"].fillna("Unknown")
    merged_df["genre"] = merged_df["genres"].apply(get_genres)
    merged_df["rating"] = merged_df["imdb_id"].apply(lambda x: get_movie_rating(x, API_KEY))
    merged_df["recordID"] = [f"{i:06d}" for i in range(1, len(merged_df) + 1)]

    output_df = merged_df[["recordID", "title", "director", "runtime", "rating", "genre"]]
    output_df = output_df.rename(columns={"runtime": "duration"})

    output_df.to_json(json_file, orient="records", indent=4)