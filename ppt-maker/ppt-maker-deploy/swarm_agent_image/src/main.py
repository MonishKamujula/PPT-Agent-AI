from typing import List , TypedDict , Optional
import json
from swarm.repl import run_demo_loop
from swarm import Agent
from swarm import Swarm

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import requests

import time
import dotenv
dotenv.load_dotenv()


class Message(TypedDict):
    role: str
    content: str
    name : Optional[str]

def convert_to_dict(input_string):
    sections = input_string.split("<CONTENT>")
    titles = sections[0].replace("<TITLES>", "").strip()
    descriptions = sections[1].strip()
    
    titles = titles.replace("<SEP>", "^")
    descriptions = descriptions.replace("<SEP>", "^")
    
    return {
        "title": titles,
        "description": descriptions
    }

def generate_ppt_api_request(data):
    url = "https://wwckrerv6vv3slv7t5dg54lqum0curtc.lambda-url.ap-south-1.on.aws/"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to get a valid response", "status_code": response.status_code}
    

def generate_csv_api_request(data):
    url = "https://insjcgm3iqze6g6tfl6lqcv2ru0yasgm.lambda-url.ap-south-1.on.aws/"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json={"data": data}, headers=headers)

    print("THE RESPONSE LOOKS LIKE THIS : " , response)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to get a valid response", "status_code": response.status_code}


def generate_ppt(ppt_content):
    """Generate PowerPoint content based on a single formatted string."""
    print(f"[mock] Generating PPT with content: {ppt_content}")

    data = convert_to_dict(ppt_content)
    result = generate_ppt_api_request(data)
    print(result)

    return result

def generate_csv(data):
    """Generate CSV content based on user input."""
    print("THE PROVIDED DATA IS : " , data)

    result = generate_csv_api_request(data)

    print("THE RESULT LOOKS LIKE THIS : ")
    print(result)
    return result

triage_agent = Agent(
    name="Triage Agent",
    model="gpt-4o-mini",
    instructions="Determine which agent is best suited to handle the user's request, and transfer the conversation to that agent.",
)

ppt_maker_agent = Agent(
    name="PPT Maker Agent",
    model="gpt-4o-mini",
    instructions=(
        "Ask the user for number of slides and Topics. "
        "Then generate structured PowerPoint content in the format: "
        "<TITLES>Titles1<SEP>Title2<SEP>Title3<CONTENT>Content1<SEP>Content2<SEP>Content3. "
        "Ensure the titles align with the content and pass a single formatted string to the function."
    ),
    functions=[generate_ppt],
)

csv_maker_agent = Agent(
    name="CSV Maker Agent",
    model="gpt-4o-mini",
    instructions=("Ask the user for a data topic and number of rows, then generate CSV data."
                  "For example Generate this if user asks for data about people: Name,Age,City\nAlice,25,New York\nBob,30,Los Angeles\nCharlie,22,Chicago"
                  "Pass a single formatted string to the function."
                  "Please ask user if they want to provide column names and number of rows"),
    functions=[generate_csv],
)

def transfer_back_to_triage():
    """Call this function if a user is asking about a topic that is not handled by the current agent."""
    return triage_agent

def transfer_to_ppt_maker():
    return ppt_maker_agent

def transfer_to_csv_maker():
    return csv_maker_agent

triage_agent.functions = [transfer_to_ppt_maker, transfer_to_csv_maker]
ppt_maker_agent.functions.append(transfer_back_to_triage)
csv_maker_agent.functions.append(transfer_back_to_triage)

def get_agent_from_messages(messages:List[Message]):
    if len(messages) < 2:
        return 'Triage Agent'
    return messages[-2]['agent']

def get_messages(session_id:str):
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    table = dynamodb.Table('idocgen_messages')
    response = table.query(
        KeyConditionExpression=Key('session_id').eq(session_id)
    )
    messages = response.get('Items', [])
    if not messages:
        print(f"No messages found for session_id: {session_id}")
        messages = []
    return messages 

def save_messages_to_dynamodb(session_id:str, messages:List[Message] , agent:str):
    """Save messages to DynamoDB table."""

    dynamodb = boto3.resource('dynamodb' , region_name='ap-south-1')
    table = dynamodb.Table('idocgen_messages')
 
    for index , message in enumerate(messages):
        try:
            if not message : continue 
            response = table.put_item(
                Item={
                    **message,
                    'session_id': session_id,
                    'content': message['content'] if message['content'] else '' , 
                    'time_stamp' :str(time.time()+index) ,
                    'role':message['role'] ,
                    'agent': agent
                }   
            )
            print("Messages saved to DynamoDB" , response)
        except ClientError as e:
            print(f"Failed to save messages: {e.response['Error']['Message']}")


agents = {
    "Triage Agent": triage_agent,
    "PPT Maker Agent": ppt_maker_agent,
    "CSV Maker Agent": csv_maker_agent,
    "transfer_back_to_triage": transfer_back_to_triage,
    "transfer_to_ppt_maker": transfer_to_ppt_maker,
    "transfer_to_csv_maker": transfer_to_csv_maker,
}

def run_demo_loop(
    session_id:str, context_variables=None, stream=False, debug=False
) -> None:
    client = Swarm()
    print("Starting Swarm CLI 🐝")

    '''
    take session_id instead of starting_agent 
    current_agent = get_current_agent(session_id)
    agent = agents[current_agent] ** important as agent object is required 
    messages = get_messages(session_id)
    '''

    messages = get_messages(session_id)
    last_agent = get_agent_from_messages(messages)
    agent = agents.get(last_agent , triage_agent)

    print("THE TYPE OF AGENT IS : " , type(agent))

    print("Agent Name is : " , agent.name)

    print("==================================")
    display_messages(messages)
    print("==================================")

    response = client.run(
        agent=agent,
        messages=messages,
        context_variables=context_variables or {},
        stream=stream,
        debug=debug,
    )

    save_messages_to_dynamodb(session_id=session_id, messages=response.messages , agent=response.agent.name)

    return response


def display_messages(messages):
    for message in messages:
        for key, value in message.items():
            print(f"{key.capitalize()}: {value}")
        print('=-=-=-' * 20)
    print()

def handler(event, context):
    
    data = event
    try:
        data = event.get('body') and json.loads(event['body']) or event
    except Exception as e:
        return {
            "statusCode": 400,
            "body": {"error": f"Invalid event == Unable to load data: {e}"}
        }
    session_id = data['session_id']
    message = {
        "role": "user",
        "content": data['message']
    }
    try:
        messages = get_messages(session_id)
        messages.append({"role": "user", "content": message})
        display_messages(messages)
        save_messages_to_dynamodb(session_id=session_id, messages=[message], agent='Triage Agent') 
    except Exception as e:
        return {
            "statusCode": 400,
            "body": {"error": f"Unable to access DynamoDB: {e}"}
        }
    
    response = run_demo_loop(session_id=session_id, debug=False)

    return {
        "statusCode": 200,
        "body": {"messages": response.messages , "agent": response.agent.name}}
