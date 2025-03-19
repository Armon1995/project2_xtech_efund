"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Generake synthetic news (only for test)
"""
import pandas as pd
import random
from datetime import datetime, timedelta


def generate_news_csv(file_path: str):
    """
    Generates a CSV file with at least 100 financial news entries and saves it to the specified directory.

    Args:
        file_path (str): The full path where the CSV file will be saved.
    """
    num_entries = 100
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)

    titles = [
        "Stock Market Rallies as Tech Shares Surge",
        "Federal Reserve Signals Possible Interest Rate Cut",
        "Global Markets React to Inflation Data",
        "Bitcoin Hits New All-Time High Amid Crypto Boom",
        "Gold Prices Climb as Investors Seek Safe Haven",
        "Oil Prices Drop as Supply Concerns Ease",
        "US Job Market Shows Signs of Slowing Growth",
        "China’s GDP Growth Slows Amid Economic Uncertainty",
        "European Central Bank Maintains Interest Rates",
        "Investors Brace for Upcoming Earnings Season",
        "Tech Giants Report Record Profits Amid AI Boom",
        "US Inflation Rate Falls to Lowest Level in Two Years",
        "Federal Reserve Hints at Possible Interest Rate Hike",
        "Dow Jones Hits Record High on Strong Corporate Earnings",
        "Crude Oil Prices Surge as OPEC Announces Production Cuts",
        "Real Estate Market Slows as Mortgage Rates Rise",
        "S&P 500 Posts Best Monthly Gain Since 2020",
        "US Dollar Strengthens Against Major Currencies",
        "China's Export Growth Slows Amid Trade Tensions",
        "Central Banks Around the World Adjust Monetary Policies",
        "Global Supply Chain Issues Persist in Manufacturing Sector",
        "Tech Startups Struggle as VC Funding Dries Up",
        "Consumer Confidence Rises as Inflation Concerns Ease",
        "Wall Street Analysts Predict Strong Earnings for Q2",
        "Bond Market Volatility Increases Amid Rate Uncertainty",
        "European Markets Rally on Strong Economic Data",
        "US Unemployment Rate Remains Steady at 3.5%",
        "Goldman Sachs Revises GDP Growth Forecast for 2025",
        "Crypto Regulations Tighten as Governments Step In",
        "Major Banks Report Strong Earnings Despite Market Turbulence",
        "Retail Sales Surge Ahead of Holiday Shopping Season",
        "Automakers Face Supply Chain Challenges Amid Chip Shortages",
        "Federal Reserve Chair Signals Policy Shift in Upcoming Meeting",
        "Global Investors Eye Emerging Markets for Growth Opportunities",
        "Real Estate Prices in Major Cities Continue to Rise",
        "Hedge Funds Bet Big on Renewable Energy Stocks",
        "Commodities Market Faces Uncertainty Amid Global Conflicts",
        "US Treasury Yields Rise Amid Inflation Concerns",
        "Bank of Japan Maintains Ultra-Loose Monetary Policy",
        "Tech Sector Leads Market Gains as AI Investments Increase",
        "Housing Market Faces Headwinds as Interest Rates Climb",
        "Retail Giants Report Mixed Earnings as Consumer Spending Shifts",
        "Private Equity Firms Eye Distressed Assets for Investment",
        "US Budget Deficit Widens Amid Increased Government Spending",
        "Manufacturing Sector Rebounds as Supply Chains Improve",
        "Corporate Mergers and Acquisitions Hit Record Levels",
        "Financial Markets Brace for Key Economic Reports This Week",
        "Central Banks Face Challenges Balancing Inflation and Growth",
        "Luxury Goods Market Booms as High-End Demand Grows",
        "Energy Sector Outperforms as Oil and Gas Prices Climb"
    ]

    data = {
        'news_publish_time': [start_date + timedelta(days=random.randint(0, (end_date - start_date).days)) for _ in range(num_entries)],
        'news_title': [random.choice(titles) for _ in range(num_entries)],
        's3_url': [f'https://example-bucket.s3.amazonaws.com/news_{i}.pdf' for i in range(1, num_entries + 1)],
        'news_url': [f'https://news_website/news_{i}.pdf' for i in range(1, num_entries + 1)]
    }

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, encoding='utf-8')
    print(f"CSV file saved at: {file_path}")


# Example usage
filename = "yifangda_news/synthetic_news_data.csv"
generate_news_csv(filename)
