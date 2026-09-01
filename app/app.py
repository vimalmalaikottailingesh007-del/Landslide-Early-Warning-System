import streamlit as st
import pandas as pd
import joblib
import requests
import math
import folium
from streamlit_folium import st_folium


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Landslide Early Warning System",
    page_icon="🏔️",
    layout="wide"
)


# ============================================================
# LOAD MODEL + DATASET
# ============================================================

@st.cache_resource
def load_model():
    return joblib.load("model/landslide_model.pkl")


@st.cache_data
def load_dataset():
    return pd.read_csv("dataset/wsn_landslide_data.csv")


model = load_model()
data = load_dataset()

features = data.drop("Label", axis=1).columns.tolist()


# ============================================================
# SESSION STATE
# ============================================================

if "latitude" not in st.session_state:
    st.session_state.latitude = 20.5937

if "longitude" not in st.session_state:
    st.session_state.longitude = 78.9629

if "location_name" not in st.session_state:
    st.session_state.location_name = "India"

if "country" not in st.session_state:
    st.session_state.country = "India"

if "state" not in st.session_state:
    st.session_state.state = ""


# ============================================================
# WORLDWIDE LOCATION SEARCH
# ============================================================

def search_place(place):

    place = place.strip()

    if not place:
        return None

    # --------------------------------------------------------
    # OPEN-METEO SEARCH
    # --------------------------------------------------------

    open_meteo_url = (
        "https://geocoding-api.open-meteo.com/v1/search"
    )

    def open_meteo_search(
        search_text,
        country_code=None
    ):

        params = {
            "name": search_text,
            "count": 100,
            "language": "en",
            "format": "json"
        }

        if country_code:
            params["countryCode"] = country_code

        try:

            response = requests.get(
                open_meteo_url,
                params=params,
                timeout=15
            )

            response.raise_for_status()

            return response.json().get(
                "results",
                []
            )

        except Exception:

            return []

    # --------------------------------------------------------
    # NORMAL WORLDWIDE SEARCH
    # --------------------------------------------------------

    results = open_meteo_search(place)

    if results:

        query = " ".join(
            place.lower().split()
        )

        # Exact name
        for item in results:

            name = str(
                item.get("name", "")
            ).lower().strip()

            if name == query:
                return item

        # Exact state / province / region
        for item in results:

            admin1 = str(
                item.get("admin1", "")
            ).lower().strip()

            if admin1 == query:
                return item

        # Exact second-level administrative region
        for item in results:

            admin2 = str(
                item.get("admin2", "")
            ).lower().strip()

            if admin2 == query:
                return item

        # Prefer administrative regions
        for item in results:

            feature = str(
                item.get(
                    "feature_code",
                    ""
                )
            ).upper()

            if feature in [
                "ADM1",
                "ADM2"
            ]:
                return item

        return results[0]

    # --------------------------------------------------------
    # INDIA RETRY
    # --------------------------------------------------------
    # This is dynamic.
    # No state/place list is hard-coded.
    # --------------------------------------------------------

    results = open_meteo_search(
        f"{place}, India",
        "IN"
    )

    if results:

        query = " ".join(
            place.lower().split()
        )

        for item in results:

            name = str(
                item.get("name", "")
            ).lower().strip()

            admin1 = str(
                item.get("admin1", "")
            ).lower().strip()

            admin2 = str(
                item.get("admin2", "")
            ).lower().strip()

            if (
                name == query
                or admin1 == query
                or admin2 == query
            ):
                return item

        for item in results:

            feature = str(
                item.get(
                    "feature_code",
                    ""
                )
            ).upper()

            if feature in [
                "ADM1",
                "ADM2"
            ]:
                return item

        return results[0]

    # --------------------------------------------------------
    # NOMINATIM / OPENSTREETMAP FALLBACK
    # --------------------------------------------------------

    nominatim_url = (
        "https://nominatim.openstreetmap.org/search"
    )

    nominatim_params = {
        "q": place,
        "format": "jsonv2",
        "limit": 10,
        "addressdetails": 1
    }

    headers = {
        "User-Agent":
        "Landslide-Early-Warning-System/1.0"
    }

    try:

        response = requests.get(
            nominatim_url,
            params=nominatim_params,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        results = response.json()

        if results:

            # Try to find exact display/name match first
            query = place.lower().strip()

            for result in results:

                display_name = str(
                    result.get(
                        "display_name",
                        ""
                    )
                ).lower()

                if query in display_name:

                    best = result
                    break

            else:

                best = results[0]

            address = best.get(
                "address",
                {}
            )

            return {
                "name": (
                    address.get("state")
                    or address.get("city")
                    or address.get("town")
                    or address.get("village")
                    or address.get("county")
                    or place
                ),

                "latitude": float(
                    best["lat"]
                ),

                "longitude": float(
                    best["lon"]
                ),

                "country": address.get(
                    "country",
                    ""
                ),

                "admin1": address.get(
                    "state",
                    ""
                ),

                "country_code": address.get(
                    "country_code",
                    ""
                ).upper()
            }

    except Exception:

        pass

    return None


# ============================================================
# ENVIRONMENTAL DATA
# ============================================================

def get_environmental_data(
    latitude,
    longitude
):

    url = (
        "https://api.open-meteo.com/v1/forecast"
    )

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
        timeout=15
    )

    response.raise_for_status()

    result = response.json()

    current = result.get(
        "current",
        {}
    )

    temperature = current.get(
        "temperature_2m"
    )

    if temperature is None:
        temperature = 0.0

    humidity = current.get(
        "relative_humidity_2m"
    )

    if humidity is None:
        humidity = 0.0

    soil_moisture_raw = current.get(
        "soil_moisture_0_to_7cm"
    )

    if soil_moisture_raw is None:

        if "Soil_Moisture_Content" in data.columns:

            soil_moisture = float(
                data[
                    "Soil_Moisture_Content"
                ].mean()
            )

        elif "Soil_Saturation" in data.columns:

            soil_moisture = float(
                data[
                    "Soil_Saturation"
                ].mean()
            )

        else:

            soil_moisture = 0.0

    else:

        soil_moisture = (
            float(soil_moisture_raw) * 100
        )

    precipitation = (
        result
        .get("hourly", {})
        .get("precipitation", [])
    )

    rainfall_values = precipitation[-24:]

    rainfall = sum(
        float(value)
        for value in rainfall_values
        if value is not None
    )

    return {
        "temperature": temperature,
        "humidity": humidity,
        "rainfall": rainfall,
        "soil_moisture": soil_moisture
    }


# ============================================================
# ELEVATION
# ============================================================

def get_elevation(
    latitude,
    longitude
):

    url = (
        "https://api.open-meteo.com/v1/elevation"
    )

    params = {
        "latitude": latitude,
        "longitude": longitude
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    result = response.json()

    elevation = result.get(
        "elevation"
    )

    if not elevation:
        return 0.0

    return float(elevation[0])


# ============================================================
# SLOPE
# ============================================================

def calculate_slope(
    latitude,
    longitude
):

    offset = 0.002

    north = get_elevation(
        latitude + offset,
        longitude
    )

    south = get_elevation(
        latitude - offset,
        longitude
    )

    east = get_elevation(
        latitude,
        longitude + offset
    )

    west = get_elevation(
        latitude,
        longitude - offset
    )

    lat_distance = (
        2 * offset * 111320
    )

    lon_distance = (
        2
        * offset
        * 111320
        * math.cos(
            math.radians(latitude)
        )
    )

    if lon_distance == 0:
        return 0.0

    dz_dy = (
        (north - south)
        / lat_distance
    )

    dz_dx = (
        (east - west)
        / lon_distance
    )

    gradient = math.sqrt(
        dz_dx ** 2 +
        dz_dy ** 2
    )

    slope = math.degrees(
        math.atan(gradient)
    )

    return max(
        0.0,
        min(90.0, slope)
    )


# ============================================================
# TITLE
# ============================================================

st.title(
    "🏔️ AI-Based Landslide Early Warning System"
)

st.write(
    "AI-powered system for monitoring environmental "
    "conditions and estimating landslide risk."
)

st.divider()


# ============================================================
# LOCATION SEARCH UI
# ============================================================

st.header(
    "🌍 Worldwide Monitoring Location"
)

col1, col2 = st.columns([5, 1])

with col1:

    place = st.text_input(
        "🔎 Search any place in the world",
        placeholder=(
            "Example: Himachal Pradesh, "
            "Gujarat, Uttar Pradesh, Nepal, Tokyo..."
        )
    )

with col2:

    st.write("")

    search_clicked = st.button(
        "📍 FIND",
        use_container_width=True
    )


# ============================================================
# SEARCH ACTION
# ============================================================

if search_clicked:

    if not place.strip():

        st.warning(
            "Please enter a place name."
        )

    else:

        with st.spinner(
            "🔎 Finding location..."
        ):

            try:

                result = search_place(
                    place.strip()
                )

                if result is None:

                    st.error(
                        "❌ Location not found. "
                        "Try another place."
                    )

                else:

                    st.session_state.latitude = float(
                        result["latitude"]
                    )

                    st.session_state.longitude = float(
                        result["longitude"]
                    )

                    st.session_state.location_name = (
                        result.get(
                            "name",
                            place
                        )
                    )

                    st.session_state.country = (
                        result.get(
                            "country",
                            ""
                        )
                    )

                    st.session_state.state = (
                        result.get(
                            "admin1",
                            ""
                        )
                    )

                    st.success(
                        "✅ Location selected successfully."
                    )

            except Exception as e:

                st.error(
                    f"❌ Location search error: {e}"
                )


# ============================================================
# SELECTED LOCATION
# ============================================================

latitude = st.session_state.latitude
longitude = st.session_state.longitude

location_name = (
    st.session_state.location_name
)

country = (
    st.session_state.country
)

state = (
    st.session_state.state
)


if state:

    st.write(
        f"📍 Selected Location: "
        f"**{location_name}, {state}, {country}**"
    )

else:

    st.write(
        f"📍 Selected Location: "
        f"**{location_name}, {country}**"
    )


st.write(
    f"🌐 Coordinates: "
    f"**{latitude:.4f}, {longitude:.4f}**"
)


# ============================================================
# GET LIVE ENVIRONMENT
# ============================================================

try:

    environment = get_environmental_data(
        latitude,
        longitude
    )

    rainfall = environment[
        "rainfall"
    ]

    soil_moisture = environment[
        "soil_moisture"
    ]

    humidity = environment[
        "humidity"
    ]

    temperature = environment[
        "temperature"
    ]

except Exception as e:

    st.error(
        f"Environmental data error: {e}"
    )

    st.stop()


# ============================================================
# SLOPE
# ============================================================

try:

    slope = calculate_slope(
        latitude,
        longitude
    )

except Exception:

    if "Slope_Angle" in data.columns:

        slope = float(
            data["Slope_Angle"].mean()
        )

    else:

        slope = 0.0


# ============================================================
# LIVE ENVIRONMENTAL DATA
# ============================================================

st.subheader(
    "🌦️ Live Environmental Data"
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "🌧️ Rainfall",
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
    f"⛰️ Terrain Slope: "
    f"**{slope:.1f}°**"
)

st.divider()


# ============================================================
# ENVIRONMENTAL CONDITIONS
# ============================================================

st.header(
    "🌧️ Environmental Conditions"
)

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "🌧️ 24h Rainfall",
        f"{rainfall:.1f} mm"
    )

    st.metric(
        "⛰️ Terrain Slope",
        f"{slope:.1f}°"
    )

    st.metric(
        "💧 Soil Moisture",
        f"{soil_moisture:.1f}%"
    )

with col2:

    st.metric(
        "💦 Humidity",
        f"{humidity:.1f}%"
    )

    st.metric(
        "🌡️ Temperature",
        f"{temperature:.1f} °C"
    )


st.divider()


# ============================================================
# ANALYZE LANDSLIDE RISK
# ============================================================

analyze_clicked = st.button(
    "🔍 ANALYZE LANDSLIDE RISK",
    use_container_width=True
)


if analyze_clicked:

    input_data = (
        data[features]
        .mean()
        .to_frame()
        .T
    )

    if "Rainfall_mm" in input_data.columns:

        input_data[
            "Rainfall_mm"
        ] = rainfall

    if "Slope_Angle" in input_data.columns:

        input_data[
            "Slope_Angle"
        ] = slope

    if "Soil_Moisture_Content" in input_data.columns:

        input_data[
            "Soil_Moisture_Content"
        ] = soil_moisture

    if "Soil_Saturation" in input_data.columns:

        input_data[
            "Soil_Saturation"
        ] = soil_moisture

    if "Humidity_percent" in input_data.columns:

        input_data[
            "Humidity_percent"
        ] = humidity

    if "Temperature_C" in input_data.columns:

        input_data[
            "Temperature_C"
        ] = temperature

    # ========================================================
    # AI PREDICTION
    # ========================================================

    try:

        prediction = model.predict(
            input_data
        )[0]

        probability = (
            model.predict_proba(
                input_data
            )[0][1] * 100
        )

    except Exception as e:

        st.error(
            f"❌ Model prediction error: {e}"
        )

        st.stop()

    probability = max(
        0.0,
        min(100.0, probability)
    )

    # ========================================================
    # RISK LEVEL
    # ========================================================

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

    # ========================================================
    # RISK METRICS
    # ========================================================

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Risk Score",
            f"{probability:.1f}%"
        )

    with col2:

        st.metric(
            "Terrain Slope",
            f"{slope:.1f}°"
        )

    with col3:

        st.metric(
            "24h Rainfall",
            f"{rainfall:.1f} mm"
        )

    # ========================================================
    # AI ASSESSMENT
    # ========================================================

    st.subheader(
        "🤖 AI Assessment"
    )

    if prediction == 1:

        st.warning(
            "⚠️ The AI model predicts a possible "
            "landslide under the current "
            "environmental conditions."
        )

    else:

        st.success(
            "✅ The AI model predicts no landslide "
            "under the current environmental conditions."
        )

    # ========================================================
    # RISK EXPLANATION
    # ========================================================

    st.subheader(
        f"🧠 Why is the Risk {risk_level}?"
    )

    reasons = []

    if rainfall > 150:

        reasons.append(
            "🌧️ Heavy rainfall detected."
        )

    elif rainfall > 75:

        reasons.append(
            "🌧️ Significant rainfall detected."
        )

    if slope > 35:

        reasons.append(
            "⛰️ High terrain slope detected."
        )

    elif slope > 20:

        reasons.append(
            "⛰️ Moderately steep terrain detected."
        )

    if soil_moisture > 70:

        reasons.append(
            "💧 High soil moisture detected."
        )

    if humidity > 80:

        reasons.append(
            "💦 High humidity detected."
        )

    if reasons:

        for reason in reasons:

            st.write(reason)

    else:

        st.write(
            "✅ No individual environmental "
            "factor crossed the configured "
            "warning threshold."
        )

    # ========================================================
    # EARLY WARNING
    # ========================================================

    if risk_level in [
        "HIGH",
        "CRITICAL"
    ]:

        st.error(
            "🚨 EARLY WARNING: High-risk "
            "environmental conditions detected. "
            "Further monitoring is recommended."
        )

    # ========================================================
    # INTERACTIVE MAP
    # ========================================================

    st.divider()

    st.subheader(
        "🗺️ Interactive Worldwide Map"
    )

    st.write(
        "🖱️ Drag, zoom and explore the world map."
    )

    # ========================================================
    # CREATE MAP
    # ========================================================

    m = folium.Map(
        location=[
            latitude,
            longitude
        ],
        zoom_start=6,
        min_zoom=2,
        max_zoom=18,
        control_scale=True,
        tiles=None,
        world_copy_jump=False
    )

    # ========================================================
    # STREET MAP
    # ========================================================

    folium.TileLayer(
        tiles="OpenStreetMap",
        name="🗺️ Street Map",
        attr="© OpenStreetMap contributors",
        control=True,
        no_wrap=True
    ).add_to(m)

    # ========================================================
    # SATELLITE MAP
    # ========================================================

    folium.TileLayer(
        tiles=(
            "https://server.arcgisonline.com/"
            "ArcGIS/rest/services/"
            "World_Imagery/MapServer/tile/"
            "{z}/{y}/{x}"
        ),
        name="🛰️ Satellite",
        attr="© Esri",
        control=True,
        no_wrap=True
    ).add_to(m)

    # ========================================================
    # TERRAIN MAP
    # ========================================================

    folium.TileLayer(
        tiles=(
            "https://{s}.tile.opentopomap.org/"
            "{z}/{x}/{y}.png"
        ),
        name="⛰️ Terrain",
        attr="© OpenTopoMap contributors",
        control=True,
        no_wrap=True
    ).add_to(m)

    # ========================================================
    # MARKER COLOR
    # ========================================================

    if risk_level == "LOW":

        marker_color = "green"

    elif risk_level == "MODERATE":

        marker_color = "orange"

    elif risk_level == "HIGH":

        marker_color = "red"

    else:

        marker_color = "darkred"

    # ========================================================
    # POPUP LOCATION TEXT
    # ========================================================

    if state:

        popup_location = (
            f"{location_name}, "
            f"{state}, "
            f"{country}"
        )

    else:

        popup_location = (
            f"{location_name}, "
            f"{country}"
        )

    # ========================================================
    # POPUP
    # ========================================================

    popup_html = f"""
    <div style="width:260px">

        <h4>📍 {popup_location}</h4>

        🌐 <b>Latitude:</b> {latitude:.4f}<br>
        🌐 <b>Longitude:</b> {longitude:.4f}<br><br>

        🌧️ <b>Rainfall:</b> {rainfall:.1f} mm<br>
        💧 <b>Soil Moisture:</b> {soil_moisture:.1f}%<br>
        💦 <b>Humidity:</b> {humidity:.1f}%<br>
        🌡️ <b>Temperature:</b> {temperature:.1f} °C<br>
        ⛰️ <b>Slope:</b> {slope:.1f}°<br><br>

        🚨 <b>Risk:</b> {risk_level}<br>
        📊 <b>Risk Score:</b> {probability:.1f}%

    </div>
    """

    # ========================================================
    # LOCATION MARKER
    # ========================================================

    folium.Marker(
        [
            latitude,
            longitude
        ],
        tooltip=(
            f"📍 {location_name} — "
            f"{risk_level}"
        ),
        popup=folium.Popup(
            popup_html,
            max_width=320
        ),
        icon=folium.Icon(
            color=marker_color,
            icon="warning-sign"
        )
    ).add_to(m)

    # ========================================================
    # 5 KM MONITORING AREA
    # ========================================================

    folium.Circle(
        location=[
            latitude,
            longitude
        ],
        radius=5000,
        color=marker_color,
        fill=True,
        fill_opacity=0.12,
        popup="5 km Monitoring Area"
    ).add_to(m)

    # ========================================================
    # MAP MODE SWITCH
    # ========================================================

    folium.LayerControl(
        position="topright",
        collapsed=False
    ).add_to(m)

    # ========================================================
    # DISPLAY MAP
    # ========================================================

    st_folium(
        m,
        width=None,
        height=600,
        returned_objects=[]
    )

    # ========================================================
    # COORDINATES
    # ========================================================

    st.caption(
        f"📍 Monitoring coordinates: "
        f"{latitude:.4f}, {longitude:.4f}"
    )
