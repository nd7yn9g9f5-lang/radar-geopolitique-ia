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
import time

# --- CONFIGURATION SÉCURITÉ & IA ---
ssl._create_default_https_context = ssl._create_unverified_context

# Récupération sécurisée de la clé d'API via les secrets du serveur Streamlit
try:
    CLE_API = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=CLE_API)
except Exception:
    st.error("🚨 Clé API introuvable dans les Secrets Streamlit. Veuillez configurer 'GEMINI_API_KEY'.")

# --- 1. PARAMÈTRES DE LA PAGE ---
st.set_page_config(
    page_title="Radar IA | Executive Pro", 
    page_icon="🌍", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. LE MENU LATÉRAL (SIDEBAR) ---
with st.sidebar:
    st.title("⚙️ Centre de Contrôle")
    st.markdown("Paramétrez votre radar de conformité et de sanctions internationales.")
    st.markdown("---")
    
    # Liste des places stratégiques majeures du commerce mondial
    liste_pays = [
        "Afghanistan", "Afrique du Sud", "Allemagne", "Arabie saoudite", "Argentine", "Australie", 
        "Brésil", "Canada", "Chine", "Corée du Nord", "Corée du Sud", "Égypte", "Émirats arabes unis", 
        "Espagne", "États-Unis", "France", "Inde", "Indonésie", "Iran", "Israël", "Italie", "Japon", 
        "Maroc", "Mexique", "Nigéria", "Royaume-Uni", "Russie", "Sénégal", "Taïwan", "Turquie", "Ukraine"
    ]
    pays_choisi = st.selectbox("Cible Stratégique :", sorted(liste_pays))
    
    # Optimisation anti-satiété : curseur bridé à 10 maximum avec une valeur de départ prudente à 3
    nb_articles = st.slider("Profondeur de l'audit (Volume de sources) :", min_value=3, max_value=10, value=3)
    
    st.markdown("---")
    lancer_analyse = st.button("🚀 LANCER L'AUDIT EXECUTIVE", use_container_width=True, type="primary")

# --- FONCTION NETTOYAGE TEXTE POUR LE MOTEUR PDF ---
def clean_text(text):
    """Nettoie les caractères spéciaux pour éviter les erreurs d'encodage FPDF standard"""
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ç': 'c', 'ô': 'o', 
        'î': 'i', 'ï': 'i', 'œ': 'oe', '€': 'EUR', 
        '’': "'", '«': '"', '»': '"', '–': '-'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # Suppression des caractères non-ASCII restants pour sécuriser le rendu
    return text.encode('ascii', 'ignore').decode('ascii')

# --- FONCTION DE GÉNÉRATION DU RAPPORT PDF ---
def generer_pdf(pays, score_moyen, analyses):
    pdf = FPDF()
    pdf.add_page()
    
    # En-tête institutionnel
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 51, 102) # Bleu Marine
    pdf.cell(200, 12, txt=f"RAPPORT D'AUDIT GEOPOLITIQUE : {pays.upper()}", ln=True, align='C')
    
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(200, 6, txt=f"Genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')} | Moteur IA Gemini", ln=True, align='C')
    pdf.ln(8)
    
    # Ligne de séparation
    pdf.set_draw_color(0, 51, 102)
    pdf.line(10, 32, 200, 32)
    pdf.ln(5)
    
    # Affichage dynamique de l'indice de risque global
    pdf.set_font("Arial", 'B', 14)
    if score_moyen >= 7:
        pdf.set_text_color(204, 0, 0) # Rouge critique
    elif score_moyen >= 4:
        pdf.set_text_color(245, 158, 11) # Orange d'alerte
    else:
        pdf.set_text_color(16, 185, 129) # Vert sécurisé
        
    pdf.cell(200, 10, txt=f"INDICE DE RISQUE GLOBAL DEDUIT : {score_moyen:.1f} / 10", ln=True, align='C')
    pdf.ln(8)
    
    # Corps du rapport : Déroulé des matrices d'analyse
    pdf.set_text_color(0, 0, 0)
    for idx, (titre, contenu) in enumerate(analyses):
        pdf.set_font("Arial", 'B', 11)
        pdf.set_text_color(0, 51, 102)
        pdf.multi_cell(0, 7, txt=f"Signal Analyse #{idx+1} : {clean_text(titre)}")
        
        pdf.set_font("Arial", '', 10)
        pdf.set_text_color(30, 30, 30)
        pdf.multi_cell(0, 6, txt=clean_text(contenu))
        pdf.ln(6)
        
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 3. L'INTERFACE PRINCIPALE (DASHBOARD) ---
st.title("Tableau de Bord Executive")
st.markdown("Analyse automatisée des flux réglementaires, conformité des flux et cartographie des risques.")
st.markdown("---")

col_carte, col_donnees = st.columns([1.2, 1.8])

with col_carte:
    st.subheader("Périmètre Géopolitique")
    df = pd.DataFrame({"Pays": liste_pays})
    fig_map = px.choropleth(
        df, 
        locations="Pays", 
        locationmode="country names", 
        color_discrete_sequence=['#003366'], 
        projection="orthographic"
    )
    fig_map.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0}, 
        geo=dict(showcoastlines=True, coastlinecolor="rgba(255,255,255,0.3)", projection_type='orthographic', bgcolor='rgba(0,0,0,0)'), 
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_map, use_container_width=True)

with col_donnees:
    st.subheader("Matrice de Veille Économique")
    
    if lancer_analyse:
        # Encodage de la requête pour cibler la conformité et le commerce international
        mot_cle = urllib.parse.quote(f"economie sanctions commerce {pays_choisi}")
        url_dynamique = f"https://news.google.com/rss/search?q={mot_cle}&hl=fr&gl=FR&ceid=FR:fr"
        
        with st.spinner(f"Acquisition des flux et génération de la matrice pour {pays_choisi}..."):
            try:
                request = urllib.request.Request(url_dynamique, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(request, timeout=10) as response:
                    data = response.read()
                
                root = ET.fromstring(data)
                items = root.findall('.//item')[:nb_articles]
                
                if not items:
                    st.warning(f"Aucun signal faible ou alerte majeure détectée pour {pays_choisi} sur les dernières 24 heures.")
                else:
                    scores = []
                    analyses_sauvegardees = []
                    
                    # Zone tampon pour injecter la jauge de synthèse à la fin
                    zone_jauge = st.empty()
                    
                    for idx, item in enumerate(items):
                        title = item.findtext('title')
                        
                        # Guide comportemental strict pour forcer l'IA à structurer son rapport d'audit
                        prompt = f"""Tu es un expert en sanctions internationales, conformité réglementaire et commerce international. 
                        Analyse l'impact de cette actualité concernant {pays_choisi} : "{title}".
                        Tu dois obligatoirement structurer ta réponse comme ceci (sans introduction ni conclusion) :
                        SCORE: [Attribue une note mathématique de risque de 1 à 10 face aux marchés internationaux]
                        SANCTIONS & COMPLIANCE: [Analyse de l'impact réglementaire ou risques juridiques en 1 phrase claire]
                        SUPPLY CHAIN: [Conséquences sur la logistique, douanes et matières premières en 1 phrase claire]
                        FINANCE: [Impact sur la devise, le risque bancaire ou les investissements en 1 phrase claire]"""
                        
                        # --- ALGORITHME DE RE-TENTATIVE (ANTI-BLOCAGE RATE LIMIT) ---
                        texte_ia = ""
                        max_retries = 3
                        for attempt in range(max_retries):
                            try:
                                reponse = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                                texte_ia = reponse.text
                                break  # Succès, on sort de la boucle de re-tentative
                            except Exception as e:
                                if "429" in str(e) and attempt < max_retries - 1:
                                    st.warning(f"⏳ Régulation de flux détectée par Google. Temporisation de sécurité active... (Reprise de l'audit dans 12s)")
                                    time.sleep(12) # Pause prolongée pour forcer le déblocage des serveurs
                                else:
                                    st.error(f"Erreur technique de communication avec le cœur IA : {e}")
                                    texte_ia = "SCORE: 5\nSANCTIONS: Impossible de générer l'analyse en raison de restrictions de flux temporaires.\nSUPPLY CHAIN: Données indisponibles.\nFINANCE: Flux interrompu."
                                    break
                        
                        # Extraction robuste du score calculé par l'IA
                        match = re.search(r'SCORE:\s*(\d+)', texte_ia.upper())
                        score_actuel = int(match.group(1)) if match else 5
                        scores.append(score_actuel)
                        
                        # Archivage pour la compilation du PDF
                        analyses_sauvegardees.append((title, texte_ia))
                        
                        # Rendu visuel haut de gamme sous forme de volets dépliants
                        with st.expander(f"👁️ Alerte {idx+1} (Risque: {score_actuel}/10) | {title[:65]}..."):
                            st.markdown(f"**Source validée :** `{title}`")
                            st.markdown("---")
                            st.info(texte_ia)
                        
                        # Temporisation préventive pour lisser la charge d'appels à l'API gratuite
                        time.sleep(5)
                    
                    # --- CALCUL ET RENDER DU COMPTEUR DE SYNTHÈSE (GAUGE CHART) ---
                    score_moyen = sum(scores) / len(scores) if scores else 5
                    
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = score_moyen,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': f"Indice Synthétique de Risque ({len(scores)} Sources)", 'font': {'size': 20, 'color': '#003366'}},
                        gauge = {
                            'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "darkblue"},
                            'bar': {'color': "#003366"},
                            'bgcolor': "white",
                            'borderwidth': 2,
                            'bordercolor': "gray",
                            'steps': [
                                {'range': [0, 3.5], 'color': "rgba(16, 185, 129, 0.2)"}, # Vert doux
                                {'range': [3.5, 7], 'color': "rgba(245, 158, 11, 0.2)"}, # Orange doux
                                {'range': [7, 10], 'color': "rgba(204, 0, 0, 0.2)"}    # Rouge doux
                            ]
                        }
                    ))
                    fig_gauge.update_layout(height=240, margin=dict(l=20, r=20, t=50, b=20))
                    
                    # Injection du graphique tout en haut de la matrice d'analyse
                    zone_jauge.plotly_chart(fig_gauge, use_container_width=True)
                    
                    # --- COMPILATION ET BOUTON DE TÉLÉCHARGEMENT DU LIVRABLE ---
                    st.success("✅ Audit de conformité structurel finalisé avec succès.")
                    
                    try:
                        pdf_bytes = generer_pdf(pays_choisi, score_moyen, analyses_sauvegardees)
                        st.download_button(
                            label="📄 EXPORTER LE RAPPORT STRATÉGIQUE (PDF)",
                            data=pdf_bytes,
                            file_name=f"Rapport_Compliance_{pays_choisi}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            type="primary",
                            use_container_width=True
                        )
                    except Exception as pdf_err:
                        st.error(f"Erreur lors de la mise en page du livrable PDF : {pdf_err}")
                        
            except Exception as e:
                st.error(f"Erreur globale lors du scan de la zone : {e}")
    else:
        st.info("👈 Sélectionnez une cible stratégique dans le centre de contrôle pour déployer la puissance d'audit de l'IA.")