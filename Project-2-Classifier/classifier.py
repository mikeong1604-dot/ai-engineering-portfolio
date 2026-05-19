transactions = [
    "GRAB* RIDE 15NOV SGP $12.50",
    "FAIRPRICE FINEST TAMPINES 14NOV $67.30",
    "NETFLIX.COM 13NOV $15.98",
    "ATM WITHDRAWAL BEDOK NORTH 12NOV $500.00",
    "UNKNOWN MERCHANT XJ992 11NOV $9,999.00",
    "STARBUCKS #1242 ORCHARD 10NOV $8.90",
    "GRAB* FOOD 09NOV SGP $34.20",
    "SP SERVICES PTE LTD 08NOV $123.45",
    "COURTS MEGASTORE TAMPINES 07NOV $1,299.00",
    "TRF TO ACCOUNT 1129384756 06NOV $50.00"
]
import os
from dotenv import load_dotenv
import anthropic
import json
import re
import pandas as pd

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
def classify_transaction(transaction):
    default_system_prompt = """Based on the transaction details, determine the fields stated in the JSON in the prompt to your best discretion. 
    Refer to the JSON format below to see what values are allowed in each JSON field, the values will be delimited by a "/". 
    amount value should always be a number, with "$" appended at the front, and should be a double.
    If there is no such values, take it as a free text and answer to the best of your knowledge.
    For Anomaly detection, if the merchant name is not well known or if the amount is suspicious for that kind of transaction, classify it as an anomaly. 
    If you are not sure, classify it as not an anomaly.
    I will pass in a full list of transactions as the user input, and you will classify each transaction one by one and return the results in a list of JSON objects.
    Return the response only in JSON Format, the JSON format will be like this: 
        {"merchant": "merchant_name",
        "category": "Transport/Food/Groceries/Entertainment/Utilities/Shopping/Transfer/Other",
        "merchant_type": "merchant_type_name",
        "amount": amount_value,
        "anomaly": True/False,
        "anomaly_reason": "reason_if_any else return null"}
    """ #Set JSON format in instructions.
    transaction_text = json.dumps(transaction) # You need to pass in string into the user input. So use json dumps to conver into string)
    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=default_system_prompt,
            messages=[
                {"role": "user", "content": transaction_text}
            ]
        )
        text = message.content[0].text
        text = re.sub(r"^```json\n", "", text.strip()) #In case response is not pure JSON.
        text = re.sub(r"\n```$", "", text)
        try:
            output = json.loads(text)
            if len(output) != len(transaction):
                print("Warning: The number of classified transactions does not match the input transactions. Please check the response format and content.")
                return False
        except json.JSONDecodeError:
            output = {"error": "Failed to parse JSON", "raw_response": text}
        return output
    except anthropic.APIStatusError as e:
       print(f"HTTP error occurred: {e.status_code} - {e.message}")
    except anthropic.APIConnectionError as e:
        print(f"Connection error occurred: {e}")
    except anthropic.APITimeoutError as e:
        print(f"Request timed out: {e}")
    except  anthropic.APIError as e:
        print(f"An error occurred: {e}")
def classify_all(transactions: list):
    classification = classify_transaction(transactions)
    if not classification:
        print("Classification failed. Please check the error messages and try again.")
        return []
    else:
        return pd.DataFrame(classification)
df =classify_all(transactions)
print(f"Total Transactions: {len(df)}")
print(f"Categories breakdown:\n{df['category'].value_counts()}")
print(f"Anomalies detected: {(df['anomaly'] == True).sum()}")
anomalies = df.loc[df['anomaly'] == True, ["merchant","amount","anomaly_reason"]].values
for i in range(len(anomalies)):
    merchant, amount, reason = anomalies[i]
    print(f"- {merchant} {amount} -> {reason}")

