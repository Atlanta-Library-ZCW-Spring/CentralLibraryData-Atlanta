import csv
import json
import random
from pathlib import Path

csv_file = Path("data/booksdata.csv")
json_file = Path("data/booksout.json")
used_isbns = set()

def generate_isbn():  #generate a unique 13 digit isbn-like number

    while True:
        isbn = str(random.randint(1000000000000, 9999999999999))

        if isbn not in used_isbns:
            used_isbns.add(isbn)
            return isbn

def read_books(csv_file):
    with open(csv_file, 'r', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        books = []
        
        for row in reader:
            books.append(row) 

    return books 

def clean_books(books):
    """1.  Add an isbn to each book/row
    """
    for book in books:
        if "isbn" not in book:
            book["isbn"] = generate_isbn()

    return books

def validate_books(cleaned_books):


    return cleaned_books

def write_json(valid_books, json_file):
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(valid_books, file, indent=4)

    return json_file


if __name__ == "__main__":
    books = read_books(csv_file)

    cleaned_books = clean_books(books)

    valid_books = validate_books(cleaned_books)

    write_books = (valid_books, json_file)
    
    #this is so only the first 5 rows are returned for testing purposes
    for book in books[:5]:
        print(book)

