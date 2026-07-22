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
    cleaned_books = []

    for book in books:
        cleaned_book = {}

        cleaned_book["text_number"] = book.get("Text#", "").strip()
        cleaned_book["type"] = book.get("Type", "").strip()
        cleaned_book["issued"] = book.get("Issued", "").strip()
        cleaned_book["title"] = book.get("Title", "").strip()
        cleaned_book["language"] = book.get("Language", "").strip()
        cleaned_book["authors"] = clean_authors(book.get("Authors", ""))
        cleaned_book["subjects"] = book.get("Subjects", "").strip()
        cleaned_book["locc"] = book.get("LoCC", "").strip()
        cleaned_book["bookshelves"] = book.get("Bookshelves", "").strip()
        cleaned_book["isbn"] = generate_isbn()

        cleaned_books.append(cleaned_book)

    # for book in books:
    #     if "isbn" not in book:
    #         book["isbn"] = generate_isbn()

    return cleaned_books

def clean_authors(author_field):
    if not author_field:
        return[]
    
    authors = author_field.split(";")

    cleaned_authors = []

    for author in authors:
        cleaned_authors.append(author.strip())

    return cleaned_authors

def validate_books(cleaned_books):
    valid_books = []
    missing_title = 0
    missing_authors = 0
    invalid_isbn = 0

    for book in cleaned_books:
        title = book.get("title", "").strip()
        authors = book.get("authors", [])
        isbn = book.get("isbn","").strip()

        if not title:
            missing_title += 1
            continue

        if not authors:
            missing_authors += 1
            continue

        if len(isbn) != 13:
            invalid_isbn += 1
            continue

        valid_books.append(book)

    print("Missing title: ", missing_title)
    print("Missing authors: ", missing_authors)
    print("Invalid ISBN: ", invalid_isbn)

    return valid_books

def write_json(valid_books, json_file):
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(valid_books, file, indent=4)

    return json_file


if __name__ == "__main__":
    books = read_books(csv_file)

    cleaned_books = clean_books(books)

    print(cleaned_books[0])
    print(cleaned_books[0].keys())

    valid_books = validate_books(cleaned_books)

    print("Books read: ", len(books))
    print("Books cleaned: ", len(cleaned_books))
    print("Books validated: ", len(valid_books))


    write_json(valid_books, json_file)
    
    #this is so only the first 5 rows are returned for testing purposes
    # for book in books[:5]:
    #     print(book)

