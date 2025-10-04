import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import date, timedelta
import math

# ===========================
# 🔧 CONFIGURATION GÉNÉRALE
# ===========================
st.set_page_config(page_title="🌍 Simulateur d'impact NEO & USGS", layout="wide")
st.title("🌍 Plateforme d’analyse et de simulation des risques d’impact d’astéroïdes")

# ✅ Clés API et URLs (intégrées directement ici)
API_KEY = "tAKnYtwhaIbRB9VZaDFQ1XypYfk0Q38FGdCcXmKr"  # <- Clé publique de la NASA, fonctionne sans compte
NASA_URL = "https://api.nasa.gov/neo/rest/v1/feed"
USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

# ===========================
# 📅 SÉLECTION DE LA PÉRIODE
# ===========================
st.sidebar.header("🗓 Période d’analyse")
start_date = st.sidebar.date_input("Date de début", date.today() - timedelta(days=1))
end_date = st.sidebar.date_input("Date de fin", date.today())

# ===========================
# 🚀 FONCTIONS UTILITAIRES
# ===========================
@st.cache_data
def get_neo_data(start_date, end_date):
    """Récupère les données des astéroïdes (NEO) depuis l’API NASA."""
    url = f"{NASA_URL}?start_date={start_date}&end_date={end_date}&api_key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        neos = []
        for date_key in data["near_earth_objects"]:
            for neo in data["near_earth_objects"][date_key]:
                neo_info = {
                    "nom": neo["name"],
                    "date": date_key,
                    "diametre_m": (neo["estimated_diameter"]["meters"]["estimated_diameter_min"] +
                                   neo["estimated_diameter"]["meters"]["estimated_diameter_max"]) / 2,
                    "vitesse_kmh": float(neo["close_approach_data"][0]["relative_velocity"]["kilometers_per_hour"]),
                    "distance_lune": float(neo["close_approach_data"][0]["miss_distance"]["lunar"]),
                    "danger_potentiel": neo["is_potentially_hazardous_asteroid"],
                    "magnitude": neo["absolute_magnitude_h"]
                }
                neos.append(neo_info)
        return pd.DataFrame(neos)
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données NEO : {e}")
        return pd.DataFrame()

@st.cache_data
def get_usgs_data():
    """Récupère les données sismiques depuis l’USGS."""
    try:
        response = requests.get(USGS_URL)
        response.raise_for_status()
        data = response.json()
        earthquakes = []
        for feature in data["features"]:
            prop = feature["properties"]
            coords = feature["geometry"]["coordinates"]
            earthquakes.append({
                "lieu": prop["place"],
                "magnitude": prop["mag"],
                "temps": pd.to_datetime(prop["time"], unit="ms"),
                "longitude": coords[0],
                "latitude": coords[1],
                "profondeur_km": coords[2]
            })
        return pd.DataFrame(earthquakes)
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données USGS : {e}")
        return pd.DataFrame()

def calculer_energie(diametre, vitesse):
    """Calcule l’énergie cinétique approximative d’un astéroïde (en kilotonnes de TNT)."""
    rayon = diametre / 2
    volume = (4 / 3) * math.pi * (rayon ** 3)
    masse = volume * 3000  # densité approximative en kg/m³
    vitesse_ms = vitesse * 1000 / 3600
    energie_joules = 0.5 * masse * (vitesse_ms ** 2)
    return energie_joules / 4.184e12  # Conversion Joules → kilotonnes TNT

# ===========================
# 📊 RÉCUPÉRATION DES DONNÉES
# ===========================
st.info("⏳ Chargement des données en cours...")
df_neo = get_neo_data(start_date, end_date)
df_usgs = get_usgs_data()

if not df_neo.empty:
    st.success(f"{len(df_neo)} astéroïdes récupérés depuis la NASA 🚀")
    df_neo["energie_kt"] = df_neo.apply(lambda x: calculer_energie(x["diametre_m"], x["vitesse_kmh"]), axis=1)
else:
    st.warning("Aucun NEO trouvé pour la période sélectionnée.")

if not df_usgs.empty:
    st.success(f"{len(df_usgs)} séismes récupérés depuis l’USGS 🌋")
else:
    st.warning("Aucune donnée USGS disponible.")

# ===========================
# 🌍 CARTE INTERACTIVE
# ===========================
st.subheader("🗺 Carte mondiale des risques")
world_map = folium.Map(location=[0, 0], zoom_start=2)

# Ajout des NEOs
for _, neo in df_neo.iterrows():
    folium.CircleMarker(
        location=[0, 0],  # Approximation (pas de coordonnée fournie)
        radius=5 + neo["energie_kt"] / 1000,
        color="red" if neo["danger_potentiel"] else "blue",
        popup=f"{neo['nom']}<br>Énergie: {neo['energie_kt']:.1f} kt<br>Distance: {neo['distance_lune']:.1f} Lune(s)"
    ).add_to(world_map)

# Ajout des séismes
for _, eq in df_usgs.iterrows():
    folium.CircleMarker(
        location=[eq["latitude"], eq["longitude"]],
        radius=eq["magnitude"] * 2,
        color="orange",
        popup=f"{eq['lieu']}<br>Magnitude: {eq['magnitude']}<br>Profondeur: {eq['profondeur_km']} km"
    ).add_to(world_map)

st_folium(world_map, width=1200, height=600)

# ===========================
# 📈 TABLEAUX ET GRAPHIQUES
# ===========================
st.subheader("📊 Données analytiques")

col1, col2 = st.columns(2)
with col1:
    st.write("*Astéroïdes détectés*")
    st.dataframe(df_neo)
with col2:
    st.write("*Activité sismique mondiale*")
    st.dataframe(df_usgs)

st.markdown("---")
st.caption("🛰 Données issues des API NASA NEO et USGS | Outil pédagogique et décisionnel pour la gestion mondiale des risques liés aux astéroïdes.")