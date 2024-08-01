import pandas as pd
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

# Read CSV files
entities_df = pd.read_csv('/media/taymur/EXTERNAL_USB/large/legal_datasets/judgements_uk_baili/data/cleaned_entities_output.csv')
texts_df = pd.read_csv('/media/taymur/EXTERNAL_USB/large/legal_datasets/judgements_uk_baili/data/text_globalid.csv')

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

def filter_entities_with_casename_citation_provision(entities_df):
    casename_ids = set(entities_df[entities_df['entity_label'] == 'CASENAME']['global_id'])
    citation_ids = set(entities_df[entities_df['entity_label'] == 'CITATION']['global_id'])
    provision_ids = set(entities_df[entities_df['entity_label'] == 'PROVISION']['global_id'])
    valid_ids = casename_ids.intersection(citation_ids).intersection(provision_ids)
    return entities_df[entities_df['global_id'].isin(valid_ids)], valid_ids

def store_embeddings_in_chromadb(filtered_entities_df, valid_ids):
    chroma_client = chromadb.PersistentClient(path=db_dir)
    collection, created = get_or_create_collection(chroma_client, "entity_texts", openai_ef)
    print("Collection initialized:", created)

    # Filter texts_df to include only the valid global_ids
    filtered_texts_df = texts_df[texts_df['global_id'].isin(valid_ids)]

    # Further filter to include only the first 10 unique global_ids
    first_10_global_ids = filtered_texts_df['global_id'].unique()[:10]
    filtered_texts_df = filtered_texts_df[filtered_texts_df['global_id'].isin(first_10_global_ids)]

    for index, row in filtered_texts_df.iterrows():
        global_id = row['global_id']
        text = row['text']
        chunks = split_into_chunks(text)

        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            entity_texts = filtered_entities_df[filtered_entities_df['global_id'] == global_id]['entity_text'].tolist()
            entity_labels = filtered_entities_df[filtered_entities_df['global_id'] == global_id]['entity_label'].tolist()
            
            # Convert lists to comma-separated strings
            entity_texts_str = ', '.join(entity_texts)
            entity_labels_str = ', '.join(entity_labels)
            
            print(f'Embedding for: {entity_texts_str}', embedding)
            metadata = {
                "global_id": global_id,
                "chunk_id": f"{global_id}_chunk_{i}",
                "entity_texts": entity_texts_str,
                "entity_labels": entity_labels_str
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
        if target_label in metadata['entity_labels'].split(', '):  # Adjusting the check for string lists
            matched_entities.append({
                "global_id": metadata['global_id'],
                "chunk_id": metadata['chunk_id'],
                "entity_texts": metadata['entity_texts'],
                "entity_labels": metadata['entity_labels'],
                "matched_chunk": results['documents'][0]
            })
    
    return matched_entities

# Filter entities_df to include only global_ids with CASENAME, CITATION, and PROVISION
filtered_entities_df, valid_ids = filter_entities_with_casename_citation_provision(entities_df)

# Store embeddings in ChromaDB for the first 10 valid global_ids
store_embeddings_in_chromadb(filtered_entities_df, valid_ids)

# Example query
query_text = "Supreme Court decision in 2009"
target_label = "CASENAME"
results = query_embeddings(query_text, target_label)
print("Query results:", results)
