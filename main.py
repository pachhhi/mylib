import requests as req
import json
import inquirer 
import os
import sqlite3

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"

#Database
conn = sqlite3.connect("books.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        year INTEGER,
        cover TEXT
    )
''')

conn.commit()
conn.close()



def searchlib(title):
    url = f"https://openlibrary.org/search.json?q={title.replace(' ', '+')}&limit=1"
    res = req.get(url)
    data = res.json()

    if data["numFound"] > 0:
        lib = data["docs"][0]
        cover_id = lib.get("cover_i")
        cover = f"https://openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else "Sin Portada"
    
        complete = {
            "Title": lib.get("title"),
            "Author": lib.get("author_name", [0]),
            "Date": lib.get("first_publish_year"),
            "Cover": cover
            }
        return complete
    else:
        return {"error": "Book not found"}


def addBook(book):
        print(f"{GREEN}Adding book...{RESET}")
        conn = sqlite3.connect("books.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO books (title, author, year, cover) VALUES (?, ?, ?, ?)",
                        (book["Title"],book["Author"][0],book["Date"],book["Cover"]))
        
        conn.commit()
        conn.close()
        print(f"{GREEN}Book saved successfully!{RESET}")

def loadBooks():
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, author, year FROM books")
    books = cursor.fetchall()

    conn.close()

    if books:
        for book in books:
            print(f"{GREEN}{book}{RESET}")

    else:
        print(f"{RED}No books saved yet!{RESET}")

while True:
    questions = [
        inquirer.List('action',
                    message= f"{GREEN}What do you want do?{RESET}",
                    choices=['1. Search a Book', '2. View my books', '3. Exit'],
                    ),
            ]
    action = inquirer.prompt(questions)
    if action['action'] == '1. Search a Book':
        title = input(f"{GREEN}Write your book in here: {RESET}")
        result = searchlib(title)
        print(result)

        if result:
            questions = [
                    inquirer.List('save',
                        message= f"{GREEN}Save in My Books?{RESET}",
                        choices=['1. Yes ', '2. No '],
                        ),
                        ]
        saveAction = inquirer.prompt(questions)
        if saveAction['save'] == '1. Yes ':
            addBook(result)
        else: 
            print("Not Saved")


    elif action['action'] == '2. View my books':
        print(f"{GREEN}Your books: {RESET}")
        loadBooks()

    elif action['action'] == '3. Exit':
        exit(1)


