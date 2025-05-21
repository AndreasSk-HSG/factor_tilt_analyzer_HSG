import pytest
import pandas as pd
import numpy as np
from unittest import mock
from ..analysis.portfolio_analyzer import (
    read_fama_french_csv,
    create_factor_dataset,
    factor_analysis_regression,
    analyze_factor_exposures,
    interpret_exposure
)

# ---------- Tests for read_fama_french_csv ----------

def test_read_fama_french_csv_valid(tmp_path):
    path = tmp_path / "test.csv" # Create a path inside the temp directory
    data = "Date,Factor\n202001,1.0\n202002,2.0"
    path.write_text(data)

    df = read_fama_french_csv(str(path), ["Factor"])
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 1)
    assert df.columns[0] == "Factor"
    assert df.index[0] == pd.Timestamp("2020-01-01")

def test_read_fama_french_csv_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_fama_french_csv("non_existent.csv", ["A"])

def test_read_fama_french_csv_invalid_column_names(tmp_path):
    path = tmp_path / "test.csv"
    path.write_text("Date,Val1,Val2\n202001,1,2")
    with pytest.raises(TypeError):
        read_fama_french_csv(str(path), "Val")

def test_read_fama_french_csv_column_mismatch(tmp_path):
    path = tmp_path / "test.csv"
    path.write_text("Date,Val1,Val2\n202001,1,2")
    with pytest.raises(ValueError):
        read_fama_french_csv(str(path), ["OnlyOne"])

def test_read_fama_french_csv_invalid_date(tmp_path):
    path = tmp_path / "test.csv"
    path.write_text("Date,Val\nBadDate,1")
    with pytest.raises(ValueError):
        read_fama_french_csv(str(path), ["Val"])

# ---------- Tests for create_factor_dataset ----------

@mock.patch("factor_tilt_analyzer.analysis.portfolio_analyzer.read_fama_french_csv")
def test_create_factor_dataset_valid(mock_read_csv):
    idx = pd.date_range("2020-01", periods=2, freq="ME")
    mom_df = pd.DataFrame({"Mom": [0.01, 0.02]}, index=idx)
    ff_df = pd.DataFrame({
        "Mkt_rf": [0.03, 0.04],
        "SMB": [0.01, 0.01],
        "HML": [0.00, 0.01],
        "Rf": [0.005, 0.005]
    }, index=idx)
    mock_read_csv.side_effect = [mom_df, ff_df]

    df = create_factor_dataset()
    assert list(df.columns) == ["Mom", "Mkt_rf", "SMB", "HML", "Rf"]

@mock.patch("factor_tilt_analyzer.analysis.portfolio_analyzer.read_fama_french_csv")
def test_create_factor_dataset_missing_values(mock_read_csv):
    idx = pd.date_range("2020-01", periods=2, freq="ME")
    mom_df = pd.DataFrame({"Mom": [0.01, None]}, index=idx)
    ff_df = pd.DataFrame({
        "Mkt_rf": [0.03, 0.04],
        "SMB": [0.01, 0.01],
        "HML": [0.00, 0.01],
        "Rf": [0.005, 0.005]
    }, index=idx)
    mock_read_csv.side_effect = [mom_df, ff_df]
    with pytest.raises(ValueError):
        create_factor_dataset()
        
# ---------- Tests for factor_analysis_regression ----------

def test_factor_analysis_regression_non_datetime_index():
    port = pd.Series([0.01, 0.02], index=[0, 1])
    market = pd.Series([0.02, 0.03], index=[0, 1])
    with pytest.raises(TypeError):
        factor_analysis_regression(port, market)

def test_factor_analysis_regression_no_overlap():
    port = pd.Series([0.01], index=pd.to_datetime(["2020-01-31"]))
    market = pd.Series([0.02], index=pd.to_datetime(["2021-01-31"]))
    with pytest.raises(ValueError):
        factor_analysis_regression(port, market)

def test_factor_analysis_regression_with_nans():
    idx = pd.date_range("2020-01-01", periods=2, freq="ME")
    port = pd.Series([0.01, np.nan], index=idx)
    market = pd.Series([0.02, 0.03], index=idx)
    with pytest.raises(ValueError):
        factor_analysis_regression(port, market)

@mock.patch("factor_tilt_analyzer.analysis.portfolio_analyzer.create_factor_dataset")
def test_factor_analysis_regression_insufficient_rows(mock_factors):
    idx = pd.date_range("2020-01-01", periods=4, freq="ME")  # only 4 rows
    port = pd.Series([0.01] * 4, index=idx)
    market = pd.Series([0.02] * 4, index=idx)
    factors = pd.DataFrame({
        "Mom": [0.01] * 4,
        "Mkt_rf": [0.02] * 4,
        "SMB": [0.01] * 4,
        "HML": [0.01] * 4,
        "Rf": [0.005] * 4
    }, index=idx)
    mock_factors.return_value = factors

    with pytest.raises(ValueError):
        factor_analysis_regression(port, market)
        
@pytest.mark.filterwarnings("ignore::UserWarning")
@mock.patch("factor_tilt_analyzer.analysis.portfolio_analyzer.create_factor_dataset")
def test_factor_analysis_regression_success(mock_factors):
    idx = pd.date_range("2020-01-01", periods=10, freq="ME")
    port = pd.Series([0.01, 0.015, 0.02, 0.005, 0.02, 0.025, 0.01, 0.012, 0.018, 0.022], index=idx)
    market = pd.Series([0.02, 0.025, 0.03, 0.015, 0.02, 0.03, 0.018, 0.021, 0.027, 0.029], index=idx)

    # Make all factors vary independently
    factors = pd.DataFrame({
        "Mom":    [0.01, 0.012, 0.014, 0.011, 0.013, 0.015, 0.012, 0.013, 0.016, 0.017],
        "Mkt_rf": [0.02, 0.022, 0.025, 0.021, 0.023, 0.026, 0.024, 0.027, 0.029, 0.03],
        "SMB":    [0.01, 0.009, 0.012, 0.011, 0.008, 0.013, 0.012, 0.01, 0.009, 0.011],
        "HML":    [0.015, 0.014, 0.016, 0.013, 0.012, 0.018, 0.017, 0.016, 0.015, 0.014],
        "Rf":     [0.005, 0.005, 0.005, 0.005, 0.005, 0.005, 0.005, 0.005, 0.005, 0.005]
    }, index=idx)

    mock_factors.return_value = factors

    betas = factor_analysis_regression(port, market)
    assert isinstance(betas, pd.Series)
    assert all(factor in betas.index for factor in ["Mom", "Mkt_rf", "SMB", "HML"])

def test_factor_analysis_regression_invalid_inputs():
    with pytest.raises(TypeError):
        factor_analysis_regression("not_series", pd.Series([0.01], index=pd.date_range("2020-01", periods=1, freq="ME")))
    with pytest.raises(ValueError):
        factor_analysis_regression(pd.Series([], dtype=float), pd.Series([], dtype=float))

# ---------- Tests for analyze_factor_exposures ----------

def test_analyze_factor_exposures_valid(capsys): # Check printing to console
    betas = pd.Series({"Mkt_rf": 0.5, "SMB": -0.3, "HML": 0.0})
    analyze_factor_exposures(betas, width=20, scale=1.0)
    captured = capsys.readouterr() # Capture printed output
    assert "Mkt_rf" in captured.out
    assert "Strong exposure" in captured.out or "Mild exposure" in captured.out

def test_analyze_factor_exposures_invalid_type():
    with pytest.raises(TypeError):
        analyze_factor_exposures([1, 2, 3], width=20, scale=1.0)

def test_analyze_factor_exposures_invalid_value():
    betas = pd.Series({"Mkt_rf": np.nan})
    with pytest.raises(ValueError):
        analyze_factor_exposures(betas)

# ---------- Tests for interpret_exposure ----------

def test_interpret_exposure_values():
    assert interpret_exposure(0.7) == "Strong exposure ↑"
    assert interpret_exposure(0.4) == "Mild exposure ↑"
    assert interpret_exposure(0.2) == "Slight exposure ↑"
    assert interpret_exposure(0.0) == "Neutral exposure"
    assert interpret_exposure(-0.2) == "Slight exposure ↓"
    assert interpret_exposure(-0.4) == "Mild exposure ↓"
    assert interpret_exposure(-0.7) == "Strong exposure ↓"

def test_interpret_exposure_invalid():
    with pytest.raises(TypeError):
        interpret_exposure("bad")
