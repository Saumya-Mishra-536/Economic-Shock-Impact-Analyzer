import yfinance as yf

tickers = {
    "Crude Oil": "CL=F",
    "Brent Crude": "BZ=F",
    "Natural Gas": "NG=F",
    "Gold": "GC=F",
    "Copper": "HG=F",
    "Corn": "ZC=F",
    "Wheat": "ZW=F",
    "Sugar": "SB=F",
    "Coffee": "KC=F",
    "Cotton": "CT=F",
    "Aluminum": "ALI=F",
    "Palm Oil": "FCPO.KL",
}

for name, ticker in tickers.items():
    try:
        price = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
        print(f"{name}: ${price:.2f}")
    except:
        print(f"{name}: not available")
