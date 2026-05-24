import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import ssl
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from google import genai
from fpdf import FPDF
import re
from datetime import datetime

# --- CONFIGURATION SÉCURITÉ & IA ---
ssl._create_default_https_context = ssl._create_unverified_context

try:
    CLE_API = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=CLE_API)
except Exception:
    st.error("🚨 Clé API introuvable dans les Secrets Streamlit. Veuillez configurer 'GEMINI_API_KEY'.")

# --- 1. PARAMÈTRES DE LA PAGE ---
st.set_page_config(page_title="Radar IA | Executive Pro", page_icon="🌍", layout="wide", initial_sidebar_state="expanded")

# --- 2. LE MENU LATÉRAL (SIDEBAR) ---
with st.sidebar:
    st.title("⚙️ Centre de Contrôle")
    st.markdown("Paramétrez votre radar de conformité et de sanctions.")
    st.markdown("---")
    
    liste_pays = [
        "Afghanistan", "Afrique du Sud", "Allemagne", "Arabie saoudite", "Argentine", "Australie", 
        "Brésil", "Canada", "Chine", "Corée du Nord", "Corée du Sud", "Égypte", "Émirats arabes unis", 
        "Espagne", "États-Unis", "France", "Inde", "Indonésie", "Iran", "Israël", "Italie", "Japon", 
        "Maroc", "Mexique", "Nigéria", "Royaume-Uni", "Russie", "Sénégal", "Taïwan", "Turquie", "Ukraine"
    ]
    pays_choisi = st.selectbox("Cible Stratégique :", sorted(liste_pays))
    nb_articles = st.slider("Profondeur de l'audit (Volume de sources) :", min_value=3, max_value=10, value=3)
    
    st.markdown("---")
    lancer_analyse = st.button("🚀 LANCER L'AUDIT EXECUTIVE", use_container_width=True, type="primary")

# --- FONCTION NETTOYAGE PDF ---
def clean_text(text):
    replacements = {'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e', 'à': 'a', 'â': 'a', 'ç': 'c', 'ô': 'o', 'î': 'i', 'ï': 'i', 'œ': 'oe', '€': 'EUR', '’': "'", '«': '"', '»': '"', '–': '-'}
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode('ascii', 'ignore').decode('ascii')

def generer_pdf(pays, score_moyen, titre_sources, texte_complet):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(200, 12, txt=f"RAPPORT D'AUDIT GEOPOLITIQUE : {pays.upper()}", ln=True, align='C')
    
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(200, 6, txt=f"Genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')} | Moteur IA Gemini", ln=True, align='C')
    pdf.ln(8)
    
    pdf.set_font("Arial", 'B', 14)
    if score_moyen >= 7: pdf.set_text_color(204, 0, 0)
    elif score_moyen >= 4: pdf.set_text_color(245, 158, 11)
    else: pdf.set_text_color(16, 185, 129)
        
    pdf.cell(200, 10, txt=f"INDICE DE RISQUE GLOBAL DEDUIT : {score_moyen:.1f} / 10", ln=True, align='C')
    pdf.ln(8)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="SOURCES ANALYSEES :", ln=True)
    pdf.set_font("Arial", '', 10)
    for source in titre_sources:
        pdf.multi_cell(0, 6, txt=f"- {clean_text(source)}")
    pdf.ln(8)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="SYNTHESE DES RISQUES :", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 6, txt=clean_text(texte_complet))
        
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 3. L'INTERFACE PRINCIPALE ---
st.title("Tableau de Bord Executive")
st.markdown("Analyse automatisée des flux réglementaires, conformité des flux et cartographie des risques.")
st.markdown("---")

col_carte, col_donnees = st.columns([1.2, 1.8])

with col_carte:
    st.subheader("Périmètre Géopolitique")
    df = pd.DataFrame({"Pays": liste_pays})
    fig_map = px.choropleth(df, locations="Pays", locationmode="country names", color_discrete_sequence=['#003366'], projection="orthographic")
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, geo=dict(showcoastlines=True, coastlinecolor="rgba(255,255,255,0.3)", projection_type='orthographic', bgcolor='rgba(0,0,0,0)'), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_map, use_container_width=True)

with col_donnees:
    st.subheader("Matrice de Veille Économique")
    
    if lancer_analyse:
        mot_cle = urllib.parse.quote(f"economie sanctions commerce {pays_choisi}")
        url_dynamique = f"https://news.google.com/rss/search?q={mot_cle}&hl=fr&gl=FR&ceid=FR:fr"
        
        with st.spinner(f"Acquisition des flux en cours (Architecture Batching)..."):
            try:
                request = urllib.request.Request(url_dynamique, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(request, timeout=10) as response:
                    data = response.read()
                
                root = ET.fromstring(data)
                items = root.findall('.//item')[:nb_articles]
                
                if not items:
                    st.warning(f"Aucun signal faible détecté pour {pays_choisi}.")
                else:
                    # --- NOUVELLE STRATÉGIE BATCHING (1 SEUL APPEL API) ---
                    titres_articles = [item.findtext('title') for item in items]
                    texte_sources = "\n".join([f"- {t}" for t in titres_articles])
                    
                    prompt = f"""Tu es un expert en sanctions internationales. Voici {len(titres_articles)} actualités récentes concernant {pays_choisi} :
                    {texte_sources}
                    
                    Fais une synthèse globale de l'impact de ces actualités combinées. 
                    Structure ta réponse exactement comme ceci :
                    SCORE GLOBAL: [Donne une note moyenne de risque de 1 à 10]
                    SANCTIONS & COMPLIANCE: [Résumé en 2 phrases]
                    SUPPLY CHAIN: [Résumé en 2 phrases]
                    FINANCE: [Résumé en 2 phrases]"""
                    
                    # 1 seul appel à l'IA, plus de problème de rate limit !
                    reponse = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                    texte_ia = reponse.text
                    
                    # Extraction du score global
                    match = re.search(r'SCORE GLOBAL:\s*(\d+)', texte_ia.upper())
                    score_moyen = int(match.group(1)) if match else 5
                    
                    # Affichage de la jauge
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = score_moyen,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': f"Indice Synthétique de Risque", 'font': {'size': 20, 'color': '#003366'}},
                        gauge = {
                            'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "darkblue"},
                            'bar': {'color': "#003366"},
                            'steps': [
                                {'range': [0, 3.5], 'color': "rgba(16, 185, 129, 0.2)"},
                                {'range': [3.5, 7], 'color': "rgba(245, 158, 11, 0.2)"},
                                {'range': [7, 10], 'color': "rgba(204, 0, 0, 0.2)"}
                            ]
                        }
                    ))
                    fig_gauge.update_layout(height=240, margin=dict(l=20, r=20, t=50, b=20))
                    st.plotly_chart(fig_gauge, use_container_width=True)
                    
                    # Affichage des résultats
                    st.markdown("### 📰 Sources analysées :")
                    for t in titres_articles:
                        st.markdown(f"- `{t}`")
                        
                    st.markdown("### 🧠 Audit Consolidé de l'IA :")
                    st.info(texte_ia)
                    
                    # Génération PDF
                    st.success("✅ Audit finalisé du premier coup. Plus de blocage !")
                    pdf_bytes = generer_pdf(pays_choisi, score_moyen, titres_articles, texte_ia)
                    st.download_button(
                        label="📄 EXPORTER LE RAPPORT STRATÉGIQUE (PDF)",
                        data=pdf_bytes, file_name=f"Rapport_Compliance_{pays_choisi}.pdf", mime="application/pdf", type="primary", use_container_width=True
                    )
                        
            except Exception as e:
                st.error(f"Erreur globale : {e}")
    else:
        st.info("👈 Déployez l'analyse. La nouvelle architecture à requête unique est activée.")