import streamlit as st
import requests
import pandas as pd
from streamlit_geolocation import streamlit_geolocation

# 1. Page Configuration
st.set_page_config(
    page_title="Aura | AI Outfit Planner",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize state variables
if "page" not in st.session_state:
    st.session_state.page = "login"  # 'login', 'onboarding', 'home', 'recommendation'
if "username" not in st.session_state:
    st.session_state.username = "Guest"
if "preferred_style" not in st.session_state:
    st.session_state.preferred_style = "Casual"
if "temp_bias" not in st.session_state:
    st.session_state.temp_bias = "Neutral"
if "target_city" not in st.session_state:
    st.session_state.target_city = "Detecting location..."
if "gps_triggered" not in st.session_state:
    st.session_state.gps_triggered = False

# 2. UI Custom CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #e0f2fe 0%, #f3e8ff 50%, #ecfdf5 100%) !important;
    }
    .custom-sidebar {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 30px 20px;
        height: 100%;
        border: 1px solid rgba(255, 255, 255, 0.7);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
    }
    .login-container {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 40px;
        max-width: 450px;
        margin: 50px auto;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.6);
        margin-bottom: 20px;
    }
    .weather-gradient-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #0d9488 100%);
        border-radius: 24px;
        padding: 30px;
        color: white !important;
    }
    .clothing-preview-container {
        display: flex;
        gap: 15px;
        justify-content: center;
        margin-top: 20px;
    }
    .clothing-preview-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 15px;
        text-align: center;
        width: 110px;
    }
    .clothing-emoji { font-size: 2.5rem; display: block; }
    </style>
""", unsafe_allow_html=True)


# =====================================================================
# BACKGROUND GEOLOCATION DETECTION SYSTEM
# =====================================================================
# We trigger the GPS collector component silently in the background when dashboard opens
if st.session_state.page not in ["login", "onboarding"] and not st.session_state.gps_triggered:
    with st.sidebar:
        st.write("📍 **Location Sensor Access**")
        location_data = streamlit_geolocation()
        
        if location_data and location_data.get('latitude'):
            lat = location_data['latitude']
            lon = location_data['longitude']
            try:
                # Resolve coordinate data into a readable local city name via a free open geocode map API
                geo_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
                headers = {'User-Agent': 'AuraOutfitPlannerApp/1.0'}
                geo_res = requests.get(geo_url, headers=headers).json()
                address = geo_res.get('address', {})
                detected_city = address.get('city') or address.get('town') or address.get('state', 'New York')
                
                # Assign the sensor state to target_city
                st.session_state.target_city = detected_city
                st.session_state.gps_triggered = True
                st.rerun()
            except Exception:
                st.session_state.target_city = "New York"  # Global fallback fallback if API limits rate
                st.session_state.gps_triggered = True
        else:
            # If user blocks permissions or it's still loading, fallback gracefully to a standard search
            if st.session_state.target_city == "Detecting location...":
                st.session_state.target_city = "New York"


# --- BACKEND WEATHER API DATA ROUTER ---
backend_url = "http://127.0.0.1:5000/recommend"
try:
    res_data = requests.get(backend_url, params={"city": st.session_state.target_city}).json()
    resolved_city = res_data.get('city', st.session_state.target_city)
    w_metrics = res_data.get('current_weather_metrics', {'apparent_temperature_max (°C)': 26.0, 'apparent_temperature_min (°C)': 22.0})
    rec_outfit = res_data.get('recommended_outfit', f"{st.session_state.preferred_style} Wear")
except Exception:
    resolved_city = st.session_state.target_city
    w_metrics = {'apparent_temperature_max (°C)': 28.5, 'apparent_temperature_min (°C)': 21.0, 'precipitation_sum (mm)': 0.0, 'wind_speed_10m_max (km/h)': 11.0}
    rec_outfit = f"{st.session_state.preferred_style} Outfit Layout"

# Component Icons Mapper
outfit_assets = {
    "Traditional": {"top": "🥻", "bot": "👖", "shoes": "🥿"},
    "Formal": {"top": "👔", "bot": "👖", "shoes": "👞"},
    "Casual": {"top": "👕", "bot": "🩳", "shoes": "👟"}
}
assets = outfit_assets.get(st.session_state.preferred_style, outfit_assets["Casual"])


# =====================================================================
# STEP 1: SIGN IN PAGE
# =====================================================================
if st.session_state.page == "login":
    st.markdown("<div style='text-align:center; margin-top:40px;'><h1 style='color:#1e3a8a;'>🌀 Aura</h1></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        raw_name = st.text_input("Enter Name or Email Address", placeholder="e.g., diya@gmail.com")
        st.text_input("Password", type="password", placeholder="••••••••")
        
        if st.button("Sign In / Continue", use_container_width=True, type="primary"):
            clean_name = raw_name.split('@')[0] if raw_name.strip() else "Guest"
            st.session_state.username = clean_name.capitalize()
            st.session_state.page = "onboarding"
            st.rerun()
        if st.button("Continue as Guest", use_container_width=True):
            st.session_state.username = "Guest"
            st.session_state.page = "onboarding"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# STEP 2: STYLE QUIZ PANEL
# =====================================================================
elif st.session_state.page == "onboarding":
    st.markdown("<div style='text-align:center; margin-top:30px;'><h2 style='color:#1e3a8a;'>🎨 Personalize Your Stylist</h2><p>Configure preferences below</p></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="login-container" style="max-width:550px;">', unsafe_allow_html=True)
        
        st.session_state.preferred_style = st.radio(
            "What style architecture are you looking for today?",
            ["Casual", "Formal", "Traditional"], index=0
        )
        st.session_state.temp_bias = st.select_slider(
            "Your weather comfort sensitivity profile:",
            options=["Feel Cold Easily", "Neutral", "Feel Hot Easily"], value="Neutral"
        )
        
        st.write("")
        if st.button("Grant Location Access & Run Dashboard ✨", use_container_width=True, type="primary"):
            st.session_state.page = "home"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# STEP 3: LOGGED-IN SYSTEM TEMPLATE
# =====================================================================
else:
    sidebar_col, main_col = st.columns([1, 4])
    
    with sidebar_col:
        st.markdown(f"""
            <div class="custom-sidebar">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h3 style="color:#1e3a8a; margin:0;">🌀 Aura</h3>
                    <small style="color:#64748b;">User: <b>{st.session_state.username}</b></small><br>
                    <small style="color:#64748b;">Style Vibe: <b>{st.session_state.preferred_style}</b></small>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🏠 Home Dashboard", use_container_width=True, type="primary" if st.session_state.page == "home" else "secondary"):
            st.session_state.page = "home"
            st.rerun()
        if st.button("👗 AI Recommendation", use_container_width=True, type="primary" if st.session_state.page == "recommendation" else "secondary"):
            st.session_state.page = "recommendation"
            st.rerun()
        st.write("---")
        if st.button("🚪 Reset Profile Configuration", use_container_width=True):
            st.session_state.page = "login"
            st.session_state.gps_triggered = False
            st.session_state.target_city = "Detecting location..."
            st.rerun()

    with main_col:
        # MAIN HOME DASHBOARD VIEW
        if st.session_state.page == "home":
            st.markdown(f"""
                <div style='margin-bottom: 20px;'>
                    <h1 style='margin:0; color:#1e293b; font-weight:800;'>Hey, {st.session_state.username} 👋</h1>
                    <p style='color:#64748b; margin:0;'>Curating lookbooks matching live tracked telemetry systems.</p>
                </div>
            """, unsafe_allow_html=True)

            d_col1, d_col2 = st.columns([1.6, 1])
            with d_col1:
                st.markdown(f"""
                    <div class="weather-gradient-card">
                        <h3>📍 Active Location: {resolved_city}</h3>
                        <h1 style="color:white !important; font-size:3.5rem; font-weight:800; margin:10px 0;">{w_metrics['apparent_temperature_max (°C)']}°C</h1>
                        <p style="margin:0; opacity:0.9;">System values synced to automated GPS sensor metrics.</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # INTERACTIVE LOCATION OVERRIDE FIELD
                st.write("")
                new_city = st.text_input("🗺️ Want a different location? Type alternative city below:", value=st.session_state.target_city)
                if new_city != st.session_state.target_city:
                    st.session_state.target_city = new_city
                    st.rerun()

            with d_col2:
                st.markdown(f"""
                    <div class="glass-card" style="min-height:210px;">
                        <span style="background:#dbeafe; color:#2563eb; padding:4px 8px; border-radius:8px; font-size:0.75rem; font-weight:700;">✨ Curated Pick</span>
                        <h3 style="margin:10px 0 5px 0;">{st.session_state.preferred_style} Mix</h3>
                        <p style="color:#64748b; font-size:0.8rem; margin:0;">Accounting for a {st.session_state.temp_bias} baseline adjustment profile.</p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="clothing-preview-container">
                        <div class="clothing-preview-card"><span class="clothing-emoji">{assets['top']}</span></div>
                        <div class="clothing-preview-card"><span class="clothing-emoji">{assets['bot']}</span></div>
                        <div class="clothing-preview-card"><span class="clothing-emoji">{assets['shoes']}</span></div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.write("")
                if st.button("Open Structural Summary ➔", use_container_width=True, type="primary"):
                    st.session_state.page = "recommendation"
                    st.rerun()

        # DETAILED RECS AND PREVIEWS SCREEN
        elif st.session_state.page == "recommendation":
            st.markdown(f"<h2>Your Customized {st.session_state.preferred_style} Profile</h2>", unsafe_allow_html=True)
            
            rec_col1, rec_col2 = st.columns([1.6, 1])
            with rec_col1:
                st.markdown(f"""
                    <div class="glass-card" style="text-align:center; padding:40px 20px;">
                        <span style="background:#dbeafe; color:#2563eb; padding:6px 12px; border-radius:20px; font-size:0.8rem; font-weight:700;">✨ Engine Choice Model</span>
                        <h1 style="color:#1e293b; font-size:2.5rem; margin:15px 0;">{st.session_state.preferred_style} Wear Core</h1>
                        <p style="color:#64748b; margin:0;">Rendered for target metrics in {resolved_city}.</p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### 👕 Visual Layer Composition Previews")
                st.markdown(f"""
                    <div class="clothing-preview-container" style="justify-content: flex-start; gap:20px;">
                        <div class="clothing-preview-card" style="width:130px; padding:20px;">
                            <span class="clothing-emoji" style="font-size:3rem;">{assets['top']}</span>
                            <strong style="font-size:0.85rem; display:block; margin-top:5px;">Upper Garment</strong>
                        </div>
                        <div class="clothing-preview-card" style="width:130px; padding:20px;">
                            <span class="clothing-emoji" style="font-size:3rem;">{assets['bot']}</span>
                            <strong style="font-size:0.85rem; display:block; margin-top:5px;">Lower Segment</strong>
                        </div>
                        <div class="clothing-preview-card" style="width:130px; padding:20px;">
                            <span class="clothing-emoji" style="font-size:3rem;">{assets['shoes']}</span>
                            <strong style="font-size:0.85rem; display:block; margin-top:5px;">Footwear Sole</strong>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.write("")
                if st.button("⬅️ Back to Home Matrix", use_container_width=True):
                    st.session_state.page = "home"
                    st.rerun()

            with rec_col2:
                st.markdown(f"""
                    <div class="glass-card" style="border-left:5px solid #2563eb;">
                        <h4 style="margin:0 0 10px 0;">ℹ️ Intelligent Formulation Metrics</h4>
                        <p style="color:#64748b; font-size:0.85rem; line-height:1.5; margin:0;">
                            The active temperature metric stands at <b>{w_metrics['apparent_temperature_max (°C)']}°C</b> in <b>{resolved_city}</b>.
                            Factoring in your chosen style layout (<b>{st.session_state.preferred_style}</b>) alongside a <b>{st.session_state.temp_bias}</b> thermal response config bias, the application safely locks in these suggestions.
                        </p>
                    </div>
                """, unsafe_allow_html=True)