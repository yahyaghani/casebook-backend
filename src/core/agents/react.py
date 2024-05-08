# from langchain import hub
# from langchain.agents import AgentExecutor, create_react_agent
# from langchain_community.tools.tavily_search import TavilySearchResults
# from langchain_openai import OpenAI
# from langchain_core.messages import AIMessage, HumanMessage
# from src.core.test_tool_customsearch import GoogleSearchInput, GoogleSearchTool, google_search, google_search_tool

# ##### Don't use langchain comps, a waste of time ######


# # tools = [TavilySearchResults(max_results=2)]
# tavily=TavilySearchResults(max_results=2)
# # Get the prompt to use - you can modify this!
# prompt = hub.pull("hwchase17/react")

# # Choose the LLM to use
# llm = OpenAI()
# tools = [ google_search_tool]

# # # Construct the ReAct agent
# # agent = create_react_agent(llm, tools, prompt)

# # # Create an agent executor by passing in the agent and tools
# # agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# # agent_executor.invoke({"input": "Fine the key legal caselaw for multiple claimaints, then lets analyse how we can challenge our current judgement based on the readings from the retrieved caselaw,current judgement=I reiterate, however, what I said at [8] and [51] above, namely that O15 r4 allowed \nmultiple claimants to bring their claims in a single writ (now claim form) where \u201csome \ncommon question of law or fact\u201d arose and where their claims arose out of the same \ntransaction or series of transactions. Those were not exclusionary tests, because there \nremained the fall back of the permission of the court. Nonetheless, it seems to me that \nit would be valuable for the CPRC to have another look at the current provisions, with \na  view  to  considering  whether  the  existing  rules  are  working  well  or  whether  a \nrequirement for common questions of law or fact to be identified could usefully have \nbeen brought across from the RSC"})

