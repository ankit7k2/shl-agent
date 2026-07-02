import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Load catalog
with open(
    "data/shl_catalog.json",
    "r",
    encoding="utf-8"
) as f:
    catalog = json.load(f)


# Load FAISS index
index = faiss.read_index("data/shl_index.faiss")


def recommend(query, top_k=20):
    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding, dtype=np.float32)

    distances, indices = index.search(query_embedding, top_k)

    categories_needed = {
        "Knowledge & Skills": 5,
        "Personality & Behavior": 2,
        "Ability & Aptitude": 2,
        "Competencies": 1
    }

    recommendations = []
    used_names = set()

    for idx in indices[0]:
        item = catalog[idx]

        if item["name"] in used_names:
            continue

        item_categories = item.get("keys", [])

        selected = False

        for category in item_categories:

            if (
                category in categories_needed
                and categories_needed[category] > 0
            ):

                recommendations.append({
                    "name": item["name"],
                    "url": item["link"],
                    "test_type": category
                })

                categories_needed[category] -= 1
                used_names.add(item["name"])
                selected = True
                break

        if selected and len(recommendations) >= 10:
            break

    return recommendations


if __name__ == "__main__":

    query = input("Enter requirement: ")

    results = recommend(query)

    print("\nRecommended Assessments:\n")

    for i, item in enumerate(results, start=1):

        print(f"{i}. {item['name']}")
        print(f"Type: {item['test_type']}")
        print(item["url"])
        print()
