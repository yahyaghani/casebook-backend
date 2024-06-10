import os
import chromadb
import openai
from chromadb.utils import embedding_functions
from src.core.process.embeddings import get_embedding
from src.util_helpers.graph_utils import parse_to_graph
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


def query_embeddings(query_text, n_results=1):
    chroma_client = chromadb.PersistentClient(path=db_dir)
    collection, _ = get_or_create_collection(chroma_client, "entity_texts", openai_ef)
    
    query_embedding = get_embedding(query_text)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["metadatas"]
    )

    casename_list = []
    citation_list = []
    provision_list = []

    for metadata in results['metadatas'][0]:
        if metadata.get('casename_ents'):
            casename_list.extend(
                [(text, "CASENAME") for text in metadata['casename_ents'].split(', ')
                 if " v " in text]
            )
        if metadata.get('citation_ents'):
            citation_list.extend(
                [(text, "CITATION") for text in metadata['citation_ents'].split(', ')
                 if any(c in text for c in "()[]")]
            )
        if metadata.get('provision_ents'):
            provision_list.extend(
                [(text, "PROVISION") for text in metadata['provision_ents'].split(', ')
                 if any(keyword in text.lower() for keyword in ["section", "article"])]
            )

    # Remove duplicates
    casename_list = list(set(casename_list))[:10]
    citation_list = list(set(citation_list))[:10]
    provision_list = list(set(provision_list))[:10]
    graph_data = parse_to_graph(casename_list, citation_list, provision_list)

    return graph_data

# ### For testing ### 

# # Example query
# query_text = "Freedom of Speech a political extradition Case"
# target_label = "CITATION"
# casename_list, citation_list, provision_list = query_embeddings(query_text, n_results=2)

# print("Casename List:", casename_list)
# print("Citation List:", citation_list)
# print("Provision List:", provision_list)
