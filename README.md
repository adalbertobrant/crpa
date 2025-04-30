```markdown
# 📜 README.md

---

## 🚀 Country Risk Premium (CRP) Calculator for Brazil vs. USA

This script calculates the **Country Risk Premium (CRP)** between Brazil and the United States using real-time financial data from various sources, including `yfinance`, the Brazilian Central Bank (BCB), and web scraping from [Investing.com](https://www.investing.com). The CRP is a crucial metric in algorithmic trading and investment analysis to assess the additional risk of investing in a country compared to a benchmark (in this case, the US).

---

## 🎯 Purpose

The goal of this code is to:

- Fetch U.S. Treasury yields and Brazilian bond yields.
- Calculate the CRP as the spread between yield curves adjusted for currency exchange.
- Provide complementary market data like USD/BRL exchange rate and 10-year bond yields for both countries.
- Offer an integrated analysis based on the calculated CRP.

---

## 🧠 How It Works

### 🔹 Step 1: Data Collection

#### ✅ **U.S. Treasuries**
- Uses `yfinance` to fetch U.S. Treasury yields for different maturities (2Y, 5Y, 10Y, 30Y).
- Converts percentages into decimal form for consistency.

#### 🇧🇷 **Brazilian Bonds**
- Retrieves the latest 10-year bond yield via BCB API.
- Calculates the duration based on the bond's maturity date.
- Adjusts the yield by dividing it by the USD/BRL exchange rate to get an equivalent U.S.-denominated yield.

#### 💰 **Exchange Rate (USD/BRL)**
- Obtained directly from the BCB API for accuracy.

#### 🌐 **Web Scraping**
- Fetches additional market data from Investing.com (e.g., 10-year bond yields for Brazil and the U.S.).
- Uses robust selectors and fallback methods to handle dynamic content or layout changes.

---

### 🔹 Step 2: Calculation

#### 📈 **Yield Curve Interpolation**
- Both U.S. and Brazilian yield curves are interpolated over a common set of durations using linear interpolation (`np.interp`).
- This allows comparison across all time horizons where data exists for both countries.

#### ⚖️ **CRP Calculation**
- The CRP is computed as the average difference between the interpolated Brazilian and U.S. yield curves.
- Final result is expressed in **basis points (bps)**:
  
  ```python
  crp_bps = np.mean(spread) * 10000
  ```

- A negative CRP indicates higher perceived risk in Brazil relative to the U.S.

---

### 🔹 Step 3: Output & Analysis

- Displays:
  - CRP value with interpretation.
  - U.S. and Brazilian 10-year bond yields.
  - USD/BRL exchange rate.
  - An **integrated analysis** that combines all these metrics to give a holistic view of the market situation.

---

## 🛠️ Requirements

To run this script, you need the following Python packages:

```bash
pip install yfinance numpy requests beautifulsoup4 lxml python-dotenv
```

---

## 🧪 Example Output

```
=== Cálculo do Country Risk Premium (CRP) ===

=== Dados de Mercado ===

=== Resultados Finais ===
CRP (Risco País): 250.4 bps
Taxa de Juros Brasil 10 anos: 11.8%
Taxa de Juros EUA 10 anos: 4.2%
Câmbio USD/BRL (BCB): 5.25

Análise Integrada: 6.78%
(Valores negativos indicam maior risco Brasil)
```

---

## 📦 License

This project is licensed under the **Custom License**, which grants permission to use the code for educational, research, or commercial purposes **only if the following conditions are met**:

1. **Attribution Required**: You must **cite the original author** when using or modifying the code.
   - Format: `"Adapted from the Country Risk Premium Calculator by [Adalberto Brant]."`
2. **Email Notification**: Before using the code, you **must send an email to [adalbertobrant@gmail.com]** requesting permission. This helps track users and maintain accountability.
3. **No Redistribution Without Permission**: You may not redistribute the code publicly or commercially without explicit written consent from the author.

---

## 📩 Contact

If you have any questions, want to contribute, or need help adapting this code to other countries, feel free to reach out!

📧 Email: adalbertobrant@gmail.com  
🌐 Website: https://github.com/adalbertobrant

---

## 🌟 Contributing

Contributions are welcome! If you find bugs or have suggestions for improvements, please open an issue or submit a pull request.

---

## 🧾 Acknowledgments

- [`yfinance`](https://github.com/ranaroussi/yfinance) – For fetching U.S. Treasury data.
- [`requests`](https://docs.python-requests.org/en/latest/) – For API calls.
- [`BeautifulSoup`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) – For web scraping.
- [`numpy`](https://numpy.org/) – For numerical calculations and interpolation.

---

## 🧭 Roadmap

- ✅ Add support for more countries.
- ✅ Improve error handling and logging.
- ✅ Implement caching for faster execution.
- ✅ Expand documentation and add unit tests.
- ✅ Create a CLI or GUI version for easier access.

---

Thanks for using my tool! Let's make better decisions together with smarter data. 🚀📊
```
