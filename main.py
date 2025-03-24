import requests as req
import json
from fastapi import FastAPI

def searchlib(title):
    url = f"https://openlibrary.org/search.json?q={title.replace(' ', '+')}&limit=1"
    res = req.get(url)
    data = res.json()

    if data["numFound"] > 0:
        lib = data["docs"][0]
        portada_id = lib.get("cover_i")
        portada = f"https://openlibrary.org/b/id/{portada_id}-L.jpg" if portada_id else "Sin Portada"
    
        complete = {
            "Title": lib.get("title"),
            "Author": lib.get("author_name", [0]),
            "Date": lib.get("first_publish_year"),
            "Portada": portada
            }
        return json.dumps(complete, indent=4)
    else:
        return json.dumps({"error": "Book not found"}, indent="4")

print(searchlib("1984"))
