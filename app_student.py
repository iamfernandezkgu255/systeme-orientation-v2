"""
Système d'Aide à l'Orientation Professionnelle pour Étudiants au Bénin (Version 2)
Application Streamlit principale
"""

import streamlit as st
import json
from typing import Dict, List, Optional
import traceback

# Import des modules personnalisés
from knowledge_base_loader import KnowledgeBaseLoader
from recommendation_logic_student import RecommendationEngine
from llm_interface import LLMInterface

def main():
    """Application principale Streamlit"""
    
    # Configuration de la page
    st.set_page_config(
        page_title="Orientation Professionnelle - Bénin",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Style CSS personnalisé
    st.markdown("""
    <style>
    .main-title {
        color: #2E8B57;
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .section-header {
        color: #4169E1;
        font-size: 1.3rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .recommendation-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #4169E1;
    }
    .university-card {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #2E8B57;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Titre principal
    st.markdown('<h1 class="main-title">🎓 Système d\'Orientation Professionnelle du Bénin</h1>', 
                unsafe_allow_html=True)
    
    # Initialisation des composants
    if 'knowledge_base' not in st.session_state:
        try:
            st.session_state.knowledge_base = KnowledgeBaseLoader()
            st.session_state.recommendation_engine = RecommendationEngine(st.session_state.knowledge_base)
            st.session_state.llm_interface = LLMInterface()
        except Exception as e:
            st.error(f"Erreur lors de l'initialisation : {str(e)}")
            st.stop()
    
    # Sidebar pour les informations du profil
    with st.sidebar:
        st.header("📋 Votre Profil")
        
        # Informations personnelles (optionnelles)
        nom = st.text_input("Nom (optionnel)", placeholder="Votre nom de famille")
        prenom = st.text_input("Prénom (optionnel)", placeholder="Votre prénom")
        
        # Statut étudiant
        statut = st.radio(
            "Votre statut actuel :",
            ["Élève (Futur Bachelier)", "Étudiant Universitaire"]
        )
        
        # Série du BAC ou filière actuelle
        if statut == "Élève (Futur Bachelier)":
            series_bac = [
                "A1 (Lettres-Langues)", 
                "A2 (Lettres-Sciences Sociales)", 
                "B (Sciences Sociales)", 
                "C (Mathématiques-Sciences Physiques)", 
                "D (Mathématiques-Sciences Naturelles)", 
                "E (Mathématiques-Techniques)", 
                "EA (Économie-Administration)",
                "F1 (Électrotechnique)", 
                "F2 (Mécanique Générale)", 
                "F3 (Électricité)", 
                "F4 (Génie Civil)",
                "G1 (Secrétariat)", 
                "G2 (Comptabilité)", 
                "G3 (Commerce)"
            ]
            serie_bac = st.selectbox("Votre série du BAC :", series_bac)
            filiere_actuelle = None
        else:
            serie_bac = None
            filiere_actuelle = st.text_input(
                "Filière universitaire actuelle :", 
                placeholder="Ex: Licence en Informatique, Master en Gestion..."
            )
        
        # Carrière envisagée
        carriere_envisagee = st.text_input(
            "Carrière que vous envisagez :",
            placeholder="Ex: Médecin, Ingénieur en informatique, Avocat..."
        )
        
        # Bouton d'analyse
        analyser = st.button("🔍 Analyser mon profil", type="primary")
    
    # Zone principale de contenu
    if analyser and carriere_envisagee:
        with st.spinner("Analyse de votre profil en cours..."):
            try:
                # Création du profil utilisateur
                profil_utilisateur = {
                    "nom": nom if nom else None,
                    "prenom": prenom if prenom else None,
                    "statut": statut,
                    "serie_bac": serie_bac,
                    "filiere_actuelle": filiere_actuelle,
                    "carriere_envisagee": carriere_envisagee
                }
                
                # Génération des recommandations
                recommandations = st.session_state.recommendation_engine.generer_recommandations(profil_utilisateur)
                
                # Analyse avec l'IA
                analyse_ia = st.session_state.llm_interface.analyser_profil(
                    profil_utilisateur, 
                    recommandations
                )
                
                # Affichage des résultats
                afficher_resultats(profil_utilisateur, recommandations, analyse_ia)
                
            except Exception as e:
                st.error(f"Erreur lors de l'analyse : {str(e)}")
                with st.expander("Détails de l'erreur"):
                    st.code(traceback.format_exc())
    
    elif analyser and not carriere_envisagee:
        st.warning("⚠️ Veuillez renseigner la carrière que vous envisagez.")
    
    else:
        # Page d'accueil
        afficher_page_accueil()

def afficher_page_accueil():
    """Affiche la page d'accueil avec les instructions"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ### 🌟 Bienvenue dans votre guide d'orientation !
        
        Cette application vous aide à :
        - **Analyser** votre choix de carrière
        - **Découvrir** les universités adaptées à votre profil
        - **Planifier** votre parcours d'études
        
        ### 📝 Comment ça marche ?
        
        1. **Remplissez votre profil** dans la barre latérale
        2. **Indiquez votre carrière envisagée**
        3. **Cliquez sur "Analyser"** pour obtenir vos recommandations
        
        ### 🎯 Informations nécessaires :
        
        - Votre série de BAC (si vous êtes élève)
        - Votre filière actuelle (si vous êtes déjà étudiant)
        - La carrière professionnelle que vous envisagez
        """)
        
        # Statistiques de la base de connaissances
        try:
            stats = st.session_state.knowledge_base.get_statistics()
            
            st.markdown("### 📊 Notre base de données inclut :")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Métiers", stats.get('nb_metiers', 'N/A'))
            with col_b:
                st.metric("Universités", stats.get('nb_universites', 'N/A'))
            with col_c:
                st.metric("Filières", stats.get('nb_filieres', 'N/A'))
                
        except:
            pass

def afficher_resultats(profil: Dict, recommandations: Dict, analyse_ia: str):
    """Affiche les résultats de l'analyse"""
    
    # En-tête avec le profil
    st.markdown('<div class="section-header">👤 Votre Profil</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if profil['nom'] and profil['prenom']:
            st.write(f"**Nom :** {profil['prenom']} {profil['nom']}")
        st.write(f"**Statut :** {profil['statut']}")
        if profil['serie_bac']:
            st.write(f"**Série BAC :** {profil['serie_bac']}")
    
    with col2:
        if profil['filiere_actuelle']:
            st.write(f"**Filière actuelle :** {profil['filiere_actuelle']}")
        st.write(f"**Carrière envisagée :** {profil['carriere_envisagee']}")
    
    # Analyse de l'IA
    st.markdown('<div class="section-header">🤖 Analyse de votre choix</div>', unsafe_allow_html=True)
    st.markdown('<div class="recommendation-card">', unsafe_allow_html=True)
    st.markdown(analyse_ia)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Universités recommandées
    if recommandations.get('universites_recommandees'):
        st.markdown('<div class="section-header">🏛️ Universités et Filières Recommandées</div>', 
                   unsafe_allow_html=True)
        
        for universite in recommandations['universites_recommandees']:
            afficher_carte_universite(universite)
    
    # Carrières alternatives
    if recommandations.get('carrieres_alternatives'):
        st.markdown('<div class="section-header">💼 Carrières Alternatives à Considérer</div>', 
                   unsafe_allow_html=True)
        
        for i, carriere in enumerate(recommandations['carrieres_alternatives'][:3], 1):
            with st.expander(f"{i}. {carriere['nom_metier']}"):
                st.write(f"**Secteur :** {carriere['secteur_activite']}")
                st.write(f"**Description :** {carriere['description']}")
                if carriere.get('niveau_demande_marche'):
                    st.write(f"**Demande sur le marché :** {carriere['niveau_demande_marche']}")

def afficher_carte_universite(universite_info: Dict):
    """Affiche les informations d'une université sous forme de carte"""
    
    st.markdown('<div class="university-card">', unsafe_allow_html=True)
    
    # En-tête de l'université
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**🏛️ {universite_info['nom_universite']}**")
        if universite_info.get('sigle'):
            st.markdown(f"*({universite_info['sigle']})*")
    
    with col2:
        statut_color = "🟢" if universite_info['statut'] == "Public" else "🔵"
        st.markdown(f"{statut_color} {universite_info['statut']}")
    
    # Informations générales
    if universite_info.get('localisation'):
        st.markdown(f"📍 **Localisation :** {universite_info['localisation']}")
    
    # Filières recommandées
    if universite_info.get('filieres_recommandees'):
        st.markdown("**📚 Filières adaptées à votre profil :**")
        
        for filiere in universite_info['filieres_recommandees']:
            with st.expander(f"• {filiere['nom_filiere']} ({filiere['diplome_delivre']})"):
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**Durée :** {filiere['duree_etudes_ans']} ans")
                    if filiere.get('series_bac_requises'):
                        st.write(f"**Séries BAC acceptées :** {', '.join(filiere['series_bac_requises'])}")
                
                with col_b:
                    if filiere.get('autres_prerequis'):
                        st.write(f"**Autres prérequis :** {filiere['autres_prerequis']}")
                
                if filiere.get('description_filiere'):
                    st.write(f"**Description :** {filiere['description_filiere']}")
                
                if filiere.get('metiers_vises_typiques'):
                    st.write(f"**Métiers visés :** {', '.join(filiere['metiers_vises_typiques'])}")
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
