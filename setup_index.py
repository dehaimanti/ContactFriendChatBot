from pymongo import MongoClient

# === CONFIGURATION ===
MONGO_URI = "mongodb+srv://hde:<password>@hdemongodb.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
DB_NAME = "pdf_chat"
COLLECTION_NAME = "pdf_chunks"
VECTOR_DIM = 1536  # for OpenAI ada-002 embeddings

def setup_vector_index():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Create vector index
    print("🔧 Creating vector index in Cosmos DB...")
    collection.create_index(
        [("embedding", "cosmosSearch")],
        name="vector_index",
        cosmosSearchOptions={
            "kind": "vector-ivf",
            "numLists": 1
        },
        type="vector",
        dimensions=VECTOR_DIM
    )
    print("✅ Vector index created!")

if __name__ == "__main__":
    setup_vector_index()