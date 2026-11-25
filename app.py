 
import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="AQI Monitoring Dashboard",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 AQI Monitoring Dashboard")
st.write("Real-time Environmental Monitoring - RGUKT RK Valley, Kadapa")

# Location
latitude = 14.3357
longitude = 78.5384

try:
    # -------- AQI DATA --------
    aqi_url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    aqi_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "us_aqi,pm2_5,pm10,carbon_dioxide",
        "timezone": "Asia/Kolkata"
    }

    aqi_response = requests.get(
        aqi_url, params=aqi_params, timeout=20
    )
    aqi_response.raise_for_status()
    aqi_data = aqi_response.json()
    aqi_current = aqi_data["current"]

    aqi = aqi_current.get("us_aqi")
    pm25 = aqi_current.get("pm2_5")
    pm10 = aqi_current.get("pm10")
    co2 = aqi_current.get("carbon_dioxide")

    # -------- WEATHER DATA --------
    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m",
        "timezone": "Asia/Kolkata"
    }

    weather_response = requests.get(
        weather_url, params=weather_params, timeout=20
    )
    weather_response.raise_for_status()
    weather_data = weather_response.json()
    weather_current = weather_data["current"]

    temperature = weather_current.get("temperature_2m")
    humidity = weather_current.get("relative_humidity_2m")

    # -------- AQI CATEGORY --------
    if aqi is not None:
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
    else:
        category = "Unavailable"

    # -------- DISPLAY --------
    st.subheader("📍 RGUKT RK Valley")

    col1, col2, col3 = st.columns(3)

    col1.metric("AQI", aqi if aqi is not None else "N/A")
    col2.metric("PM2.5", f"{pm25} µg/m³" if pm25 is not None else "N/A")
    col3.metric("PM10", f"{pm10} µg/m³" if pm10 is not None else "N/A")

    col4, col5, col6 = st.columns(3)

    col4.metric(
        "🌡️ Temperature",
        f"{temperature} °C" if temperature is not None else "N/A"
    )

    col5.metric(
        "💧 Humidity",
        f"{humidity} %" if humidity is not None else "N/A"
    )

    col6.metric(
        "🫧 CO₂",
        f"{co2} ppm" if co2 is not None else "N/A"
    )

    st.subheader("AQI Status")
    st.write(category)

    # -------- DATA TABLE --------
    df = pd.DataFrame({
        "Parameter": [
            "AQI", "PM2.5", "PM10",
            "Temperature", "Humidity", "CO2"
        ],
        "Value": [
            aqi, pm25, pm10,
            temperature, humidity, co2
        ],
        "Unit": [
            "AQI", "µg/m³", "µg/m³",
            "°C", "%", "ppm"
        ]
    })

    st.subheader("📊 Environmental Data")
    st.dataframe(df, use_container_width=True)

    # -------- GRAPH --------
    st.subheader("📈 Environmental Graph")

    graph_df = pd.DataFrame({
        "Parameter": ["AQI", "PM2.5", "PM10", "Temperature", "Humidity", "CO2"],
        "Value": [aqi, pm25, pm10, temperature, humidity, co2]
    })

    graph_df = graph_df.dropna()

    st.bar_chart(graph_df.set_index("Parameter"))

    # -------- TELEGRAM --------
    st.subheader("📲 Share Dashboard on Telegram")

    bot_token = st.secrets.get("BOT_TOKEN", "")
    chat_id = st.secrets.get("CHAT_ID", "")
    dashboard_url = st.secrets.get("DASHBOARD_URL", "")

    # Send AQI Report
    if st.button("📊 Send AQI Report to Telegram"):

        if not bot_token or not chat_id:
            st.error("Please configure BOT_TOKEN and CHAT_ID in Secrets.")

        else:
            message = (
                "🌍 Environmental Monitoring Report\n\n"
                "📍 RGUKT RK Valley, Kadapa\n"
                f"🌫️ AQI: {aqi}\n"
                f"🫧 PM2.5: {pm25} µg/m³\n"
                f"🌪️ PM10: {pm10} µg/m³\n"
                f"🌡️ Temperature: {temperature} °C\n"
                f"💧 Humidity: {humidity} %\n"
                f"🫧 CO2: {co2} ppm\n"
                f"📋 AQI Status: {category}"
            )

            try:
                telegram_response = requests.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    data={"chat_id": chat_id, "text": message},
                    timeout=20
                )

                telegram_response.raise_for_status()

                if telegram_response.json().get("ok"):
                    st.success("Report sent successfully to Telegram!")
                else:
                    st.error("Telegram could not send the report.")

            except Exception as e:
                st.error(f"Telegram error: {e}")

    # Send Dashboard Link
    if st.button("🔗 Send Dashboard Link to Telegram"):

        if not bot_token or not chat_id or not dashboard_url:
            st.error("Please configure all Telegram Secrets.")

        else:
            message = (
                "🌍 AQI Monitoring Dashboard\n\n"
                "Open the live dashboard here:\n"
                f"{dashboard_url}"
            )

            try:
                telegram_response = requests.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    data={"chat_id": chat_id, "text": message},
                    timeout=20
                )

                telegram_response.raise_for_status()

                if telegram_response.json().get("ok"):
                    st.success("Dashboard link sent successfully to Telegram!")
                else:
                    st.error("Telegram could not send the link.")

            except Exception as e:
                st.error(f"Telegram error: {e}")

except Exception as e:
    st.error(f"Unable to load dashboard data: {e}")

 
