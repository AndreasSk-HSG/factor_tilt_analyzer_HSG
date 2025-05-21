import pytest
from unittest.mock import patch
import pandas as pd
from requests.exceptions import HTTPError
from ..data.data_fetcher import get_start_date, fetch_returns, fetch_benchmark_returns

# === Tests for get_start_date ===

@pytest.mark.parametrize("in_end, in_period, expected", [
    ("2025-01-01", "1y", "2024-01-01"),
    ("2025-01-01", "6mo", "2024-07-01"),
    ("2025-01-01", "30d", "2024-12-02")
])
def test_get_start_date_valid(in_end, in_period, expected):
    assert get_start_date(in_end, in_period) == expected

@pytest.mark.parametrize("in_end", [None, 20250101])
def test_get_start_date_invalid_end_type(in_end):
    with pytest.raises(TypeError):
        get_start_date(in_end, "1y")

@pytest.mark.parametrize("in_period", [None, 1])
def test_get_start_date_invalid_period_type(in_period):
    with pytest.raises(TypeError):
        get_start_date("2025-01-01", in_period)

@pytest.mark.parametrize("in_period", ["", "5", "yy"])
def test_get_start_date_invalid_format(in_period):
    with pytest.raises(ValueError):
        get_start_date("2025-01-01", in_period)

@pytest.mark.parametrize("in_period", ["5w", "6h"])
def test_get_start_date_unsupported_unit(in_period):
    with pytest.raises(ValueError):
        get_start_date("2025-01-01", in_period)

# === Tests for fetch_returns ===

@patch("factor_tilt_analyzer.data.data_fetcher.yf.download")
def test_fetch_returns_single_ticker(mock_download):
    date_index = pd.date_range(start="2023-01-01", periods=5, freq="ME")
    prices = pd.Series([100, 105, 110, 120, 130], index=date_index)
    mock_df = pd.DataFrame({"Adj Close": prices})
    mock_download.return_value = mock_df

    df = fetch_returns(["AAPL"], in_period="1y", in_interval="1mo", in_auto_adjust=False, in_end="2024-01-01")
    assert isinstance(df, pd.DataFrame)
    assert "AAPL" in df.columns
    assert len(df) == 4  # 5 prices -> 4 returns

@patch("factor_tilt_analyzer.data.data_fetcher.yf.download")
def test_fetch_returns_empty_data(mock_download):
    mock_download.return_value = pd.DataFrame()
    with pytest.raises(HTTPError):
        fetch_returns(["AAPL"], in_end="2024-01-01")

@pytest.mark.parametrize("tickers", [None, "AAPL", 123])
def test_fetch_returns_invalid_ticker_type(tickers):
    with pytest.raises(TypeError):
        fetch_returns(tickers)

@pytest.mark.parametrize("tickers", [[], [""]])
def test_fetch_returns_empty_or_blank_tickers(tickers):
    with pytest.raises(ValueError):
        fetch_returns(tickers)
        
def test_fetch_returns_raises_typeerror_for_non_list_tickers():
    with pytest.raises(TypeError, match="Tickers must be a list"):
        fetch_returns("AAPL")  # Passing a string instead of a list

# === Tests for fetch_benchmark_returns ===

@patch("factor_tilt_analyzer.data.data_fetcher.fetch_returns")
def test_fetch_benchmark_returns_valid(mock_fetch_returns):
    dummy_df = pd.DataFrame({"^GSPC": [0.01, 0.02]}, index=pd.date_range("2023-01-01", periods=2, freq="ME"))
    mock_fetch_returns.return_value = dummy_df

    result = fetch_benchmark_returns("^GSPC")
    assert isinstance(result, pd.DataFrame)
    assert "MKT" in result.columns
    assert result.shape[1] == 1

@pytest.mark.parametrize("ticker", [None, 123, 5.5])
def test_fetch_benchmark_returns_invalid_type(ticker):
    with pytest.raises(TypeError):
        fetch_benchmark_returns(ticker)

@pytest.mark.parametrize("ticker", ["", "INVALID"])
def test_fetch_benchmark_returns_invalid_value(ticker):
    with pytest.raises(ValueError):
        fetch_benchmark_returns(ticker)

@patch("factor_tilt_analyzer.data.data_fetcher.fetch_returns")
def test_fetch_benchmark_returns_multiple_columns(mock_fetch_returns):
    mock_df = pd.DataFrame({
        "^GSPC": [0.01, 0.02],
        "SPY": [0.01, 0.02]
    }, index=pd.date_range("2023-01-01", periods=2, freq="ME"))
    mock_fetch_returns.return_value = mock_df

    with pytest.raises(ValueError):
        fetch_benchmark_returns("^GSPC") # must contain exactly one column
