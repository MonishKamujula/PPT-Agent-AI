from agents import run_demo_loop, display_messages, get_messages, save_messages_to_dynamodb
import json

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