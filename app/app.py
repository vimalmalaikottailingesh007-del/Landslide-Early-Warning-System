import streamlit as st
import pandas as pd
import joblib
import requests
import math
import folium
from streamlit_folium import st_folium
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Landslide Early Warning System",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# ADVANCED FRONTEND
# =========================================================

st.html("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 10% 0%,
            rgba(37, 104, 133, 0.20),
            transparent 28%
        ),
        radial-gradient(
            circle at 90% 5%,
            rgba(43, 111, 89, 0.13),
            transparent 25%
        ),
        #07131f;
    color: #f3f7fa;
}

.block-container {
    max-width: 1500px;
    padding-top: 1.1rem;
    padding-bottom: 2rem;
}

/* =====================================================
   HERO
   ===================================================== */

.hero {
    position: relative;
    height: 370px;
    overflow: hidden;
    border-radius: 28px;
    border: 1px solid rgba(130,170,190,.20);

    background:
        linear-gradient(
            180deg,
            rgba(6,18,29,.10),
            rgba(6,18,29,.92)
        ),
        linear-gradient(
            135deg,
            #173b50 0%,
            #0d2939 48%,
            #07141f 100%
        );

    box-shadow:
        0 30px 80px rgba(0,0,0,.32);

    animation: heroAppear .8s ease-out;
}

.hero-glow {
    position: absolute;
    width: 420px;
    height: 420px;
    right: -140px;
    top: -180px;
    border-radius: 50%;
    background: rgba(80,180,150,.09);
    filter: blur(20px);
}

.hero-content {
    position: relative;
    z-index: 10;
    height: 100%;

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    text-align: center;
}

.hero-icon {
    font-size: 58px;
    animation: floatMountain 3.5s ease-in-out infinite;
}

.hero-title {
    margin-top: 8px;
    font-size: 40px;
    font-weight: 800;
    letter-spacing: -1.2px;
}

.hero-subtitle {
    margin-top: 8px;
    color: #9eb1c0;
    font-size: 14px;
}

.live-status {
    display: inline-flex;
    align-items: center;
    gap: 9px;

    margin-top: 20px;
    padding: 8px 15px;

    border-radius: 30px;

    background: rgba(70,210,140,.07);
    border: 1px solid rgba(70,210,140,.25);

    color: #62dc9c;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .5px;
}

.live-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #52dc91;

    box-shadow:
        0 0 10px rgba(82,220,145,.8);

    animation: livePulse 1.5s infinite;
}

/* Mountains */

.mountain-back {
    position: absolute;
    bottom: -10px;
    left: -5%;
    width: 110%;
    height: 175px;

    background:
        linear-gradient(
            135deg,
            transparent 34%,
            rgba(38,75,83,.75) 34%,
            rgba(38,75,83,.75) 53%,
            transparent 53%
        );

    animation: mountainMove 9s ease-in-out infinite alternate;
}

.mountain-front {
    position: absolute;
    bottom: -45px;
    left: -10%;
    width: 120%;
    height: 155px;

    background:
        linear-gradient(
            150deg,
            transparent 38%,
            rgba(11,40,50,.98) 38%,
            rgba(11,40,50,.98) 59%,
            transparent 59%
        );

    animation: mountainMove2 11s ease-in-out infinite alternate;
}

/* =====================================================
   SECTIONS
   ===================================================== */

.section-title {
    margin-top: 27px;
    margin-bottom: 13px;

    font-size: 20px;
    font-weight: 800;
    color: #f4f7fa;
}

.section-subtitle {
    color: #748a9b;
    font-size: 11px;
    margin-top: -8px;
    margin-bottom: 13px;
}

/* =====================================================
   SEARCH
   ===================================================== */

.stTextInput input {
    height: 47px !important;

    background: #0b1c2a !important;
    color: #f3f7fa !important;

    border: 1px solid #29495d !important;
    border-radius: 13px !important;

    font-size: 14px !important;
}

.stTextInput input:focus {
    border-color: #4c8aa6 !important;
    box-shadow: 0 0 0 2px rgba(76,138,166,.12) !important;
}

.stButton button {
    height: 47px !important;

    border-radius: 13px !important;

    background:
        linear-gradient(
            135deg,
            #17475e,
            #123b50
        ) !important;

    color: white !important;

    border: 1px solid #2c617b !important;

    font-weight: 700 !important;

    transition: all .25s ease;
}

.stButton button:hover {
    transform: translateY(-2px);
    border-color: #4e8ba5 !important;
}

/* =====================================================
   LOCATION CARD
   ===================================================== */

.location-card {
    margin-top: 14px;

    padding: 15px 18px;

    border-radius: 16px;

    background:
        linear-gradient(
            135deg,
            rgba(16,39,55,.96),
            rgba(9,25,38,.96)
        );

    border: 1px solid rgba(100,150,175,.18);

    box-shadow:
        0 12px 30px rgba(0,0,0,.15);
}

.location-name {
    font-size: 15px;
    font-weight: 700;
}

.location-meta {
    margin-top: 5px;
    color: #7890a1;
    font-size: 11px;
}

/* =====================================================
   METRIC CARDS
   ===================================================== */

.metric-card {
    min-height: 125px;

    padding: 18px;

    border-radius: 18px;

    background:
        linear-gradient(
            145deg,
            #10283a,
            #091a28
        );

    border: 1px solid rgba(105,150,175,.17);

    transition:
        transform .25s ease,
        border-color .25s ease;

    animation: cardAppear .6s ease-out;
}

.metric-card:hover {
    transform: translateY(-4px);
    border-color: rgba(90,170,190,.42);
}

.metric-icon {
    font-size: 22px;
}

.metric-label {
    margin-top: 8px;

    color: #7e96a7;

    font-size: 11px;
    font-weight: 500;
}

.metric-value {
    margin-top: 3px;

    font-size: 23px;
    font-weight: 800;
}

/* =====================================================
   MAP CARD
   ===================================================== */

.map-card {
    padding: 8px;

    border-radius: 20px;

    background: #091a28;

    border: 1px solid rgba(100,150,175,.18);

    overflow: hidden;
}

/* =====================================================
   RISK PANEL
   ===================================================== */

.risk-card {
    min-height: 560px;

    padding: 28px;

    border-radius: 22px;

    background:
        linear-gradient(
            145deg,
            #112b3d,
            #091a28
        );

    border: 1px solid rgba(105,155,175,.19);

    box-shadow:
        0 20px 50px rgba(0,0,0,.20);

    animation: riskAppear .7s ease-out;
}

.risk-small {
    color: #7e96a7;

    font-size: 11px;
    font-weight: 700;

    letter-spacing: .7px;
}

.risk-level {
    margin-top: 13px;

    font-size: 38px;
    font-weight: 800;
}

.risk-prob {
    margin-top: 4px;

    color: #a5b6c2;

    font-size: 14px;
}

.progress-container {
    width: 100%;
    height: 9px;

    margin-top: 20px;

    overflow: hidden;

    border-radius: 20px;

    background: #1a3345;
}

.progress {
    height: 100%;

    border-radius: 20px;

    background:
        linear-gradient(
            90deg,
            #4caa91,
            #6bc49f
        );

    transition:
        width 1.2s ease;
}

.risk-message {
    margin-top: 22px;

    color: #a9b9c5;

    font-size: 13px;
    line-height: 1.7;
}

/* =====================================================
   RISK FACTORS
   ===================================================== */

.factor {
    margin-top: 11px;

    padding: 12px 13px;

    border-radius: 12px;

    background: rgba(7,20,31,.65);

    border: 1px solid rgba(100,140,160,.12);

    font-size: 12px;

    color: #bdcbd4;
}

.factor strong {
    color: #f0f5f7;
}

/* =====================================================
   WHY RISK
   ===================================================== */

.reason-card {
    padding: 21px;

    border-radius: 19px;

    background:
        linear-gradient(
            145deg,
            rgba(14,34,49,.96),
            rgba(8,22,34,.96)
        );

    border: 1px solid rgba(95,140,160,.17);
}

.reason-row {
    padding: 12px 0;

    border-bottom:
        1px solid rgba(110,140,160,.11);

    color: #b7c5ce;

    font-size: 12px;

    line-height: 1.6;
}

.reason-row:last-child {
    border-bottom: none;
}

/* =====================================================
   WARNING
   ===================================================== */

.warning-card {
    margin-top: 16px;

    padding: 17px 19px;

    border-radius: 17px;

    background:
        rgba(220,70,70,.07);

    border:
        1px solid rgba(220,90,90,.28);

    animation: warningPulse 2.2s infinite;
}

.warning-title {
    color: #f17b7b;

    font-size: 14px;
    font-weight: 800;
}

.warning-text {
    margin-top: 5px;

    color: #c0ccd4;

    font-size: 12px;

    line-height: 1.6;
}

/* =====================================================
   INFO PANEL
   ===================================================== */

.info-card {
    padding: 20px;

    border-radius: 18px;

    background: #0b1e2d;

    border: 1px solid rgba(100,145,165,.15);
}

.info-row {
    display: flex;
    justify-content: space-between;

    padding: 9px 0;

    border-bottom:
        1px solid rgba(100,140,160,.10);

    font-size: 12px;
}

.info-row:last-child {
    border-bottom: none;
}

.info-label {
    color: #728a9b;
}

.info-value {
    color: #d4dfe5;
    font-weight: 600;
}

/* =====================================================
   FOOTER
   ===================================================== */

.footer {
    padding-top: 35px;

    text-align: center;

    color: #607788;

    font-size: 10px;

    line-height: 1.7;
}

/* =====================================================
   ANIMATIONS
   ===================================================== */

@keyframes heroAppear {
    from {
        opacity: 0;
        transform: translateY(16px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes floatMountain {
    0%,100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-8px);
    }
}

@keyframes livePulse {
    0%,100% {
        transform: scale(.75);
        opacity: .55;
    }

    50% {
        transform: scale(1.2);
        opacity: 1;
    }
}

@keyframes mountainMove {
    from {
        transform: translateX(-15px);
    }

    to {
        transform: translateX(15px);
    }
}

@keyframes mountainMove2 {
    from {
        transform: translateX(12px);
    }

    to {
        transform: translateX(-12px);
    }
}

@keyframes cardAppear {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes riskAppear {
    from {
        opacity: 0;
        transform: scale(.97);
    }

    to {
        opacity: 1;
        transform: scale(1);
    }
}

@keyframes warningPulse {
    0%,100% {
        box-shadow: 0 0 0 rgba(220,70,70,0);
    }

    50% {
        box-shadow:
            0 0 22px rgba(220,70,70,.08);
    }
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""")

# =========================================================
# LOAD MODEL + DATASET
# =========================================================

@st.cache_resource
def load_model():
    return joblib.load("model/landslide_model.pkl")


@st.cache_data
def load_dataset():
    return pd.read_csv("dataset/wsn_landslide_data.csv")


model = load_model()
data = load_dataset()

features = [
    col for col in data.columns
    if col != "Label"
]

# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "latitude": 20.5937,
    "longitude": 78.9629,
    "location_name": "India",
    "country": "India",
    "state": ""
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# HERO
# =========================================================

st.html("""
<div class="hero">

    <div class="hero-glow"></div>

    <div class="mountain-back"></div>
    <div class="mountain-front"></div>

    <div class="hero-content">

        <div class="hero-icon">
            🏔️
        </div>

        <div class="hero-title">
            Landslide Early Warning System
        </div>

        <div class="hero-subtitle">
            AI-powered environmental and terrain monitoring
        </div>

        <div class="live-status">
            <span class="live-dot"></span>
            LIVE MONITORING
        </div>

    </div>

</div>
""")

# =========================================================
# LOCATION SEARCH
# =========================================================

st.markdown(
    '<div class="section-title">📍 Monitor a Location</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Search any city, district, state or region'
    '</div>',
    unsafe_allow_html=True
)

search_col, button_col = st.columns(
    [5, 1],
    gap="medium"
)

with search_col:

    search = st.text_input(
        "Location",
        placeholder="Enter city, district or state...",
        label_visibility="collapsed"
    )

with button_col:

    analyze = st.button(
        "Analyze",
        use_container_width=True
    )

# =========================================================
# GEOCODING
# =========================================================

def search_place(place):

    place = place.strip()

    if not place:
        return None

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

    # -----------------------------------------
    # SEARCH 1
    # -----------------------------------------

    results = open_meteo_search(place)

    if results:

        query = " ".join(
            place.lower().split()
        )

        # Exact name
        for item in results:

            if (
                str(item.get("name", ""))
                .lower()
                .strip()
                == query
            ):
                return item

        # Exact state
        for item in results:

            if (
                str(item.get("admin1", ""))
                .lower()
                .strip()
                == query
            ):
                return item

        # Exact district
        for item in results:

            if (
                str(item.get("admin2", ""))
                .lower()
                .strip()
                == query
            ):
                return item

        # Admin regions
        for item in results:

            feature = str(
                item.get("feature_code", "")
            ).upper()

            if feature in ["ADM1", "ADM2"]:
                return item

        return results[0]

    # -----------------------------------------
    # SEARCH 2 — INDIA
    # -----------------------------------------

    results = open_meteo_search(
        f"{place}, India",
        "IN"
    )

    if results:

        query = place.lower().strip()

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
                item.get("feature_code", "")
            ).upper()

            if feature in ["ADM1", "ADM2"]:
                return item

        return results[0]

    # -----------------------------------------
    # SEARCH 3 — NOMINATIM
    # -----------------------------------------

    try:

        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": place,
                "format": "jsonv2",
                "limit": 10,
                "addressdetails": 1
            },
            headers={
                "User-Agent":
                "Landslide-Early-Warning-System/1.0"
            },
            timeout=15
        )

        response.raise_for_status()

        results = response.json()

        if results:

            best = results[0]
            address = best.get(
                "address",
                {}
            )

            return {
                "name":
                    address.get("state")
                    or address.get("city")
                    or address.get("town")
                    or address.get("village")
                    or address.get("county")
                    or place,

                "latitude":
                    float(best["lat"]),

                "longitude":
                    float(best["lon"]),

                "country":
                    address.get(
                        "country",
                        ""
                    ),

                "admin1":
                    address.get(
                        "state",
                        ""
                    )
            }

    except Exception:
        pass

    return None

# =========================================================
# LOCATION UPDATE
# =========================================================

if analyze and search.strip():

    with st.spinner(
        "Locating and analyzing..."
    ):

        location = search_place(
            search
        )

        if location:

            st.session_state.latitude = float(
                location["latitude"]
            )

            st.session_state.longitude = float(
                location["longitude"]
            )

            st.session_state.location_name = (
                location.get("name")
                or search
            )

            st.session_state.country = (
                location.get("country")
                or ""
            )

            st.session_state.state = (
                location.get("admin1")
                or ""
            )

            st.success(
                "Location detected successfully."
            )

        else:

            st.error(
                "Location not found. "
                "Try a city, district or state name."
            )

latitude = st.session_state.latitude
longitude = st.session_state.longitude

# =========================================================
# ENVIRONMENT API
# =========================================================

def get_environmental_data(
    latitude,
    longitude
):

    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,

            "current":
                "temperature_2m,"
                "relative_humidity_2m,"
                "soil_moisture_0_to_7cm",

            "hourly":
                "precipitation",

            "past_days": 1,
            "forecast_days": 1,
            "timezone": "auto"
        },
        timeout=15
    )

    response.raise_for_status()

    result = response.json()

    current = result.get(
        "current",
        {}
    )

    temperature = (
        current.get(
            "temperature_2m"
        )
        or 0
    )

    humidity = (
        current.get(
            "relative_humidity_2m"
        )
        or 0
    )

    soil_raw = current.get(
        "soil_moisture_0_to_7cm"
    )

    if soil_raw is None:

        if "Soil_Moisture_Content" in data:

            soil_moisture = float(
                data[
                    "Soil_Moisture_Content"
                ].mean()
            )

        elif "Soil_Saturation" in data:

            soil_moisture = float(
                data[
                    "Soil_Saturation"
                ].mean()
            )

        else:

            soil_moisture = 0

    else:

        soil_moisture = (
            float(soil_raw) * 100
        )

    precipitation = result.get(
        "hourly",
        {}
    ).get(
        "precipitation",
        []
    )

    rainfall_values = precipitation[-24:]

    rainfall = sum(
        float(value)
        for value in rainfall_values
        if value is not None
    )

    return (
        temperature,
        humidity,
        soil_moisture,
        rainfall
    )

# =========================================================
# ELEVATION
# =========================================================

def get_elevation(
    latitude,
    longitude
):

    response = requests.get(
        "https://api.open-meteo.com/v1/elevation",
        params={
            "latitude": latitude,
            "longitude": longitude
        },
        timeout=15
    )

    response.raise_for_status()

    values = response.json().get(
        "elevation"
    )

    if not values:
        return 0

    return float(values[0])

# =========================================================
# SLOPE
# =========================================================

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
        2
        * offset
        * 111320
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
        return 0

    dz_dy = (
        north - south
    ) / lat_distance

    dz_dx = (
        east - west
    ) / lon_distance

    gradient = math.sqrt(
        dz_dx ** 2
        + dz_dy ** 2
    )

    slope = math.degrees(
        math.atan(gradient)
    )

    return max(
        0,
        min(90, slope)
    )

# =========================================================
# FETCH LIVE DATA
# =========================================================

try:

    (
        temperature,
        humidity,
        soil_moisture,
        rainfall
    ) = get_environmental_data(
        latitude,
        longitude
    )

    elevation = get_elevation(
        latitude,
        longitude
    )

    slope = calculate_slope(
        latitude,
        longitude
    )

except Exception:

    temperature = 0
    humidity = 0
    soil_moisture = 0
    rainfall = 0
    elevation = 0
    slope = 0

# =========================================================
# LOCATION INFO
# =========================================================

st.html(f"""
<div class="location-card">

    <div class="location-name">
        📍 {st.session_state.location_name}
    </div>

    <div class="location-meta">
        {st.session_state.state}
        &nbsp; • &nbsp;
        {st.session_state.country}
        &nbsp; • &nbsp;
        {latitude:.5f}, {longitude:.5f}
    </div>

</div>
""")

# =========================================================
# LIVE CONDITIONS
# =========================================================

st.markdown(
    '<div class="section-title">🌍 Live Conditions</div>',
    unsafe_allow_html=True
)

metrics = [
    (
        "🌧️",
        "Rainfall",
        f"{rainfall:.1f} mm"
    ),
    (
        "💧",
        "Soil Moisture",
        f"{soil_moisture:.1f}%"
    ),
    (
        "🌡️",
        "Temperature",
        f"{temperature:.1f} °C"
    ),
    (
        "💨",
        "Humidity",
        f"{humidity:.1f}%"
    ),
    (
        "⛰️",
        "Elevation",
        f"{elevation:.0f} m"
    ),
    (
        "📐",
        "Slope",
        f"{slope:.1f}°"
    )
]

metric_cols = st.columns(
    6,
    gap="small"
)

for col, metric in zip(
    metric_cols,
    metrics
):

    icon, label, value = metric

    with col:

        st.html(f"""
        <div class="metric-card">

            <div class="metric-icon">
                {icon}
            </div>

            <div class="metric-label">
                {label}
            </div>

            <div class="metric-value">
                {value}
            </div>

        </div>
        """)

# =========================================================
# MODEL INPUT
# =========================================================

input_data = (
    data[features]
    .mean()
    .to_frame()
    .T
)

if "Rainfall_mm" in input_data.columns:
    input_data["Rainfall_mm"] = rainfall

if "Slope_Angle" in input_data.columns:
    input_data["Slope_Angle"] = slope

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

if "Elevation_m" in input_data.columns:
    input_data[
        "Elevation_m"
    ] = elevation

# =========================================================
# AI PREDICTION
# =========================================================

prediction = model.predict(
    input_data
)[0]

try:

    probabilities = model.predict_proba(
        input_data
    )[0]

    classes = list(
        model.classes_
    )

    if 1 in classes:

        risk_probability = (
            probabilities[
                classes.index(1)
            ] * 100
        )

    else:

        risk_probability = (
            max(probabilities) * 100
        )

except Exception:

    risk_probability = (
        float(prediction) * 100
        if prediction in [0, 1]
        else 50
    )

risk_probability = max(
    0,
    min(
        100,
        float(risk_probability)
    )
)

# =========================================================
# RISK CLASSIFICATION
# =========================================================

if risk_probability < 30:

    risk = "LOW"
    risk_icon = "🟢"

    risk_message = (
        "Current environmental conditions "
        "indicate relatively low landslide risk."
    )

elif risk_probability < 60:

    risk = "MODERATE"
    risk_icon = "🟡"

    risk_message = (
        "Some environmental indicators require "
        "continued monitoring."
    )

elif risk_probability < 80:

    risk = "HIGH"
    risk_icon = "🟠"

    risk_message = (
        "Several conditions indicate elevated "
        "landslide susceptibility."
    )

else:

    risk = "CRITICAL"
    risk_icon = "🔴"

    risk_message = (
        "The current combination of indicators "
        "shows a very high estimated risk."
    )

# =========================================================
# MAP + AI RISK
# =========================================================

st.markdown(
    '<div class="section-title">🛰️ Risk Monitoring</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Interactive location and terrain monitoring'
    '</div>',
    unsafe_allow_html=True
)

map_col, risk_col = st.columns(
    [2.05, 1],
    gap="medium"
)

# =========================================================
# MAP
# =========================================================

with map_col:

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

    # Street
    folium.TileLayer(
        tiles="OpenStreetMap",
        name="🗺️ Street",
        attr="© OpenStreetMap contributors",
        control=True,
        no_wrap=True
    ).add_to(m)

    # Satellite
    folium.TileLayer(
        tiles=(
            "https://server.arcgisonline.com/"
            "ArcGIS/rest/services/"
            "World_Imagery/MapServer/"
            "tile/{z}/{y}/{x}"
        ),
        name="🛰️ Satellite",
        attr="© Esri",
        control=True,
        no_wrap=True
    ).add_to(m)

    # Terrain
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

    # Marker colour
    if risk == "LOW":
        marker_color = "green"

    elif risk == "MODERATE":
        marker_color = "orange"

    elif risk == "HIGH":
        marker_color = "orange"

    else:
        marker_color = "red"

    # Location marker
    folium.Marker(
        [
            latitude,
            longitude
        ],

        tooltip=(
            f"{st.session_state.location_name}"
            f" • {risk}"
        ),

        popup=f"""
        <b>{st.session_state.location_name}</b>
        <br><br>
        Risk: {risk}
        <br>
        Probability: {risk_probability:.1f}%
        <br>
        Rainfall: {rainfall:.1f} mm
        <br>
        Soil Moisture: {soil_moisture:.1f}%
        <br>
        Slope: {slope:.1f}°
        <br>
        Elevation: {elevation:.0f} m
        """,

        icon=folium.Icon(
            color=marker_color,
            icon="warning-sign"
        )

    ).add_to(m)

    # Monitoring radius
    folium.Circle(
        [
            latitude,
            longitude
        ],

        radius=5000,

        color="#58b99a",

        fill=True,

        fill_opacity=.07,

        popup="5 km monitoring zone"

    ).add_to(m)

    # Layer switch
    folium.LayerControl(
        position="topright",
        collapsed=False
    ).add_to(m)

    st.html(
        '<div class="map-card">'
    )

    st_folium(
        m,
        width=None,
        height=560,
        returned_objects=[]
    )

# =========================================================
# RISK PANEL
# =========================================================

with risk_col:

    st.html(f"""
    <div class="risk-card">

        <div class="risk-small">
            AI LANDSLIDE RISK ASSESSMENT
        </div>

        <div class="risk-level">
            {risk_icon} {risk}
        </div>

        <div class="risk-prob">
            Estimated probability:
            <b>{risk_probability:.1f}%</b>
        </div>

        <div class="progress-container">

            <div
                class="progress"
                style="width:{risk_probability}%">
            </div>

        </div>

        <div class="risk-message">
            {risk_message}
        </div>

        <div style="
            margin-top:25px;
            color:#71899a;
            font-size:11px;
            font-weight:700;
        ">
            KEY RISK INDICATORS
        </div>

        <div class="factor">
            🌧️ <strong>Rainfall</strong>
            <br>
            {rainfall:.1f} mm
        </div>

        <div class="factor">
            💧 <strong>Soil Moisture</strong>
            <br>
            {soil_moisture:.1f}%
        </div>

        <div class="factor">
            📐 <strong>Slope</strong>
            <br>
            {slope:.1f}°
        </div>

        <div class="factor">
            💨 <strong>Humidity</strong>
            <br>
            {humidity:.1f}%
        </div>

    </div>
    """)

# =========================================================
# WHY THIS RISK
# =========================================================

st.markdown(
    '<div class="section-title">🧠 Why This Risk?</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Environmental indicators influencing the current assessment'
    '</div>',
    unsafe_allow_html=True
)

reasons = []

# Rainfall
if rainfall > 150:

    reasons.append(
        f"""
        🌧️ <b>Heavy rainfall detected</b> —
        {rainfall:.1f} mm of rainfall was detected.
        High rainfall can increase water infiltration
        and reduce slope stability.
        """
    )

elif rainfall > 75:

    reasons.append(
        f"""
        🌧️ <b>Moderate rainfall detected</b> —
        {rainfall:.1f} mm recorded.
        Continued rainfall can increase ground
        saturation and slope instability.
        """
    )

else:

    reasons.append(
        f"""
        🌧️ <b>Rainfall condition</b> —
        {rainfall:.1f} mm recorded.
        Rainfall is currently not a major
        threshold-based warning factor.
        """
    )

# Slope
if slope > 35:

    reasons.append(
        f"""
        📐 <b>Steep terrain detected</b> —
        slope is approximately {slope:.1f}°.
        Steeper slopes generally have greater
        susceptibility to slope failure.
        """
    )

elif slope > 20:

    reasons.append(
        f"""
        📐 <b>Moderate terrain slope</b> —
        slope is approximately {slope:.1f}°.
        Terrain geometry contributes moderately
        to the estimated risk.
        """
    )

else:

    reasons.append(
        f"""
        📐 <b>Gentle terrain</b> —
        estimated slope is {slope:.1f}°.
        Slope is currently not a major
        threshold-based warning factor.
        """
    )

# Soil
if soil_moisture > 70:

    reasons.append(
        f"""
        💧 <b>High soil moisture</b> —
        {soil_moisture:.1f}% estimated soil moisture.
        Wet soil conditions can reduce
        effective soil stability.
        """
    )

elif soil_moisture > 45:

    reasons.append(
        f"""
        💧 <b>Moderate soil moisture</b> —
        {soil_moisture:.1f}% estimated.
        Moisture is present but below the
        high-moisture warning threshold.
        """
    )

else:

    reasons.append(
        f"""
        💧 <b>Lower soil moisture</b> —
        {soil_moisture:.1f}% estimated.
        No high-moisture warning is currently detected.
        """
    )

# Humidity
if humidity > 80:

    reasons.append(
        f"""
        💨 <b>High humidity</b> —
        relative humidity is {humidity:.1f}%.
        High atmospheric moisture can support
        persistent wet environmental conditions.
        """
    )

else:

    reasons.append(
        f"""
        💨 <b>Humidity condition</b> —
        relative humidity is {humidity:.1f}%.
        It is not currently a major
        threshold-based warning factor.
        """
    )

# AI
reasons.append(
    f"""
    🤖 <b>AI model assessment</b> —
    the trained model estimates an overall
    landslide risk probability of
    <b>{risk_probability:.1f}%</b>
    for the selected location.
    """
)

reason_html = ""

for reason in reasons:

    reason_html += f"""
    <div class="reason-row">
        {reason}
    </div>
    """

st.html(f"""
<div class="reason-card">

    {reason_html}

</div>
""")

# =========================================================
# EARLY WARNING
# =========================================================

if risk in ["HIGH", "CRITICAL"]:

    st.html(f"""
    <div class="warning-card">

        <div class="warning-title">
            🚨 {risk} RISK DETECTED
        </div>

        <div class="warning-text">
            Elevated landslide susceptibility has been
            estimated around
            <b>{st.session_state.location_name}</b>.
            Continuous monitoring and appropriate
            safety precautions are recommended.
        </div>

    </div>
    """)

elif risk == "MODERATE":

    st.html(f"""
    <div class="warning-card"
         style="
         background:rgba(220,170,60,.06);
         border-color:rgba(220,170,60,.25);
         animation:none;
         ">

        <div class="warning-title"
             style="color:#e0bd68;">
            ⚠️ MONITORING ADVISED
        </div>

        <div class="warning-text">
            Conditions are currently moderate.
            Continue monitoring environmental changes
            around <b>{st.session_state.location_name}</b>.
        </div>

    </div>
    """)

# =========================================================
# LOCATION ANALYSIS
# =========================================================

st.markdown(
    '<div class="section-title">📊 Location Analysis</div>',
    unsafe_allow_html=True
)

info_col1, info_col2 = st.columns(
    2,
    gap="medium"
)

with info_col1:

    st.html(f"""
    <div class="info-card">

        <div class="info-row">
            <span class="info-label">
                Location
            </span>

            <span class="info-value">
                {st.session_state.location_name}
            </span>
        </div>

        <div class="info-row">
            <span class="info-label">
                State / Region
            </span>

            <span class="info-value">
                {st.session_state.state or "—"}
            </span>
        </div>

        <div class="info-row">
            <span class="info-label">
                Country
            </span>

            <span class="info-value">
                {st.session_state.country or "—"}
            </span>
        </div>

        <div class="info-row">
            <span class="info-label">
                Latitude
            </span>

            <span class="info-value">
                {latitude:.5f}
            </span>
        </div>

        <div class="info-row">
            <span class="info-label">
                Longitude
            </span>

            <span class="info-value">
                {longitude:.5f}
            </span>
        </div>

    </div>
    """)

with info_col2:

    st.html(f"""
    <div class="info-card">

        <div class="info-row">
            <span class="info-label">
                Elevation
            </span>

            <span class="info-value">
                {elevation:.0f} m
            </span>
        </div>

        <div class="info-row">
            <span class="info-label">
                Terrain Slope
            </span>

            <span class="info-value">
                {slope:.1f}°
            </span>
        </div>

        <div class="info-row">
            <span class="info-label">
                Rainfall
            </span>

            <span class="info-value">
                {rainfall:.1f} mm
            </span>
        </div>

        <div class="info-row">
            <span class="info-label">
                Soil Moisture
            </span>

            <span class="info-value">
                {soil_moisture:.1f}%
            </span>
        </div>

        <div class="info-row">
            <span class="info-label">
                AI Risk
            </span>

            <span class="info-value">
                {risk_probability:.1f}%
            </span>
        </div>

    </div>
    """)

# =========================================================
# FOOTER
# =========================================================

timestamp = datetime.now().strftime(
    "%d %b %Y • %I:%M %p"
)

st.html(f"""
<div class="footer">

    Landslide Early Warning System
    &nbsp; • &nbsp;
    AI Environmental Monitoring

    <br>

    Last analysis:
    {timestamp}

    <br>

    Prototype risk assessment using
    environmental, weather and terrain indicators.

</div>
""")
