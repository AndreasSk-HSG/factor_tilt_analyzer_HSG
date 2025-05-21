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

You can install the dependencies via:
```bash
pip install -r requirements.txt
```

If downloads fail from Yahoo Finance, make sure that the **most recent version of yfinance** is installed.
```bash
pip install --upgrade yfinance
```


## Short description of what the thing does + Folder structure 


Description of each file 
Folder structure 






## Execution
Download the thing
Navigate to factor_... directory on your system in the concosle.
Run with python main.py



Examplary demonstration with Tesla (TSLA), Apple (AAPL), Ford (F), and McDonalds (MCD).


![alt text](img/demonstration.gif)
  












## Disclaimer:
Worked in May with Version XXX, Windows, ...
