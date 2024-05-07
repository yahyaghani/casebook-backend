from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Type, Any, List
import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain import hub
from langchain.tools import BaseTool
from langchain.tools.tavily_search import TavilySearchResults
from langchain.pydantic_v1 import BaseModel,Field
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from typing import Optional, Type, Any
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from fastapi import FastAPI
from typing import Type, Any, List, Dict
from langchain_google_community import GoogleSearchAPIWrapper

class GoogleSearchInput(BaseModel):
    query: str = Field(description="The search query string")
    document_type: str = Field(description="The type of document: legislation or caselaw")
    k: int = Field(default=5, description="Number of search results to return")

class GoogleSearchTool(BaseTool):
    name = "Google_Search_Tool"
    description = "Searches using Google Custom Search Engine based on document type and returns top results, to run the search we need a{query},the{document_type},and number of searches{5}"
    args_schema: Type[BaseModel] = GoogleSearchInput

    def _run(self, query: str, document_type: str, k: int, run_manager: Any = None) -> List[Dict]:
        results = google_search(query, document_type, k)
        # Convert results into a structured list of dicts
        formatted_results = [{"title": item.split(",")[0][7:], "link": item.split(",")[1][6:]} for item in results.split('\n')]
        return formatted_results

# Base environment variables for API access
api_key = os.getenv('GOOGLE_API_KEY')

# Define the google_search function
def google_search(query: str, document_type: str, k: int = 5) -> str:
    # Assuming that CSE_IDS is defined somewhere in the file
    CSE_IDS = {
        "legislation": "e26f2cfedfd1c425b",
        "caselaw": "754370c1b456c454f"
    }
    
    if document_type not in CSE_IDS:
        raise ValueError("Invalid document type provided.")
    
    os.environ["GOOGLE_CSE_ID"] = CSE_IDS[document_type]
    search_api = GoogleSearchAPIWrapper()  # Make sure GoogleSearchAPIWrapper is defined or imported
    results = search_api.results(query, k)
    return "\n".join([f"Title: {item['title']}, Link: {item['link']}" for item in results])

# Assuming previous imports and definitions are available

# Initialize your Google search tool
google_search_tool = GoogleSearchTool()

###############
# from here we will use in agents , this is just for demo
# List all tools including the new Google search tool
tools = [ google_search_tool]

model = ChatOpenAI(model="gpt-3.5-turbo")
# Bind these tools to your language model
llm_with_tools = model.bind_tools(tools=tools)
prompt = hub.pull("hwchase17/openai-tools-agent")

# Define your agent with the tools
agent = (
    {"input": lambda x: x["input"], "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"])}
    | prompt
    | llm_with_tools
    | OpenAIToolsAgentOutputParser()
)

# Set up the agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# agent_executor.invoke({"input": "Fine the key legal caselaw for multiple claimaints, then lets analyse how we can challenge our current judgement based on the readings from the retrieved caselaw,current judgement=I reiterate, however, what I said at [8] and [51] above, namely that O15 r4 allowed \nmultiple claimants to bring their claims in a single writ (now claim form) where \u201csome \ncommon question of law or fact\u201d arose and where their claims arose out of the same \ntransaction or series of transactions. Those were not exclusionary tests, because there \nremained the fall back of the permission of the court. Nonetheless, it seems to me that \nit would be valuable for the CPRC to have another look at the current provisions, with \na  view  to  considering  whether  the  existing  rules  are  working  well  or  whether  a \nrequirement for common questions of law or fact to be identified could usefully have \nbeen brought across from the RSC"})
