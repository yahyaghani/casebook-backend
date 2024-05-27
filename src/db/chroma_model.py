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
from src.core.process.instructional_parsers import (
    smart_parse_action_input, openai_structured_response_return_title_url)
from src.core.agents.main_client import client
from src.core.process.pydantic_models import ChromadbArguments, ChromadbResult

# Setup OpenAI embedding function
api_key = "sk-test-1-EVd45S4JPy7m0zpf6rLTT3BlbkFJpUkAAFT6ClLo2njFl1RJ"

OPENAI_API_KEY = api_key
openai_ef = embedding_functions.OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY, model_name="text-embedding-ada-002")

# Setup directories for database storage
current_dir = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(current_dir, "chromadb_data")
print('dir',db_dir)
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

def split_into_chunks(text, max_length=3000):
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

def fetch_and_store_content_chromadb(arguments: ChromadbArguments, instruction: str) -> dict:
    actioned_input_dict = openai_structured_response_return_title_url(arguments.requestBody)
    title = actioned_input_dict['title']
    url = actioned_input_dict['url']
    
    try:
        # Check if the URL already exists in the collection
        existing_urls_response = collection.query(
            query_texts=[url],
            n_results=1,
            include=["metadatas"]
        )
        
        if existing_urls_response and 'metadatas' in existing_urls_response and existing_urls_response['metadatas']:
            # URL already exists, fetch the top 3 closest chunks
            top_3_chunks = query_articles(instruction)
            return {"message": "URL already exists in the database, fetched top 3 closest chunks.", "top_3_chunks": top_3_chunks}

        # Fetch and process content from the URL
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type')
        cleaned_text = extract_text_from_pdf(response.content) if 'application/pdf' in content_type else extract_text_from_html(response.text)
        chunks = split_into_chunks(cleaned_text)
        embeddings = [get_embedding(chunk) for chunk in chunks]

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            doc_id = f"{title.replace(' ', '_')}_{url}_chunk_{i+1}"
            
            collection.add(
                documents=[chunk],
                metadatas=[{"title": title, "url": url, "chunk": i+1, "total_chunks": len(chunks)}],
                ids=[doc_id],
                embeddings=[embedding]
            )

        # After storing, query for the top 3 chunks based on the instruction
        top_3_chunks = query_articles(instruction)
        return {"message": "Content fetched and stored successfully, fetched top 3 closest chunks.", "top_3_chunks": top_3_chunks}
    except Exception as e:
        raise ValueError(f"Error processing content: {e}")

def query_articles(query: str) -> list:
    print('incoming query articles', query)
    query_embeddings = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embeddings],
        n_results=3,
        include=["documents", "metadatas","embeddings"]
    )

    if results and 'metadatas' in results and 'documents' in results:
        metadatas = results['metadatas'][0]
        documents = results['documents'][0]
        print('results', results)
        top_3_chunks = []
        for metadata, document in zip(metadatas, documents):
            top_3_chunks.append({
                "title": metadata.get('title', 'No title available'),
                "url": metadata.get('url', 'No URL available'),
                "chunk": metadata.get('chunk', 'N/A'),
                "total_chunks": metadata.get('total_chunks', 'N/A'),
                "document": document
            })
        return top_3_chunks
    else:
        return []

# Main operations
chroma_client = chromadb.PersistentClient(path=db_dir)
collection, created = get_or_create_collection(chroma_client, "web_content", openai_ef)
print("Collection initialized:", created)
