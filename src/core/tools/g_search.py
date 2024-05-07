import os
from typing import List, Dict
from langchain_google_community import GoogleSearchAPIWrapper



# Custom Search Engine IDs for each type
CSE_ID_LEGISLATION = "754370c1b456c454f"
CSE_ID_CASELAW = "e26f2cfedfd1c425b"

def google_search_legislation(query: str) -> str:
    """
    Performs a Google search for legislation using a specific Custom Search Engine and returns the top 3 results.
    
    Args:
    query (str): The search term or question related to legislation.
    
    Returns:
    str: Formatted string of search results.
    """
    # Set environment variable for CSE ID
    os.environ["GOOGLE_CSE_ID"] = CSE_ID_LEGISLATION
    
    # Initialize the search API with the selected CSE ID
    search_api = GoogleSearchAPIWrapper()
    results = search_api.results(query, 7)
    print(results)
    result_str = "\n".join([f"Title: {item['title']}, Link: {item['link']}" for item in results])
    return result_str

def google_search_caselaw(query: str) -> str:
    """
    Performs a Google search for case law using a specific Custom Search Engine and returns the top 3 results.
    
    Args:
    query (str): The search term or question related to case law.
    
    Returns:
    str: Formatted string of search results.
    """
    # Set environment variable for CSE ID
    os.environ["GOOGLE_CSE_ID"] = CSE_ID_CASELAW
    
    # Initialize the search API with the selected CSE ID
    search_api = GoogleSearchAPIWrapper(CSE_ID_CASELAW)
    results = search_api.results(query, 3)
    result_str = "\n".join([f"Title: {item['title']}, Link: {item['link']}" for item in results])
    return result_str
