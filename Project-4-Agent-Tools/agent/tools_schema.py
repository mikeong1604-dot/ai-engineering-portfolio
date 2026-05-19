tools = [
    {
        "name": "get_stock_price",
        "description": """This tool is used for pulling basic information from yfinance about a ticker such as
         the fifty two week high and low, volume and current price. This can be used for both Singapore and US stocks. You need to pass in the actual stock market ticker of the company.
         Call this API when you need real-time data of the ticker
         if the ticker is invalid, a error response will be given to you.  """,  # TODO: Write a clear description
                               # Claude uses this to decide when to call the tool
                               # Vague descriptions = wrong tool selection
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": """Pass in the ticker symbol of the stock. 
                    For SGX tickers, append .SI to the SGX Ticker symbol. Example, for OCBC Bank, pass the ticker as OCBC.SI
                    For US stocks, you can pass the Ticker symbol as is. Example, Microsoft will be simply MSFT
                    """  # TODO: Be specific about format
                                          # e.g. SGX tickers end in .SI
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "query_company_data",
        "description": """Query from a pre-loaded CSV file that contain stock information. 
        Querying from this csv file will give, if existing in the file, information such as company name, sector, market cap (In billions)
        pe_ratio, dividend yields percentage and revenute growth percentage.
        This csv contains more in-depth information then the yfinance API call, however, this csv does not hold real-time data.
        Call this tool if the data is not time-sensitive and does not need to be real-time.""",  # TODO: Explain what data this returns
        
                               # and when to use it vs get_stock_price                   
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": """Pass in the ticker symbol of the stock. 
                    For SGX tickers, append .SI to the SGX Ticker symbol. Example, for OCBC Bank, pass the ticker as OCBC.SI
                    For US stocks, you can pass the Ticker symbol as is. Example, Microsoft will be simply MSFT
                    you should ONLY pass in the ticker symbol as a string, do not make it into a dictionary.
                    """
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "calculate_metrics",
        "description": """Call this tool when you are trying to compare the differences of two similar metrics between different stocks.
        This metrics will only tell you the certain mathematical operations such as, sum, average, max, min and percentage difference.
        All operations except percentage difference can work on a list with more than 2 keys.
        Percentage difference will only work correctly if there is 2 keys in the list passed in """,  # TODO: Explain when to use this tool
        "input_schema": {
            "type": "object",
            "properties": {
                "nums":{
                    "type": "array",
                    "items": {"type": "number"},
                    "description": """This should be the list of values that you are trying to compare or do some mathematical operation on. 
                    For example, if you are trying to compare the PE ratio between microsoft and apple, you will pass in a list like this:
                    list = [55,50]
                    If you have multiple companies, more than 2, you can add into the list with the same format.
                    """
                }
            },
            "required": ["nums"]
        }
    }
]  