# V4.0 MARKET DATA FETCHER - Get live crypto prices

import pandas as pd
import requests
import json
from datetime import datetime

def get_bitcoin_price():
    """Fetch current Bitcoin price from CoinGecko (FREE API)"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        price = data['bitcoin']['usd']
        return price
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def get_multiple_prices():
    """Fetch prices for multiple cryptocurrencies"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        return data
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return None

def get_historical_data(days=30):
    """Get historical Bitcoin price data for backtesting"""
    try:
        url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}"
        response = requests.get(url)
        data = response.json()
        
        # Convert to DataFrame
        prices = data['prices']
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['date'] = df['timestamp'].dt.date
        
        return df
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return None

# TEST THE DATA FETCHER
if __name__ == "__main__":
    print("=" * 50)
    print("V4.0 MARKET DATA FETCHER TEST")
    print("=" * 50)
    
    # Test 1: Get current Bitcoin price
    print("\nTest 1: Getting current Bitcoin price...")
    btc_price = get_bitcoin_price()
    if btc_price:
        print(f"✅ Bitcoin Price: ${btc_price:,.2f}")
    else:
        print("❌ Failed to get price")
    
    # Test 2: Get multiple crypto prices
    print("\nTest 2: Getting multiple crypto prices...")
    prices = get_multiple_prices()
    if prices:
        for coin, data in prices.items():
            print(f"  {coin.upper()}: ${data['usd']:,.2f}")
    else:
        print("❌ Failed to get prices")
    
    # Test 3: Get historical data
    print("\nTest 3: Getting historical data (last 7 days)...")
    df = get_historical_data(7)
    if df is not None:
        print(f"✅ Got {len(df)} data points")
        print(f"   First price: ${df['price'].iloc[0]:,.2f}")
        print(f"   Latest price: ${df['price'].iloc[-1]:,.2f}")
        print(f"   Highest: ${df['price'].max():,.2f}")
        print(f"   Lowest: ${df['price'].min():,.2f}")
    else:
        print("❌ Failed to get historical data")
    
    print("\n" + "=" * 50)
    print("✅ Market Data Fetcher is working!")