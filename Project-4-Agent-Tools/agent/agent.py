import anthropic
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
from tools_schema import tools
from tools import get_stock_price, query_company_data, calculate_metrics

functions = {"get_stock_price": get_stock_price, "query_company_data":query_company_data, "calculate_metrics":calculate_metrics}
load_dotenv()
client = anthropic.Anthropic()

# Map tool names to actual functions
tool_map = {
    "get_stock_price": get_stock_price,
    "query_company_data": query_company_data,
    "calculate_metrics": calculate_metrics
}

def run_agent(user_question: str, max_iterations: int = 10) -> str:
    message = [{"role": "user", "content": user_question}] # Store history
    system_prompt = """You will use tools if available first until you find the answer. 
     I will give you the company name, based on your judgement find the ticker and input that ticker into the tools where you seem fit
     Always show your reasoning before you give your answer. Give me the reason why you decided to invoke a certain tool if needed
     Explicitly state whether data comes from live data or csv data
     You should refuse requests outside of the financial service scope, only answer when the prompt is about financial data of a ticker
     You should always give an output saying that this is not financial advice
     If you get back an error response from any tools saying the ticker is invalid, show the error message to the user and ask him to input a valid ticker"""
    for iteration in range(max_iterations):
        print(f"\n--- Iteration {iteration + 1} ---")
        print(message)
        try:
            response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens = 1000,
            system = system_prompt,
            messages = message,
            tools = tools
            )
        except anthropic.APIError as e:
            print(f"An error occurred: {e}")
            return
        if response.stop_reason == "end_turn":
            return response.content[0].text
        elif response.stop_reason == "tool_use":
            message.append({"role":"assistant","content": response.content})
            tool_message = []
            for i in response.content:
                if i.type == "tool_use": # You need to loop through all, as there can be multiple tool_use types of responses in one iteration
                    tool_id = i.id
                    tool_name = i.name
                    tool_input = i.input
                    #print(tool_name,tool_input)
                    tool_result = functions[tool_name](**tool_input)
                    #print(tool_result)
                    tool_result = json.dumps(tool_result)
                    new_message = {"type":"tool_result", "tool_use_id":tool_id, "content": tool_result}
                    tool_message.append(new_message)
            message.append({"role":"user","content":tool_message})
           
                
        
        # TODO: Call Claude with tools passed in
        # TODO: Print what the model is doing at each step
        # TODO: Check the stop_reason on the response
        #       If stop_reason == "end_turn" → model is done, return final answer
        #       If stop_reason == "tool_use" → model wants to call a tool
        
        # TODO: Loop through response content blocks
        #       Find blocks where type == "tool_use"
        #       Extract tool name and input parameters
        #       Look up the function in tool_map
        #       Execute it with the provided parameters
        #       Print what tool was called and what it returned
        
        # TODO: Append assistant response to messages
        # TODO: Append tool results to messages in correct format
        # TODO: Continue loop
        
    
    return "Max iterations reached without final answer"

if __name__ == "__main__":
    result = run_agent("Get me DBS current and previous price, compare the P/E between the two",10)
    print(f"\nFinal answer: {result}")