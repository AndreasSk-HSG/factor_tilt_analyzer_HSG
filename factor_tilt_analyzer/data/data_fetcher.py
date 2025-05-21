import yfinance as yf
import pandas as pd
from requests.exceptions import HTTPError
from config import valid_mkt_benchmarks

def get_start_date(in_end: str, in_period: str) -> str:
    """
    Calculates the start date by subtracting a time period from the end date (helper function)

    Parameters
    ----------
    in_end : str
        End date in string format, e.g., "2025-01-01". Must be a valid ISO date.
    in_period : str
        Time period to subtract from end date. Supported formats:
        - "2y" for 2 years
        - "18mo" for 18 months
        - "90d" for 90 days

    Raises
    ------
    TypeError
        If in_end or in_period is not a string.
    ValueError
        If the end date is not a valid date, or if the period format is unsupported.

    Returns
    -------
    str
        Start date in YYYY-MM-DD format.
    """
    
    if not isinstance(in_end, str):
        raise TypeError("End date must be provided as a string.")
    if not isinstance(in_period, str):
        raise TypeError("Time period must be provided as a string.")

    try:
        end = pd.to_datetime(in_end)
    except Exception as e:
        raise ValueError(f"Invalid end date format: {in_end}") from e

    # Extract numeric value and unit from in_period (e.g., "2y", "18mo", "90d")
    value_str = ''.join(filter(str.isdigit, in_period))
    unit = ''.join(filter(str.isalpha, in_period))

    # If either is empty, raise an Error since the format is invalid
    if not value_str or not unit:
        raise ValueError(f"Invalid period format: '{in_period}'. Use formats like '2y', '18mo', or '90d'.")

    value = int(value_str)

    if unit == "y":
        start = end - pd.DateOffset(years=value)
    elif unit == "mo":
        start = end - pd.DateOffset(months=value)
    elif unit == "d":
        start = end - pd.Timedelta(days=value)
    else:
        raise ValueError(f"Unsupported period unit: '{unit}'. Only 'y', 'mo', and 'd' are supported.")

    return start.strftime("%Y-%m-%d")
 

def fetch_returns(tickers: list[str], in_period: str = "2y", in_interval: str = "1mo", in_auto_adjust: bool = False, in_end: str = "2025-01-01") -> pd.DataFrame:
    """
    Fetches return time series for one or more tickers using the Yahoo Finance API (via yfinance). Financial data is retrieved from Yahoo Finance and the Adjusted Closing 
    Price is used to calculate the time series of returns for individual stocks and market indices.

    Parameters
    ----------
    tickers : list[str]
        List with stock tickers in the format of, for example, AAPL for Apple Inc. or TSLA for Tesla Inc. Retrieving the return time series
        for both would require the input ["AAPL", "TSLA"]. To retrieve the return series for the market benchmark, a list with a single ticker needs to
        be provided, e.g., ["^RUT"] for the Russell 2000 index return time series.
    in_period : str, optional
        Input period, determines how far back the time series should go. The default is "2y", representing 2 years of past data, counting from today.
    in_interval : str, optional
        Input interval, determines the data frequency. The default is "1mo", representing monthly data.
    in_auto_adjust : bool, optional
        Boolean value to download additional data. The default is False, and is required to download the Adjusted Closing Price, which is adjusted for
        stock splits and dividends.
    end : str
        Last included date. Default "2025-01-01".

    Raises
    ------
    TypeError
        If variable tickers is not of type list, or stock tickers in list tickers are not strings.
    ValueError
        If list tickers is empty, or the list contains individual stock tickers with length 0.
    HTTPError
        If call to the Yahoo Finance API returns an empty DataFrame, meaning no data was found.

    Returns
    -------
    returns_df : pd.DataFrame
        DataFrame of % returns with tickers as columns and datetime index.
        
    """
    
    # Type checks
    if not isinstance(tickers, list):
        raise TypeError("Tickers must be a list.")
    if not all(isinstance(ticker, str) for ticker in tickers):
        raise TypeError("All tickers must be strings.")
    # Value checks
    if not tickers:
        raise ValueError("Ticker list cannot be empty.")
    if not all(len(ticker.strip()) > 0 for ticker in tickers):
        raise ValueError("Each ticker must be a non-empty string.")

    # Get end and start date for download
    in_start = get_start_date(in_end = in_end, in_period = in_period)
    # Download the return series for the stock ticker(s) and first store them in a dictionary
    returns = {}
    
    for ticker in tickers:
        try:
            df = yf.download(ticker, period=in_period, interval=in_interval, auto_adjust=in_auto_adjust, start=in_start, end=in_end)
            
            # Abort the program if the API returns an empty DataFrame (implying no data was found)
            if df.empty:
                raise HTTPError(f"No data returned for ticker '{ticker}'. It may be delisted or unavailable.")
            
            # Calculate returns based on the Adjusted Closing Price (Adjusted for Stock Splits and Dividends)
            # Drop the first row with NaN values, because no % change can be calculated as the month before the first month is not downloaded
            return_series = df["Adj Close"].pct_change().dropna()
            return_series.name = ticker
            
            returns[ticker] = return_series
        except Exception as e:
            raise HTTPError(f"Failed to fetch data for '{ticker}': {e}")

    if not returns:
        raise HTTPError("No return data fetched for any ticker.")

    # Combine all return time series into a DataFrame by aligning on the index (Date)
    returns_df = pd.concat(returns.values(), axis=1)

    # Return the return time series of all stock tickers
    return returns_df


def fetch_benchmark_returns(mkt_benchmark_ticker: str, in_period: str = "2y", in_interval: str = "1mo", in_auto_adjust: bool = False, in_end: str = "2025-01-01") -> pd.DataFrame:
    """
    Fetches the return time series for a specified market benchmark ticker using the same structure as fetch_returns().
    Default arguments are set identically as in fetch_returns.

    Parameters
    ----------
    mkt_benchmark_ticker : str
        The market benchmark ticker (e.g., "^RUT", "^GSPC). Stock tickers for market benchmarks always start with '^' on Yahoo Finance.
    in_period : str, optional
        Time period for data (default = "2y"), representing 2 years of historical data from today.
    in_interval : str, optional
        Interval between observations (default = "1mo"), representing monthly data.
    in_auto_adjust : bool, optional
        Boolean value required to download the Adjusted Closing Price (default = False).
    end : str
        Last included date. Default "2025-01-01".

    Raises
    ------
    TypeError
        Market benchmark ticker is not of type string.
    ValueError
        If the ticker is empty or not in the predefined list of valid market benchmarks.
    RuntimeError
        If data fetch fails unexpectedly.

    Returns
    -------
    mkt_returns_df : pd.DataFrame
        DataFrame containing monthly returns for the specified market benchmark.
    """
    
    # Type checks
    if not isinstance(mkt_benchmark_ticker, str):
        raise TypeError("Ticker of the market benchmark must be a string.")

    mkt_benchmark_ticker = mkt_benchmark_ticker.strip()

    # Value checks
    if len(mkt_benchmark_ticker) == 0:
        raise ValueError("Market benchmark ticker must contain at least one character.")
    if not hasattr(valid_mkt_benchmarks, "__contains__"):
        raise TypeError("'valid_mkt_benchmarks' must be an iterable like a list or set.")
    if mkt_benchmark_ticker not in valid_mkt_benchmarks:
        raise ValueError(f"Invalid benchmark ticker '{mkt_benchmark_ticker}'. Valid options: {valid_mkt_benchmarks}")

    # Call the fetch_returns function with the default parameters and return a DataFrame with the return time series for the market benchmark
    try:
        mkt_returns_df = fetch_returns(
            tickers=[mkt_benchmark_ticker],
            in_period=in_period,
            in_interval=in_interval,
            in_auto_adjust=in_auto_adjust,
            in_end=in_end
        )
    except Exception as e:
        raise RuntimeError(f"Failed to fetch benchmark returns for '{mkt_benchmark_ticker}': {e}") from e

    if mkt_returns_df.shape[1] != 1:
        raise ValueError("Benchmark returns DataFrame must contain exactly one column.")

    # Rename the column into a uniform format
    mkt_returns_df.columns = ["MKT"]
    return mkt_returns_df