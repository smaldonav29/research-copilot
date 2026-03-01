import json
import os

# Ajustamos la ruta porque estamos dentro de src
path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "papers",
    "paper_catalog.json"
)

if not os.path.exists(path):
    print("❌ paper_catalog.json NOT FOUND")
    print("Buscado en:", path)
    exit()

with open(path, "r", encoding="utf-8") as f:
    catalog = json.load(f)

papers = catalog.get("papers", [])

if not papers:
    print("⚠ No papers found in catalog.")
else:
    print("✅ Titles found:\n")
    for paper in papers:
        print("-", paper.get("title", "No Title"))