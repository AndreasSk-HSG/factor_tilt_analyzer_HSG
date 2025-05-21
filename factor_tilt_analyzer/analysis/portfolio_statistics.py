import numpy as np
import pandas as pd

# Interval factors are required to scale daily, monthly, or yearly returns and volatility
# Daily -> 252 trading days / year
# Monthly -> 12 months / year 
valid_interval_factors = {"daily": 252, "monthly": 12, "yearly": 1} 


def compare_portfolio_with_market_benchmark(portfolio_returns: pd.Series, mkt_returns: pd.Series, interval: str = "monthly") -> None:
    """
    Calculates key portfolio statistics for the portfolio of stocks and a chosen market benchmark, and prints the 
    summary statistics in the console for each portfolio.
    
    Parameters
    ----------
    portfolio_returns : pd.Series
        Time series of returns for the portfolio of stocks.
    mkt_returns : pd.Series
        Time series of returns for the market benchmark portfolio.
    interval : str, optional
        Frequency of the returns used for annualization. Must be 'daily', 'monthly', or 'yearly'.
        Default is 'monthly'.
    
    Raises
    ------
    TypeError
        If input types are incorrect. Interval must be string, time series of both returns must be pd.Series.

    ValueError
        If the return series are empty, misaligned, contain invalid values, or the interval is not supported.
        Only 'daily', 'monthly' and 'yearly' intervals are valid.
    
    Returns
    -------
    None
        Prints the calculated statistics to the console.
    """


    # Type checks
    if not isinstance(interval, str):
        raise TypeError("Interval must be a string.")
    if not isinstance(portfolio_returns, pd.Series):
        raise TypeError("Portfolio returns must be a pandas Series.")
    if not isinstance(mkt_returns, pd.Series):
        raise TypeError("Market returns must be a pandas Series.")
    
    # Value checks
    if portfolio_returns.empty or mkt_returns.empty:
        raise ValueError("Return series cannot be empty.")        
    if not np.isfinite(portfolio_returns).all():
        raise ValueError("Portfolio return series contains NaN or infinite values.")
    if not np.isfinite(mkt_returns).all():
        raise ValueError("Market return series contains NaN or infinite values.")

    if portfolio_returns.index.intersection(mkt_returns.index).empty:
        raise ValueError("Portfolio and market return series must share overlapping dates.")

    interval = interval.lower()
    if interval not in valid_interval_factors:
        raise ValueError("Invalid interval. Must be 'daily', 'monthly', or 'yearly'.")

    # Calculate portfolio statistics for the MVP portfolio and the market benchmark:
    portfolio_stats = calculate_portfolio_statistics(portfolio_returns = portfolio_returns, interval = interval)
    mkt_stats = calculate_portfolio_statistics(portfolio_returns = mkt_returns, interval = interval)
    
    # Print the portfolio statistics:
    print_portfolio_statistics(portfolio_stats = portfolio_stats, portfolio_name = "Minimum Variance Portfolio")
    print_portfolio_statistics(portfolio_stats = mkt_stats, portfolio_name = "Market Benchmark")


def calculate_portfolio_statistics(portfolio_returns: pd.Series, interval: str = "monthly") -> dict:        
    """
    Calculates key portfolio statistics based on the provided time series of returns.
    
    Parameters
    ----------
    portfolio_returns : pd.Series
        Time series of portfolio returns. Must not contain NaNs or infinite values.
    interval : str, optional
        Frequency of the returns (used for annualization). One of: 'daily', 'monthly', 'yearly'.
        Default is 'monthly'.
    
    Raises
    ------
    TypeError
        If inputs are not of expected types. Interval must be string, time series of returns must be pd.Series.
    ValueError
        If the return series is empty, contains invalid values, or the interval string is not recognized.
    
    Returns
    -------
    dict
        Dictionary with key portfolio statistics containing:
            - mean_return
            - annualized_return
            - std_dev
            - annualized_volatility
            - sharpe_ratio (rf=0)
            - cumulative_return
            - max_drawdown
    """
    
    
    # Type validation
    if not isinstance(interval, str):
        raise TypeError("Interval must be a string.")
    if not isinstance(portfolio_returns, pd.Series):
        raise TypeError("Portfolio returns must be a pandas Series.")
   
    # Value checks
    if portfolio_returns.empty:
        raise ValueError("Portfolio return series cannot be empty.")
    if not np.isfinite(portfolio_returns).all():
        raise ValueError("Portfolio return series contains NaN or infinite values.")

    interval = interval.lower()
    if interval not in valid_interval_factors:
        raise ValueError("Invalid interval factor. Must be one of: daily, monthly, yearly.")
        
        
    interval_factor = valid_interval_factors[interval]
    
    mean_return = portfolio_returns.mean() # Avg. return
    annualized_return = mean_return * interval_factor # Annualized return (approximately: mean_return * interval)

    # Portfolio standard deviation and annualized standard deviation:
    std_dev = portfolio_returns.std()
    annualized_volatility = std_dev * np.sqrt(interval_factor)

    # Sharpe ratio (assuming risk-free rate is 0):
    if annualized_volatility == 0:
        sharpe_ratio = np.nan
    else:
        sharpe_ratio = annualized_return / annualized_volatility
    
    # Cumulative geometric return:
    cumulative_return = (1 + portfolio_returns).cumprod()
    # Last value from time series of returns:
    cum_return = cumulative_return.iloc[-1] - 1

    # Maximum drawdown:
    rolling_max = cumulative_return.cummax()
    drawdown = cumulative_return / rolling_max - 1
    max_drawdown = drawdown.min()
    
    # Return a dictionary with the key portfolio statistics:
    return {
        "mean_return": mean_return,
        "annualized_return": annualized_return,
        "std_dev": std_dev,
        "annualized_volatility": annualized_volatility,
        "sharpe_ratio": sharpe_ratio,
        "cumulative_return": cum_return,
        "max_drawdown": max_drawdown
    }


def print_portfolio_statistics(portfolio_stats: dict, portfolio_name: str) -> None:
    """
    Prints standardized summary statistics for a portfolio to the console.
    
    Parameters
    ----------
    portfolio_stats : dict
        Dictionary containing key performance statistics of the portfolio.
        Must include: mean_return, annualized_return, std_dev, annualized_volatility,
        sharpe_ratio, cumulative_return, max_drawdown.
    portfolio_name : str
        Label for the portfolio (e.g., "Minimum Variance Portfolio", "Market Benchmark").
    
    Raises
    ------
    TypeError
        If inputs are not the correct types, or if dictionary values are not numeric. 
        portfolio_stats must be dictionary, portfolio_name must be string.
    ValueError
        If the input dictionary is empty.
    KeyError
        If any required keys are missing from the dictionary.
    
    Returns
    -------
    None
        No return value, function only prints standardized output to console.
    """
    
    
    # Type checks
    if not isinstance(portfolio_stats, dict):
        raise TypeError("Portfolio statistics must be provided as a dictionary.")
    if not isinstance(portfolio_name, str):
        raise TypeError("Portfolio name must be provided as a string.")
    
    # Value checks
    if len(portfolio_stats) == 0:
        raise ValueError("Portfolio statistics dictionary cannot be empty.")
    
    required_keys = [
       "mean_return", "annualized_return", "std_dev",
       "annualized_volatility", "sharpe_ratio",
       "cumulative_return", "max_drawdown"]
    
    # Check if any dictionary keys are missing
    missing_keys = [key for key in required_keys if key not in portfolio_stats]
    if missing_keys:
       raise KeyError(f"Missing key(s) in portfolio statistics dictionary: {missing_keys}. "
                      f"Required keys are: {required_keys}.")
    
    # Values in dictionary must be int or float
    for key in required_keys:
        if not isinstance(portfolio_stats[key], (int, float)):
           raise TypeError(f"Value for '{key}' must be numeric (int or float), but got {type(portfolio_stats[key]).__name__}.")
    
   
    # Begin printing
    print(f"\n\t=== {portfolio_name} Performance ===\n")

    output = f"""\
        Mean Return          : {portfolio_stats["mean_return"]:.2%}
        Annualized Return    : {portfolio_stats["annualized_return"]:.2%}
        Volatility           : {portfolio_stats["std_dev"]:.2%}
        Annualized Volatility: {portfolio_stats["annualized_volatility"]:.2%}
        Sharpe Ratio (rf=0)  : {portfolio_stats["sharpe_ratio"]:.2f}
        Cumulative Return    : {portfolio_stats["cumulative_return"]:.2%}
        Maximum Drawdown     : {portfolio_stats["max_drawdown"]:.2%} \n
    """

    print(output)

