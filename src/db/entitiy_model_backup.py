import pandas as pd
import os
import chromadb
import requests
from chromadb.utils import embedding_functions
from src.core.process.embeddings import get_embedding
import openai
import sqlite3

# Setup OpenAI embedding function
api_key = "sk-test-1-EVd45S4JPy7m0zpf6rLTT3BlbkFJpUkAAFT6ClLo2njFl1RJ"
OPENAI_API_KEY = api_key
openai_ef = embedding_functions.OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY, model_name="text-embedding-ada-002")

# Setup directories for database storage
current_dir = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(current_dir, "chromadb_data")
os.makedirs(db_dir, exist_ok=True)

# Read CSV files
entities_df = pd.read_csv('entities_output.csv')
texts_df = pd.read_csv('text_globalid.csv')

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

def split_into_chunks(text, max_length=8000):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(' '.join(current_chunk)) > max_length:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def get_embedding(text, model="text-embedding-ada-002"):
    openai.api_key = OPENAI_API_KEY
    response = openai.Embedding.create(input=[text], model=model)
    return response['data'][0]['embedding']

def store_embeddings_in_chromadb():
    chroma_client = chromadb.PersistentClient(path=db_dir)
    collection, created = get_or_create_collection(chroma_client, "entity_texts", openai_ef)
    print("Collection initialized:", created)

    for index, row in texts_df.iterrows():
        global_id = row['global_id']
        text = row['text']
        chunks = split_into_chunks(text)

        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            entity_texts = entities_df[entities_df['global_id'] == global_id]['entitity_text'].tolist()
            entity_labels = entities_df[entities_df['global_id'] == global_id]['entity_label'].tolist()
            
            metadata = {
                "global_id": global_id,
                "chunk_id": f"{global_id}_chunk_{i}",
                "entity_texts": entity_texts,
                "entity_labels": entity_labels
            }

            collection.add(
                documents=[chunk],
                metadatas=[metadata],
                ids=[metadata['chunk_id']],
                embeddings=[embedding]
            )

def query_embeddings(query_text, target_label):
    chroma_client = chromadb.PersistentClient(path=db_dir)
    collection, _ = get_or_create_collection(chroma_client, "entity_texts", openai_ef)
    
    query_embedding = get_embedding(query_text)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        include=["documents", "metadatas"]
    )

    matched_entities = []
    for metadata in results['metadatas'][0]:
        if target_label in metadata['entity_labels']:
            matched_entities.append({
                "global_id": metadata['global_id'],
                "chunk_id": metadata['chunk_id'],
                "entity_texts": metadata['entity_texts'],
                "entity_labels": metadata['entity_labels'],
                "matched_chunk": results['documents'][0]
            })
    
    return matched_entities

# Store embeddings in ChromaDB
store_embeddings_in_chromadb()

# Example query
query_text = "Supreme Court decision in 2009"
target_label = "CASENAME"
results = query_embeddings(query_text, target_label)
print("Query results:", results)
