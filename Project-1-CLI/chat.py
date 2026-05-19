import os
from dotenv import load_dotenv
import requests
import anthropic

# Load your API key from .env
load_dotenv()

# Initialise the client
# It automatically reads ANTHROPIC_API_KEY from environment
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
message_history = []
def get_input():
    user_input = input("You: ")
    return user_input
def call_claude(message_history):
    default_system_prompt = "You only answer in A,B,C,D" #Use system prompt to set the be
    #haviour of claude.
    # TODO: Call client.messages.create() with the right parameters
    # Refer to: https://docs.anthropic.com/en/api/getting-started
    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1,
            system=default_system_prompt,
            messages=message_history #You can send message_history as a list of messages.
        )
    except anthropic.APIStatusError as e: #Error codes From documentation.
       print(f"HTTP error occurred: {e.status_code} - {e.message}")
    except anthropic.APIConnectionError as e:
        print(f"Connection error occurred: {e}")
    except anthropic.APITimeoutError as e:
        print(f"Request timed out: {e}")
    except  anthropic.APIError as e: #Generic error should be the last except.
        print(f"An error occurred: {e}")
    else:  
        if message.stop_reason == "max_tokens":
            print("Response was cut off due to max_tokens limit, please increase max_tokens and try again")
            return False
        else:
            text = message.content[0].text
            input_usage = message.usage.input_tokens
            output_usage = message.usage.output_tokens
            print(f"Input tokens used: {input_usage}, Output tokens used: {output_usage}")
            message_history.append({"role": "assistant", "content": text})
            return (text, input_usage, output_usage)
def clear_message_history():
    message_history.clear()
    output_counter = 0
    print("Message history cleared. You can start a new conversation.")

# TODO: Print the response text
# Hint: the response object is not a plain string
# Try printing the whole `message` object first to see its structure
output_counter = 0
user_input = get_input()
while user_input != "exit":
    if user_input == "clear":
        clear_message_history()
        break
    else:
        if output_counter >= 100:
            print("You have reached the output token limit of 100 tokens. Please clear the message history to continue.")
            continue
        else:
            message_history.append({"role": "user", "content":user_input})
            response = call_claude(message_history)
            if response == False:
                break
            text, input_usage, output_usage = response
            output_counter += output_usage
            print(f"Input tokens used: {input_usage}, Output tokens used: {output_usage}, Total output tokens used:{output_counter}")
            print(f"Claude: {text}")
            if output_counter>= 100:
                print("You have reached the output token limit of 100 tokens. Please clear the message history to continue.")
                break
    user_input = get_input()
print("Thanks for using the chat, see you again")
