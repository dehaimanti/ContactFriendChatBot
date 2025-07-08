from pymongo import MongoClient

client = MongoClient("your-cosmos-mongo-uri")
db = client["pdf_chat"]
collection = db["pdf_chunks"]

collection.create_index(
    [("embedding", "cosmosSearch")],
    name="vector_index",
    default_language="none",
    cosmosSearchOptions={
        "kind": "vector-ivf",
        "numLists": 1
    },
    type="vector",
    dimensions=1536
)