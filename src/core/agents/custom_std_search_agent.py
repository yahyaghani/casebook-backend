import os
import re
import httpx
from openai import OpenAI
from src.core.process.helpers_web_parse_cleaner import (
    extract_text_from_pdf, extract_text_from_html, clean_html, tfidf_extract_keywords,
    convert_spaces_to_percent20, perform_google_search, perform_google_search_legislation,
    fetch_and_clean_url_content
)
from src.db.chroma_model import query_articles, fetch_and_store_content_chromadb
# Assuming OpenAI and other imports are correctly set
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

known_actions = {
    "legislation_search": perform_google_search_legislation,
    "google_search": perform_google_search,
    "store_website_content": fetch_and_store_content_chromadb,
    'read_stored_articles': query_articles
}

action_re = re.compile(r'^Action: (\w+): (.*)$')

class SearchAgent:
    def __init__(self, initial_prompt):
        self.prompt = initial_prompt

    def query(self, question, max_tokens=350, temperature=0.3):
        prompt = self.prompt + "\nGolfer: " + question + "\nGolf AI Assistant:"
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",  # Replace with your desired model
            prompt=prompt,
            max_tokens=max_tokens,
            stop=None,
            temperature=temperature
        )
        # Extract and return text and any action from the response
        response_text = response.choices[0].text.strip()
        action_match = action_re.search(response_text)
        if action_match:
            action, action_input = action_match.groups()
            if action in known_actions:
                result = known_actions[action](action_input)
                return f"Action: {action}, Input: {action_input}, Result: {result}"
            else:
                raise ValueError(f"Action '{action}' is not defined.")
        return response_text

# Usage example
agent = SearchAgent(initial_prompt="Here's what happened last:")
result = agent.query("What is the legislation on AI in the UK?")
print(result)
