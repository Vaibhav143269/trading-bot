# V4.0 TELEGRAM TRADING BOT - Get all updates on your phone!

import requests
import time
import pandas as pd
from datetime import datetime
import json

class TradingBotTelegram:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.last_signal = None
        self.last_price = None
        self.trade_count = 0
        self.wins = 0
        self.losses = 0
        self.total_profit = 0
        
    def send_message(self, message):
        """Send message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            params = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.get(url, params=params)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def get_market_data(self):
        """Get current market data"""
        try:
            # Get current price
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd"
            response = requests.get(url)
            data = response.json()
            
            prices = {
                'bitcoin': data['bitcoin']['usd'],
                'ethereum': data['ethereum']['usd'],
                'solana': data['solana']['usd']
            }
            
            # Get historical data for signals
            url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=100"
            response = requests.get(url)
            hist_data = response.json()
            hist_prices = hist_data['prices']
            df = pd.DataFrame(hist_prices, columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['date'] = df['timestamp'].dt.date
            
            # Run strategy
            from advanced_strategy import AdvancedStrategy
            strategy = AdvancedStrategy(df)
            strategy.calculate_indicators()
            signals = strategy.generate_signals()
            
            latest = signals[-1]
            
            return {
                'bitcoin': prices['bitcoin'],
                'ethereum': prices['ethereum'],
                'solana': prices['solana'],
                'signal': latest['signal'],
                'rsi': latest['rsi'],
                'price': latest['price'],
                'reason': latest['reason'],
                'buy_score': latest['buy_score'],
                'sell_score': latest['sell_score']
            }
        except Exception as e:
            print(f"Error getting data: {e}")
            return None
    
    def get_performance(self):
        """Get trading performance"""
        total_trades = self.trade_count
        win_rate = (self.wins / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'wins': self.wins,
            'losses': self.losses,
            'win_rate': win_rate,
            'total_profit': self.total_profit
        }
    
    def monitor(self, check_interval=30):
        """Monitor and send all updates to Telegram"""
        print("=" * 60)
        print("🤖 V4.0 TELEGRAM TRADING BOT")
        print("=" * 60)
        print(f"📱 Sending alerts to Telegram!")
        print(f"⏱️ Checking every {check_interval} seconds")
        print("=" * 60)
        
        # Send startup message
        self.send_message("🚀 <b>Trading Bot Started!</b>\n\n✅ Bot is now monitoring the market\n📊 You'll receive real-time updates")
        
        cycle_count = 0
        
        while True:
            try:
                # Get market data
                data = self.get_market_data()
                if data is None:
                    time.sleep(10)
                    continue
                
                # Check for signal change
                if data['signal'] != self.last_signal and data['signal'] != 'HOLD':
                    # Send signal alert
                    emoji = {
                        'STRONG BUY': '🚀',
                        'BUY': '📈',
                        'SELL': '📉',
                        'STRONG SELL': '🔻'
                    }.get(data['signal'], '⚪')
                    
                    message = f"""
{emoji} <b>{data['signal']} SIGNAL</b>

💰 Bitcoin: ${data['bitcoin']:,.2f}
📊 RSI: {data['rsi']:.2f}
📈 Buy Score: {data['buy_score']}/100
📉 Sell Score: {data['sell_score']}/100
🕐 Time: {datetime.now().strftime('%H:%M:%S')}

📝 Reason: {data['reason']}
                    """
                    self.send_message(message)
                    self.last_signal = data['signal']
                
                # Send price update every 2 minutes
                cycle_count += 1
                if cycle_count % 4 == 0:  # Every 2 minutes (4 * 30 seconds)
                    message = f"""
📊 <b>MARKET UPDATE</b>

🟠 Bitcoin: ${data['bitcoin']:,.2f}
🟣 Ethereum: ${data['ethereum']:,.2f}
🟢 Solana: ${data['solana']:,.2f}

📈 Signal: {data['signal']}
🕐 Time: {datetime.now().strftime('%H:%M:%S')}
                    """
                    self.send_message(message)
                    print(f"📱 Sent market update")
                
                # Send performance update every 10 minutes
                if cycle_count % 20 == 0:  # Every 10 minutes
                    perf = self.get_performance()
                    message = f"""
📈 <b>PERFORMANCE UPDATE</b>

📊 Total Trades: {perf['total_trades']}
✅ Wins: {perf['wins']}
❌ Losses: {perf['losses']}
🎯 Win Rate: {perf['win_rate']:.1f}%
💰 Total Profit: ${perf['total_profit']:,.2f}
                    """
                    self.send_message(message)
                
                # Send heartbeat every 30 minutes
                if cycle_count % 60 == 0:  # Every 30 minutes
                    self.send_message("❤️ Bot is still running... Checking market constantly!")
                
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                self.send_message("⏹️ Trading Bot Stopped!\n\nThanks for using V4.0 Trading Bot!")
                print("\n\n⏹️ Bot stopped")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(10)

# ============================================================
# SETUP - REPLACE WITH YOUR TOKEN AND CHAT ID
# ============================================================

# YOUR TOKEN from @BotFather (replace this with your actual token)
BOT_TOKEN = "8931515551:AAHvOYWER4ba02DxXStPNgFiymEa8mKj5oA"

# YOUR CHAT ID from @userinfobot (replace this with your actual chat ID)
CHAT_ID = "1449083410"

# ============================================================

print("=" * 60)
print("🤖 V4.0 TELEGRAM TRADING BOT")
print("=" * 60)

# Check if user has set their token and chat ID
if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or CHAT_ID == "YOUR_CHAT_ID_HERE":
    print("\n⚠️ SETUP REQUIRED!")
    print("=" * 60)
    print("1. Open Telegram on your phone")
    print("2. Search for @BotFather")
    print("3. Send: /newbot")
    print("4. Name your bot: TradingBot")
    print("5. Username: YourBotName_bot")
    print("6. COPY the token BotFather gives you")
    print("7. Search for @userinfobot and send /start")
    print("8. COPY your chat ID")
    print("\nThen edit this file and replace:")
    print("   BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'")
    print("   CHAT_ID = 'YOUR_CHAT_ID_HERE'")
    print("=" * 60)
else:
    # Start monitoring
    bot = TradingBotTelegram(BOT_TOKEN, CHAT_ID)
    bot.monitor()