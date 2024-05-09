from openai import OpenAI
import re
import httpx
import os 
from src.core.process.helpers_web_parse_cleaner import clean_html,tfidf_extract_keywords,convert_spaces_to_percent20,perform_google_search,perform_google_search_legislation,fetch_and_clean_url_content,smart_parse_action_input
from src.core.tools.g_search import GoogleSearchAPIWrapper
from src.core.test_tool_customsearch import agent_executor
from bs4 import BeautifulSoup
from src.core.prompts.search_prompt import search_sample
from src.db.chroma_model import query_articles,fetch_and_store_content_chromadb
# from app import socketio  # Import the socketio instance
# from src.extensions import socketio
# from flask_socketio import emit

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

known_actions = {
    "legislation_search":  perform_google_search_legislation, 
    "google_search":perform_google_search,
    "store_website_content":fetch_and_store_content_chromadb,
    'read_stored_articles':query_articles

}

action_re = re.compile('^Action: (\w+): (.*)$')

def extract_last_action(text):
    # Extracts and returns the last planned action before a PAUSE
    actions = [action_re.match(a) for a in text.split('\n') if action_re.match(a)]
    if actions:
        return actions[-1].groups()
    return None, None


class SearchAgent:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})
    
    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result
    
    def execute(self):
        completion = client.chat.completions.create(model="gpt-3.5-turbo-0125", messages=self.messages,
                                                    temperature=0.5)
        
        
        # Uncomment this to print out token usage each time, e.g.
        # {"completion_tokens": 86, "prompt_tokens": 26, "total_tokens": 112}
        # print(completion.usage)
        return completion.choices[0].message.content

def handle_chat_query(question, max_turns=4):
    i = 0
    bot = SearchAgent(search_sample)
    next_prompt = question
    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        print('result from next iteration of bot',result)
        # Emit answer if it exists in the response
        for line in result.split('\n'):
            if line.startswith("Answer:"):
                socketio.emit('openai-query-response', {'recommendation': line[7:]})  # Emit only the text after 'Answer:'
            
        actions = [action_re.match(a) for a in result.split('\n') if action_re.match(a)]
        
        if actions:
            action, action_input = actions[0].groups()
            if action not in known_actions:
                raise Exception(f"Unknown action: {action}: {action_input}")
            print(f" -- running {action} {action_input}")
            # Execute the action
            observation = known_actions[action](action_input)
            print("Observation after actions:", observation)
            # Update the prompt with the observation to move out of PAUSE
            next_prompt = f"Observation: {observation}"
        else:
            if "PAUSE" in result:
                # If in PAUSE, move to perform the action
                last_action, last_input = extract_last_action(result)
                if last_action and last_input:
                    observation = known_actions[last_action](last_input)
                    print("Observation after PAUSE:", observation)
                    next_prompt = f"Observation: {observation}, I must remember the user's query  :{question}"
                continue
            return
        

# # Test the improved function with a complex input
# query("What is the legislation on AI in the UK?")

        