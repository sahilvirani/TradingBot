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

# Next 50 S&P 500 stocks (51-100)
SP500_NEXT50 = [
    "INTU",  # Intuit Inc.
    "ISRG",  # Intuitive Surgical Inc.
    "GILD",  # Gilead Sciences Inc.
    "CVS",  # CVS Health Corporation
    "DE",  # Deere & Company
    "GE",  # General Electric Company
    "NOW",  # ServiceNow Inc.
    "VRTX",  # Vertex Pharmaceuticals Incorporated
    "MDLZ",  # Mondelez International Inc.
    "C",  # Citigroup Inc.
    "HON",  # Honeywell International Inc.
    "AXP",  # American Express Company
    "PFE",  # Pfizer Inc.
    "BA",  # Boeing Company
    "SYK",  # Stryker Corporation
    "LRCX",  # Lam Research Corporation
    "KLAC",  # KLA Corporation
    "ADI",  # Analog Devices Inc.
    "SCHW",  # Charles Schwab Corporation
    "AMP",  # Ameriprise Financial Inc.
    "MU",  # Micron Technology Inc.
    "PANW",  # Palo Alto Networks Inc.
    "REGN",  # Regeneron Pharmaceuticals Inc.
    "MSI",  # Motorola Solutions Inc.
    "BMY",  # Bristol-Myers Squibb Company
    "SO",  # Southern Company
    "MDT",  # Medtronic plc
    "PLD",  # Prologis Inc.
    "CB",  # Chubb Limited
    "SBUX",  # Starbucks Corporation
    "AMT",  # American Tower Corporation
    "BLK",  # BlackRock Inc.
    "MO",  # Altria Group Inc.
    "T",  # AT&T Inc.
    "TMUS",  # T-Mobile US Inc.
    "CI",  # Cigna Corporation
    "APH",  # Amphenol Corporation
    "ZTS",  # Zoetis Inc.
    "LOW",  # Lowe's Companies Inc.
    "GOOG",  # Alphabet Inc. (Class C)
    "DUK",  # Duke Energy Corporation
    "ICE",  # Intercontinental Exchange Inc.
    "EOG",  # EOG Resources Inc.
    "FIS",  # Fidelity National Information Services Inc.
    "USB",  # U.S. Bancorp
    "TJX",  # TJX Companies Inc.
    "COP",  # ConocoPhillips
    "APD",  # Air Products and Chemicals Inc.
    "SHW",  # Sherwin-Williams Company
    "CME",  # CME Group Inc.
]

# Combined top 100
SP500_TOP100 = SP500_TOP50 + SP500_NEXT50


def get_top50_symbols() -> list[str]:
    """Return the list of top 50 S&P 500 symbols."""
    return SP500_TOP50


def get_top100_symbols() -> list[str]:
    """Return the list of top 100 S&P 500 symbols."""
    return SP500_TOP100
