import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import ssl
import streamlit as st
import plotly.express as px
import pandas as pd
from google import genai

# --- CONFIGURATION SÉCURITÉ & IA ---
ssl._create_default_https_context = ssl._create_unverified_context
CLE_API = "AIzaSyBOf1mMO6Rps_JVfR04ADCY3lgTcZG9kgY"
client = genai.Client(api_key=CLE_API)

# --- 1. PARAMÈTRES DE LA PAGE ---
st.set_page_config(page_title="Radar IA | Pro", page_icon="🌍", layout="wide", initial_sidebar_state="expanded")

# --- 2. LE MENU LATÉRAL (SIDEBAR) ---
with st.sidebar:
    st.title("⚙️ Centre de Contrôle")
    st.markdown("Paramétrez votre radar géopolitique.")
    st.markdown("---")
    
    # La liste mondiale complète (196 zones stratégiques)
    liste_pays = [
        "Afghanistan", "Afrique du Sud", "Albanie", "Algérie", "Allemagne", "Andorre", "Angola",
        "Antigua-et-Barbuda", "Arabie saoudite", "Argentine", "Arménie", "Australie", "Autriche",
        "Azerbaïdjan", "Bahamas", "Bahreïn", "Bangladesh", "Barbade", "Belgique", "Belize", "Bénin",
        "Bhoutan", "Biélorussie", "Birmanie", "Bolivie", "Bosnie-Herzégovine", "Botswana", "Brésil",
        "Brunei", "Bulgarie", "Burkina Faso", "Burundi", "Cambodge", "Cameroun", "Canada", "Cap-Vert",
        "Centrafrique", "Chili", "Chine", "Chypre", "Colombie", "Comores", "Congo",
        "République démocratique du Congo", "Corée du Nord", "Corée du Sud", "Costa Rica",
        "Côte d'Ivoire", "Croatie", "Cuba", "Danemark", "Djibouti", "Dominique", "Égypte",
        "Émirats arabes unis", "Équateur", "Érythrée", "Espagne", "Estonie", "Eswatini",
        "États-Unis", "Éthiopie", "Fidji", "Finlande", "France", "Gabon", "Gambie", "Géorgie",
        "Ghana", "Grèce", "Grenade", "Guatemala", "Guinée", "Guinée-Bissau", "Guinée équatoriale",
        "Guyana", "Haïti", "Honduras", "Hongrie", "Îles Marshall", "Îles Salomon", "Inde",
        "Indonésie", "Irak", "Iran", "Irlande", "Islande", "Israël", "Italie", "Jamaïque", "Japon",
        "Jordanie", "Kazakhstan", "Kenya", "Kirghizistan", "Kiribati", "Koweït", "Laos", "Lesotho",
        "Lettonie", "Liban", "Liberia", "Libye", "Liechtenstein", "Lituanie", "Luxembourg",
        "Macédoine du Nord", "Madagascar", "Malaisie", "Malawi", "Maldives", "Mali", "Malte",
        "Maroc", "Maurice", "Mauritanie", "Mexique", "Micronésie", "Moldavie", "Monaco", "Mongolie",
        "Monténégro", "Mozambique", "Namibie", "Nauru", "Népal", "Nicaragua", "Niger", "Nigéria",
        "Norvège", "Nouvelle-Zélande", "Oman", "Ouganda", "Ouzbékistan", "Pakistan", "Palaos",
        "Panama", "Papouasie-Nouvelle-Guinée", "Paraguay", "Pays-Bas", "Pérou", "Philippines",
        "Pologne", "Portugal", "Qatar", "Roumanie", "Royaume-Uni", "Russie", "Rwanda",
        "Saint-Kitts-et-Nevis", "Saint-Marin", "Saint-Vincent-et-les-Grenadines", "Sainte-Lucie",
        "Salvador", "Samoa", "São Tomé-et-Principe", "Sénégal", "Serbie", "Seychelles",
        "Sierra Leone", "Singapour", "Slovaquie", "Slovénie", "Somalie", "Soudan", "Soudan du Sud",
        "Sri Lanka", "Suède", "Suisse", "Suriname", "Syrie", "Tadjikistan", "Taïwan", "Tanzanie",
        "Tchad", "Tchéquie", "Thaïlande", "Timor oriental", "Togo", "Tonga", "Trinité-et-Tobago",
        "Tunisie", "Turkménistan", "Turquie", "Tuvalu", "Ukraine", "Uruguay", "Vanuatu", "Vatican",
        "Venezuela", "Vietnam", "Yémen", "Zambie", "Zimbabwe"
    ]
    pays_choisi = st.selectbox("Cible Stratégique :", sorted(liste_pays))
    
    st.markdown("---")
    lancer_analyse = st.button("🚀 DÉPLOYER L'IA", use_container_width=True, type="primary")

# --- 3. L'INTERFACE PRINCIPALE (MAIN) ---
st.title("Tableau de Bord Stratégique")
st.markdown("Surveillance des flux économiques mondiaux en temps réel.")

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
col_kpi1.metric(label="Statut du Radar", value="En ligne", delta="Sécurisé")
col_kpi2.metric(label="Zone Ciblée", value=pays_choisi)
col_kpi3.metric(label="Moteur Analytique", value="Gemini 2.5", delta="Ultra-rapide")

st.markdown("---")

col_carte, col_donnees = st.columns([1.5, 1])

with col_carte:
    df = pd.DataFrame({"Pays": liste_pays})
    fig = px.choropleth(df, locations="Pays", locationmode="country names", color_discrete_sequence=['#4F8BF9'], projection="orthographic")
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0}, 
        geo=dict(showcoastlines=True, coastlinecolor="rgba(255,255,255,0.2)", projection_type='orthographic', bgcolor='rgba(0,0,0,0)'),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)

with col_donnees:
    st.subheader("Signaux Faibles & Alertes")
    
    if lancer_analyse:
        mot_cle = urllib.parse.quote(f"géopolitique économie {pays_choisi}")
        url_dynamique = f"https://news.google.com/rss/search?q={mot_cle}&hl=fr&gl=FR&ceid=FR:fr"
        
        with st.spinner(f"Acquisition des données pour {pays_choisi}..."):
            try:
                request = urllib.request.Request(url_dynamique, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(request, timeout=10) as response:
                    data = response.read()
                
                root = ET.fromstring(data)
                items = root.findall('.//item')[:3]
                
                if not items:
                    st.warning(f"Aucune actualité géopolitique économique majeure détectée pour {pays_choisi} aujourd'hui.")
                else:
                    st.success("✅ Données traitées avec succès.")
                    
                    for item in items:
                        title = item.findtext('title')
                        titre_court = title[:60] + "..." if len(title) > 60 else title
                        
                        with st.expander(f"📰 {titre_court}"):
                            st.markdown(f"**Source originale :** {title}")
                            
                            prompt = f"Tu es analyste en risque géopolitique. Résume l'impact direct de cette annonce concernant {pays_choisi} sur le commerce international et les entreprises en 2 phrases claires : {title}"
                            reponse = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                            
                            st.info(f"**Synthèse IA :**\n\n{reponse.text}")
                        
            except Exception as e:
                st.error(f"Erreur de flux : {e}")
    else:
        st.info("👈 Sélectionnez un pays dans le menu latéral et cliquez sur 'Déployer l'IA' pour lancer le scan.")