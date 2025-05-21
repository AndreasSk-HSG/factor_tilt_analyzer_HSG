import yfinance as yf
import re

def check_validity_tickers(tickers: list[str]) -> bool:
    """
    Runs a number of checks to validate the input provided by the user before the input is passed to other functions.

    Parameters
    ----------
    tickers : list[str]
        List of stock tickers, in string format.

    Returns
    -------
    bool
        True if all tickers are valid, False otherwise.

    """
        
    
    # Tickers need to be in a list
    if not isinstance(tickers, list):
        return False
    # List of tickers cannot be empty
    if not tickers:
        return False
    # Individual tickers must be a string
    if not all(isinstance(ticker, str) for ticker in tickers):
        return False
    
    # Strip whitespace from each ticker
    tickers = [ticker.strip() for ticker in tickers]
    
    # Tickers must be at least one character
    if not all(len(ticker) >= 1 for ticker in tickers):
        return False
    
    # Regex allows uppercase/lowercase letters, digits, '.', '-', '^'
    pattern = re.compile(r"^[A-Za-z0-9\-\.\^]+$")
    if not all(pattern.match(ticker) for ticker in tickers):
        return False
    
    # Individual tickers must be valid:
    # Check if Yahoo Finance has a valid record for each individual ticker by calling the API
    for ticker in tickers:
        try:
            if not check_valid_ticker_with_API(ticker):
                return False
        except Exception:
            return False

    return True

    
def check_valid_ticker_with_API(ticker: str) -> bool:  
    """
    Checks whether a stock ticker is valid by querying Yahoo Finance via yfinance.
    
    Parameters
    ----------
    ticker : str
        A single stock ticker symbol.
    
    Raises
    ------
    TypeError
        If input is not a string.
    ValueError
        If input is an empty string.
    Exception
        Yahoo Finance API will raise an AttributeError for invalid stock tickers. 
    
    Returns
    -------
    bool
        True if ticker is valid (i.e., info is returned), False otherwise.
    """
    
    
    if not isinstance(ticker, str):
        raise TypeError("Ticker must be a string.")
    ticker = ticker.strip()
    if not ticker:
        raise ValueError("Ticker cannot be an empty string.")
        
    # Call the Yahoo Finance API
    # API will raise an AttributeError for invalid stock tickers
    try:
        info = yf.Ticker(ticker).info
        # Sometimes yf.Ticker(ticker).info does not raise an error but returns an empty dict {}
        # Handle this here
        return info is not None and len(info) > 0
    except:
        return False

