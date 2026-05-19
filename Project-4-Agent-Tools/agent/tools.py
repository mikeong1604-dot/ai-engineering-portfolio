import yfinance as yf
import pandas as pd
import os

data = pd.read_csv(os.path.join(os.path.dirname(__file__), "data/companies.csv"))
BLOCKED_TICKERS = ["GME", "AMC", "BBBY"]  # Example: block meme stocks

def validate_ticker(ticker: str) -> bool:
    if ticker in BLOCKED_TICKERS:
        return False
    if "@" in ticker or "/"in ticker or "#" in ticker or "!" in ticker or "?" in ticker:
        return False
    return True
    # TODO: Return False if ticker is in BLOCKED_TICKERS
    # TODO: Return False if ticker contains special characters
    # TODO: Return True otherwise
def get_stock_price(ticker: str) -> dict:
    if not validate_ticker(ticker):
        return {"Error" : "ticker is invalid, please remove any special characters or input a valid ticker symbol. Please try again"}
    t = yf.Ticker(ticker)
    result= t.info
    output = {}
    try:
        fiftyweekhigh = result["fiftyTwoWeekHigh"]
        fiftyweeklow = result["fiftyTwoWeekLow"]
        price = result["currentPrice"]
        volume = result["volume"]
        output = {
            "fifty_two_week_high": fiftyweekhigh,
            "fifty_two_week_low": fiftyweeklow,
            "current_price": price,
            "volume": volume
        }
    except:
        return {"error": "Invalid ticker or data not available"}
    # TODO: Use yfinance to fetch current price, 
    #       52 week high/low, and volume for the ticker
    # TODO: Return as a dict
    # TODO: Handle invalid tickers gracefully — 
    #       return an error dict, don't crash
    return output

def query_company_data(ticker: str) -> dict:
    if not validate_ticker(ticker):
        return {"Error" : "ticker is invalid, please remove any special characters or input a valid ticker symbol. Please try again"}
    if ticker in data["ticker"].values:
        result = data.loc[data["ticker"] == ticker]
        output = result.to_dict(orient="records")
        return output
    else:
        return {"error": "Company not found"}
    # TODO: Load companies.csv into a DataFrame
    # TODO: Find the row matching the ticker
    # TODO: Return all fields as a dict
    # TODO: If ticker not found, return an error dict

def calculate_metrics(nums: list):
     #Get list of values in the dictionary
    results = {
        "sum": sum(nums),
        "average": sum(nums) / len(nums) if len(nums) > 0 else 0,
        "max": max(nums) if len(nums)>0 else None,
        "min": min(nums) if len(nums)>0 else None,
        "percentage_difference":abs(nums[1] - nums[0])/nums[0] *100 if len(nums) >1 and nums[0] != 0 else 0,
    }
    return results
    # TODO: Accept a dict of named values
    # TODO: Calculate: sum, average, max, min, percentage_difference
    #       between first and second value if exactly two values provided
    # TODO: Return results dict
    # TODO: Handle division by zero and invalid inputs
if __name__ == "__main__":
    print(get_stock_price("D05.SI"))
    print(query_company_data("OCBC.SI"))
    #print(calculate_metrics({"dbs_pe": 11.2, "ocbc_pe": 9.8}))