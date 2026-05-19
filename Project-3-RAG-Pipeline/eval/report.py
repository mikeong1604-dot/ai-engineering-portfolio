import json
with open("eval/v1_results.json") as f:
    v1_results = json.load(f)
with open("eval/v2_results.json") as f:
    v2_results = json.load(f)    
print(v1_results[0])
print(v2_results[0])
v1_total_score = sum(item["total"] for item in v1_results)
v2_total_score = sum(item["total"] for item in v2_results)
v1_factual = sum(item["factual_correctness"] for item in v1_results)
v1_groundedness = sum(item["groundedness"] for item in v1_results)
v2_factual = sum(item["factual_correctness"] for item in v2_results)
v2_groundedness = sum(item["groundedness"] for item in v2_results)
v1_completeness = sum(item["completeness"] for item in v1_results)
v2_completeness = sum(item["completeness"] for item in v2_results)
print("=" * 40)
print("     RAG EVAL REPORT — MAS FEAT DOC")
print("=" * 40)
print("Overall Scores")
print("-" * 20)
print(f"Prompt V1: {v1_total_score} / {len(v1_results) * 9} ({v1_total_score / (len(v1_results) * 9) * 100:.2f}%)") # Max score is 9 per question
print(f"Prompt V2: {v2_total_score} / {len(v2_results) * 9} ({v2_total_score / (len(v2_results) * 9) * 100:.2f}%)") # Max score is 9 per question
if v1_total_score > v2_total_score:
    winner = "Prompt V1"
else:
    winner = "Prompt V2"
print(f"Winner: {winner}")
print("SCORES BY DIMENSION")
print("-" * 20)
print(" " * 20 + "V1" + " " * 5 + "V2")
print(f"Factual Correctness: {v1_factual}/{len(v1_results)*3}    {v2_factual}/{len(v2_results)*3}")
print(f"Groundedness:        {v1_groundedness}/{len(v1_results)*3}    {v2_groundedness}/{len(v2_results)*3}")
print(f"Completeness:        {v1_completeness}/{len(v1_results)*3}    {v2_completeness}/{len(v2_results)*3}")
