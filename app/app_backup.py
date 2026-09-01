import streamlit as st
import pandas as pd
import joblib
import requests

st.set_page_config(
    page_title="Landslide Early Warning System",
    page_icon="🏔️",
    layout="wide"
)

# =========================================================
# LOAD MODEL AND DATASET
# =========================================================

model = joblib.load("model/landslide_model.pkl")
data = pd.read_csv("dataset/wsn_landslide_data.csv")

features = data.drop("Label", axis=1).columns.tolist()


# =========================================================
# GET LOCATION INFORMATION
# =========================================================

def search_location(place):

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": place,
        "count": 5,
        "language": "en",
        "format": "json"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    result = response.json()

    return result.get("results", [])


# =========================================================
# GET LIVE ENVIRONMENTAL DATA
# =========================================================

def get_environmental_data(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "soil_moisture_0_to_7cm"
        ),

        "hourly": "precipitation",

        "past_days": 1,
        "forecast_days": 1,

        "timezone": "auto"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    result = response.json()

    current = result["current"]

    temperature = current["temperature_2m"]

    humidity = current["relative_humidity_2m"]

    soil_moisture = (
        current["soil_moisture_0_to_7cm"] * 100
    )

    precipitation = result["hourly"]["precipitation"]

    rainfall = sum(
        value
        for value in precipitation[-24:]
        if value is not None
    )

    elevation = result.get("elevation", 0)

    return {
        "temperature": temperature,
        "humidity": humidity,
        "soil_moisture": soil_moisture,
        "rainfall": rainfall,
        "elevation": elevation
    }


# =========================================================
# TITLE
# =========================================================

st.title(
    "🏔️ AI-Based Landslide Early Warning System"
)

st.write(
    "AI-powered system for monitoring environmental "
    "conditions and estimating landslide risk."
)

st.divider()


# =========================================================
# WORLDWIDE LOCATION SEARCH
# =========================================================

st.header("🌍 Worldwide Monitoring Location")

place = st.text_input(
    "🔎 Search for a place",
    placeholder="Example: Chennai, Tokyo, London..."
)


if place:

    try:

        locations = search_location(place)

        if len(locations) == 0:

            st.error(
                "❌ Location not found. Try another place."
            )

        else:

            location_names = []

            for item in locations:

                country = item.get("country", "")

                name = item.get("name", "")

                display_name = f"{name}, {country}"

                location_names.append(
                    display_name
                )

            selected = st.selectbox(
                "📍 Select Location",
                location_names
            )

            selected_index = location_names.index(
                selected
            )

            selected_location = locations[
                selected_index
            ]

            latitude = selected_location["latitude"]

            longitude = selected_location["longitude"]

            st.success(
                f"📍 Selected: {selected}"
            )

            st.write(
                f"Latitude: **{latitude:.4f}**"
            )

            st.write(
                f"Longitude: **{longitude:.4f}**"
            )


            # =================================================
            # GET LIVE ENVIRONMENT
            # =================================================

            environment = get_environmental_data(
                latitude,
                longitude
            )

            rainfall = environment["rainfall"]

            soil_moisture = environment[
                "soil_moisture"
            ]

            humidity = environment["humidity"]

            temperature = environment[
                "temperature"
            ]

            elevation = environment[
                "elevation"
            ]


            # =================================================
            # SLOPE
            # =================================================

            # Current dataset does not contain
            # location-specific slope data.
            # Therefore use dataset median as baseline.

            slope = data["Slope_Angle"].median()


            # =================================================
            # LIVE ENVIRONMENTAL DATA
            # =================================================

            st.divider()

            st.header(
                "🌦️ Live Environmental Conditions"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "🌧️ 24h Rainfall",
                    f"{rainfall:.1f} mm"
                )

            with col2:

                st.metric(
                    "💧 Soil Moisture",
                    f"{soil_moisture:.1f}%"
                )

            with col3:

                st.metric(
                    "💦 Humidity",
                    f"{humidity:.1f}%"
                )

            with col4:

                st.metric(
                    "🌡️ Temperature",
                    f"{temperature:.1f} °C"
                )


            st.write(
                f"🏔️ Elevation: "
                f"**{elevation:.1f} m**"
            )

            st.write(
                f"⛰️ Slope: "
                f"**{slope:.1f}°**"
            )

            st.caption(
                "ℹ️ Weather and soil-moisture values are "
                "retrieved automatically from live environmental data."
            )


            # =================================================
            # ANALYZE BUTTON
            # =================================================

            st.divider()

            if st.button(
                "🔍 ANALYZE LANDSLIDE RISK",
                use_container_width=True
            ):

                # ---------------------------------------------
                # Create input using dataset averages
                # ---------------------------------------------

                input_data = (
                    data[features]
                    .mean()
                    .to_frame()
                    .T
                )


                # ---------------------------------------------
                # Replace important environmental values
                # ---------------------------------------------

                input_data["Rainfall_mm"] = rainfall

                input_data["Slope_Angle"] = slope

                input_data[
                    "Soil_Moisture_Content"
                ] = soil_moisture

                input_data[
                    "Humidity_percent"
                ] = humidity

                input_data[
                    "Temperature_C"
                ] = temperature


                # ---------------------------------------------
                # AI Prediction
                # ---------------------------------------------

                prediction = model.predict(
                    input_data
                )[0]

                probability = (
                    model.predict_proba(
                        input_data
                    )[0][1] * 100
                )


                # =================================================
                # RISK ANALYSIS
                # =================================================

                st.divider()

                st.header(
                    "📊 Landslide Risk Analysis"
                )


                if probability < 30:

                    risk_level = "LOW"

                    st.success(
                        f"🟢 LOW RISK — "
                        f"{probability:.1f}%"
                    )

                elif probability < 60:

                    risk_level = "MODERATE"

                    st.warning(
                        f"🟡 MODERATE RISK — "
                        f"{probability:.1f}%"
                    )

                elif probability < 80:

                    risk_level = "HIGH"

                    st.warning(
                        f"🟠 HIGH RISK — "
                        f"{probability:.1f}%"
                    )

                else:

                    risk_level = "CRITICAL"

                    st.error(
                        f"🔴 CRITICAL RISK — "
                        f"{probability:.1f}%"
                    )


                # =================================================
                # RISK METRICS
                # =================================================

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "Risk Score",
                        f"{probability:.1f}%"
                    )

                with col2:

                    st.metric(
                        "Slope",
                        f"{slope:.1f}°"
                    )

                with col3:

                    st.metric(
                        "24h Rainfall",
                        f"{rainfall:.1f} mm"
                    )


                # =================================================
                # AI ASSESSMENT
                # =================================================

                st.subheader(
                    "🤖 AI Assessment"
                )

                if prediction == 1:

                    st.warning(
                        "⚠️ The AI model predicts a "
                        "possible landslide under the "
                        "current environmental conditions."
                    )

                else:

                    st.success(
                        "✅ The AI model predicts no "
                        "landslide under the current "
                        "environmental conditions."
                    )


                # =================================================
                # WHY THIS RISK?
                # =================================================

                st.subheader(
                    f"🧠 Why is the Risk {risk_level}?"
                )

                explanation_found = False


                if rainfall > 150:

                    st.write(
                        "🌧️ Heavy rainfall detected."
                    )

                    explanation_found = True


                if slope > 35:

                    st.write(
                        "⛰️ High slope angle detected."
                    )

                    explanation_found = True


                if soil_moisture > 70:

                    st.write(
                        "💧 High soil moisture detected."
                    )

                    explanation_found = True


                if humidity > 80:

                    st.write(
                        "💦 High humidity detected."
                    )

                    explanation_found = True


                if not explanation_found:

                    st.write(
                        "✅ Current environmental "
                        "conditions are within "
                        "relatively safer ranges."
                    )


                # =================================================
                # EARLY WARNING
                # =================================================

                if risk_level in [
                    "HIGH",
                    "CRITICAL"
                ]:

                    st.error(
                        "🚨 EARLY WARNING: High-risk "
                        "environmental conditions detected. "
                        "Further monitoring is recommended."
                    )


                # =================================================
                # WORLD MAP
                # =================================================

                st.subheader(
                    "🗺️ Monitoring Location"
                )

                map_data = pd.DataFrame({
                    "latitude": [latitude],
                    "longitude": [longitude]
                })

                st.map(
                    map_data,
                    zoom=5
                )

                st.caption(
                    f"📍 Monitoring: {selected}"
                )


    except Exception as e:

        st.error(
            f"❌ Unable to retrieve environmental data: {e}"
        )