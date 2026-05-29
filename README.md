# ₱£R$O₦AL Finance: Advanced Portfolio Dashboard

![CodeQL Passing Badge](https://github.com/your-username/personal-finance/actions/workflows/github-code-scanning/codeql/badge.svg)

#### Video Demo:  [Watch on YouTube](https://youtu.be/ogH2wI5TgyU)

#### Description:

## 1. Project Overview

**₱£R$O₦AL Finance** is a professional-grade web application built using the Flask framework. This project's scope expands into a comprehensive wealth management tool. It moves beyond simple buy/sell mechanics to offer users **real-time portfolio analytics** and **data visualization**.




The application is designed to simulate a modern brokerage experience, providing users with the data-driven insights necessary to track "Unrealized Gains", "Asset Allocation" and "Historical Trends" in a single, cohesive interface.



## 2. Core Vision and UX Philosophy

The design philosophy for this project was "**Frictionless Financial Intelligence.**" Standard financial tools often suffer from fragmented data. This project solves that by implementing:

* **A "Dashboard-First" Approach**: The most critical metrics—Net Worth, Cash Liquidity, and Asset Distribution—are presented visually the moment a user logs in.
* **Actionable Connectivity**: High-friction tasks, such as looking up a stock and then navigating to buy it, are streamlined via "Quick-Action" buttons that carry data across routes.
* **Global Navigation**: A persistent search utility in the navbar ensures that the path to market data is zero-click from any page.




## 3. Advanced Feature Set

### 3.1. Dynamic Portfolio Dashboard (Index)

The home page has been re-engineered from a static list into a live analytics command center:

* **Net Worth Tracking**: Real-time calculation of total assets by aggregating live market values with current liquid cash.
* **Unrealized Profit/Loss (P/L)**: The system tracks the "Cost Basis" for every holding. By comparing the weighted average price paid against the current market price, users can see their "Paper Gains" or losses.
* **Day Change Indicators**: Next to each stock price, the app displays a movement indicator (▲/▼) and a percentage change, showing how the stock has performed since the previous market close.




### 3.2. Data Visualization (Chart.js)

To improve data digestibility, I integrated the **Chart.js** library for high-fidelity rendering:

* **Portfolio Allocation (Doughnut Chart)**: A responsive chart that dynamically calculates the weight of each stock and cash as a percentage of the total portfolio. This helps users visualize their diversification levels.
* **Historical Trends (Line Chart)**: The Quote page features a 90-day historical price chart, allowing users to analyze trends rather than relying on a single price point.




### 3.3. Integrated Trading Workflows

* **"Quick Buy" & "Quick Sell"**: Buttons on the Quote and Index pages use URL parameters to pre-fill the symbol and share counts into the trade forms. This reduces manual entry and prevents user error.
* **Smart Search**: A global search bar in the navbar allows for instant ticker lookups from any page in the application.




### 3.4. Enhanced Transaction Ledger

Users can  review their lifetime trading patterns and see the individual performance of every historical transaction.



## 4. Technical Architecture

### 4.1. The Backend (Python & Flask)

The application logic is written in Python, utilizing the Flask micro-framework. Key logic highlights include:

* **API Orchestration**: Integrating the `yfinance` library to fetch multi-dimensional data including Current Price, Previous Close, and Historical Close.
* **Session Security**: Implementing secure, server-side session management to protect user data and financial records.




### 4.2. The Database (SQLite)

The data layer utilizes a relational schema optimized for speed:

* `users`: Manages credentials (hashed via PBKDF2) and cash balances.
* `transactions`: The immutable "Source of Truth," logging every buy/sell event with price and timestamp.
* `ownerships`: A summary table used for rapid portfolio rendering, tracking net positions per ticker.




## 5. Mathematical Methodologies

### 5.1. Unrealized Profit/Loss

For each holding, the system determines performance by subtracting the total investment from the current market value:

$$Unrealized P/L = (Current Price \times Shares Held) - \sum (Purchase Price \times Shares Purchased)$$

### 5.2. Portfolio Allocation

The doughnut chart calculates allocation by dividing individual asset values by the total net worth:

$$Allocation \% = \left( \frac{Asset Value}{Total Net Worth} \right) \times 100$$

### 5.3. Day Change

Daily movement is calculated by comparing the current price ($P_c$) against the previous close ($P_{pc}$):

$$Change \% = \left( \frac{P_c - P_{pc}}{P_{pc}} \right) \times 100$$

## 6. Security and Input Validation

A financial application requires strict data integrity. This project implements:

* **SQL Injection Prevention**: All database queries use parameterized inputs via the CS50 library.
* **Transaction Guardrails**: Validates that users cannot sell more shares than they own or spend more cash than they possess.
* **Password Security**: Uses `werkzeug.security` for hashing and salt protection.
* **API Robustness**: The `lookup` function handles API failures gracefully using try-except blocks to prevent application crashes.




## 7. Installation and Setup

1. **Clone the Repository**:
```bash
git clone https://github.com/aritha-alahakoon/personal-finance.git
cd personal-finance

```


2. **Create a Virtual Environment**:
* For macOS/Linux: `python3 -m venv venv`
* For Windows: `python -m venv venv`


3. **Activate the Virtual Environment**:
* For macOS/Linux: `source venv/bin/activate`
* For Windows (Command Prompt): `venv\Scripts\activate.bat`
* For Windows (PowerShell): `.\venv\Scripts\Activate.ps1`


4. **Install Dependencies**:
```bash
pip install -r requirements.txt

```


5. **Run the Flask Server**:
```bash
flask run

```



> ⚠️ **Security Note:** Never commit real API keys or your Flask `SECRET_KEY` to a public GitHub repository. Use environment variables (`.env` files) to manage sensitive credentials locally.

## 8. Conclusion

This project represents a bridge between academic exercise and real-world application. By focusing on data visualization, user experience, and financial accuracy, **₱£R$O₦AL Finance** provides a meaningful simulation of modern wealth management. It demonstrates proficiency in full-stack development, API integration, and relational database management.

## 9. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Summary of the MIT License:

* **Commercial Use:** You can use this code for commercial purposes.
* **Modification:** You can alter the code however you see fit.
* **Distribution:** You can share this code with anyone.
* **Sublicense:** You can incorporate this into other software.
* **Limitation of Liability/Warranty:** The software is provided "as is", without warranty of any kind.

#### Author: Aritha Alahakoon
