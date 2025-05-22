import pandas as pd
import numpy as np
import statsmodels.api as sm
import os 
import logging

# Logging config — Log the regression model summary
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='factor_analysis.log', 
    filemode='a'  # 'a' to append 
)


def read_fama_french_csv(path_name: str, column_names: list[str]) -> pd.DataFrame:
    """
    Reads a Fama-French style CSV file and returns a cleaned DataFrame with a datetime index.

    This function expects the CSV file to have a date index in YYYYMM format and data values
    starting from the second column. It renames the columns based on the provided list
    and converts the index to datetime format for time series compatibility.

    Parameters
    ----------
    path_name : str
        Full path to the CSV file to read. The file must contain a YYYYMM-formatted index in the first column.
    column_names : list[str]
        A list of strings to rename the columns in the file. Must match the number of data columns in the CSV file.

    Raises
    ------
    FileNotFoundError
        If the file at "path_name" does not exist.
    TypeError
        If "column_names" is not a list of strings.
    ValueError
        If the number of columns in the CSV does not match the length of "column_names",
        or if the index cannot be converted to datetime using the format "%Y%m".

    Returns
    -------
    df : pandas.DataFrame
        A DataFrame with a datetime index and renamed columns corresponding to "column_names".
    """

    
    # Check file exists
    if not os.path.isfile(path_name):
        raise FileNotFoundError(f"File not found: {path_name}")
    
    # Check column_names is a list of strings
    if not isinstance(column_names, list) or not all(isinstance(col, str) for col in column_names):
        raise TypeError("column_names must be a list of strings.")
    
    try:
        # index_col = 0 -> Columns at column index 0 are set as row labels
        df = pd.read_csv(path_name, index_col = 0)
    except Exception as e:
        raise ValueError(f"Failed to read CSV: {e}")
        
    # Check column count
    if df.shape[1] != len(column_names):
        raise ValueError(f"Expected {len(column_names)} columns, but found {df.shape[1]} in the file.")
    
    # Rename columns
    df.columns = column_names    
    
    # Convert index from YYYYMM to datetime
    try:
        df.index = pd.to_datetime(df.index.astype(str), format="%Y%m")
    except Exception as e:
       raise ValueError(f"Failed to convert index to datetime (expected YYYYMM format): {e}")
    
    return df


def create_factor_dataset() -> pd.DataFrame:
    """
    Loads and combines momentum and Fama-French factor datasets into a single DataFrame.

    The function reads two CSV files. One containing the momentum factor (Mom),
    and one containing the Fama-French 3-factor model data (Mkt_rf, SMB, HML, Rf).
    It joins the two datasets on their datetime index and performs basic validation.

    Raises
    ------
    FileNotFoundError
        If any of the required CSV files are missing.
    IOError
        If an error occurs while reading the CSV files.
    ValueError
        If the datasets cannot be joined, contain missing values after the join,
        or do not include all expected columns ("Mom", "Mkt_rf", "SMB", "HML", "Rf").

    Returns
    -------
    combined_factors_df : pandas.DataFrame
        A DataFrame indexed by datetime, containing the combined factor data:
        - Mom: Momentum factor
        - Mkt_rf: Market excess return
        - SMB: Size premium
        - HML: Value premium
        - Rf: Risk-free rate
    """
        
    # Load the CSV with the momentum factor
    mom_path = "input/momentum_factor.csv"
    
    # Load the CSV with the other three factors (Market, SMB, HML)
    three_factors_path = "input/research_factors.csv"
    
    # Make sure path is valid
    if not os.path.exists(mom_path):
        raise FileNotFoundError(f"Missing file: {mom_path}")
    if not os.path.exists(three_factors_path):
        raise FileNotFoundError(f"Missing file: {three_factors_path}")
    
    # Error-handling for reading CSV files
    try:
        mom_df = read_fama_french_csv(mom_path, ["Mom"])
    except Exception as e:
        raise IOError(f"Failed to read {mom_path}: {e}")

    try:
        three_factors_df = read_fama_french_csv(three_factors_path, ["Mkt_rf", "SMB", "HML", "Rf"])
    except Exception as e:
        raise IOError(f"Failed to read {three_factors_path}: {e}")

    # Error-handling for joining CSV files
    try:
        combined_factors_df = mom_df.join(three_factors_df, how="inner")
    except Exception as e:
        raise ValueError(f"Failed to join momentum and Fama-French datasets: {e}")

    # Checks for the final DataFrame
    if combined_factors_df.isnull().values.any():
        raise ValueError("Combined factor dataset contains missing values after join.")

    required_columns = {"Mom", "Mkt_rf", "SMB", "HML", "Rf"}
    if not required_columns.issubset(combined_factors_df.columns):
        missing = required_columns - set(combined_factors_df.columns)
        raise ValueError(f"Missing required columns in combined dataset: {missing}")

    return combined_factors_df


def factor_analysis_regression(portfolio_returns: pd.Series, mkt_returns: pd.Series, log: bool = True) -> pd.Series:
    """
    Fits an OLS regression of portfolio returns on Fama-French factors.
    Specifically, portfolio returns are regressed on Mkt_rf, SMB, HML, and Mom.

    Parameters
    ----------
    portfolio_returns : pd.Series
        Time series of returns of the constructed portfolio (with datetime index).
    mkt_returns : pd.Series
        Time series of market benchmark returns (with datetime index).
    log : bool, optional
        If True, logs the regression summary to file via the logging module.

    Raises
    ------
    TypeError
        If inputs are not pandas Series or lack a datetime index.
    ValueError
        If inputs are empty, unaligned in time, or contain missing values. If the final regression dataset has fewer 
        than 5 rows, which would overfit the model.
    RuntimeError
        If the regression model fails to fit.

    Returns
    -------
    betas : pd.Series
        The factor exposures (betas) from the OLS regression, excluding the intercept.
    """
    
    # Input validation 
    if not isinstance(portfolio_returns, pd.Series):
        raise TypeError("Portfolio returns must be provided as pandas Series.")
    if not isinstance(mkt_returns, pd.Series):
        raise TypeError("Market returns must be provided as pandas Series.")
    
    if len(portfolio_returns) == 0 or len(mkt_returns) == 0:
        raise ValueError("Both input series must be non-empty.")

    if portfolio_returns.index.dtype != "datetime64[ns]" or mkt_returns.index.dtype != "datetime64[ns]":
        raise TypeError("Both series must have a datetime index.")

    if portfolio_returns.index.intersection(mkt_returns.index).empty:
        raise ValueError("The input series must have overlapping dates.")
    
    # Combine the pd.Series for portfolio returns and market returns into a DataFrame
    joined_returns = pd.concat([portfolio_returns, mkt_returns], axis=1)
    joined_returns.columns = ["Portfolio", "MKT"]
    
    if joined_returns.isnull().values.any():
        raise ValueError("Input return series contain missing values. Please clean the data first.")
    
    # Scale by 100, so that all values are expressed as percentages for the regression
    joined_returns *= 100
    
    # Join the combined returns to the factor DataFrame
    combined_factors_df = create_factor_dataset()
    final_df = joined_returns.join(combined_factors_df, how="inner")

    if final_df.shape[0] < 5:
        raise ValueError("Not enough overlapping data points to run regression.")

    # Calculate the excess portfolio return
    final_df["Portfolio_excess"] = final_df["Portfolio"] - final_df["Rf"] 

    # Run the regression
    X = sm.add_constant(final_df[["Mkt_rf", "SMB", "HML", "Mom"]]) # add intercept
    y = final_df["Portfolio_excess"]
    
    # Fit OLS model 
    
    try:
       model = sm.OLS(y, X).fit()
    except Exception as e:
       raise RuntimeError(f"Failed to fit OLS regression model: {e}")
    
    if log:
        # Log model summary to file
        logging.info("\n" + model.summary().as_text())
    
    # Drop the constant 
    betas = model.params.drop("const", errors="ignore")

    return betas


def analyze_factor_exposures(betas: pd.Series, width: int = 20, scale: float = 1.0) -> None:
    """
    Visualizes factor exposures (regression betas) as a horizontal bar chart using characters
    like ▇ and ▁ to indicate the strength and direction (positive or negative) of the exposure.
    Intended for console output.

    Parameters
    ----------
    betas : pd.Series
        A Series of factor exposures, where the index contains factor names and the values
        are numeric regression coefficients.
    width : int, optional
        The total width of the visual bar (default = 20 characters). Must be a small positive integer.
    scale : float, optional
        The max absolute value to normalize exposures (e.g., a beta of 1.0 becomes the full half-bar).
        Values above/below are clamped. Default is 1.0.

    Raises
    ------
    TypeError
        If betas is not a pandas Series, or its values are not numeric.
        If width is not an int, or scale is not a float.
    ValueError
        If betas is empty, contains non-finite values (NaN/inf), or if width/scale are non-positive.
        If width exceeds 40 characters (to avoid excessive terminal clutter).
    RuntimeError
        If rendering of the visual output fails unexpectedly.

    Returns
    -------
    None
        Only prints a visualization of factor exposures to the console.
    """
    
    # Type checks
    if not isinstance(betas, pd.Series):
        raise TypeError("Betas must be provided as pandas Series.")
    if not pd.api.types.is_numeric_dtype(betas):
        raise TypeError("All values in betas must be numeric.")
    if not isinstance(width, int):
        raise TypeError("Width must be an integer.")
    if not isinstance(scale, float):
        raise TypeError("Scale must be a floating point number.")
        
    # Value checks
    if len(betas) == 0:
        raise ValueError("Betas must contain at least one value.")
    if not np.isfinite(betas.values).all():
        raise ValueError("Betas must not contain NaN or infinite values.")
    if width <= 0 or width > 40:
        raise ValueError("Width must be a positive integer no greater than 40.")
    if scale <= 0:
        raise ValueError("Scale must be a positive floating point number.")
    
    
    print("\t=== Realized Factor Exposures ===") # Section header
    # Set a midpoint as factor exposures can be both negative and positive
    midpoint = width // 2

    for factor, value in betas.items():
        # Factor exposures (betas) can be greater +1 or lower -1
        # For visualization purposes, restrict betas to [-1, +1] via scale
        clamped = max(min(value, scale), -scale)  # Clamp between -scale and +scale
        
        # Converts the beta to an integer bar length, scaled to half the bar (midpoint)
        scaled = int((clamped / scale) * midpoint)
        
        try:
            # Bar construction logic:
            if scaled > 0:
                # Left side: "▁" until the midpoint
                # Right side: ▇ * scaled -> actual exposure bar, then "▁" for padding to fill out width
                bar = "▁" * midpoint + "▇" * scaled + "▁" * (midpoint - scaled)
            elif scaled < 0:
                # Analogous to above
                bar = "▁" * (midpoint - abs(scaled)) + "▇" * abs(scaled) + "▁" * midpoint
            else:
                # Completely flat bar -> No exposure
                bar = "▁" * width
    
            exposure = interpret_exposure(value)
            print(f"{factor:<10} {bar} ({value:+.2f})  {exposure}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to visualize factor '{factor}': {e}")


def interpret_exposure(val: float) -> str:
    """
    Provides qualitative interpretation for factor exposures of a style analysis OLS regression, including
    an arrow indicating the direction of the factor exposure.
    
    Parameters
    ----------
    val : float
        Beta coefficients from the OLS regression.

    Raises
    ------
    TypeError
        Values must be floating point numbers.

    Returns
    -------
    str
        Qualitative interpretation of factor exposure.

    """
    
    
    if not isinstance(val, float):
        raise TypeError("Input value must be floating point number.")
    
    
    if val > 0.6: return "Strong exposure ↑"
    elif val > 0.3: return "Mild exposure ↑"
    elif val > 0.1: return "Slight exposure ↑"
    elif val < -0.6: return "Strong exposure ↓"
    elif val < -0.3: return "Mild exposure ↓"
    elif val < -0.1: return "Slight exposure ↓"
    else: return "Neutral exposure"
