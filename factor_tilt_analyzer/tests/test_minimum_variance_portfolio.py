import pytest
import pandas as pd
import numpy as np
from ..analysis.minimum_variance_portfolio import (
    calculate_mvp_weights,
    calculate_mvp_portfolio
)


# ------------------ Fixtures ------------------
@pytest.fixture
def mock_returns_df():
    np.random.seed(42)
    data = np.random.normal(0.01, 0.05, size=(60, 3))  # 60 months, 3 assets
    return pd.DataFrame(data, columns=["AAPL", "GOOG", "TSLA"])

@pytest.fixture
def mock_returns_df_with_nan():
    df = pd.DataFrame({"AAPL": [0.01, 0.02, np.nan], "GOOG": [0.01, 0.03, 0.02]})
    return df

# ------------------ Tests for calculate_mvp_weights ------------------

def test_mvp_weights_output_type(mock_returns_df):
    weights = calculate_mvp_weights(mock_returns_df)
    assert isinstance(weights, pd.Series), "Output should be a pandas Series."

def test_mvp_weights_sum_to_one(mock_returns_df):
    weights = calculate_mvp_weights(mock_returns_df)
    np.testing.assert_almost_equal(weights.sum(), 1.0, decimal=5)

def test_mvp_weights_index_alignment(mock_returns_df):
    weights = calculate_mvp_weights(mock_returns_df)
    assert all(weights.index == mock_returns_df.columns), "Indices of weights must match input columns."

def test_mvp_weights_invalid_input_type():
    with pytest.raises(TypeError):
        calculate_mvp_weights([[0.01, 0.02], [0.03, 0.04]])

def test_mvp_weights_empty_df():
    with pytest.raises(ValueError):
        calculate_mvp_weights(pd.DataFrame())

def test_mvp_weights_nan_values(mock_returns_df_with_nan):
    with pytest.raises(ValueError):
        calculate_mvp_weights(mock_returns_df_with_nan)

def test_mvp_weights_insufficient_assets():
    df = pd.DataFrame({"AAPL": [0.01, 0.02, 0.03]})
    with pytest.raises(ValueError):
        calculate_mvp_weights(df)

def test_mvp_weights_few_observations():
    df = pd.DataFrame({"AAPL": [0.01, 0.02], "GOOG": [0.01, 0.02], "TSLA": [0.01, 0.02]})
    with pytest.raises(ValueError):
        calculate_mvp_weights(df)

def test_mvp_weights_singular_matrix():
    df = pd.DataFrame(np.tile([0.01, 0.02, 0.03], (10, 1)), columns=["AAPL", "GOOG", "TSLA"])
    with pytest.raises(ValueError):
        calculate_mvp_weights(df)

# ------------------ Tests for calculate_mvp_portfolio ------------------

def test_mvp_portfolio_output_type(mock_returns_df):
    returns = calculate_mvp_portfolio(mock_returns_df)
    assert isinstance(returns, pd.Series), "Output should be a pandas Series."

def test_mvp_portfolio_length(mock_returns_df):
    returns = calculate_mvp_portfolio(mock_returns_df)
    assert len(returns) == mock_returns_df.shape[0], "Output series should match input time periods."

def test_mvp_portfolio_empty_df():
    with pytest.raises(ValueError):
        calculate_mvp_portfolio(pd.DataFrame())

def test_mvp_portfolio_nan_input(mock_returns_df_with_nan):
    with pytest.raises(ValueError):
        calculate_mvp_portfolio(mock_returns_df_with_nan)

def test_mvp_portfolio_invalid_input_type():
    with pytest.raises(TypeError):
        calculate_mvp_portfolio([0.01, 0.02, 0.03])
