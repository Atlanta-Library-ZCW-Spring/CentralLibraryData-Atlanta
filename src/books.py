import csv
import json
import random
import re
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
        parsed_authors = clean_authors(book.get("Authors", ""))

        cleaned_book = {
          #  "text_number": book.get("Text#", "").strip(),
          #  "type": book.get("Type", "").strip(),
            
            "title": book.get("Title", "").strip(),
            "issued": book.get("Issued", "").strip(),
            "language": book.get("Language", "").strip(),
            "authors": [
                author["name"]
                for author in parsed_authors
            ],
            "author_lifespan": [
                author["lifespan"]
                for author in parsed_authors
                if author["lifespan"]
            ],
            "subjects": clean_subjects(book.get("Subjects", "")),
         #   "locc": book.get("LoCC", "").strip(),
            "bookshelves": book.get("Bookshelves", "").strip(),
            "isbn": generate_isbn()
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

