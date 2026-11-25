 
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="AQI Dashboard", page_icon="🌍", layout="wide")

st.title("🌍 AQI Monitoring Dashboard")
st.write("RGUKT RK Valley, Kadapa")

latitude = 14.3357
longitude = 78.5384

try:
    response = requests.get(
        "https://air-quality-api.open-meteo.com/v1/air-quality",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "us_aqi,pm2_5,pm10",
            "timezone": "Asia/Kolkata"
        },
        timeout=20
    )
    response.raise_for_status()
    data = response.json()
    current = data["current"]

    aqi = current["us_aqi"]
    pm25 = current["pm2_5"]
    pm10 = current["pm10"]

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

    st.subheader("📍 RGUKT RK Valley")

    c1, c2, c3 = st.columns(3)
    c1.metric("AQI", aqi)
    c2.metric("PM2.5", f"{pm25} µg/m³")
    c3.metric("PM10", f"{pm10} µg/m³")

    st.subheader("AQI Status")
    st.write(category)

    df = pd.DataFrame({
        "Parameter": ["AQI", "PM2.5", "PM10"],
        "Value": [aqi, pm25, pm10]
    })

    st.subheader("📊 Air Quality Data")
    st.dataframe(df, use_container_width=True)

    st.subheader("📈 Graph")
    st.bar_chart(df.set_index("Parameter"))

    st.subheader("📲 Telegram Sharing")

    # Safely read secrets
    bot_token = st.secrets.get("BOT_TOKEN", "")
    chat_id = st.secrets.get("CHAT_ID", "")
    dashboard_url = st.secrets.get("DASHBOARD_URL", "")

    if not bot_token or not chat_id:
        st.warning("Please configure BOT_TOKEN and CHAT_ID in Streamlit Secrets.")

    # Send AQI Report
    if st.button("📊 Send AQI Report to Telegram"):
        if not bot_token or not chat_id:
            st.error("Telegram secrets are missing.")
        else:
            message = (
                "🌍 AQI Monitoring Report\n\n"
                "📍 RGUKT RK Valley, Kadapa\n"
                f"🌫️ AQI: {aqi}\n"
                f"🫧 PM2.5: {pm25} µg/m³\n"
                f"🌪️ PM10: {pm10} µg/m³\n"
                f"📋 Status: {category}"
            )

            try:
                result = requests.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    data={"chat_id": chat_id, "text": message},
                    timeout=20
                )
                result.raise_for_status()

                if result.json().get("ok"):
                    st.success("AQI report sent to Telegram!")
                else:
                    st.error(result.json().get("description", "Telegram error"))

            except Exception as e:
                st.error(f"Report sending error: {e}")

    # Send Dashboard Link
    if st.button("🔗 Send Dashboard Link to Telegram"):
        if not bot_token or not chat_id or not dashboard_url:
            st.error("BOT_TOKEN, CHAT_ID or DASHBOARD_URL is missing in Secrets.")
        else:
            message = (
                "🌍 AQI Monitoring Dashboard\n\n"
                "Open the live dashboard:\n"
                f"{dashboard_url}"
            )

            try:
                result = requests.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    data={"chat_id": chat_id, "text": message},
                    timeout=20
                )
                result.raise_for_status()

                if result.json().get("ok"):
                    st.success("Dashboard link sent to Telegram!")
                else:
                    st.error(result.json().get("description", "Telegram error"))

            except Exception as e:
                st.error(f"Link sending error: {e}")

except Exception as e:
    st.error(f"AQI loading error: {e}")
