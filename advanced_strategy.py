# V4.0 ADVANCED TRADING STRATEGY - RSI + MACD + Bollinger Bands

import pandas as pd
import numpy as np
import requests
from datetime import datetime

class AdvancedStrategy:
    def __init__(self, data):
        self.data = data.copy()
        self.signals = []
        
    def calculate_rsi(self, period=14):
        """Calculate Relative Strength Index (RSI)"""
        delta = self.data['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        exp1 = self.data['price'].ewm(span=12, adjust=False).mean()
        exp2 = self.data['price'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        return macd, signal, histogram
    
    def calculate_bollinger_bands(self, period=20):
        """Calculate Bollinger Bands"""
        sma = self.data['price'].rolling(window=period).mean()
        std = self.data['price'].rolling(window=period).std()
        upper = sma + (std * 2)
        lower = sma - (std * 2)
        return upper, sma, lower
    
    def calculate_indicators(self):
        """Calculate all indicators"""
        # Moving Averages
        self.data['MA5'] = self.data['price'].rolling(window=5).mean()
        self.data['MA20'] = self.data['price'].rolling(window=20).mean()
        self.data['MA50'] = self.data['price'].rolling(window=50).mean()
        
        # RSI
        self.data['RSI'] = self.calculate_rsi(14)
        
        # MACD
        self.data['MACD'], self.data['MACD_Signal'], self.data['MACD_Hist'] = self.calculate_macd()
        
        # Bollinger Bands
        self.data['BB_Upper'], self.data['BB_Middle'], self.data['BB_Lower'] = self.calculate_bollinger_bands(20)
        
        # Volume (simulated for demo)
        self.data['Volume'] = np.random.randint(1000, 5000, len(self.data))
        
    def generate_signals(self):
        """Generate BUY/SELL signals using multiple indicators"""
        signals = []
        
        for i in range(len(self.data)):
            if i < 50:  # Skip first 50 days for indicators to stabilize
                signals.append({
                    'date': self.data['date'].iloc[i],
                    'price': self.data['price'].iloc[i],
                    'signal': 'HOLD',
                    'reason': 'Not enough data'
                })
                continue
            
            price = self.data['price'].iloc[i]
            ma5 = self.data['MA5'].iloc[i]
            ma20 = self.data['MA20'].iloc[i]
            ma50 = self.data['MA50'].iloc[i]
            rsi = self.data['RSI'].iloc[i]
            macd = self.data['MACD'].iloc[i]
            macd_signal = self.data['MACD_Signal'].iloc[i]
            macd_hist = self.data['MACD_Hist'].iloc[i]
            bb_upper = self.data['BB_Upper'].iloc[i]
            bb_lower = self.data['BB_Lower'].iloc[i]
            bb_middle = self.data['BB_Middle'].iloc[i]
            
            # Scoring system (0-100)
            buy_score = 0
            sell_score = 0
            
            # 1. Moving Average Trend (Weight: 25 points)
            if ma5 > ma20 and ma20 > ma50:
                buy_score += 25
            elif ma5 < ma20 and ma20 < ma50:
                sell_score += 25
            elif ma5 > ma20:
                buy_score += 15
            elif ma5 < ma20:
                sell_score += 15
            
            # 2. RSI (Weight: 25 points)
            if rsi < 30:  # Oversold - BUY signal
                buy_score += 25
            elif rsi > 70:  # Overbought - SELL signal
                sell_score += 25
            elif 30 <= rsi <= 70:
                if rsi < 40:
                    buy_score += 10
                elif rsi > 60:
                    sell_score += 10
            
            # 3. MACD (Weight: 25 points)
            if macd > macd_signal and macd_hist > 0:
                buy_score += 25
            elif macd < macd_signal and macd_hist < 0:
                sell_score += 25
            elif macd > macd_signal:
                buy_score += 15
            elif macd < macd_signal:
                sell_score += 15
            
            # 4. Bollinger Bands (Weight: 25 points)
            if price <= bb_lower:  # Price at lower band - BUY
                buy_score += 25
            elif price >= bb_upper:  # Price at upper band - SELL
                sell_score += 25
            elif price < bb_middle:
                buy_score += 10
            elif price > bb_middle:
                sell_score += 10
            
            # Determine signal
            if buy_score >= 60:
                signal = 'STRONG BUY'
                reason = f'Score: {buy_score}/100'
            elif buy_score >= 40:
                signal = 'BUY'
                reason = f'Score: {buy_score}/100'
            elif sell_score >= 60:
                signal = 'STRONG SELL'
                reason = f'Score: {sell_score}/100'
            elif sell_score >= 40:
                signal = 'SELL'
                reason = f'Score: {sell_score}/100'
            else:
                signal = 'HOLD'
                reason = f'Buy:{buy_score} Sell:{sell_score}'
            
            signals.append({
                'date': self.data['date'].iloc[i],
                'price': price,
                'ma5': round(ma5, 2),
                'ma20': round(ma20, 2),
                'ma50': round(ma50, 2),
                'rsi': round(rsi, 2),
                'macd': round(macd, 6),
                'bb_upper': round(bb_upper, 2),
                'bb_lower': round(bb_lower, 2),
                'signal': signal,
                'reason': reason,
                'buy_score': buy_score,
                'sell_score': sell_score
            })
        
        self.signals = signals
        return signals

# TEST THE ADVANCED STRATEGY
if __name__ == "__main__":
    print("=" * 60)
    print("V4.0 ADVANCED TRADING STRATEGY")
    print("=" * 60)
    
    # Fetch data
    print("\n📊 Fetching market data...")
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=200"
    response = requests.get(url)
    data = response.json()
    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['date'] = df['timestamp'].dt.date
    
    print(f"✅ Loaded {len(df)} days of data")
    print(f"   Price range: ${df['price'].min():,.2f} to ${df['price'].max():,.2f}")
    
    # Run strategy
    print("\n🧠 Running advanced strategy...")
    strategy = AdvancedStrategy(df)
    strategy.calculate_indicators()
    signals = strategy.generate_signals()
    
    # Show last 5 signals
    print("\n📈 LAST 5 SIGNALS:")
    print("-" * 60)
    for s in signals[-5:]:
        print(f"  {s['date']} | ${s['price']:,.2f} | {s['signal']} | {s['reason']}")
    
    # Show signal summary
    buy_count = sum(1 for s in signals if 'BUY' in s['signal'])
    sell_count = sum(1 for s in signals if 'SELL' in s['signal'])
    hold_count = sum(1 for s in signals if s['signal'] == 'HOLD')
    
    print("\n📊 SIGNAL SUMMARY:")
    print(f"  🟢 BUY signals: {buy_count}")
    print(f"  🔴 SELL signals: {sell_count}")
    print(f"  ⚪ HOLD signals: {hold_count}")
    
    # Latest signal
    latest = signals[-1]
    print("\n🎯 LATEST SIGNAL:")
    print(f"  Date: {latest['date']}")
    print(f"  Price: ${latest['price']:,.2f}")
    print(f"  RSI: {latest['rsi']}")
    print(f"  MACD: {latest['macd']}")
    print(f"  Signal: {latest['signal']}")
    print(f"  Reason: {latest['reason']}")
    
    print("\n" + "=" * 60)
    print("✅ Advanced Strategy is working!")
    print("\n💡 TIPS:")
    print("  - STRONG BUY = Great opportunity to buy")
    print("  - BUY = Good opportunity to buy")
    print("  - HOLD = Wait for better signal")
    print("  - SELL = Consider selling")
    print("  - STRONG SELL = Strong selling signal")