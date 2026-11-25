import streamlit as st
import requests
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AQI Monitoring Dashboard",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Air Quality Monitoring Dashboard")
st.write("Real-time Air Quality Monitoring at RGUKT RK Valley")

# ---------------- LOCATION ----------------
latitude = 14.3357
longitude = 78.5384

# ---------------- AQI API ----------------
url = "https://air-quality-api.open-meteo.com/v1/air-quality"

params = {
    "latitude": latitude,
    "longitude": longitude,
    "current": "us_aqi,pm2_5,pm10"
    "timezone": "Asia/Kolkata"
}

try:
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    current = data["current"]

    aqi = current["us_aqi"]
    pm25 = current["pm2_5"]
    pm10 = current["pm10"]

    # ---------------- AQI CATEGORY ----------------
    if aqi <= 50:
        category = "Good"
    elif aqi <= 100:
        category = "Moderate"
    elif aqi <= 150:
        category = "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        category = "Unhealthy"
    elif aqi <= 300:
        category = "Very Unhealthy"
    else:
        category = "Hazardous"

    # ---------------- DISPLAY DATA ----------------
    st.subheader("📍 RGUKT RK Valley, Kadapa")

    col1, col2, col3 = st.columns(3)

    col1.metric("AQI", aqi)
    col2.metric("PM2.5", f"{pm25} µg/m³")
    col3.metric("PM10", f"{pm10} µg/m³")

    st.subheader("AQI Status")
    st.success(category) if category == "Good" else st.warning(category)

    # ---------------- DATA TABLE ----------------
    df = pd.DataFrame({
        "Parameter": ["AQI", "PM2.5", "PM10"],
        "Value": [aqi, pm25, pm10],
        "Unit": ["AQI", "µg/m³", "µg/m³"]
    })

    st.subheader("📊 Air Quality Data")
    st.dataframe(df, use_container_width=True)

    # ---------------- GRAPH ----------------
    st.subheader("📈 Air Quality Graph")
    st.bar_chart(df.set_index("Parameter")["Value"])

    # ---------------- TELEGRAM ----------------
    st.subheader("📲 Share AQI Dashboard on Telegram")

    bot_token = st.secrets["BOT_TOKEN"]
    chat_id = st.secrets["CHAT_ID"]
    dashboard_url = st.secrets["DASHBOARD_URL"]

    # Send AQI report
    if st.button("📊 Send AQI Report to Telegram"):
        message = (
            "🌍 AQI Monitoring Report\n\n"
            "📍 RGUKT RK Valley, Kadapa\n"
            f"🌫️ AQI: {aqi}\n"
            f"🫧 PM2.5: {pm25} µg/m³\n"
            f"🌪️ PM10: {pm10} µg/m³\n"
            f"📋 Status: {category}"
        )

        telegram_url = (
            f"https://api.telegram.org/bot{bot_token}/sendMessage"
        )

        try:
            result = requests.post(
                telegram_url,
                data={"chat_id": chat_id, "text": message},
                timeout=20
            )
            result.raise_for_status()

            if result.json().get("ok"):
                st.success("AQI report sent successfully to Telegram!")
            else:
                st.error("Telegram could not send the report.")

        except Exception as e:
            st.error(f"Telegram error: {e}")

    # Send dashboard link
    if st.button("🔗 Send Dashboard Link to Telegram"):
        message = (
            "🌍 AQI Monitoring Dashboard\n\n"
            "Open the live dashboard here:\n"
            f"{dashboard_url}"
        )

        telegram_url = (
            f"https://api.telegram.org/bot{bot_token}/sendMessage"
        )

        try:
            result = requests.post(
                telegram_url,
                data={"chat_id": chat_id, "text": message},
                timeout=20
            )
            result.raise_for_status()

            if result.json().get("ok"):
                st.success("Dashboard link sent successfully to Telegram!")
            else:
                st.error("Telegram could not send the dashboard link.")

        except Exception as e:
            st.error(f"Telegram error: {e}")

except Exception as e:
    st.error(f"Unable to fetch AQI data: {e}")
