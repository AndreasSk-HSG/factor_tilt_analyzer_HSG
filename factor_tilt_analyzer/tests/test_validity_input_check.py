import pytest
from unittest import mock
from ..utils.validity_input_check import (
    check_validity_tickers,
    check_valid_ticker_with_API
)

# -------- Tests for check_validity_tickers --------

@mock.patch("factor_tilt_analyzer.utils.validity_input_check.check_valid_ticker_with_API")
def test_valid_ticker_list(mock_check):
    mock_check.return_value = True
    tickers = ["AAPL", "MSFT", "GOOGL"]
    assert check_validity_tickers(tickers) is True

@mock.patch("factor_tilt_analyzer.utils.validity_input_check.check_valid_ticker_with_API")
def test_ticker_list_with_spaces(mock_check):
    mock_check.return_value = True
    tickers = [" AAPL ", " MSFT "]
    assert check_validity_tickers(tickers) is True

def test_tickers_not_list():
    assert check_validity_tickers("AAPL") is False
    assert check_validity_tickers(123) is False
    assert check_validity_tickers(None) is False

def test_empty_list():
    assert check_validity_tickers([]) is False

def test_tickers_not_strings():
    tickers = ["AAPL", 123, None]
    assert check_validity_tickers(tickers) is False

def test_ticker_empty_strings():
    tickers = ["AAPL", ""]
    assert check_validity_tickers(tickers) is False

def test_ticker_invalid_characters():
    tickers = ["AAPL", "BAD!"]
    assert check_validity_tickers(tickers) is False

@mock.patch("factor_tilt_analyzer.utils.validity_input_check.check_valid_ticker_with_API")
def test_api_returns_false_for_one(mock_check):
    mock_check.side_effect = [True, False]
    tickers = ["AAPL", "INVALID"]
    assert check_validity_tickers(tickers) is False

@mock.patch("factor_tilt_analyzer.utils.validity_input_check.check_valid_ticker_with_API")
def test_api_raises_exception(mock_check):
    mock_check.side_effect = Exception("API error")
    tickers = ["AAPL"]
    assert check_validity_tickers(tickers) is False


# -------- Tests for check_valid_ticker_with_API --------

def test_check_valid_ticker_with_API_type_error():
    with pytest.raises(TypeError):
        check_valid_ticker_with_API(123)

def test_check_valid_ticker_with_API_value_error():
    with pytest.raises(ValueError):
        check_valid_ticker_with_API("   ")

@mock.patch("factor_tilt_analyzer.utils.validity_input_check.yf.Ticker")
def test_check_valid_ticker_with_API_valid(mock_ticker):
    mock_ticker.return_value.info = {"symbol": "AAPL"}
    assert check_valid_ticker_with_API("AAPL") is True

@mock.patch("factor_tilt_analyzer.utils.validity_input_check.yf.Ticker")
def test_check_valid_ticker_with_API_invalid(mock_ticker):
    mock_ticker.return_value.info = {}
    assert check_valid_ticker_with_API("INVALID") is False

@mock.patch("factor_tilt_analyzer.utils.validity_input_check.yf.Ticker")
def test_check_valid_ticker_with_API_exception(mock_ticker):
    mock_ticker.side_effect = Exception("Network error")
    assert check_valid_ticker_with_API("ERROR") is False
