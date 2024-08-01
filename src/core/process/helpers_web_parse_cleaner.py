from bs4 import BeautifulSoup
import httpx
from urllib.parse import quote
import os 
import requests
import sqlite3
import re
import json 
from typing import Optional

from src.core.process.instructional_parsers import openai_structured_response_return_title_url
from pdfminer.high_level import extract_text
from src.core.process.instructional_parsers import smart_parse_action_input
from src.core.process.pydantic_models import GoogleSearchArguments, GoogleSearchResults, GoogleSearchResultItem
from src.core.agents.main_client import client



my_api_key = os.getenv('GOOGLE_API_KEY')
my_cse_id= '754370c1b456c454f'


def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    clean_text = soup.get_text()
    # Optionally, you can also remove references or other unwanted parts here
    return clean_text

from sklearn.feature_extraction.text import TfidfVectorizer

def convert_spaces_to_percent20(text):
    # The `safe` parameter determines which characters should not be quoted. Here, we are encoding everything except the alphanumeric characters.
    return quote(text, safe='')

def parse_action_input(input_string):
    # Pattern to find key="value" pairs
    # pattern = re.compile(r'(\w+)="([^"]*)"')
    pattern = re.compile(r'(\w+):\s*([^,\s]+)')

    # Find all matches and return a dictionary of key-value pairs
    return dict(pattern.findall(input_string))


def tfidf_extract_keywords(query):
    # Initialize a TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')

    # Assume each word in the query is a separate document for simplicity
    words = query.split()
    # Fit and transform the 'documents'
    tfidf_matrix = vectorizer.fit_transform(words)

    # Get feature names to use as output
    feature_names = vectorizer.get_feature_names_out()

    # Sort words by their TF-IDF scores
    sorted_items = sorted(zip(vectorizer.idf_, feature_names), reverse=True)

    # Extract top 3 keywords
    top_keywords = [item[1] for item in sorted_items[:3]]
    return ", ".join(top_keywords)



def legislation_search(q):
    print('Query incoming:', q)
    # Extract keywords using a TF-IDF model (or any other appropriate model)
    keywords_encoded = convert_spaces_to_percent20(q)
    # print(f"Keywords extracted: {keywords_encoded}")

    # Construct the URL with URL encoding
    search_url = f"https://www.legislation.gov.uk/all?text={keywords_encoded}"
    
    # Fetch the search results page
    response = httpx.get(search_url)
    print(response)
    if response.status_code != 200:
        return "Failed to fetch legislation."

    # Parse the search results page to find links to legislation documents
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)
    links = soup.find_all('a', href=True)  # Adjust this according to the actual structure of the legislation.gov.uk search results
    
    # Collect links to the top two legislation documents
    top_legislation_links = []
    for link in links:
        if '/id/' in link['href']:  # This part depends on how links are structured on legislation.gov.uk
            top_legislation_links.append("https://www.legislation.gov.uk" + link['href'])
            if len(top_legislation_links) == 2:
                break

    # Fetch and clean the top two legislation documents
    documents = []
    for legislation_url in top_legislation_links:
        doc_response = httpx.get(legislation_url)
        if doc_response.status_code == 200:
            cleaned_text = clean_html(doc_response.text)
            documents.append(cleaned_text)

    if documents:
        return "\n\n".join(documents)
    else:
        return "No detailed legislation documents found."


def perform_google_search(arguments: GoogleSearchArguments) -> GoogleSearchResults:
    query = arguments.query
    page = arguments.page
    
    API_KEY = os.getenv('GOOGLE_API_KEY')
    SEARCH_ENGINE_ID = 'b2f924e8393114947'

    start = (page - 1) * 3 + 1
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start={start}&num=3"

    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch data: HTTP {response.status_code}")

    # Log the response content
    print(f"Response content: {response.text}")

    try:
        data = response.json()
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {str(e)}")

    search_items = data.get("items")
    if not search_items:
        raise ValueError("No results found.")

    results = []
    for i, search_item in enumerate(search_items, start=1):
        result_dict = GoogleSearchResultItem(
            result_number=i + start - 1,
            title=search_item.get("title"),
            description=search_item.get("snippet"),
            long_description=search_item.get("pagemap", {}).get("metatags", [{}])[0].get("og:description", "N/A"),
            url=search_item.get("link")
        )
        results.append(result_dict)

    return GoogleSearchResults(results=results)

def perform_google_search_legislation(arguments: GoogleSearchArguments) -> GoogleSearchResults:
    query = arguments.query
    page = arguments.page
    
    API_KEY = os.getenv('GOOGLE_API_KEY')
    SEARCH_ENGINE_ID = '754370c1b456c454f'

    start = (page - 1) * 3 + 1
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start={start}&num=3"

    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch data: HTTP {response.status_code}")

    # Log the response content
    print(f"Response content: {response.text}")

    try:
        data = response.json()
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {str(e)}")

    search_items = data.get("items")
    if not search_items:
        raise ValueError("No results found.")

    results = []
    for i, search_item in enumerate(search_items, start=1):
        result_dict = GoogleSearchResultItem(
            result_number=i + start - 1,
            title=search_item.get("title"),
            description=search_item.get("snippet"),
            long_description=search_item.get("pagemap", {}).get("metatags", [{}])[0].get("og:description", "N/A"),
            url=search_item.get("link")
        )
        results.append(result_dict)

    return GoogleSearchResults(results=results)

def googlesearch_citation_node(nodeId: str) -> Optional[str]:

    try:
        # Prepare search arguments
        search_args = GoogleSearchArguments(query=nodeId, page=1)
        
        # Perform Google search
        search_results = perform_google_search(search_args)
        
        if search_results.results:
            # Return the URL of the top result
            return search_results.results[0].url
        else:
            return None
    except Exception as e:
        print(f"An error occurred during Google search: {str(e)}")
        return None



def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return '\n'.join(chunk for chunk in chunks if chunk)

def extract_text_from_pdf(pdf_content):
    from io import BytesIO
    return extract_text(BytesIO(pdf_content))


def fetch_and_clean_url_content(actioned_input):
    print('fetch_and_clean_url_content', actioned_input)
    dict_input=openai_structured_response_return_title_url(actioned_input)
    title = dict_input['title']
    url = dict_input['url']

    try:
        # Make a request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        content_type = response.headers.get('Content-Type')

        if 'application/pdf' in content_type:
            # Handle PDF files
            print("Detected PDF file, extracting text...")
            cleaned_text = extract_text_from_pdf(response.content)
        else:
            # Handle HTML content
            print("Detected HTML content, extracting text...")
            cleaned_text = extract_text_from_html(response.text)

        # Insert into SQLite database
        conn = sqlite3.connect('web_content.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO content (title, url, content) VALUES (?, ?, ?)
        ''', (title, url, cleaned_text))
        conn.commit()
        conn.close()

        return "Content fetched and stored successfully."
    except requests.HTTPError as e:
        return f"Failed to retrieve content: {e}"
    except Exception as e:
        return f"An error occurred: {e}"


def parse_structure(function_name: str, attempted_data: dict, error: str) -> dict:
    messages = [
        {"role": "system", "content": "You are a structure correction assistant. Your job is to correct the structure of the provided data based on the validation error."},
        {"role": "user", "content": f"The function '{function_name}' received the following data: {json.dumps(attempted_data)} and encountered the following error: {error}. Please correct the structure of the data and provide only the corrected JSON object without any additional text."}
    ]
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        temperature=0.2,
    )
    
    response_content = response.choices[0].message.content.strip()
    print(f"Response content from OpenAI (parse_structure): {response_content}")  # Debugging statement
    
    try:
        corrected_structure = json.loads(response_content)
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError in parse_structure: {str(e)}")  # Log the error
        corrected_structure = attempted_data  # Fallback to attempted_data
    
    return corrected_structure
