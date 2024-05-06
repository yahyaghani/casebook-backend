import os
from typing import List, Dict
from langchain_google_community import GoogleSearchAPIWrapper

##dynamic search based on the type of doc

# Base environment variables for API access
api_key = os.getenv('GOOGLE_API_KEY')

# Mapping of document types to their respective Google Custom Search Engine IDs
CSE_IDS = {
    "legislation": "754370c1b456c454f",
    "caselaw": "e26f2cfedfd1c425b"
}

def google_search(query: str, document_type: str, k: int = 5) -> str:
    """
    Performs a Google search using a specific Custom Search Engine based on the document type
    and returns the top k results.
    
    Args:
    query (str): The search term or question.
    document_type (str): Type of the document to set the context of the search.
    k (int): The number of results to retrieve.
    
    Returns:
    str: Formatted string of search results.
    """
    # Select the appropriate CSE ID based on the document type
    if document_type in CSE_IDS:
        os.environ["GOOGLE_CSE_ID"] = CSE_IDS[document_type]
    else:
        raise ValueError("Invalid document type provided.")
    
    # Initialize the search API with the selected CSE ID
    search_api = GoogleSearchAPIWrapper()
    results = search_api.results(query, k)
    result_str = "\n".join([f"Title: {item['title']}, Link: {item['link']}" for item in results])
    return result_str

# Example usage
if __name__ == "__main__":
    query = "Fourth Amendment"
    print("Caselaw Search Results:")
    print(google_search(query, document_type="caselaw", k=3))
    print("\nLegislation Search Results:")
    query = "data protection act"
    print(google_search(query, document_type="legislation", k=3))
