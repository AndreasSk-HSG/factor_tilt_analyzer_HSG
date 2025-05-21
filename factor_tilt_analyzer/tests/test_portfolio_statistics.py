import pytest
import pandas as pd
import numpy as np
from ..analysis.portfolio_statistics import (
    compare_portfolio_with_market_benchmark,
    calculate_portfolio_statistics,
    print_portfolio_statistics
)

# ----------- Fixtures -----------

@pytest.fixture
def sample_returns():
    np.random.seed(42)
    idx = pd.date_range("2020-01-01", periods=24, freq="ME")
    returns = pd.Series(0.01 * np.random.rand(24), index=idx)
    return returns

# ----------- Tests for calculate_portfolio_statistics -----------

def test_calculate_statistics_invalid_type():
    with pytest.raises(TypeError):
        calculate_portfolio_statistics([0.01, 0.02], interval="monthly")

def test_calculate_statistics_empty_series():
    with pytest.raises(ValueError):
        calculate_portfolio_statistics(pd.Series(dtype=float), interval="monthly")

def test_calculate_statistics_with_nan():
    s = pd.Series([0.01, np.nan])
    with pytest.raises(ValueError):
        calculate_portfolio_statistics(s)

def test_calculate_statistics_invalid_interval(sample_returns):
    with pytest.raises(ValueError):
        calculate_portfolio_statistics(sample_returns, interval="weekly")

# ----------- Tests for print_portfolio_statistics -----------

def test_print_statistics_valid_output(capsys, sample_returns):
    stats = calculate_portfolio_statistics(sample_returns)
    print_portfolio_statistics(stats, "Test Portfolio")
    captured = capsys.readouterr()
    assert "Test Portfolio Performance" in captured.out
    assert "Mean Return" in captured.out

def test_print_statistics_invalid_dict_type():
    with pytest.raises(TypeError):
        print_portfolio_statistics("not a dict", "Portfolio")

def test_print_statistics_invalid_name_type():
    with pytest.raises(TypeError):
        print_portfolio_statistics({}, 123)

def test_print_statistics_empty_dict():
    with pytest.raises(ValueError):
        print_portfolio_statistics({}, "Portfolio")

def test_print_statistics_missing_keys():
    incomplete = {
        "mean_return": 0.01,
        "annualized_return": 0.12
        # missing rest
    }
    with pytest.raises(KeyError):
        print_portfolio_statistics(incomplete, "Portfolio")

def test_print_statistics_non_numeric_values():
    invalid = {
        "mean_return": "high",
        "annualized_return": 0.1,
        "std_dev": 0.1,
        "annualized_volatility": 0.1,
        "sharpe_ratio": 1.0,
        "cumulative_return": 0.1,
        "max_drawdown": 0.1,
    }
    with pytest.raises(TypeError):
        print_portfolio_statistics(invalid, "Portfolio")

# ----------- Tests for compare_portfolio_with_market_benchmark -----------

def test_compare_with_valid_input(sample_returns, capsys):
    compare_portfolio_with_market_benchmark(sample_returns, sample_returns)
    captured = capsys.readouterr()
    assert "Minimum Variance Portfolio Performance" in captured.out
    assert "Market Benchmark Performance" in captured.out

def test_compare_with_non_series_inputs():
    with pytest.raises(TypeError):
        compare_portfolio_with_market_benchmark([0.01], pd.Series([0.01]))

def test_compare_with_empty_series():
    with pytest.raises(ValueError):
        compare_portfolio_with_market_benchmark(pd.Series(dtype=float), pd.Series(dtype=float))

def test_compare_with_nan_inputs():
    bad = pd.Series([0.01, np.nan])
    with pytest.raises(ValueError):
        compare_portfolio_with_market_benchmark(bad, bad)

def test_compare_with_invalid_interval(sample_returns):
    with pytest.raises(ValueError):
        compare_portfolio_with_market_benchmark(sample_returns, sample_returns, interval="quarterly")

def test_compare_with_no_overlap():
    s1 = pd.Series([0.01], index=pd.to_datetime(["2020-01-31"]))
    s2 = pd.Series([0.01], index=pd.to_datetime(["2021-01-31"]))
    with pytest.raises(ValueError):
        compare_portfolio_with_market_benchmark(s1, s2)
