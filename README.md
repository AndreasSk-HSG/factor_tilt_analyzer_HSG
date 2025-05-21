# (8,789,1.00) Skills: Programming with Advanced Computer Languages: Factor Tilt Analyzer (Group Project Submission)
## Organizational Details:
- Submitted by: Andreas Skibin in the Spring Semester 2025
- Student-ID: 24-600-765
- Level: Graduate
- E-Mail: andreas.skibin@student.unisg.ch

## Topic Motivation:
In finance, portfolio risk is often assessed based on how sensitive the portfolio is to overall market movements. Market movements, in this context, refer to the returns of a market benchmark portfolio (e.g., the S&P 500 Index). The traditional assumption in many financial models is therefore that, for well-diversified investors, sensitivity to aggregate market movements is the only relevant measure of risk. However, research by Fama and French (1993) and Carhart (1997) showed that other factors such as size, value, and momentum also play a key, and often even more important role in explaining a portfolio’s risk exposure. For example, their research demonstrates that smaller-sized firms (proxied by market capitalization) earn consistently higher returns than larger firms. Overweighting small firms in a portfolio, however, might additional risk to a portfolio that is not captured by traditional risk measures. Since the work of Fama and French, these additional factors have become widely accepted in both academic research and professional investment practice. Yet, despite their importance, retail investors still face significant barriers when trying to assess their own portfolios in terms of these factor exposures. This tool aims to bridge that gap by enabling users to easily analyze how their portfolios are exposed to these key risk factors.

### Fama-French & Momentum Factors Explained:
- **Mkt_RF (Market Excess Return):** Return of the market portfolio minus the risk-free rate; captures the equity premium. Positive exposure reflects that the portfolio behaves like the overall market, e.g., it gains when the market goes up.
- **SMB (Small Minus Big):** Return difference between small-cap and large-cap stocks; captures the size premium. Positive exposure demonstrates that the portfolio leans toward small-cap stocks, which are typically more volatile but have higher returns.
- **HML (High Minus Low):** Return difference between high book-to-market (value) and low book-to-market (growth) stocks; captures the value premium. Positive exposure means that the portfolio is tilted toward value stocks (undervalued, often cyclical industries). 
- **Momentum (Mom):** Return spread between stocks with high recent returns and those with low recent return; captures the momentum effect. Portfolio with positive exposure to this factor holds recent winners, assuming trends continue.

## Requirements:
This project was developed using [Anaconda](https://www.anaconda.com/) with the Spyder IDE. I downloaded the Anaconda distribution and used Spyder as my development environment. For the best compatibility and to replicate the setup, I recommend installing Anaconda and running the project within Spyder as well.

The following Python libraries are required for the project to run:
- numpy
- pandas
- statsmodels
- requests
- yfinance
- pytest

You can install the dependencies via:
```bash
pip install -r requirements.txt
```

If downloads fail from the Yahoo Finance API, make sure that the **most recent version of yfinance** is installed.
```bash
pip install --upgrade yfinance
```

## Project Documentation:
### Process Description:
1. Prompt the user for stock tickers in main.py
2. Check the validity of the stock tickers and terminate the program otherwise
3. Prompt the user for a market benchmark
4. Download the return data for the stock tickers and the market benchmark from the Yahoo Finance API
5. Construct the minimum variance portfolio programmatically based on the returns of the individual stock tickers
6. Calculate and compare conventional risk and return measures of the market benchmark and the minimum variance portfolio
7. Conduct a style analysis (OLS regression) of the minimum variance portfolio and visualize the factor exposures in a graphical interpretation in the console 

### Project Directory Layout:
```
factor_tilt_analyzer/
│
├── main.py                            # Main logic of the program: Prompts the user for input, calls other functions 
├── config.py                          # Configuration file for parameters and settings (e.g., declares valid market benchmarks)
│
├── utils/                             # Utility functions:
│   └── validity_input_check.py        # Validates user input with regular expressions and by calling the Yahoo Finance API
|
├── data/                              # Data-related scripts:
│   └── data_fetcher.py                # Script to fetch returns for one or several stocks and the market benchmark from the Yahoo Finance API via yfinance
│
├── analysis/                          # Core analysis modules:
│   ├── minimum_variance_portfolio.py  # Computes the weights and returns of the minimum variance portfolio based on the stock tickers provided by the user 
│   ├── portfolio_analyzer.py          # Runs style analysis (OLS regression) of the minimum variance portfolio and prints a graphical interpretation to console 
│   └── portfolio_statistics.py        # Generates and prints conventional portfolio risk and return metrics to compare the market benchmark against the minimum variance portfolio (constructed based on user input)
│
└── input/                             # Directory for input files
|
└── tests/                             # Unit tests
    ├── __init__.py
    ├── test_data_fetcher.py
    ├── test_validity_input_check.py
    ├── test_minimum_variance_portfolio.py
    ├── test_portfolio_analyzer.py
    ├── test_portfolio_statistics.py
```

## Program Execution:
1. Download the repository from GitHub.
2. Open the console and navigate to the directory of **factor_tilt_analyzer** on your machine.
3. Execute the program with Python by running:
```bash
python main.py
```
4. Enter input as prompted by the program.
   
The following video demonstrates an example process using the stock tickers for Tesla (TSLA), Apple (AAPL), Ford (F), and McDonald's (MCD):

![alt text](img/demonstration.gif)

## Unit Tests:
1. Open the console and navigate to the root directory of **factor_tilt_analyzer** on your machine.
2. Execute the suite of all unit tests in the project by running:
```bash
python -m pytest tests/
```

![alt text](img/demonstration_unittests.gif)
  
## Academic Sources:
- Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. Journal of Financial Economics, 33(1), 3–56.
- Carhart, M. M. (1997). On persistence in mutual fund performance. The Journal of Finance, 52(1), 57–82.
- [Fama-French Data Library.](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)
- [Theoretical background for a closed-end solution for the minimum variance portfolio.](https://faculty.washington.edu/ezivot/econ424/portfolioTheoryMatrix.pdf)

## Disclaimer:
This code was developed and tested in the **Spyder IDE** using the **Anaconda Distribution** on a **Windows machine**. It was last confirmed to work correctly in **May 2025** with the following environment setup:

- **Operating System**: Windows 11  
- **Anaconda Version**: 24.11.3  
- **Python Version**: 3.12.7  
- **Library Versions**:
  - `yfinance==0.2.59`
  - `pandas==2.2.2`
  - `numpy==1.26.4`
  - `statsmodels==0.14.2`
  - `requests==2.32.3`
  - `pytest==7.4.4`
