import requests as req
import json
import inquirer 
import os
import sqlite3
from tabulate import tabulate

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
        year INTEGER
    )
''')

conn.commit()
conn.close()


books = []

def searchlib(title):
    
    books.clear()

    url = f"https://openlibrary.org/search.json?q={title.replace(' ', '+')}&limit=15"
    res = req.get(url)
    data = res.json()

    if data["numFound"] > 0:
        for index, lib in enumerate(data["docs"]):
            complete = {
                "Id": index,
                "Title": lib.get("title"),
                "Author": lib.get("author_name", ["Desconocido"])[0],
                "Date": lib.get("first_publish_year"),
                }
            books.append(complete)
             
        print(tabulate(books, headers="keys", tablefmt="fancy_grid"))
    
    else:
            return {"error": "Book not found"}

def addBook(books):
        print(f"{GREEN}Adding book...{RESET}")
        conn = sqlite3.connect("books.db")
        cursor = conn.cursor()

        author = books["Author"][0] if isinstance(books["Author"], list) else books["Author"]
        cursor.execute("INSERT INTO books (title, author, year) VALUES (?, ?, ?)",(books["Title"], author, books["Date"]))
        
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
        
        headers = ["ID", "Title", "Author", "Year"] 
        print(tabulate(books, headers=headers, tablefmt="fancy_grid"))

    else:
        print(f"{RED}No books saved yet!{RESET}")

def delBook(bookId):
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM books WHERE id = ?",(bookId,))
    conn.commit()
    print(f"{RED}Book removed...{RESET}")

    conn.close()

while True:
    questions = [
        inquirer.List('action',
                    message= f"{GREEN}What do you want do?{RESET}",
                    choices=['1. Search a Book', '2. View my books', '3. Remove a Book','4. Exit'],
                    ),
            ]
    action = inquirer.prompt(questions)
    if action['action'] == '1. Search a Book':
        title = input(f"{GREEN}Write your book in here: {RESET}")
        searchlib(title)

        if title:
            questions = [
                    inquirer.List('save',
                        message= f"{GREEN}Save in My Books?{RESET}",
                        choices=['1. Yes', '2. No'],
                        ),
                        ]
            saveAction = inquirer.prompt(questions)
            if saveAction and saveAction['save'] == '1. Yes':
                x = int(input(f"{RED}Which?: "))
                addBook(books[x])
            else: 
                print("Not Saved")
        else:
            print(f"{RED}Not results for that book{RESET}")

    elif action['action'] == '2. View my books':
        print(f"{GREEN}Your books: {RESET}")
        loadBooks()

    elif action['action'] == '3. Remove a Book':
        bookId = int(input(f"{RED}Enter the ID of the book you want delete: {GREEN}"))
        delBook(bookId)

    elif action['action'] == '4. Exit':
        exit(1)

    else:
        print(f"{RED}Invalid Option{RESET}")
