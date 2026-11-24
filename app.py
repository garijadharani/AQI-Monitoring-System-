
import streamlit as st
import requests

st.set_page_config(
    page_title="AQI Monitoring System",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 AQI Monitoring System")
st.subheader("RGUKT RK Valley, Kadapa")

latitude = 14.3357
longitude = 78.5384

url = "https://air-quality-api.open-meteo.com/v1/air-quality"

params = {
    "latitude": latitude,
    "longitude": longitude,
    "current": "us_aqi,pm2_5,pm10",
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

    if aqi <= 50:
        status = "Good"
    elif aqi <= 100:
        status = "Moderate"
    elif aqi <= 150:
        status = "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        status = "Unhealthy"
    elif aqi <= 300:
        status = "Very Unhealthy"
    else:
        status = "Hazardous"

    st.metric("Air Quality Index (AQI)", aqi)
    st.metric("PM2.5", f"{pm25} µg/m³")
    st.metric("PM10", f"{pm10} µg/m³")

    st.success(f"Air Quality Status: {status}")

    st.caption("Live data provided by Open-Meteo")

    if st.button("📩 Send AQI Report to Telegram"):
        try:
            token = st.secrets["BOT_TOKEN"]
            chat_id = st.secrets["CHAT_ID"]

            message = (
                "🌍 AQI Monitoring System\n"
                "📍 RGUKT RK Valley, Kadapa\n"
                f"🌫️ AQI: {aqi}\n"
                f"PM2.5: {pm25} µg/m³\n"
                f"PM10: {pm10} µg/m³\n"
                f"Status: {status}"
            )

            tg_url = f"https://api.telegram.org/bot{token}/sendMessage"

            result = requests.post(
                tg_url,
                data={"chat_id": chat_id, "text": message},
                timeout=15
            )

            result.raise_for_status()

            if result.json().get("ok"):
                st.success("Telegram message sent successfully!")
            else:
                st.error("Telegram message failed.")

        except Exception as e:
            st.error(f"Telegram error: {e}")

except Exception as e:
    st.error(f"Unable to fetch AQI data: {e}")
  
