# V4.0 SIMPLE TRADING STRATEGY - Moving Average Crossover

import pandas as pd
import numpy as np
from datetime import datetime

class SimpleStrategy:
    def __init__(self, data):
        self.data = data.copy()
        self.signals = []
        self.position = None
        
    def calculate_indicators(self):
        """Calculate simple moving averages"""
        # 5-day moving average (fast)
        self.data['MA5'] = self.data['price'].rolling(window=5).mean()
        # 20-day moving average (slow)
        self.data['MA20'] = self.data['price'].rolling(window=20).mean()
        # 50-day moving average (trend)
        self.data['MA50'] = self.data['price'].rolling(window=50).mean()
        
    def generate_signals(self):
        """Generate buy/sell signals"""
        signals = []
        
        for i in range(len(self.data)):
            price = self.data['price'].iloc[i]
            ma5 = self.data['MA5'].iloc[i] if not pd.isna(self.data['MA5'].iloc[i]) else 0
            ma20 = self.data['MA20'].iloc[i] if not pd.isna(self.data['MA20'].iloc[i]) else 0
            ma50 = self.data['MA50'].iloc[i] if not pd.isna(self.data['MA50'].iloc[i]) else 0
            
            signal = {
                'date': self.data['date'].iloc[i],
                'price': price,
                'ma5': ma5,
                'ma20': ma20,
                'ma50': ma50,
                'signal': 'HOLD'
            }
            
            # Strategy: Buy when MA5 crosses above MA20 (uptrend)
            if ma5 > ma20 and ma5 > ma50:
                signal['signal'] = 'BUY'
            # Sell when MA5 crosses below MA20 (downtrend)
            elif ma5 < ma20 and ma5 < ma50:
                signal['signal'] = 'SELL'
            # Strong buy when all moving averages are aligned up
            elif ma5 > ma20 and ma20 > ma50:
                signal['signal'] = 'STRONG BUY'
            # Strong sell when all moving averages are aligned down
            elif ma5 < ma20 and ma20 < ma50:
                signal['signal'] = 'STRONG SELL'
                
            signals.append(signal)
            
        self.signals = signals
        return signals

# TEST THE STRATEGY
if __name__ == "__main__":
    print("=" * 50)
    print("V4.0 SIMPLE TRADING STRATEGY TEST")
    print("=" * 50)
    
    # Load the market data
    print("\nLoading market data...")
    
    # Fetch fresh data
    import requests
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=100"
    response = requests.get(url)
    data = response.json()
    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['date'] = df['timestamp'].dt.date
    
    print(f"Loaded {len(df)} days of data")
    print(f"Price range: ${df['price'].min():,.2f} to ${df['price'].max():,.2f}")
    
    # Run the strategy
    print("\nRunning strategy...")
    strategy = SimpleStrategy(df)
    strategy.calculate_indicators()
    signals = strategy.generate_signals()
    
    # Show results
    last_signal = signals[-1]
    print(f"\nLatest Signal:")
    print(f"  Date: {last_signal['date']}")
    print(f"  Price: ${last_signal['price']:,.2f}")
    print(f"  MA5: ${last_signal['ma5']:,.2f}")
    print(f"  MA20: ${last_signal['ma20']:,.2f}")
    print(f"  MA50: ${last_signal['ma50']:,.2f}")
    print(f"  Signal: {last_signal['signal']}")
    
    # Show signal count
    buy_count = sum(1 for s in signals if s['signal'] == 'BUY' or s['signal'] == 'STRONG BUY')
    sell_count = sum(1 for s in signals if s['signal'] == 'SELL' or s['signal'] == 'STRONG SELL')
    hold_count = sum(1 for s in signals if s['signal'] == 'HOLD')
    
    print(f"\nSignal Summary:")
    print(f"  Buy signals: {buy_count}")
    print(f"  Sell signals: {sell_count}")
    print(f"  Hold signals: {hold_count}")
    
    print("\n" + "=" * 50)
    print("✅ Strategy is working!")