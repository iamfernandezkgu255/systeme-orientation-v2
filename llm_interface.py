"""
Module pour gérer les interactions avec l'API DeepSeek via OpenRouter
"""

import requests
import json
import streamlit as st
from typing import Dict, Any, Optional
import time

class LLMInterface:
    """Interface pour communiquer avec l'API DeepSeek via OpenRouter"""
    
    def __init__(self):
        """Initialise l'interface LLM avec les paramètres de configuration"""
        self.api_key = self._get_api_key()
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "deepseek/deepseek-chat"  # Modèle DeepSeek via OpenRouter
        self.max_retries = 3
        self.timeout = 30
        
        # Configuration par défaut
        self.default_config = {
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 0.9
        }
    
    def _get_api_key(self) -> Optional[str]:
        """Récupère la clé API depuis les secrets Streamlit"""
        try:
            return st.secrets["openrouter"]["api_key"]
        except KeyError:
            st.error("⚠️ Clé API OpenRouter non trouvée dans les secrets Streamlit!")
            st.markdown("""
            **Configuration requise :**
            
            Ajoutez votre clé API dans les secrets Streamlit :
            ```toml
            [openrouter]
            api_key = "votre_clé_api_ici"
            ```
            
            Vous pouvez obtenir une clé API sur [OpenRouter.ai](https://openrouter.ai)
            """)
            return None
    
    def analyser_profil(self, profil_utilisateur: Dict, recommandations: Dict) -> str:
        """Analyse le profil utilisateur avec l'aide de l'IA"""
        
        if not self.api_key:
            return self._fallback_analyse(profil_utilisateur, recommandations)
        
        # Préparer les données pour le prompt
        donnees_contexte = self._preparer_donnees_contexte(profil_utilisateur, recommandations)
        
        # Construire le prompt
        prompt = self._construire_prompt_analyse(donnees_contexte)
        
        # Faire l'appel API
        try:
            response = self._appeler_api(prompt)
            return response
        except Exception as e:
            st.warning(f"Erreur API : {e}. Utilisation de l'analyse de base.")
            return self._fallback_analyse(profil_utilisateur, recommandations)
    
    def _preparer_donnees_contexte(self, profil: Dict, recommandations: Dict) -> Dict:
        """Prépare les données contextuelles pour le LLM"""
        
        from recommendation_logic_student import RecommendationEngine
        # Simuler le moteur pour avoir accès à la méthode
        
        return {
            "profil": {
                "statut": profil["statut"],
                "serie_bac": profil.get("serie_bac"),
                "filiere_actuelle": profil.get("filiere_actuelle"),
                "carriere_envisagee": profil["carriere_envisagee"]
            },
            "analyse_metier": recommandations.get("metier_analyse", {}),
            "universites_recommandees": recommandations.get("universites_recommandees", []),
            "carrieres_alternatives": recommandations.get("carrieres_alternatives", []),
            "scores_compatibilite": recommandations.get("compatibilite_scores", {}),
            "parcours_suggere": recommandations.get("parcours_suggere", {})
        }
    
    def _construire_prompt_analyse(self, donnees: Dict) -> str:
        """Construit le prompt pour l'analyse du profil"""
        
        profil = donnees["profil"]
        metier_analyse = donnees["analyse_metier"]
        universites = donnees["universites_recommandees"]
        alternatives = donnees["carrieres_alternatives"]
        scores = donnees["scores_compatibilite"]
        
        prompt = f"""Tu es un conseiller d'orientation professionnel expert du système éducatif et du marché du travail au Bénin. 

PROFIL ÉTUDIANT:
- Statut: {profil['statut']}
- Série de BAC: {profil.get('serie_bac', 'Non spécifié')}
- Filière actuelle: {profil.get('filiere_actuelle', 'Non applicable')}
- Carrière envisagée: {profil['carriere_envisagee']}

ANALYSE DU MÉTIER ENVISAGÉ:
- Métier trouvé dans la base: {'Oui' if metier_analyse.get('metier_trouve') else 'Non'}
"""
        
        if metier_analyse.get('metier_trouve'):
            metier = metier_analyse['metier_obj']
            prompt += f"""- Secteur d'activité: {metier.secteur_activite}
- Demande sur le marché: {metier.niveau_demande_marche}
- Pertinence pour le Bénin: {metier.pertinence_realites_africaines_benin}
- Compétences techniques requises: {', '.join(metier.competences_requises_techniques[:5])}
- Compétences transversales: {', '.join(metier.competences_requises_transversales[:3])}
"""

        prompt += f"""
UNIVERSITÉS ET FILIÈRES DISPONIBLES: {len(universites)} options trouvées
"""
        
        if universites:
            prompt += "Top 3 recommandations:\n"
            for i, univ in enumerate(universites[:3], 1):
                prompt += f"{i}. {univ['nom_universite']} ({univ['statut']}) - {len(univ.get('filieres_recommandees', []))} filières compatibles\n"
        
        if alternatives:
            prompt += f"\nCARRIÈRES ALTERNATIVES IDENTIFIÉES: {len(alternatives)}\n"
            for alt in alternatives[:3]:
                prompt += f"- {alt.nom_metier} (Secteur: {alt.secteur_activite})\n"
        
        if scores:
            prompt += f"\nSCORES DE COMPATIBILITÉ:\n"
            prompt += f"- Compatibilité série-métier: {scores.get('serie_metier', 0):.1%}\n"
            prompt += f"- Pertinence marché béninois: {scores.get('marche_benin', 0):.1%}\n"
            prompt += f"- Formations disponibles: {scores.get('formation_disponible', 0):.1%}\n"
        
        prompt += f"""
MISSION:
Fournis une analyse personnalisée et des conseils d'orientation pour cet étudiant béninois. Ton analyse doit inclure:

1. **ÉVALUATION DU CHOIX DE CARRIÈRE** (2-3 phrases)
   - Pertinence du choix par rapport au profil et au contexte béninois
   - Forces et défis potentiels

2. **RECOMMANDATIONS D'UNIVERSITÉS** (3-4 phrases)
   - Pourquoi les universités recommandées sont adaptées
   - Conseils sur les critères de choix (public vs privé, localisation, etc.)

3. **PARCOURS PERSONNALISÉ** (4-5 points concrets)
   - Étapes clés à suivre
   - Compétences prioritaires à développer
   - Conseils spécifiques au contexte béninois

4. **CONSEILS PRATIQUES** (2-3 recommandations)
   - Actions immédiates à entreprendre
   - Ressources ou contacts utiles

STYLE: Professionnel mais bienveillant, concret et actionnable. Adapte tes conseils à la réalité du marché du travail et du système éducatif béninois.

LONGUEUR: 300-400 mots maximum.
"""
        
        return prompt
    
    def _appeler_api(self, prompt: str, config_custom: Optional[Dict] = None) -> str:
        """Effectue l'appel API vers OpenRouter/DeepSeek"""
        
        config = self.default_config.copy()
        if config_custom:
            config.update(config_custom)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://streamlit.io",  # Identifier l'origine
            "X-Title": "Système Orientation Bénin"  # Nom de l'app
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "Tu es un conseiller d'orientation professionnel expert du Bénin, spécialisé dans l'aide aux étudiants pour leurs choix de carrière et d'études."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            **config
        }
        
        # Tentatives avec retry
        for tentative in range(self.max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content'].strip()
                    else:
                        raise Exception("Réponse API invalide")
                
                elif response.status_code == 429:
                    # Rate limit - attendre avant de réessayer
                    wait_time = 2 ** tentative  # Backoff exponentiel
                    time.sleep(wait_time)
                    continue
                
                else:
                    raise Exception(f"Erreur API {response.status_code}: {response.text}")
            
            except requests.exceptions.Timeout:
                if tentative < self.max_retries - 1:
                    time.sleep(1)
                    continue
                raise Exception("Timeout - API non disponible")
            
            except requests.exceptions.RequestException as e:
                if tentative < self.max_retries - 1:
                    time.sleep(1)
                    continue
                raise Exception(f"Erreur de connexion: {str(e)}")
        
        raise Exception("Échec après plusieurs tentatives")
    
    def _fallback_analyse(self, profil: Dict, recommandations: Dict) -> str:
        """Analyse de base sans IA en cas d'échec de l'API"""
        
        carriere = profil["carriere_envisagee"]
        serie = profil.get("serie_bac", "Non spécifié")
        statut = profil["statut"]
        
        analyse = f"""**🎯 Évaluation de votre choix : {carriere}**

Votre profil ({serie if serie != "Non spécifié" else statut}) a été analysé en fonction de notre base de données des opportunités au Bénin.

**📊 Analyse de compatibilité :**
"""
        
        # Informations sur le métier si trouvé
        metier_analyse = recommandations.get("metier_analyse", {})
        if metier_analyse.get("metier_trouve"):
            metier = metier_analyse["metier_obj"]
            analyse += f"""
- **Secteur d'activité :** {metier.secteur_activite}
- **Demande sur le marché :** {metier.niveau_demande_marche or 'À évaluer'}
- **Pertinence au Bénin :** {metier.pertinence_realites_africaines_benin or 'Secteur en développement'}
"""
        else:
            analyse += f"\nLe métier '{carriere}' nécessite une analyse plus approfondie. "
        
        # Universités disponibles
        universites = recommandations.get("universites_recommandees", [])
        if universites:
            analyse += f"""

**🏛️ Formations disponibles :**
Nous avons identifié {len(universites)} institution(s) proposant des formations dans ce domaine, incluant des options publiques et privées agréées.
"""
        else:
            analyse += f"""

**🏛️ Formations :**
Les formations pour ce métier pourraient nécessiter des recherches supplémentaires ou être disponibles dans des institutions spécialisées.
"""
        
        # Recommandations générales
        analyse += f"""

**📋 Recommandations personnalisées :**

1. **Validation du choix :** Rencontrez des professionnels du domaine pour confirmer votre intérêt
2. **Préparation académique :** Renforcez vos compétences dans les matières clés de votre série
3. **Exploration d'alternatives :** Considérez des métiers connexes dans le même secteur
4. **Recherche d'informations :** Contactez directement les universités pour les conditions d'admission

**🔍 Prochaines étapes :**
- Visitez les universités recommandées lors de leurs journées portes ouvertes
- Consultez un conseiller d'orientation dans votre établissement
- Préparez-vous aux éventuels concours d'entrée
"""
        
        return analyse
    
    def tester_connexion(self) -> Dict[str, Any]:
        """Test la connexion à l'API"""
        
        if not self.api_key:
            return {"success": False, "message": "Clé API non configurée"}
        
        try:
            test_prompt = "Bonjour, veuillez répondre simplement 'Test réussi' pour confirmer la connexion."
            response = self._appeler_api(test_prompt, {"max_tokens": 20, "temperature": 0})
            
            return {
                "success": True, 
                "message": "Connexion réussie",
                "response": response
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Erreur de connexion : {str(e)}"
            }
    
    def generer_conseil_supplementaire(self, domaine: str) -> str:
        """Génère un conseil supplémentaire pour un domaine spécifique"""
        
        if not self.api_key:
            return f"Conseil : Explorez davantage les opportunités dans le domaine {domaine} au Bénin."
        
        prompt = f"""Donne un conseil pratique et spécifique de 2-3 phrases pour un étudiant béninois intéressé par le domaine {domaine}. 
        
        Le conseil doit être:
        - Actionnable
        - Adapté au contexte béninois
        - Encourageant
        
        Commence directement par le conseil sans préambule."""
        
        try:
            return self._appeler_api(prompt, {"max_tokens": 150, "temperature": 0.8})
        except:
            return f"Explorez les opportunités croissantes dans le domaine {domaine} en vous rapprochant des professionnels locaux et des associations sectorielles."
