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
CLE_API = "AIzaSyBOf1mMO6Rps_JVfR04ADCY3lgTcZG9kgY"
client = genai.Client(api_key=CLE_API)

# --- 1. PARAMÈTRES DE LA PAGE ---
st.set_page_config(page_title="Radar IA | Executive", page_icon="🌍", layout="wide", initial_sidebar_state="expanded")

# --- 2. LE MENU LATÉRAL ---
with st.sidebar:
    st.title("⚙️ Centre de Contrôle")
    st.markdown("Paramétrez votre radar géopolitique.")
    st.markdown("---")
    
    liste_pays = [
        "Afghanistan", "Afrique du Sud", "Allemagne", "Arabie saoudite", "Argentine", "Australie", 
        "Brésil", "Canada", "Chine", "Corée du Nord", "Corée du Sud", "Égypte", "Émirats arabes unis", 
        "Espagne", "États-Unis", "France", "Inde", "Indonésie", "Iran", "Israël", "Italie", "Japon", 
        "Maroc", "Mexique", "Nigéria", "Royaume-Uni", "Russie", "Sénégal", "Taïwan", "Turquie", "Ukraine"
    ]
    pays_choisi = st.selectbox("Cible Stratégique :", sorted(liste_pays))
    
    # NOUVEAUTÉ : Le curseur de profondeur
    nb_articles = st.slider("Profondeur de l'audit (Volume de sources) :", min_value=3, max_value=15, value=5)
    
    st.markdown("---")
    lancer_analyse = st.button("🚀 LANCER L'AUDIT IA", use_container_width=True, type="primary")

# --- FONCTION NETTOYAGE TEXTE POUR PDF ---
def clean_text(text):
    replacements = {'é': 'e', 'è': 'e', 'ê': 'e', 'à': 'a', 'â': 'a', 'ç': 'c', 'ô': 'o', 'î': 'i', 'ï': 'i', 'œ': 'oe', '€': 'EUR', '’': "'", '«': '"', '»': '"'}
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

# --- FONCTION CRÉATION PDF ---
def generer_pdf(pays, score_moyen, analyses):
    pdf = FPDF()
    pdf.add_page()
    
    # En-tête
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(200, 10, txt=f"RAPPORT D'AUDIT GEOPOLITIQUE : {pays.upper()}", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(200, 10, txt=f"Genere le {datetime.now().strftime('%d/%m/%Y')} par l'IA Gemini", ln=True, align='C')
    pdf.ln(5)
    
    # Score de Risque
    pdf.set_font("Arial", 'B', 14)
    if score_moyen >= 7:
        pdf.set_text_color(200, 0, 0)
    elif score_moyen >= 4:
        pdf.set_text_color(255, 140, 0)
    else:
        pdf.set_text_color(0, 150, 0)
    pdf.cell(200, 10, txt=f"INDICE DE RISQUE GLOBAL : {score_moyen:.1f} / 10", ln=True, align='C')
    pdf.ln(10)
    
    # Analyses
    pdf.set_text_color(0, 0, 0)
    for idx, (titre, contenu) in enumerate(analyses):
        pdf.set_font("Arial", 'B', 11)
        pdf.multi_cell(0, 8, txt=f"Alerte #{idx+1} : {clean_text(titre)}")
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 6, txt=clean_text(contenu))
        pdf.ln(5)
        
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 3. L'INTERFACE PRINCIPALE ---
st.title("Tableau de Bord Executive")
st.markdown("Surveillance des flux commerciaux, conformité et sanctions en temps réel.")

col_carte, col_donnees = st.columns([1.2, 1.8])

with col_carte:
    st.subheader("Cartographie")
    df = pd.DataFrame({"Pays": liste_pays})
    fig_map = px.choropleth(df, locations="Pays", locationmode="country names", color_discrete_sequence=['#1f77b4'], projection="orthographic")
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, geo=dict(showcoastlines=True, projection_type='orthographic', bgcolor='rgba(0,0,0,0)'), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_map, use_container_width=True)

with col_donnees:
    st.subheader("Matrice d'Analyse IA")
    
    if lancer_analyse:
        mot_cle = urllib.parse.quote(f"économie sanctions commerce {pays_choisi}")
        url_dynamique = f"https://news.google.com/rss/search?q={mot_cle}&hl=fr&gl=FR&ceid=FR:fr"
        
        with st.spinner(f"Audit IA en cours (Traitement de {nb_articles} sources)..."):
            try:
                request = urllib.request.Request(url_dynamique, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(request, timeout=10) as response:
                    data = response.read()
                
                root = ET.fromstring(data)
                # NOUVEAUTÉ : On récupère le nombre d'articles choisi par l'utilisateur
                items = root.findall('.//item')[:nb_articles]
                
                if not items:
                    st.warning("Aucune donnée stratégique détectée aujourd'hui.")
                else:
                    scores = []
                    analyses_sauvegardees = []
                    
                    zone_jauge = st.empty()
                    
                    for item in items:
                        title = item.findtext('title')
                        
                        prompt = f"""Tu es un expert en sanctions internationales et commerce. Analyse cette actualité pour {pays_choisi} : "{title}". 
                        Réponds STRICTEMENT avec cette structure :
                        SCORE: [donne une note de risque de 1 à 10]
                        SANCTIONS: [Impact sur la conformité en 1 phrase]
                        SUPPLY CHAIN: [Impact logistique en 1 phrase]
                        FINANCE: [Impact financier en 1 phrase]"""
                        
                        reponse = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                        texte_ia = reponse.text
                        
                        match = re.search(r'SCORE:\s*(\d+)', texte_ia.upper())
                        score_actuel = int(match.group(1)) if match else 5
                        scores.append(score_actuel)
                        
                        analyses_sauvegardees.append((title, texte_ia))
                        
                        with st.expander(f"🔴 Score: {score_actuel}/10 | {title[:50]}..."):
                            st.markdown(f"**Source :** {title}")
                            st.info(texte_ia)
                    
                    score_moyen = sum(scores) / len(scores) if scores else 5
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = score_moyen,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': f"Indice de Risque Global ({len(scores)} sources)", 'font': {'size': 24}},
                        gauge = {
                            'axis': {'range': [0, 10]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 3], 'color': "lightgreen"},
                                {'range': [3, 7], 'color': "gold"},
                                {'range': [7, 10], 'color': "salmon"}
                            ]}
                    ))
                    fig_gauge.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10))
                    zone_jauge.plotly_chart(fig_gauge, use_container_width=True)
                    
                    st.success("✅ Audit terminé. Rapport prêt pour l'export.")
                    pdf_bytes = generer_pdf(pays_choisi, score_moyen, analyses_sauvegardees)
                    st.download_button(
                        label="📄 TÉLÉCHARGER LE RAPPORT EXECUTIVE (PDF)",
                        data=pdf_bytes,
                        file_name=f"Audit_Geopolitique_{pays_choisi}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                        
            except Exception as e:
                st.error(f"Erreur du radar : {e}")
    else:
        st.info("👈 Lancez l'audit pour générer les graphiques et le rapport PDF.")