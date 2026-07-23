import csv
import json
import ast
#import re
from pathlib import Path

credit_file = Path("data/movies-archive/credits.csv")
movies_file = Path("data/movies-archive/movies_metadata.csv")
ratings_file = Path("data/movies-archive/ratings.csv")
json_file = Path("data/dvdout.json")
 

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
    crew_list = ast.literal_eval(credits[0]["crew"])
    print(type(crew_list))

def read_ratings(ratings_file):
    ratings = []
    with open(ratings_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            ratings.append(row)

    return ratings

def merge_files(movies, credits, ratings):
    pass

def clean_data():
    pass

def validate_data():
    pass

def write_json():
    pass


if __name__ == "__main__":

    movies = read_movies_metadata(movies_file)
    movies_to_process = movies[:50]
   # for movie in movies_to_process[:5]:
   #     print(movie)

    credits = read_credits(credit_file)
    credits_to_process = credits[:50]
   # for credit in credits_to_process[:5]:
   #     print(credit)
    print("-------------------------------")
    print(credits[0]["crew"])
    print("-------------------------------")
    print("eor")

    ratings = read_ratings(ratings_file)
    ratings_to_process = ratings[:50]
    for rating in ratings_to_process[:5]:
        print(rating)

    print("Total movies read:", len(movies))
    print("Movies selected:", len(movies_to_process))

    print("Total credits read: ", len(credits))
    print("Credits selected: ", len(credits_to_process))

    print("Total ratings read: ", len(ratings))
    print("ratings selected: ", len(ratings_to_process))
