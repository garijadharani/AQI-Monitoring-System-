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

AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

air_params = {
    "latitude": latitude,
    "longitude": longitude,
    "current": (
        "us_aqi,pm2_5,pm10,carbon_monoxide,"
        "carbon_dioxide,nitrogen_dioxide,"
        "sulphur_dioxide,ozone"
    ),
    "hourly": "carbon_dioxide",
    "timezone": "Asia/Kolkata"
}

weather_params = {
    "latitude": latitude,
    "longitude": longitude,
    "current": "temperature_2m,relative_humidity_2m",
    "timezone": "Asia/Kolkata"
}

def display_value(value, unit):
    if value is None:
        return "Unavailable"
    return f"{value} {unit}"

try:
    air_response = requests.get(
        AIR_URL, params=air_params, timeout=20
    )
    air_response.raise_for_status()
    air_data = air_response.json()
    current = air_data["current"]

    weather_response = requests.get(
        WEATHER_URL, params=weather_params, timeout=20
    )
    weather_response.raise_for_status()
    weather = weather_response.json()["current"]

    aqi = current.get("us_aqi")
    pm25 = current.get("pm2_5")
    pm10 = current.get("pm10")
    co = current.get("carbon_monoxide")
    no2 = current.get("nitrogen_dioxide")
    so2 = current.get("sulphur_dioxide")
    ozone = current.get("ozone")

    temperature = weather.get("temperature_2m")
    humidity = weather.get("relative_humidity_2m")

    # CO2 is hourly data, not current data
    hourly = air_data.get("hourly", {})
    co2_values = hourly.get("carbon_dioxide", [])
    co2_times = hourly.get("time", [])

    co2 = None
    if co2_values and co2_times:
        air_time = current.get("time")
        if air_time in co2_times:
            co2 = co2_values[co2_times.index(air_time)]

    if aqi is None:
        status = "Unavailable"
    elif aqi <= 50:
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

    st.markdown("### 🌫️ Air Quality Readings")

    c1, c2, c3 = st.columns(3)
    c1.metric("AQI", display_value(aqi, ""))
    c2.metric("PM2.5", display_value(pm25, "µg/m³"))
    c3.metric("PM10", display_value(pm10, "µg/m³"))

    st.success(f"Air Quality Status: {status}")

    st.markdown("### 🌡️ Weather Readings")

    c4, c5 = st.columns(2)
    c4.metric("Temperature", display_value(temperature, "°C"))
    c5.metric("Humidity", display_value(humidity, "%"))

    st.markdown("### 🧪 Gas Concentrations")

    c6, c7, c8 = st.columns(3)
    c6.metric("CO₂", display_value(co2, "ppm"))
    c7.metric("CO", display_value(co, "µg/m³"))
    c8.metric("NO₂", display_value(no2, "µg/m³"))

    c9, c10 = st.columns(2)
    c9.metric("SO₂", display_value(so2, "µg/m³"))
    c10.metric("O₃", display_value(ozone, "µg/m³"))

    st.caption(
        "Environmental estimates from Open-Meteo APIs. "
        "These are not physical sensor measurements."
    )

    st.markdown("### 📩 Telegram Notification")

    if st.button("Send AQI Report to Telegram"):
        try:
            token = st.secrets["BOT_TOKEN"]
            chat_id = st.secrets["CHAT_ID"]

            message = (
                "🌍 AQI Monitoring System\n"
                "📍 RGUKT RK Valley, Kadapa\n\n"
                f"AQI: {display_value(aqi, '')}\n"
                f"Status: {status}\n"
                f"PM2.5: {display_value(pm25, 'µg/m³')}\n"
                f"PM10: {display_value(pm10, 'µg/m³')}\n"
                f"Temperature: {display_value(temperature, '°C')}\n"
                f"Humidity: {display_value(humidity, '%')}\n"
                f"CO2: {display_value(co2, 'ppm')}\n"
                f"CO: {display_value(co, 'µg/m³')}\n"
                f"NO2: {display_value(no2, 'µg/m³')}\n"
                f"SO2: {display_value(so2, 'µg/m³')}\n"
                f"O3: {display_value(ozone, 'µg/m³')}"
            )

            tg_url = (
                f"https://api.telegram.org/bot{token}/sendMessage"
            )

            result = requests.post(
                tg_url,
                data={"chat_id": chat_id, "text": message},
                timeout=15
            )

            result.raise_for_status()

            if result.json().get("ok"):
                st.success("Telegram report sent successfully!")
            else:
                st.error("Telegram message failed.")

        except KeyError:
            st.error(
                "Add BOT_TOKEN and CHAT_ID in Streamlit Secrets."
            )
        except Exception as e:
            st.error(f"Telegram error: {e}")

except Exception as e:
    st.error(f"Unable to fetch data: {e}")
    st.markdown("### 🔗 Share AQI Dashboard on Telegram")

    if st.button("📲 Send Dashboard Link to Telegram"):
        try:
            token = st.secrets["BOT_TOKEN"]
            chat_id = st.secrets["CHAT_ID"]

            dashboard_link = "https://aqimonitoringsystem.streamlit.app/"

            message = (
                "🌍 AQI Monitoring System\n\n"
                "📍 RGUKT RK Valley, Kadapa\n\n"
                "📊 Open Live AQI Dashboard:\n"
                f"{dashboard_link}\n\n"
                "Features:\n"
                "✅ AQI and PM2.5 / PM10\n"
                "✅ Temperature and Humidity\n"
                "✅ CO2 and other gases"
            )

            tg_url = (
                f"https://api.telegram.org/bot{token}/sendMessage"
            )

            result = requests.post(
                tg_url,
                data={"chat_id": chat_id, "text": message},
                timeout=15
            )

            result.raise_for_status()

            if result.json().get("ok"):
                st.success("Dashboard link sent to Telegram!")

        except Exception as e:
            st.error(f"Telegram error: {e}")
            
    
