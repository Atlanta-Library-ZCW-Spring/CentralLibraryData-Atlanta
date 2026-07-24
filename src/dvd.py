import csv
import json
import ast
# import pandas as pd
import requests
import os

API_KEY = os.getenv("OMDB_API_KEY")
rating_cache = {}

from pathlib import Path

credit_file = Path("data/movies-archive/credits.csv")
movies_file = Path("data/movies-archive/movies_metadata.csv")
json_file = Path("data/dvdout.json")


def get_movie_rating(imdb_id, api_key):
    if not imdb_id:
        return "Not Rated"

    if imdb_id in rating_cache:
        return rating_cache[imdb_id]

    url = "https://www.omdbapi.com/"
    parameters = {
        "apikey": api_key,
        "i": imdb_id
    }
    try:
        response = requests.get(url, params=parameters, timeout=10)
        response.raise_for_status()
        movie_data = response.json()
        rating = movie_data.get("Rated", "NR")
    except requests.RequestException:
        rating = "NR"

    rating_cache[imdb_id] = rating
    return rating
    

def read_movies_metadata(movies_file):
    movies = []
    with open(movies_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            movies.append(row)

    return movies

def clean_movies(movies):
    pass

def read_credits(credit_file):
    credits = []
    with open(credit_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            credits.append(row)

    return credits

def get_director(crew_string):

    try:
        crew_list = ast.literal_eval(crew_string)
    except (ValueError, SyntaxError):
        return "Unknown"

    for crew_member in crew_list:
        if crew_member.get("job") == "Director":
            return crew_member.get("name")

    return "Unknown"

def get_genres(genres_string):
    try:
        genres_list = ast.literal_eval(genres_string)

        genre_names = []

        for genre in genres_list:
            genre_names.append(genre["name"])

        return ", ".join(genre_names)

    except (ValueError, SyntaxError):
        return "Unknown"

def merge_files(movies, credits_data):
    credit_lookup = {}

    # get the director name
    for credit in credits_data:
        credit_lookup[credit["id"]] = get_director(credit["crew"])

    merged_movies = []
    record_number = 1

    for movie in movies:
        movie_id = movie.get("id", "")
        imdb_id = movie.get("imdb_id", "")

        director = credit_lookup.get(movie_id, "Unknown")
        #rating = get_movie_rating(imdb_id, API_KEY)
        rating = "NOT YET LOADED FOR TEST"    #TESTING PURPOSES ONLY HARDCODING RATING

        merged_movie = {
            "recordID": f"{record_number:06d}",
            "title": movie.get("title", ""),
            "director": director,
            "duration": movie.get("runtime", ""),
            "rating": rating,
            "genre": get_genres(movie.get("genres", "[]"))
        }

        merged_movies.append(merged_movie)
        record_number += 1

    return merged_movies

def write_json(movies, json_file):
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(movies, file, indent=4)

    return json_file


if __name__ == "__main__":

    # print(get_movie_rating("tt0114709", API_KEY))

    movies = read_movies_metadata(movies_file)
    movies_to_process = movies[:50]

    credits_data = read_credits(credit_file)

    merged_movies = merge_files(
        movies_to_process, credits_data
    )

    write_json(merged_movies, json_file)
