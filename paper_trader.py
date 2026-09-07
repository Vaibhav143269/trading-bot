# V4.0 PAPER TRADER - Auto trade with fake money

import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime
from risk_kernel import RiskKernel
from advanced_strategy import AdvancedStrategy

class PaperTrader:
    def __init__(self, initial_capital=10000):
        self.capital = initial_capital
        self.balance = initial_capital
        self.position = None
        self.portfolio_value = initial_capital
        self.trades = []
        self.total_profit = 0
        self.risk_kernel = RiskKernel(initial_capital)
        self.last_price = None
        self.last_signal = None
        self.trading_active = True
        
    def get_price(self):
        """Fetch current Bitcoin price"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
            response = requests.get(url)
            data = response.json()
            price = data['bitcoin']['usd']
            return price
        except:
            print("⚠️ Error fetching price")
            return None
    
    def get_signal(self, price):
        """Get trading signal from strategy"""
        try:
            # Fetch 100 days of data for strategy
            url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=100"
            response = requests.get(url)
            data = response.json()
            prices = data['prices']
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['date'] = df['timestamp'].dt.date
            
            # Run strategy
            strategy = AdvancedStrategy(df)
            strategy.calculate_indicators()
            signals = strategy.generate_signals()
            
            return signals[-1]['signal'], signals[-1]
        except Exception as e:
            print(f"⚠️ Error getting signal: {e}")
            return 'HOLD', None
    
    def execute_trade(self, price, signal):
        """Execute trade based on signal"""
        if not self.trading_active:
            return
        
        # Check risk
        approved, message = self.risk_kernel.approve_trade('BTC/USD', 0.01, price)
        if not approved:
            print(f"   ⛔ Risk veto: {message}")
            return
        
        # BUY signal
        if 'BUY' in signal and self.position is None:
            # Buy 0.01 BTC
            cost = 0.01 * price
            if cost <= self.balance:
                self.position = {
                    'entry_price': price,
                    'size': 0.01,
                    'entry_date': datetime.now()
                }
                self.balance -= cost
                print(f"   📈 BUY EXECUTED at ${price:,.2f}")
                print(f"   💰 Balance: ${self.balance:,.2f}")
        
        # SELL signal
        elif 'SELL' in signal and self.position is not None:
            profit = (price - self.position['entry_price']) * self.position['size']
            self.balance += self.position['size'] * price
            
            trade = {
                'entry_price': self.position['entry_price'],
                'exit_price': price,
                'profit': profit,
                'profit_percent': (profit / (self.position['entry_price'] * self.position['size'])) * 100,
                'entry_date': self.position['entry_date'],
                'exit_date': datetime.now()
            }
            self.trades.append(trade)
            self.total_profit += profit
            
            profit_emoji = "✅" if profit > 0 else "❌"
            print(f"   📉 SELL EXECUTED at ${price:,.2f}")
            print(f"   {profit_emoji} Profit: ${profit:,.2f}")
            print(f"   💰 Balance: ${self.balance:,.2f}")
            
            self.position = None
    
    def update_portfolio(self, price):
        """Update portfolio value"""
        position_value = 0
        if self.position:
            position_value = self.position['size'] * price
        
        self.portfolio_value = self.balance + position_value
        return self.portfolio_value
    
    def get_summary(self):
        """Get trading summary"""
        total_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t['profit'] > 0)
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_return = ((self.portfolio_value - 10000) / 10000) * 100
        
        return {
            'balance': self.balance,
            'portfolio_value': self.portfolio_value,
            'position': self.position,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_profit': self.total_profit,
            'total_return': total_return
        }
    
    def run(self, seconds_between_checks=30):
        """Run paper trader continuously"""
        print("=" * 60)
        print("🚀 V4.0 PAPER TRADER RUNNING")
        print("=" * 60)
        print(f"💰 Starting Capital: ${self.capital:,.2f}")
        print(f"⏱️ Checking every {seconds_between_checks} seconds")
        print("=" * 60)
        
        try:
            while self.trading_active:
                # Get price
                price = self.get_price()
                if price is None:
                    print("⚠️ Waiting for price data...")
                    time.sleep(10)
                    continue
                
                # Get signal
                signal, signal_data = self.get_signal(price)
                
                # Only show if signal changed
                if signal != self.last_signal:
                    print(f"\n📊 {datetime.now().strftime('%H:%M:%S')}")
                    print(f"   Price: ${price:,.2f}")
                    print(f"   Signal: {signal}")
                    self.last_signal = signal
                
                # Execute trade
                if signal != 'HOLD':
                    self.execute_trade(price, signal)
                
                # Update portfolio
                self.update_portfolio(price)
                
                # Show summary every 5 minutes
                if int(time.time()) % 300 < seconds_between_checks:
                    summary = self.get_summary()
                    print(f"\n📈 SUMMARY:")
                    print(f"   Balance: ${summary['balance']:,.2f}")
                    print(f"   Portfolio: ${summary['portfolio_value']:,.2f}")
                    print(f"   Return: {summary['total_return']:.2f}%")
                    print(f"   Win Rate: {summary['win_rate']:.1f}%")
                
                time.sleep(seconds_between_checks)
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Paper trading stopped by user")
            self.display_final_report()
    
    def display_final_report(self):
        """Show final report"""
        summary = self.get_summary()
        print("\n" + "=" * 60)
        print("📊 FINAL TRADING REPORT")
        print("=" * 60)
        print(f"\n💰 Final Portfolio: ${summary['portfolio_value']:,.2f}")
        print(f"📈 Total Return: {summary['total_return']:.2f}%")
        print(f"📊 Trades: {summary['total_trades']}")
        print(f"   Wins: {summary['winning_trades']}")
        print(f"   Losses: {summary['losing_trades']}")
        print(f"   Win Rate: {summary['win_rate']:.1f}%")
        
        if self.trades:
            print(f"\n📋 LAST 5 TRADES:")
            for trade in self.trades[-5:]:
                profit_emoji = "✅" if trade['profit'] > 0 else "❌"
                print(f"   {profit_emoji} ${trade['profit']:,.2f} ({trade['profit_percent']:.2f}%)")

# RUN PAPER TRADER
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 V4.0 PAPER TRADER")
    print("=" * 60)
    print("\n⚠️ This uses FAKE MONEY - No real risk!")
    print("⚠️ Press Ctrl+C to stop anytime")
    print("=" * 60)
    
    trader = PaperTrader(10000)
    trader.run(seconds_between_checks=30)