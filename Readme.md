# 🌌 Galaxy Trade (Galactic Exchange)

Galaxy Trade is a high-fidelity, space-themed virtual stock market simulator built with Django. It allows users to trade real-world stocks using virtual currency ("Buying Power") while experiencing a highly interactive, futuristic user interface. This platform is perfect for beginners wanting to learn the stock market without financial risk.

## 🚀 Features

### 1. User Authentication & Security
* **Identity Management:** Secure registration and login system.
* **Access Recovery:** Password reset functionality.
* **Private Portfolios:** Each user gets an isolated virtual wallet and portfolio instance.

### 2. Live Market Dashboard
* **Real-Time Data:** Fetches live stock prices and market data using the `yfinance` API.
* **Interactive Charts:** Integrated TradingView widgets for advanced technical analysis (Timeframes, Candlesticks, Indicators).
* **Discovery Radar:** Quick-access list of popular stocks (AAPL, TSLA, MSFT, etc.).
* **Watchlist:** Toggle feature to save and monitor specific stocks of interest.

### 3. Virtual Trading System
* **Buying & Selling:** Execute trades seamlessly. The system calculates total costs based on live market prices.
* **Portfolio Tracking:** Dynamically updates "Buying Power" and owned "Quantity" of stocks.
* **Dynamic Net Worth:** A centralized calculation engine automatically computes the user's Total Net Worth (Remaining Cash + Current Live Value of all owned assets) across all pages.

### 4. Educational Hub
* **Pilot Training Manual:** A built-in tutorial page explaining trading mechanics (Profit/Loss), chart reading, technical indicators, and platform terminology.

### 5. UI/UX Design (Galactic Theme)
* **Glassmorphism:** Semi-transparent, blurred cosmic boxes for a sleek, modern feel.
* **Deep Space Aesthetic:** Radial dark gradients, neon cyan/magenta accents, and `Space Mono` typography.
* **Responsive Design:** Ensures a smooth experience across different screen sizes.

---

## 🛠️ Technical Stack

**Backend:**
* Python (3.12+)
* Django (6.0+)
* SQLite3 (Database)

**Frontend:**
* HTML5 / CSS3 (Custom Galactic Theme)
* JavaScript
* TradingView Advanced Chart Widget

**APIs & Libraries:**
* `yfinance` (Yahoo Finance API for real-time stock data)

---

## ⚙️ Installation & Setup

To run this project locally on your machine, follow these steps:

### 1. Clone the repository
```bash
git clone [https://github.com/yourusername/galaxy-trade.git](https://github.com/yourusername/galaxy-trade.git)
cd galaxy-trade

### How to Run these:
1. Create and activate virtual environment.
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

2. Installl Dependencies.

pip install django yfinance
# OR
pip install -r requirements.txt

3.After writing codes Apply database migrations:
python manage.py makemigrations
python manage.py migrate

4. Create superuser(Admin) for starters or register when deployed:

python manage.py createsuperuser

5. Runserver and redirect to the browser using the https link.

python manage.py runserver

Visit http://127.0.0.1:8000/ in your browser to enter the Galaxy!