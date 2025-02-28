from swarm import Swarm, Agent
from openai import OpenAI
from run_demo_loop import run_demo_loop
import json
import requests
import os

# Modify the prs object to prevent overwriting the file every time.
router_agent = Agent(
    name="Router", 
    model="gpt-4o-mini", 
    instructions="""
    Your task is to identify the nature of the user's request and forward it accordingly.

     **Steps**:
    1 If the request is a general question, respond directly.
    2 If the request is related to summarizing a book or making a presentation, **forward** it to the Summarizer Agent.
    3 Ensure smooth communication between the user and the Summarizer Agent.
    4 Provide accurate and meaningful responses to general queries.
    """
)

summarizer = Agent(
    name="Summarizer",
    model="gpt-4o-mini",
    instructions="""
    You are responsible for summarizing the book of user choice.
    
    follow the following steps:

    Only ask the following questions.

    1. Ask for the name of the book to summarize.
    2. Ask how many key points the user wants.

    Show summary to the user ask the user if they want to make any changes to the summary, and make changes as the user says.

    Once user says they don't want to make any changes to the summary then ask the user if they want to make a presentation out of it.
    if user aggres to make a presentation then call the make_presentation function. Notify the user when the presentation is successfully created.
    else Ask the user if they want to do any thing else with the summary.
    """
)


def transfer_to_summarizer():
    """
    This function redirects the request to the Summarizer agent. Do not pass any arguments.
    """
    print("Transferring to Summarizer...")
    return summarizer

def transfer_to_router():
    """
    This function redirects the request to the Router agent. Do not pass any arguments.
    """
    print("Transferring to Router...")
    return router_agent

def make_presentation(titles: str, descriptions: str):
    """
    This is a function that makes a presentation based on the provided titles and descriptions. please provide the titles and descriptions in the following format.
    
    Parameters:
    titles (str): A string containing slide titles separated by '^'.
    descriptions (str): A string containing slide descriptions separated by '^'.
    
    Example:
    titles = "Introduction^Main Idea^Conclusion"
    descriptions = "Brief overview^Detailed discussion^Final thoughts"
    """
    print("Makeing presentation...")
    response = requests.post(
        url="http://127.0.0.1:5001/create_ppt",
        json={
            "title": titles,
            "description": descriptions
        }
    )
    if response.status_code != 200:
        print(response.status_code)
        raise Exception("Failed to create the presentation.")
    return "SUCCESS!"

router_agent.functions.append(transfer_to_summarizer)
summarizer.functions = [transfer_to_router, make_presentation]

def _run_demo_loop(messages_starting, last_agent):
    if last_agent is None: 
        last_agent = router_agent
    chatgpt_client = OpenAI(
        base_url="https://api.openai.com/v1",        
        api_key=os.getenv("OPENAI_API_KEY")          
    )
    # ollama_client = OpenAI(
    #     base_url="http://localhost:11434/v1/",
    #     api_key="ollama"
    # )
    client = Swarm(client=chatgpt_client)

    messages = client.run(
        agent=last_agent,
        messages=messages_starting,
    )
    content = []
    for message in messages.messages:
        if message["role"] != "assistant":
            continue

        # Print response, if any
        if message["content"]:
            content = message["content"]

        # Print tool calls in purple, if any
        tool_calls = message.get("tool_calls") or []
        if len(tool_calls) > 1:
            print("print tool call...")
        for tool_call in tool_calls:
            f = tool_call["function"]
            name, args = f["name"], f["arguments"]
            arg_str = json.dumps(json.loads(args)).replace(":", "=")
            tool_call = (f"{name}({arg_str[1:-1]})")
    last_agent = messages.agent
    role =  message["role"]
    return content, role, last_agent