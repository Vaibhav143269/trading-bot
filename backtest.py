# V4.0 BACKTESTING ENGINE - Test your strategy performance

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta

class Backtester:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.portfolio = []
        self.trades = []
        self.balance = initial_capital
        self.position = None
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        
    def buy(self, price, date, size=0.01):
        """Execute a BUY trade"""
        if self.position is None:
            cost = size * price
            if cost <= self.balance:
                self.position = {
                    'entry_price': price,
                    'size': size,
                    'entry_date': date
                }
                self.balance -= cost
                self.total_trades += 1
                return True
        return False
    
    def sell(self, price, date):
        """Execute a SELL trade"""
        if self.position is not None:
            profit = (price - self.position['entry_price']) * self.position['size']
            self.balance += self.position['size'] * price
            
            # Track win/loss
            if profit > 0:
                self.winning_trades += 1
            else:
                self.losing_trades += 1
            
            self.trades.append({
                'entry_date': self.position['entry_date'],
                'exit_date': date,
                'entry_price': self.position['entry_price'],
                'exit_price': price,
                'profit': profit,
                'profit_percent': (profit / (self.position['entry_price'] * self.position['size'])) * 100,
                'size': self.position['size']
            })
            
            self.position = None
            return True
        return False
    
    def run_backtest(self, signals, risk_kernel=None):
        """Run backtest on signals"""
        for i, signal in enumerate(signals):
            if i < 50:  # Skip first 50 days
                continue
            
            price = signal['price']
            date = signal['date']
            signal_type = signal['signal']
            
            # Check risk before trading
            if risk_kernel:
                approved, message = risk_kernel.approve_trade('BTC/USD', 0.01, price)
                if not approved:
                    continue
            
            if 'BUY' in signal_type and self.position is None:
                self.buy(price, date, 0.01)  # Buy 0.01 BTC
            
            elif 'SELL' in signal_type and self.position is not None:
                self.sell(price, date)
        
        # Close any open position at the end
        if self.position is not None:
            self.sell(signals[-1]['price'], signals[-1]['date'])
    
    def get_performance(self):
        """Calculate performance metrics"""
        total_profit = self.balance - self.initial_capital
        total_return = (total_profit / self.initial_capital) * 100
        
        if len(self.trades) > 0:
            win_rate = (self.winning_trades / len(self.trades)) * 100
            avg_profit = sum(t['profit'] for t in self.trades) / len(self.trades)
            max_profit = max(t['profit'] for t in self.trades) if self.trades else 0
            max_loss = min(t['profit'] for t in self.trades) if self.trades else 0
            sharpe_ratio = self.calculate_sharpe()
        else:
            win_rate = 0
            avg_profit = 0
            max_profit = 0
            max_loss = 0
            sharpe_ratio = 0
        
        return {
            'initial_capital': self.initial_capital,
            'final_balance': self.balance,
            'total_profit': total_profit,
            'total_return': total_return,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'avg_profit_per_trade': avg_profit,
            'max_profit_per_trade': max_profit,
            'max_loss_per_trade': max_loss,
            'sharpe_ratio': sharpe_ratio,
            'trades': self.trades
        }
    
    def calculate_sharpe(self):
        """Calculate Sharpe Ratio (risk-adjusted return)"""
        if len(self.trades) < 2:
            return 0
        
        profits = [t['profit'] for t in self.trades]
        avg_profit = np.mean(profits)
        std_profit = np.std(profits) if len(profits) > 1 else 1
        
        if std_profit == 0:
            return 0
        
        return (avg_profit / std_profit) * np.sqrt(252)  # Annualized

# FETCH DATA AND RUN BACKTEST
if __name__ == "__main__":
    print("=" * 60)
    print("📊 V4.0 BACKTESTING ENGINE")
    print("=" * 60)
    
    # Fetch data
    print("\n📥 Fetching historical data...")
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=365"
    response = requests.get(url)
    data = response.json()
    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['date'] = df['timestamp'].dt.date
    
    print(f"✅ Loaded {len(df)} days of data")
    print(f"   Price range: ${df['price'].min():,.2f} to ${df['price'].max():,.2f}")
    
    # Run strategy
    print("\n🧠 Generating signals...")
    from advanced_strategy import AdvancedStrategy
    strategy = AdvancedStrategy(df)
    strategy.calculate_indicators()
    signals = strategy.generate_signals()
    
    # Import risk kernel
    from risk_kernel import RiskKernel
    risk = RiskKernel(10000)
    
    # Run backtest
    print("\n💼 Running backtest...")
    backtester = Backtester(10000)
    backtester.run_backtest(signals, risk)
    performance = backtester.get_performance()
    
    # Show results
    print("\n" + "=" * 60)
    print("📈 BACKTEST RESULTS")
    print("=" * 60)
    
    print(f"\n💰 CAPITAL:")
    print(f"   Initial: ${performance['initial_capital']:,.2f}")
    print(f"   Final:   ${performance['final_balance']:,.2f}")
    print(f"   Profit:  ${performance['total_profit']:,.2f}")
    print(f"   Return:  {performance['total_return']:.2f}%")
    
    print(f"\n📊 TRADES:")
    print(f"   Total trades:   {performance['total_trades']}")
    print(f"   Winning trades: {performance['winning_trades']}")
    print(f"   Losing trades:  {performance['losing_trades']}")
    print(f"   Win Rate:       {performance['win_rate']:.2f}%")
    print(f"   Avg Profit:     ${performance['avg_profit_per_trade']:.2f}")
    print(f"   Max Profit:     ${performance['max_profit_per_trade']:.2f}")
    print(f"   Max Loss:       ${performance['max_loss_per_trade']:.2f}")
    print(f"   Sharpe Ratio:   {performance['sharpe_ratio']:.2f}")
    
    # Show recent trades
    if performance['trades']:
        print(f"\n📋 LAST 5 TRADES:")
        print("-" * 60)
        for trade in performance['trades'][-5:]:
            profit_emoji = "✅" if trade['profit'] > 0 else "❌"
            print(f"   {profit_emoji} Entry: ${trade['entry_price']:,.2f} | Exit: ${trade['exit_price']:,.2f} | Profit: ${trade['profit']:.2f} ({trade['profit_percent']:.2f}%)")
    
    print("\n" + "=" * 60)
    
    # Performance Rating
    print("\n📊 PERFORMANCE RATING:")
    if performance['total_return'] > 50:
        print("   🌟 EXCELLENT! Great strategy!")
    elif performance['total_return'] > 20:
        print("   ✅ GOOD! Solid performance!")
    elif performance['total_return'] > 0:
        print("   📈 DECENT! Making profit!")
    else:
        print("   📉 NEEDS IMPROVEMENT! Consider adjusting strategy")
    
    print("\n" + "=" * 60)
    print("✅ Backtest Complete!")