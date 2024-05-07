from openai import OpenAI
import re
import httpx
import os 
from src.core.process.helpers_web_parse_cleaner import clean_html,tfidf_extract_keywords,convert_spaces_to_percent20
from src.core.tools.g_search import GoogleSearchAPIWrapper,google_search_legislation
from src.core.test_tool_customsearch import agent_executor
from bs4 import BeautifulSoup

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatAgent:
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
        completion = client.chat.completions.create(model="gpt-3.5-turbo-16k-0613", messages=self.messages)
        # Uncomment this to print out token usage each time, e.g.
        # {"completion_tokens": 86, "prompt_tokens": 26, "total_tokens": 112}
        # print(completion.usage)
        return completion.choices[0].message.content

prompt = """
You operate in a cycle of Thought, Action, PAUSE, and Observation, concluding with an Answer.
Each cycle begins with a Thought, where you ponder the legal query posed to you.
Next, you undertake an Action, accessing one of the available legal databases or computational tools to gather data pertinent to the query, then you pause.
Following the pause, the Observation phase involves analyzing and interpreting the data obtained from your action.
Finally, you synthesize this information to output an Answer that addresses the user's query.

Your available actions include:


legislation_search:
e.g., legislation_search: agent_executor.invoke({input}:"data protection act")
This action involves extracting keywords from the query using a TF-IDF model,  searching for relevant legislation on legislation.gov.uk, and processing the information to provide a concise summary or the specific sections pertinent to the inquiry.


Example session:

Question: What are the penalties for non-compliance with the GDPR?
Thought: The user needs detailed information on GDPR penalties which can be complex, involving fines calculated based on various factors.
Action: legislation_search: "GDPR penalties"
PAUSE

You will be called again with this:

Observation: The GDPR outlines penalties including fines up to 4% of annual global turnover or €20 million, whichever is greater, for certain infringements.

You then output:

Answer: Penalties for non-compliance with the GDPR can include fines of up to 4% of annual global turnover or €20 million, depending on the severity of the breach.
""".strip()


action_re = re.compile('^Action: (\w+): (.*)$')

def query(question, max_turns=10):
    i = 0
    bot = ChatAgent(prompt)
    next_prompt = question
    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        print(result)
        actions = [action_re.match(a) for a in result.split('\n') if action_re.match(a)]
        
        if actions:
            action, action_input = actions[0].groups()
            if action not in known_actions:
                raise Exception(f"Unknown action: {action}: {action_input}")
            print(f" -- running {action} {action_input}")
            # Execute the action
            observation = known_actions[action](action_input)
            print("Observation:", observation)
            # Update the prompt with the observation to move out of PAUSE
            next_prompt = f"Observation: {observation}"
        else:
            if "PAUSE" in result:
                # If in PAUSE, move to perform the action
                last_action, last_input = extract_last_action(result)
                if last_action and last_input:
                    observation = known_actions[last_action](last_input)
                    print("Observation:", observation)
                    next_prompt = f"Observation: {observation}"
                continue
            return

def extract_last_action(text):
    # Extracts and returns the last planned action before a PAUSE
    actions = [action_re.match(a) for a in text.split('\n') if action_re.match(a)]
    if actions:
        return actions[-1].groups()
    return None, None

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


known_actions = {
    "legislation_search":  legislation_search # Add this line
}

# Example question
# question = "What is the simons birthday"
query("What is the legislation on data protection in the UK?")

# Call the query func