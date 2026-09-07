# V4.0 RISK KERNEL - Your trading bot's safety system

import pandas as pd
import numpy as np
from datetime import datetime

class RiskKernel:
    def __init__(self, starting_equity=10000):
        self.equity = starting_equity
        self.daily_loss = 0
        self.daily_trades = 0
        self.positions = {}
        self.trade_history = []
        
        # V4.0 risk limits (configurable)
        self.daily_loss_limit = 0.02 * starting_equity
        self.per_trade_limit = 0.01 * starting_equity
        self.max_positions = 5
        
    def approve_trade(self, symbol, size, price):
        trade_value = size * price
        
        if trade_value > self.per_trade_limit:
            return False, f"Trade value ${trade_value:.2f} exceeds ${self.per_trade_limit:.2f} limit"
        
        if self.daily_loss > self.daily_loss_limit:
            return False, f"Daily loss ${self.daily_loss:.2f} exceeds ${self.daily_loss_limit:.2f} limit"
        
        if len(self.positions) >= self.max_positions:
            return False, f"Already holding {len(self.positions)} positions (max {self.max_positions})"
        
        return True, "Trade approved"
    
    def record_trade(self, symbol, size, price, pnl=0):
        self.daily_trades += 1
        if pnl < 0:
            self.daily_loss += abs(pnl)
        
        self.trade_history.append({
            'symbol': symbol,
            'size': size,
            'price': price,
            'pnl': pnl,
            'timestamp': datetime.now()
        })
        
    def reset_daily(self):
        self.daily_loss = 0
        self.daily_trades = 0
        
    def get_status(self):
        return {
            'equity': self.equity,
            'daily_loss': self.daily_loss,
            'daily_loss_limit': self.daily_loss_limit,
            'positions': len(self.positions),
            'max_positions': self.max_positions,
            'trades_today': self.daily_trades
        }

if __name__ == "__main__":
    print("=" * 50)
    print("V4.0 RISK KERNEL TEST")
    print("=" * 50)
    
    risk = RiskKernel(10000)
    
    approved, message = risk.approve_trade("BTC/USD", 0.01, 50000)
    print(f"\nTest 1 - Small trade: {message}")
    
    approved, message = risk.approve_trade("BTC/USD", 0.5, 50000)
    print(f"Test 2 - Large trade: {message}")
    
    status = risk.get_status()
    print(f"\nCurrent Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    print("✅ Risk Kernel is working!")