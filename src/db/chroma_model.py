import os
import chromadb
import requests
from bs4 import BeautifulSoup
from src.core.process.helpers_web_parse_cleaner import (
    extract_text_from_pdf,
    extract_text_from_html
)
from src.core.process.embeddings import get_embedding
from chromadb.utils import embedding_functions

# Setup OpenAI embedding function
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
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

def fetch_and_store_content_chromadb(actioned_input, collection):
    print('Fetching and storing content for:', actioned_input)
    title = actioned_input['title']
    url = actioned_input['url']

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type')
        cleaned_text = extract_text_from_pdf(response.content) if 'application/pdf' in content_type else extract_text_from_html(response.text)
        chunks = split_into_chunks(cleaned_text)

        for i, chunk in enumerate(chunks):
            # Store each chunk as a separate document
            doc_id = f"{title.replace(' ', '_')}_{url}_chunk_{i+1}"
            collection.add(
                documents=[chunk],
                metadatas=[{"title": title, "url": url, "chunk": i+1, "total_chunks": len(chunks)}],
                ids=[doc_id]
            )
            print(f"Content chunk {i+1}/{len(chunks)} stored with ID: {doc_id}")
    except Exception as e:
        print(f"Error processing content: {e}")

def query_articles(query, collection):
    print('Querying articles for:', query)
    query_embeddings = get_embedding(query)  # Assuming this function returns the proper embeddings
    results = collection.query(
        query_embeddings=query_embeddings,
        n_results=3,
        include=["documents", "metadatas"]  # Request both documents and metadata to be returned
    )

    print(f"Results type: {type(results)}")  # Debug print to check the type of 'results'
    
    # Check if results is a dictionary and has expected keys
    if results and 'metadatas' in results and 'documents' in results:
        metadatas = results['metadatas'][0]
        documents = results['documents'][0]  # Assuming documents are in the same order as metadatas

        for metadata, document in zip(metadatas, documents):
            title = metadata.get('title', 'No title available')
            url = metadata.get('url', 'No URL available')
            chunk = metadata.get('chunk', 'N/A')
            total_chunks = metadata.get('total_chunks', 'N/A')
            print(f"Title: {title}, URL: {url}, Chunk: {chunk}/{total_chunks}")
            print("Content:", document)  # Print the actual content of the chunk

    else:
        print("No matching articles found.")

# Main operations
chroma_client = chromadb.PersistentClient(path=db_dir)
collection, created = get_or_create_collection(chroma_client, "web_content", openai_ef)
print("Collection initialized:", created)

# Define and process documents
sample_documents = [
    {
        "title": "EWC Appeal Decisions",
        "url": "https://www.bailii.org/ew/cases/EWCA/Civ/1992/2.html",
        "content": "The court has before it two appeals which raise the same point of law."
    },
    {
        "title": "REAC T: SYNERGIZING REASONING AND ACTING IN LANGUAGE MODELS",
        "url": "https://arxiv.org/pdf/2210.03629",
        "content": "While large language models (LLMs) have demonstrated impressive performance across tasks in language understanding."
    }
]

## fetch from web ##
# for doc in sample_documents:
#     fetch_and_store_content_chromadb(doc, collection)

# Query the collection
# query_text = "computational models"
# query_articles(query_text, collection)
