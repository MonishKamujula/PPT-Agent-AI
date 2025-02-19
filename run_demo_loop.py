from swarm import Swarm
from openai import OpenAI
import json
from colorama import init, Fore, Style

# Initialize colorama for colored console output
init(autoreset=True)

def process_and_print_streaming_response(response):
    """Process and print the output from a streaming response with color."""
    
    content = ""
    last_sender = ""

    for chunk in response:
        if "sender" in chunk:
            last_sender = chunk["sender"]

        if "content" in chunk and chunk["content"] is not None:
            if not content and last_sender:
                print(f"{Fore.CYAN}{last_sender}:", end=" ", flush=True)
                last_sender = ""
            print(f"{Fore.WHITE}{chunk['content']}", end="", flush=True)
            content += chunk["content"]

        if "tool_calls" in chunk and chunk["tool_calls"] is not None:
            for tool_call in chunk["tool_calls"]:
                f = tool_call["function"]
                name = f["name"]
                if not name:
                    continue
                print(f"{Fore.MAGENTA}{last_sender}: {name}()", flush=True)

        if "delim" in chunk and chunk["delim"] == "end" and content:
            print() 
            content = ""

        if "response" in chunk:
            return chunk["response"]

def pretty_print_messages(messages) -> None:
    """
    Pretty print the messages with color-coded output.
    """
    for message in messages:
        if message["role"] != "assistant":
            continue

        # Print agent name in blue
        print(f"{Fore.BLUE}{message['sender']}:", end=" ")

        # Print response, if any
        if message["content"]:
            print(f"{Fore.WHITE}{message['content']}")

        # Print tool calls in purple, if any
        tool_calls = message.get("tool_calls") or []
        if len(tool_calls) > 1:
            print()
        for tool_call in tool_calls:
            f = tool_call["function"]
            name, args = f["name"], f["arguments"]
            arg_str = json.dumps(json.loads(args)).replace(":", "=")
            print(f"{Fore.MAGENTA}{name}({arg_str[1:-1]})")

def run_demo_loop(
    starting_agent, context_variables=None, stream=False, debug=False
) -> None:
    """
    Runs an interactive demo loop with color-coded output for the CLI.
    """
    ollama_client = OpenAI(
        base_url="http://localhost:11434/v1",        
        api_key="ollama"            
    )
    client = Swarm(client=ollama_client)
    print(f"{Fore.GREEN}Starting Ollama Swarm CLI:")

    messages = []
    agent = starting_agent

    while True:
        print("-" * 30)
        user_input = input(f"{Fore.LIGHTBLACK_EX}User: ")
        print("-" * 30)

        if user_input.lower() in ["exit", "quit"]:
            print(f"{Fore.RED}Exiting...")
            break

        messages.append({"role": "user", "content": user_input})

        response = client.run(
            agent=agent,
            messages=messages,
            context_variables=context_variables or {},
            stream=stream,
            debug=debug,
        )

        if stream:
            response = process_and_print_streaming_response(response)
        else:
            pretty_print_messages(response.messages)

        messages.extend(response.messages)
        agent = response.agent
