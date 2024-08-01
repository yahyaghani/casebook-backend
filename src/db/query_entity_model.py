import os
import chromadb
import openai
from chromadb.utils import embedding_functions
from src.core.process.embeddings import get_embedding

# Echo PYTHONPATH and OPENAI_API_KEY
# pythonpath = os.environ.get('PYTHONPATH', 'PYTHONPATH not set')
# print(f"PYTHONPATH: {pythonpath}")
# openai_api_key = os.environ.get('OPENAI_API_KEY', 'OPENAI_API_KEY not set')
# print(f"OPENAI_API_KEY: {openai_api_key}")

# Setup OpenAI embedding function
api_key = os.getenv('OPENAI_API_KEY', "sk-test-1-EVd45S4JPy7m0zpf6rLTT3BlbkFJpUkAAFT6ClLo2njFl1RJ")
OPENAI_API_KEY = api_key
openai_ef = embedding_functions.OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY, model_name="text-embedding-ada-002")

# Setup directories for database storage
current_dir = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(current_dir, "chromadb_data")
os.makedirs(db_dir, exist_ok=True)

def get_or_create_collection(client, collection_name, embedding_function):
    try:
        collection = client.get_collection(name=collection_name, embedding_function=embedding_function)
        created = False
        print(f"Collection {collection_name} retrieved successfully.")
    except Exception as e:
        collection = client.create_collection(name=collection_name, embedding_function=embedding_function)
        created = True
        print(f"Collection {collection_name} created successfully.")
    return collection, created


def query_embeddings(query_text, target_label, n_results=2):
    chroma_client = chromadb.PersistentClient(path=db_dir)
    collection, _ = get_or_create_collection(chroma_client, "entity_texts", openai_ef)
    
    query_embedding = get_embedding(query_text)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas"]
    )

    matched_entities = []
    for metadata, document in zip(results['metadatas'][0], results['documents'][0]):
        if target_label in metadata['entity_labels'].split(', '):  # Adjusting the check for string lists
            entity_texts = sorted(metadata['entity_texts'].split(', '))
            entity_labels = sorted(metadata['entity_labels'].split(', '))
            entity_tuples = list(zip(entity_texts, entity_labels))
            matched_entities.append({
                "global_id": metadata['global_id'],
                "chunk_id": metadata['chunk_id'],
                "entity_tuples": entity_tuples,
                "matched_chunk": document
            })
    
    return matched_entities

# Example query
query_text = "Caselaw for Freedom of Speech Extradition Cases"
target_label = "CITATION"
results = query_embeddings(query_text, target_label, n_results=2)
print("Query results:", results)

# Print tuples for the first chunk
if results:
    print("Tuples for the first chunk:", results[0]['entity_tuples'])
