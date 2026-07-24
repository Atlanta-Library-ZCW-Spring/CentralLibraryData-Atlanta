import csv
import json
import random
import re

from pathlib import Path

csv_file = Path("data/pg_catalog.csv")
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

def get_genre(bookshelves_field):
    if not bookshelves_field:
        return "Not Available"

    bookshelves = bookshelves_field.split(";")

    # genres = []

    for shelf in bookshelves:
        shelf = shelf.strip()

        if shelf.startswith("Browsing:"):
            shelf = shelf.replace("Browsing:", "", 1)
            shelf = shelf.strip()

        if shelf:
            return shelf

    return "Not Available"

def clean_books(books):
    """1.  Add an isbn to each book/row"""
    
    cleaned_books = []
    for book in books:
        parsed_authors = clean_authors(book.get("Authors", ""))
        parsed_subjects = clean_subjects(book.get("Subjects", ""))

        # bookshelves_value = book.get("Bookshelves", "")
        # genre = get_genre(bookshelves_value)
        # print(f"Title: {book.get('Title', '').strip()}")
        # print(f"Bookshelves: '{bookshelves_value}'")
        # print(f"Genre returned: '{genre}'")
        # print("-" * 40)

        cleaned_book = {            
            "title": book.get("Title", "").strip(),
            "authors": [
                author["name"]
                for author in parsed_authors
            ],
            "author_lifespan": [
                author["lifespan"]
                for author in parsed_authors
                if author["lifespan"]
            ],
            "isbn": generate_isbn(),
            "numberOfPages": 0,

            "genre": get_genre(book.get("Bookshelves", "")),
            "subjects": parsed_subjects,
            "locc": book.get("LoCC", "").strip()   
        }

        cleaned_books.append(cleaned_book)

    return cleaned_books

def clean_authors(author_field):
    if not author_field:
        return[]
    
    authors = author_field.split(";")
    cleaned_authors = []

    for author in authors:
        author = author.strip()

        lifespan_match = re.search(
            r"\b\d{3,4}\??(?:\s+BCE)?-\d{3,4}\??(?:\s+BCE)?\b",
            author
        )
        if lifespan_match:
            lifespan = lifespan_match.group()

            name = author.replace(lifespan, "")
            name = name.strip(" ,")
        else:
            lifespan = ""
            name = author

        cleaned_authors.append({
            "name": name,
            "lifespan": lifespan
        })

    return cleaned_authors

def clean_subjects(subject_field):
    if not subject_field:
        return []
    
    subjects = subject_field.split(";")
    cleaned_subjects = []

    for subject in subjects:
        subject = subject.strip()

        if subject:
            cleaned_subjects.append(subject)

    return cleaned_subjects

def validate_books(cleaned_books):
    valid_books = []
    missing_title = 0
    missing_authors = 0
    invalid_isbn = 0
    record_number = 1

    for book in cleaned_books:

        title = book.get("title", "").strip()
        authors = book.get("authors", [])
        isbn = book.get("isbn", "").strip()

        if not title:
            missing_title += 1
            continue

        if not authors:
            missing_authors += 1
            continue

        if len(isbn) != 13:
            invalid_isbn += 1
            continue

        # Create a new dictionary with recordID as the first field
        new_book = {
            "recordID": f"{record_number:06d}"
        }

        # Add the rest of the book fields
        new_book.update(book)

        valid_books.append(new_book)
        record_number += 1

    print("Missing title:", missing_title)
    print("Missing authors:", missing_authors)
    print("Invalid ISBN:", invalid_isbn)
    print("Books validated:", len(valid_books))

    return valid_books

def write_json(valid_books, json_file):
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(valid_books, file, indent=4)

    return json_file


if __name__ == "__main__":
    books = read_books(csv_file)
    cleaned_books = clean_books(books)
    valid_books = validate_books(cleaned_books)
    books_to_process = valid_books[:50]

    print("Books read: ", len(books))
    print("Books cleaned: ", len(cleaned_books))
    print("Books validated: ", len(valid_books))

    books_to_write = valid_books[:50]
    print("Books being written to JSON file: ", len(books_to_write))
    write_json(valid_books[:50], json_file)
    
    #this is so only the first 5 rows are returned for testing purposes
    # for book in books[:5]:
    #     print(book)

