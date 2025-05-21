import numpy as np
import pandas as pd

def calculate_mvp_weights(returns_df: pd.DataFrame) -> pd.Series:
    """
    Computes a closed-end solution for the minimum variance portfolio (MVP) based on the input DataFrame, that contains
    the time series of returns. A theoretical background on the calculation is provided in e.g., Page 10 of https://faculty.washington.edu/ezivot/econ424/portfolioTheoryMatrix.pdf
    
    Parameters
    ----------
    returns_df : pd.DataFrame
        DataFrame with the time series of returns of each stock that is going to be a part of the minimum variance portfolio.
        (columns = assets, rows = time periods).

    Raises
    ------
    TypeError
        If input is not a pandas DataFrame.
    ValueError
        If the DataFrame is empty, contains NaNs, has fewer than 2 assets,
        has too few time periods, or the covariance matrix is not invertible.
    
    Returns
    -------
    mvp_weights : pd.Series
        Optimal weights (summing to 100%) for the minimum variance portfolio.

    """
    
    # Input validation 
    if not isinstance(returns_df, pd.DataFrame):
        raise TypeError("Input must be a pd.DataFrame object with stock returns.")
        
    # Value checks
    if returns_df.empty:
        raise ValueError("Input DataFrame cannot be empty.")
    if returns_df.isnull().values.any():
        raise ValueError("Input DataFrame contains NaN values. Please handle missing data before proceeding.")
    if returns_df.shape[1] < 2:
        raise ValueError("At least two assets are required to compute the minimum variance portfolio.")
    if returns_df.shape[0] <= returns_df.shape[1]:
        raise ValueError("Number of observations must exceed the number of assets to ensure covariance matrix invertibility.")
    
    # Calculate covariance matrix based on the DataFrame with the stock return time series
    cov_matrix = returns_df.cov()
    # Convert to numpy matrix
    cov = cov_matrix.values
    # Create vector of 1, needed to calculate the MVP
    ones = np.ones(len(cov))

    # MVP weights follow the formula: w = Σ⁻¹1 / (1ᵀΣ⁻¹1)
    # Σ is the covariance matrix
    # 1 is the vector of ones
    # T stands refers to transposed matrix
    try:
        inv_cov = np.linalg.inv(cov) # inverse
    except np.linalg.LinAlgError:
        raise ValueError("Covariance matrix is singular and cannot be inverted. Try removing collinear or redundant assets.")

    weights = inv_cov @ ones # matrix multiplication notation
    weights /= ones.T @ inv_cov @ ones

    # Put into a pandas Series with tickers as index
    mvp_weights = pd.Series(weights, index=returns_df.columns)

    return mvp_weights

def calculate_mvp_portfolio(returns_df: pd.DataFrame) -> pd.Series:
    """
    Calculates the time series of portfolio returns for the minimum variance portfolio (MVP).

    Parameters
    ----------
    returns_df : pd.DataFrame
        A DataFrame containing return time series for each asset (columns = assets, rows = time periods).

    Raises
    ------
    TypeError
        If the input is not a DataFrame or if returned weights are not a Series.
    ValueError
        If the input DataFrame is empty, or contains NaNs.

    Returns
    -------
    portfolio_returns : pd.Series
        Time series of portfolio returns of the MVP.

    """
    
    
    if not isinstance(returns_df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame with asset returns.")
    if returns_df.empty:
        raise ValueError("Input DataFrame cannot be empty.")
    if returns_df.isnull().values.any():
        raise ValueError("Input DataFrame contains NaN values. Please handle missing data first.")

    # Compute weights
    mvp_weights = calculate_mvp_weights(returns_df)
    if not isinstance(mvp_weights, pd.Series):
        raise TypeError("Returned MVP weights must be a pandas Series.")
       
    # Calculate portfolio returns as weighted average of (by default) monthly returns and weights in %
    portfolio_returns = returns_df @ mvp_weights # Matrix multiplication

    if not returns_df.index.equals(portfolio_returns.index):
      raise ValueError("Mismatch in index between input data and calculated portfolio returns.")
      
    return portfolio_returns

