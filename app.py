import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
import plotly.express as px

# =========================
# Page config
# =========================
st.set_page_config(
    page_title="Heatwave Dashboard (SDG 13)",
    page_icon="🔥",
    layout="wide"
)

# =========================
# White background + light UI styling
# =========================
st.markdown(
    """
    <style>
      .stApp { background-color: #FFFFFF; }
      header[data-testid="stHeader"] { background: rgba(255,255,255,0); }
      section[data-testid="stSidebar"] { background-color: #FFFFFF; }
      /* Make main container a bit tighter for cleaner screenshot */
      .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
      /* Card-like look */
      .card {
        border: 1px solid #eee;
        border-radius: 14px;
        padding: 14px 16px;
        background: #fff;
      }
      .badge-high { display:inline-block; padding:6px 10px; border-radius:999px; background:#ffe8e8; color:#b42318; font-weight:700; }
      .badge-med  { display:inline-block; padding:6px 10px; border-radius:999px; background:#fff7e6; color:#b54708; font-weight:700; }
      .badge-low  { display:inline-block; padding:6px 10px; border-radius:999px; background:#ecfdf3; color:#027a48; font-weight:700; }
      .muted { color:#6b7280; font-size:0.92rem; }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# Helpers
# =========================
def classify_risk(max_temp_c: float, heat_index: float) -> str:
    # Simple & explainable rule (good for coursework)
    if heat_index >= 41 or max_temp_c >= 38:
        return "HIGH"
    if heat_index >= 35 or max_temp_c >= 35:
        return "MEDIUM"
    return "LOW"

def advice_for_risk(risk: str) -> str:
    if risk == "HIGH":
        return "Avoid outdoor activities during peak heat hours. Stay hydrated and seek shade/air-conditioning."
    if risk == "MEDIUM":
        return "Limit prolonged outdoor exposure. Take breaks, drink water, and monitor updates."
    return "Normal conditions. Maintain routine activities and monitor weather updates."

def generate_daily_timeseries(start: date, end: date, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    days = (end - start).days + 1
    dates = [start + timedelta(days=i) for i in range(days)]

    # Demo increasing pattern + noise (for screenshot purpose)
    base_temp = np.linspace(33, 39, days) + rng.normal(0, 0.6, days)
    humidity = np.clip(60 + rng.normal(0, 6, days), 35, 90)

    # Simple heat index proxy (OK for mock-up)
    heat_index = base_temp + (humidity - 50) * 0.08

    df = pd.DataFrame({
        "date": dates,
        "max_temp_c": np.round(base_temp, 1),
        "humidity": np.round(humidity, 0).astype(int),
        "heat_index": np.round(heat_index, 1),
    })
    df["risk"] = df.apply(lambda r: classify_risk(r["max_temp_c"], r["heat_index"]), axis=1)
    return df

def infographic_table() -> pd.DataFrame:
    # Match your infographic "Global Heatwaves data"
    data = {
        "Year": [2021, 2022, 2023, 2024, 2025],
        "Max Temp (°C)": [36, 34, 37, 39, 37],
        "Humidity (%)": [70, 65, 68, 73, 69],
        "Heat Index": [42, 38, 43, 45, 43],
        "Heatwave": ["Yes", "No", "Yes", "Yes", "Yes"],
    }
    return pd.DataFrame(data)

# =========================
# Header (aligned with infographic)
# =========================
st.markdown("## **Who Made Heatwaves Hotter?**")
st.markdown("**A Data Science Approach to Climate Action (SDG 13)**")
st.markdown(
    "<div class='muted'>Using data analytics and predictive modeling to understand and forecast extreme heatwaves.</div>",
    unsafe_allow_html=True
)
st.divider()

# =========================
# Sidebar: INPUT
# =========================
with st.sidebar:
    st.header("INPUT")
    location = st.selectbox("Location", ["Kuala Lumpur", "Johor Bahru", "Penang", "Kuching", "City Name"])

    today = date.today()
    default_start = today - timedelta(days=7)
    default_end = today

    start_date = st.date_input("Start date", value=default_start)
    end_date = st.date_input("End date", value=default_end)

    if start_date > end_date:
        st.error("Start date must be <= end date.")
        st.stop()

    st.button("SUBMIT", use_container_width=True)

# Generate demo series (for analytics charts)
df = generate_daily_timeseries(start_date, end_date)

# =========================
# Layout
# =========================
left, right = st.columns([2, 1], gap="large")

# -------------------------
# LEFT: ANALYTICS
# -------------------------
with left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("ANALYTICS")

    fig_temp = px.line(
        df, x="date", y="max_temp_c", markers=True,
        title="Temperature Trend (Max Temp °C)"
    )
    fig_temp.update_layout(template="plotly_white")
    st.plotly_chart(fig_temp, use_container_width=True)

    fig_hi = px.area(
        df, x="date", y="heat_index", markers=True,
        title="Heat Index Trend"
    )
    fig_hi.update_layout(template="plotly_white")
    st.plotly_chart(fig_hi, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")

    # Infographic-aligned table
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Global Heatwaves data")
    st.dataframe(infographic_table(), use_container_width=True, hide_index=True)
    st.caption("Data from meteorological stations and climate databases. (Sample/hypothetical for mock-up)")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# RIGHT: OUTPUTS & ALERTS
# -------------------------
with right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("OUTPUTS & ALERTS")

    peak_temp = float(df["max_temp_c"].max())
    peak_hi = float(df["heat_index"].max())
    risk = classify_risk(peak_temp, peak_hi)

    c1, c2 = st.columns(2)
    c1.metric("Peak Max Temp (°C)", f"{peak_temp:.1f}")
    c2.metric("Peak Heat Index", f"{peak_hi:.1f}")

    st.markdown("### Heatwave Risk Level")
    if risk == "HIGH":
        st.markdown("<span class='badge-high'>HIGH — Extreme heat likely</span>", unsafe_allow_html=True)
    elif risk == "MEDIUM":
        st.markdown("<span class='badge-med'>MEDIUM — Heat stress possible</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='badge-low'>LOW — Normal conditions</span>", unsafe_allow_html=True)

    st.markdown("### 3-Day Forecast (Mock)")
    next3 = df.tail(min(3, len(df)))[["date", "max_temp_c", "risk"]].copy()
    next3.rename(columns={"date": "Date", "max_temp_c": "Max Temp (°C)", "risk": "Risk"}, inplace=True)
    next3["Date"] = next3["Date"].astype(str)
    st.table(next3)

    st.markdown("### Health Alert")
    st.info(advice_for_risk(risk))

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# Optional: small footer (keep minimal for clean screenshot)
# =========================
with st.expander("Technologies used (for mock-up)"):
    st.write("- Python, Pandas, NumPy, Scikit-learn (concept), Plotly, Streamlit")
