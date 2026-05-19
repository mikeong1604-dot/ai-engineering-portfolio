import json
from prompts import prompts
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Add the parent director
from scorer import score_with_llm, ask_LLM
from rag.retrieve import retrieve_chunks    

def run_eval(prompt_version: str) -> list[dict]:
    with open("eval/test_dataset.json") as f:
        dataset = json.load(f) #Json into a python dict list
    
    results = []
    
    for item in dataset:
        llm_answer = ask_LLM(item["question"], prompt_version)
        scores = score_with_llm(item["question"], item["ground_truth"], llm_answer)
        scores["question"] = item["question"]
        scores["ground_truth"] = item["ground_truth"]
        scores["system_answer"] = llm_answer
        scores["prompt_version"] = prompt_version
        results.append(scores)
        # TODO: Retrieve relevant chunks for the question
        # TODO: Generate answer using the specified prompt version
        # TODO: Score the answer against ground truth
        # TODO: Store question, ground truth, system answer, 
        #       scores, and prompt version in results
        
    
    return results

if __name__ == "__main__":
    print("Running V1...")
    v1_results = run_eval("v1")
    
    print("Running V2...")
    v2_results = run_eval("v2")
    
    # Save results for report generation
    with open("eval/v1_results.json", "w") as f:
        json.dump(v1_results, f, indent=2) # To convert the list of dicts into a nicely formatted JSON file
    
    with open("eval/v2_results.json", "w") as f:
        json.dump(v2_results, f, indent=2)
    
    print("Eval complete. Run report.py to see results.")