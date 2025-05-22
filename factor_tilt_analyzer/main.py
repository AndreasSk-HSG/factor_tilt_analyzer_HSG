import time
from config import valid_mkt_benchmarks, benchmark_names
from utils.validity_input_check import check_validity_tickers
from data.data_fetcher import fetch_returns, fetch_benchmark_returns
from analysis.portfolio_statistics import compare_portfolio_with_market_benchmark
from analysis.minimum_variance_portfolio import calculate_mvp_portfolio
from analysis.portfolio_analyzer import factor_analysis_regression, analyze_factor_exposures

"""
For testing purposes:

# tickers = ["TSLA", "AAPL", "F", "INTC", "WMT", "MCD", "KO"] # Tesla, Apple, Ford, Intel, Walmart, McDonalds, Coca Cola
# mkt_benchmark_ticker = "^GSPC" # S&P 500

returns_df = fetch_returns(tickers)
mkt_returns_df = fetch_benchmark_returns(mkt_benchmark_ticker)
"""

def main() -> None:
    """
    Entry point for the Factor Tilt Analyzer application.

    This function interacts with the user to:
    - Prompt for a list of stock tickers to analyze
    - Prompt for a market benchmark selection (e.g., S&P 500, Russell 2000)
    - Download historical monthly return data for the selected stocks and benchmark
    - Construct the minimum variance portfolio (MVP) using historical returns
    - Compare performance statistics between the MVP and the benchmark
    - Analyze the MVP’s factor exposures using a regression on Fama-French + Momentum factors

    The function performs input validation, error handling, and graceful exits 
    in case of invalid inputs or data download failures.

    Returns
    -------
    None
        This function has no return value. Results are printed directly to the console.
    """

    try: 
        print("=== Factor Tilt Analyzer ===")
    
        # Prompt for stock tickers
        # Store the input in a list and transform string to uppercase
        tickers = input("Enter tickers (comma-separated). At least two stocks are required: ").upper().split(",") 
        # Remove possible whitespace
        tickers = [ticker.strip() for ticker in tickers]
        
        if len(tickers) < 2:
            print("The program failed because at least two tickers are required to calculate the minimum variance portfolio.")
            return # Gracefully exit without stack trace
        
        print(f"\nYou selected: {tickers}\n")
        # Check the validity of the tickers: 
        if not check_validity_tickers(tickers):
            # Abort the program if some tickers are invalid
            print("The program failed because of invalid tickers. Please make sure to provide valid tickers and restart the program.")
            return # Gracefully exit without stack trace
            
        # Prompt user with options for the market portfolio (benchmark)
        print("What market index would you like to choose as a benchmark?\n")
        for i, name in enumerate(benchmark_names, start=1):
            print(f"Option {i}: {name}")
        
        # Get and validate user input
        while True:
            user_input = input("\nEnter a number between 1 and 3 for the corresponding market benchmark: ").strip()
            if user_input.isdigit():
                selection = int(user_input)
                if 1 <= selection <= len(valid_mkt_benchmarks):
                    mkt_benchmark_ticker = valid_mkt_benchmarks[selection - 1]
                    break
            print("Invalid input. Please enter 1, 2, or 3.")
            
        print(f"\nYou selected: {benchmark_names[selection - 1]} ({mkt_benchmark_ticker})\n")
    
        print("\nDownloading return data...")
        time.sleep(2) # Small break so printing is consistent
    
        # Function call to retrieve returns from the Yahoo Finance API via yfinance 
        try:
            returns_df = fetch_returns(tickers, in_end = "2025-01-01") # Return time series for all stocks
            mkt_returns_df = fetch_benchmark_returns(mkt_benchmark_ticker, in_end = "2025-01-01") # Return time series for the market benchmark
        except Exception as e:
            print(f"\nFailed to download return data: {e}. Program terminated.")
            return # Gracefully exit without stack trace
        
        if returns_df.empty:
            print("\nNo return data found for the selected tickers. Program terminated.")
            return
        if mkt_returns_df.empty:
            print("\nNo return data found for the market benchmark. Program terminated.")
            return
        if returns_df.shape[0] < 5:
            print("\nNot enough return data to analyze the portfolio (need at least 5 periods). Program terminated.")
            return
        
        # Calculate the minimum variance portfolio based on the time series of returns for the individual stocks
        portfolio_returns = calculate_mvp_portfolio(returns_df)
            
        # Compare key portfolio statistics across the constructed minimum variance portfolio and the market benchmark:
        mkt_returns = mkt_returns_df["MKT"] # Convert pd.DataFrame into pd.Series
        
        # Validate date overlap
        if portfolio_returns.index.intersection(mkt_returns.index).empty:
            print("\nNo overlapping dates between portfolio and market benchmark. Program terminated.")
            return
        
        time.sleep(1) # Small break
    
        print("\nPortfolio vs. Benchmark Statistics:")
        # Function call prints key portfolio statistics to console
        compare_portfolio_with_market_benchmark(portfolio_returns, mkt_returns)
        
        # Beyond conventional portfolio statistics, analyze the Fama-French factor exposures of the portfolio
        # Function call constructs the necessary datasets, fits the regression, and returns the regression outputs
        betas = factor_analysis_regression(portfolio_returns, mkt_returns)
        
        # Function call to analyze the betas (factor exposures) in an intuitive, visual way inside the console
        analyze_factor_exposures(betas)
    
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}. Program terminated.")
    
if __name__ == "__main__":
    main()
