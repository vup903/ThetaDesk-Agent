"""Risk-validation spike: can we pull a full US options chain for free?

Pulls AAPL's nearest monthly expiry, prints the put chain columns we need
for the wheel-strategy screener (strike, bid, IV, OI), plus earnings date
and 1y price history (needed for IV-rank context).
"""
import yfinance as yf

t = yf.Ticker("AAPL")

expiries = t.options
print("expiries:", expiries[:6])

exp = expiries[2]  # skip weeklies, grab something ~3-5 weeks out
chain = t.option_chain(exp)
puts = chain.puts

spot = t.fast_info["lastPrice"]
print(f"\nspot={spot:.2f}  expiry={exp}  puts={len(puts)} rows")
print("columns:", list(puts.columns))

# the exact fields the screener needs
otm = puts[(puts.strike < spot * 0.97) & (puts.strike > spot * 0.85)]
cols = ["contractSymbol", "strike", "bid", "ask", "impliedVolatility", "openInterest", "volume"]
print("\nOTM cash-secured-put candidates:")
print(otm[cols].tail(8).to_string(index=False))

# earnings date (needed for earnings-avoidance filter)
try:
    cal = t.calendar
    print("\nearnings calendar:", cal.get("Earnings Date"))
except Exception as e:
    print("\nearnings calendar failed:", e)

# 1y daily history (needed for IV-rank / HV context in ClickHouse)
hist = t.history(period="1y")
print(f"\n1y history rows: {len(hist)}, last close {hist['Close'].iloc[-1]:.2f}")
