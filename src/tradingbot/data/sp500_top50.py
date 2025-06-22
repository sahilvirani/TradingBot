# File: src/tradingbot/data/sp500_top50.py
"""Top 50 S&P 500 stocks by market capitalization for evaluation."""

# Top 50 S&P 500 stocks by market cap (as of 2024)
SP500_TOP50 = [
    "AAPL",  # Apple Inc.
    "MSFT",  # Microsoft Corporation
    "NVDA",  # NVIDIA Corporation
    "AMZN",  # Amazon.com Inc.
    "GOOGL",  # Alphabet Inc. (Class A)
    "META",  # Meta Platforms Inc.
    "BRK-B",  # Berkshire Hathaway Inc. (Class B)
    "LLY",  # Eli Lilly and Company
    "AVGO",  # Broadcom Inc.
    "JPM",  # JPMorgan Chase & Co.
    "TSLA",  # Tesla Inc.
    "XOM",  # Exxon Mobil Corporation
    "V",  # Visa Inc.
    "UNH",  # UnitedHealth Group Incorporated
    "MA",  # Mastercard Incorporated
    "JNJ",  # Johnson & Johnson
    "WMT",  # Walmart Inc.
    "PG",  # Procter & Gamble Company
    "HD",  # Home Depot Inc.
    "COST",  # Costco Wholesale Corporation
    "MRK",  # Merck & Co. Inc.
    "ORCL",  # Oracle Corporation
    "CVX",  # Chevron Corporation
    "ABBV",  # AbbVie Inc.
    "PEP",  # PepsiCo Inc.
    "BAC",  # Bank of America Corporation
    "ADBE",  # Adobe Inc.
    "KO",  # Coca-Cola Company
    "TMO",  # Thermo Fisher Scientific Inc.
    "LIN",  # Linde plc
    "NFLX",  # Netflix Inc.
    "CRM",  # Salesforce Inc.
    "ABNB",  # Airbnb Inc.
    "DIS",  # Walt Disney Company
    "MCD",  # McDonald's Corporation
    "AMD",  # Advanced Micro Devices Inc.
    "CMCSA",  # Comcast Corporation
    "INTC",  # Intel Corporation
    "RTX",  # Raytheon Technologies Corporation
    "PYPL",  # PayPal Holdings Inc.
    "IBM",  # International Business Machines Corporation
    "QCOM",  # QUALCOMM Incorporated
    "WFC",  # Wells Fargo & Company
    "AMAT",  # Applied Materials Inc.
    "SPGI",  # S&P Global Inc.
    "NKE",  # Nike Inc.
    "TXN",  # Texas Instruments Incorporated
    "BKNG",  # Booking Holdings Inc.
    "CAT",  # Caterpillar Inc.
    "GS",  # Goldman Sachs Group Inc.
]


def get_top50_symbols() -> list[str]:
    """Return the list of top 50 S&P 500 symbols."""
    return SP500_TOP50
