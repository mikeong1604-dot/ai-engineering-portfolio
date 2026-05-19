import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Add the parent directory to the system path to allow imports from sibling directories
import pypdf
import anthropic
import os
from dotenv import load_dotenv
import chromadb
from rag.ingest import create_collection, embed_chunks
from rag.retrieve import retrieve_chunks
import json
import re
from prompts import prompts

load_dotenv()
base_dir = os.path.dirname(__file__)  # directory of the current script
filepath = os.path.join(base_dir,"test_dataset.json")
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
#collection = chromadb.PersistentClient(path="C:\\Users\\mikeo\\Projects\\Project1-CLI\\rag\\chromadb").get_collection(name="Financial_Planning")
with open(filepath, "r") as f:
    data = json.load(f)

def score_keyword(ground_truth: str, system_answer: str) -> dict:
    arr = ground_truth.split() #Split the ground truth into keywords
    result = {}
    count = 0
    for keyword in arr:
        if keyword in system_answer:
            result[keyword] = True
            count +=1
        else:
            result[keyword] = False
    return result, count/len(arr)
    # TODO: Check if key terms from ground_truth appear in system_answer
    # TODO: Return a score between 0 and 1
    # TODO: Return which keywords matched and which didn't
    return result

def score_with_llm(question: str, ground_truth: str, system_answer: str) -> dict: #Returned one JSON object without total, causing report.py to fail
    system_prompt = """ You are an evaluator agent for a RAG system. I am going to pass you 4 elements, the original question, the model answer, the answer given from the RAG agent, and the same context as the RAG agent.
    I will pass you each element one by one in the message content, starting from question, model answer, RAG agent answer and finally the context.
    I want you to evaluate the model answer and STRICTLY return me a JSON object with with the folloiwing structure:
    YOU MUST RETURN EXACTLY THESE 5 FIELDS IN EVERY JSON OBJECT RESPONSE, DO NOT DEVIATE FROM THIS FORMAT, DO NOT RETURN ANYTHING OTHER THAN THIS JSON OBJECT: 
    {
        "factual_correctness": 0-3 integer score,
        "groundedness": 0-3 integer score,
        "completeness": 0-3 integer score,
        "total": Sum of all 3 scores,
        "reasoning": Include a brief explanation for each score
    }"""
    retrieve_rag = retrieve_chunks(question, 2)

    Scoring_message = (f"Question: {question}\nModel Answer: {ground_truth}\nRAG Agent Answer: {system_answer}\nContext: {retrieve_rag}")
    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": Scoring_message}]
        )
        text = message.content[0].text
        text = re.sub(r"^```json\n", "", text.strip()) #In case response is not pure JSON.
        text = re.sub(r"\n```$", "", text)
        try:
            output = json.loads(text)
            return output
        except json.JSONDecodeError:
            output = {"error": "Failed to parse JSON", "raw_response": text}
            return text
    except anthropic.APIStatusError as e:       
        print(f"HTTP error occurred: {e.status_code} - {e.message}")
        return
    

    # TODO: Send all three to Claude with a scoring prompt
    # TODO: Ask Claude to score on three dimensions:
    #       - Factual correctness (0-3): does it match ground truth?
    #       - Groundedness (0-3): is it based on the context, not general knowledge?
    #       - Completeness (0-3): does it fully answer the question?
    # TODO: Ask Claude to return a JSON score object
    # TODO: Parse and return the scores

def ask_LLM(question: str, version:str) -> str:
    system_prompt = """I will pass in your personality the question and the context pulled from the vector database into the message."""
    #embeddings = embed_chunks([question]) #Embed question into vectors
    RAG_context = retrieve_chunks(question, 2) # Query pre-saved CPF document data with question embeddings to get relevant context.
    context = prompts[version].format(context=RAG_context, question=question) #Paste question and retrieved context into the prompt
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": context}]
        )
        return response.content[0].text
    except anthropic.APIStatusError as e:
       print(f"HTTP error occurred: {e.status_code} - {e.message}")
       return
    except anthropic.APIConnectionError as e:
        print(f"Connection error occurred: {e}")
        return
    except anthropic.APITimeoutError as e:
        print(f"Request timed out: {e}")
        return
    except  anthropic.APIError as e:
        print(f"An error occurred: {e}")
        return

#question = data[4]["question"]
#answer = data[4]["ground_truth"]
#response = (question, "v1")
#print(score_with_llm(question, answer, response))
#print(score_keyword(data[5]["ground_truth"], response))
#print(ask_LLM("What is the maximum amount of my income I should spend on insurance?", "v1"))