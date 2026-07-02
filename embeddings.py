import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


# Load model
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# Load catalog
with open(
    "data/shl_catalog.json",
    "r",
    encoding="utf-8"
) as f:

    catalog = json.load(f)


documents = []


for item in catalog:

    text = f"""
Assessment Name:
{item['name']}

Description:
{item['description']}

Assessment Categories:
{' '.join(item['keys'])}

Suitable Job Levels:
{' '.join(item['job_levels'])}

Remote Testing:
{item['remote']}

This assessment helps evaluate candidates for hiring decisions.
"""

    documents.append(text)


print("Creating embeddings...")

embeddings = model.encode(
    documents,
    show_progress_bar=True
)


embeddings = np.array(
    embeddings,
    dtype=np.float32
)


dimension = embeddings.shape[1]


index = faiss.IndexFlatL2(dimension)

index.add(embeddings)


faiss.write_index(
    index,
    "data/shl_index.faiss"
)


print("Done!")

print("Assessments:", len(catalog))
print("Dimension:", dimension)
