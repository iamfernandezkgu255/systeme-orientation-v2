"""
Système d'Aide à l'Orientation Professionnelle pour Étudiants au Bénin (Version 2)
Application Streamlit principale
"""

import streamlit as st
import json
from typing import Dict, List, Optional
import traceback
import logging
from datetime import datetime

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
    
    # Initialisation des composants avec gestion d'erreur robuste
    if 'knowledge_base' not in st.session_state:
        try:
            with st.spinner("Chargement de la base de connaissances..."):
                st.session_state.knowledge_base = KnowledgeBaseLoader()
                st.session_state.recommendation_engine = RecommendationEngine(st.session_state.knowledge_base)
                st.session_state.llm_interface = LLMInterface()
                
                # Validation de la base de connaissances
                validation = st.session_state.knowledge_base.valider_base_connaissances()
                if validation["erreurs"]:
                    st.error("⚠️ Problèmes détectés dans la base de connaissances:")
                    for erreur in validation["erreurs"]:
                        st.error(f"• {erreur}")
                
                if validation["avertissements"]:
                    with st.expander("Avertissements (cliquez pour voir les détails)"):
                        for avertissement in validation["avertissements"]:
                            st.warning(f"• {avertissement}")
                            
        except FileNotFoundError:
            st.error("❌ Fichier de base de connaissances non trouvé. L'application fonctionne en mode dégradé.")
            st.info("💡 Un fichier exemple va être créé automatiquement.")
            try:
                st.session_state.knowledge_base = KnowledgeBaseLoader()
                st.session_state.recommendation_engine = RecommendationEngine(st.session_state.knowledge_base)
                st.session_state.llm_interface = LLMInterface()
            except Exception as e:
                st.error(f"Impossible d'initialiser l'application : {str(e)}")
                st.stop()
        except Exception as e:
            st.error(f"❌ Erreur lors de l'initialisation : {str(e)}")
            st.info("L'application essaie de continuer en mode dégradé...")
            try:
                st.session_state.knowledge_base = None
                st.session_state.recommendation_engine = None
                st.session_state.llm_interface = LLMInterface()
            except:
                st.error("Impossible de démarrer l'application.")
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
        
        # Section debug et test API
        with st.expander("⚙️ Outils de diagnostic"):
            if st.button("🔧 Tester la connexion API"):
                with st.spinner("Test de la connexion API..."):
                    test_result = st.session_state.llm_interface.tester_connexion()
                    if test_result["success"]:
                        st.success("✅ Connexion API fonctionnelle")
                        st.info(f"Réponse: {test_result.get('response', 'N/A')}")
                    else:
                        st.error(f"❌ Problème de connexion: {test_result['message']}")
            
            if st.button("📊 Statistiques de la base"):
                if st.session_state.knowledge_base:
                    stats = st.session_state.knowledge_base.get_statistics()
                    st.json(stats)
                else:
                    st.error("Base de connaissances non disponible")
    
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
                if st.session_state.recommendation_engine:
                    recommandations = st.session_state.recommendation_engine.generer_recommandations(profil_utilisateur)
                else:
                    st.warning("⚠️ Moteur de recommandation indisponible. Analyse basique uniquement.")
                    recommandations = {"mode": "degrade"}
                
                # Analyse avec l'IA
                analyse_ia = st.session_state.llm_interface.analyser_profil(
                    profil_utilisateur, 
                    recommandations
                )
                
                # Affichage des résultats
                afficher_resultats(profil_utilisateur, recommandations, analyse_ia)
                
                # Option d'export des résultats
                if st.button("📄 Exporter le rapport d'analyse"):
                    rapport = generer_rapport_export(profil_utilisateur, recommandations, analyse_ia)
                    st.download_button(
                        label="💾 Télécharger le rapport (TXT)",
                        data=rapport,
                        file_name=f"rapport_orientation_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain"
                    )
                
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
        if profil.get('nom') and profil.get('prenom'):
            st.write(f"**Nom :** {profil['prenom']} {profil['nom']}")
        st.write(f"**Statut :** {profil['statut']}")
        if profil.get('serie_bac'):
            st.write(f"**Série BAC :** {profil['serie_bac']}")
    
    with col2:
        if profil.get('filiere_actuelle'):
            st.write(f"**Filière actuelle :** {profil['filiere_actuelle']}")
        st.write(f"**Carrière envisagée :** {profil['carriere_envisagee']}")
    
    # Analyse de l'IA
    st.markdown('<div class="section-header">🤖 Analyse de votre choix</div>', unsafe_allow_html=True)
    st.markdown('<div class="recommendation-card">', unsafe_allow_html=True)
    st.markdown(analyse_ia)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Vérification du mode dégradé
    if recommandations.get("mode") == "degrade":
        st.warning("⚠️ Analyse en mode dégradé - Données limitées disponibles")
        return
    
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
            with st.expander(f"{i}. {carriere.nom_metier}"):
                st.write(f"**Secteur :** {carriere.secteur_activite}")
                st.write(f"**Description :** {carriere.description}")
                if carriere.niveau_demande_marche:
                    st.write(f"**Demande sur le marché :** {carriere.niveau_demande_marche}")
                if carriere.pertinence_realites_africaines_benin:
                    st.write(f"**Pertinence au Bénin :** {carriere.pertinence_realites_africaines_benin}")

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

def generer_rapport_export(profil: Dict, recommandations: Dict, analyse_ia: str) -> str:
    """Génère un rapport d'analyse exportable"""
    
    rapport = f"""
RAPPORT D'ORIENTATION PROFESSIONNELLE - BÉNIN
Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}
================================================

PROFIL ÉTUDIANT
---------------
Nom: {profil.get('prenom', '') + ' ' + profil.get('nom', '') if profil.get('nom') else 'Non renseigné'}
Statut: {profil['statut']}
Série BAC: {profil.get('serie_bac', 'Non applicable')}
Filière actuelle: {profil.get('filiere_actuelle', 'Non applicable')}
Carrière envisagée: {profil['carriere_envisagee']}

ANALYSE PERSONNALISÉE
--------------------
{analyse_ia}

"""
    
    if recommandations.get("mode") != "degrade":
        # Universités recommandées
        if recommandations.get('universites_recommandees'):
            rapport += "\nUNIVERSITÉS ET FILIÈRES RECOMMANDÉES\n"
            rapport += "====================================\n"
            
            for i, univ in enumerate(recommandations['universites_recommandees'][:5], 1):
                rapport += f"\n{i}. {univ['nom_universite']} ({univ['statut']})\n"
                rapport += f"   Localisation: {univ.get('localisation', 'Non spécifiée')}\n"
                
                if univ.get('filieres_recommandees'):
                    rapport += "   Filières adaptées:\n"
                    for filiere in univ['filieres_recommandees'][:3]:
                        rapport += f"   • {filiere['nom_filiere']} ({filiere['diplome_delivre']})\n"
                        rapport += f"     Durée: {filiere['duree_etudes_ans']} ans\n"
                        if filiere.get('series_bac_requises'):
                            rapport += f"     Séries BAC: {', '.join(filiere['series_bac_requises'])}\n"
                rapport += "\n"
        
        # Carrières alternatives
        if recommandations.get('carrieres_alternatives'):
            rapport += "\nCARRIÈRES ALTERNATIVES À CONSIDÉRER\n"
            rapport += "==================================\n"
            
            for i, carriere in enumerate(recommandations['carrieres_alternatives'][:3], 1):
                rapport += f"\n{i}. {carriere.nom_metier}\n"
                rapport += f"   Secteur: {carriere.secteur_activite}\n"
                rapport += f"   Description: {carriere.description}\n"
                if carriere.niveau_demande_marche:
                    rapport += f"   Demande marché: {carriere.niveau_demande_marche}\n"
    
    rapport += f"""

CONSEILS POUR LA SUITE
=====================
1. Consultez les sites web des universités recommandées
2. Assistez aux journées portes ouvertes
3. Rencontrez des professionnels du domaine
4. Préparez-vous aux concours d'entrée si nécessaire
5. Gardez des options de carrières alternatives

---
Rapport généré par le Système d'Orientation Professionnelle du Bénin
Pour plus d'informations: contactez votre conseiller d'orientation
"""
    
    return rapport

if __name__ == "__main__":
    main()
