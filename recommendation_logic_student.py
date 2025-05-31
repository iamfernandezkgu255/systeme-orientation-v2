"""
Module contenant la logique de recommandation pour le système d'orientation
"""

from typing import Dict, List, Optional, Any
from knowledge_base_loader import KnowledgeBaseLoader, Metier
import re

class RecommendationEngine:
    """Moteur de recommandation pour l'orientation professionnelle"""
    
    def __init__(self, knowledge_base_loader: KnowledgeBaseLoader):
        """Initialise le moteur avec une base de connaissances"""
        self.kb_loader = knowledge_base_loader
        
        # Mapping des séries de BAC vers leurs domaines
        self.series_bac_mapping = {
            "A1": {"domaine": "Lettres-Langues", "type": "littéraire"},
            "A2": {"domaine": "Lettres-Sciences Sociales", "type": "littéraire"},
            "B": {"domaine": "Sciences Sociales", "type": "économique"},
            "C": {"domaine": "Mathématiques-Sciences Physiques", "type": "scientifique"},
            "D": {"domaine": "Mathématiques-Sciences Naturelles", "type": "scientifique"},
            "E": {"domaine": "Mathématiques-Techniques", "type": "technique"},
            "EA": {"domaine": "Économie-Administration", "type": "économique"},
            "F1": {"domaine": "Électrotechnique", "type": "technique"},
            "F2": {"domaine": "Mécanique Générale", "type": "technique"},
            "F3": {"domaine": "Électricité", "type": "technique"},
            "F4": {"domaine": "Génie Civil", "type": "technique"},
            "G1": {"domaine": "Secrétariat", "type": "tertiaire"},
            "G2": {"domaine": "Comptabilité", "type": "tertiaire"},
            "G3": {"domaine": "Commerce", "type": "tertiaire"}
        }
    
    def generer_recommandations(self, profil_utilisateur: Dict) -> Dict[str, Any]:
        """Génère des recommandations personnalisées basées sur le profil utilisateur"""
        
        recommandations = {
            "profil_analyse": self._analyser_profil(profil_utilisateur),
            "metier_analyse": self._analyser_metier_envisage(profil_utilisateur["carriere_envisagee"]),
            "universites_recommandees": self._recommander_universites(profil_utilisateur),
            "carrieres_alternatives": self._proposer_carrieres_alternatives(profil_utilisateur),
            "compatibilite_scores": self._calculer_compatibilite(profil_utilisateur),
            "parcours_suggere": self._suggerer_parcours(profil_utilisateur)
        }
        
        return recommandations
    
    def _analyser_profil(self, profil: Dict) -> Dict[str, Any]:
        """Analyse le profil de l'utilisateur"""
        
        analyse = {
            "type_profil": "Élève" if profil["statut"] == "Élève (Futur Bachelier)" else "Étudiant",
            "domaine_origine": None,
            "forces": [],
            "recommandations_generales": []
        }
        
        if profil.get("serie_bac"):
            # Extraire la lettre de série (ex: "C" depuis "C (Mathématiques-Sciences Physiques)")
            serie_lettre = profil["serie_bac"].split()[0]
            if serie_lettre in self.series_bac_mapping:
                serie_info = self.series_bac_mapping[serie_lettre]
                analyse["domaine_origine"] = serie_info["domaine"]
                analyse["type_formation"] = serie_info["type"]
                
                # Définir les forces basées sur la série
                if serie_info["type"] == "scientifique":
                    analyse["forces"] = ["Mathématiques", "Sciences", "Logique", "Analyse"]
                elif serie_info["type"] == "littéraire":
                    analyse["forces"] = ["Communication", "Langues", "Rédaction", "Culture générale"]
                elif serie_info["type"] == "économique":
                    analyse["forces"] = ["Gestion", "Économie", "Sciences sociales", "Administration"]
                elif serie_info["type"] == "technique":
                    analyse["forces"] = ["Techniques", "Pratique", "Technologies", "Innovation"]
                elif serie_info["type"] == "tertiaire":
                    analyse["forces"] = ["Commerce", "Services", "Gestion", "Communication"]
        
        elif profil.get("filiere_actuelle"):
            analyse["domaine_origine"] = self._extraire_domaine_filiere(profil["filiere_actuelle"])
        
        return analyse
    
    def _analyser_metier_envisage(self, carriere_envisagee: str) -> Dict[str, Any]:
        """Analyse le métier envisagé par l'utilisateur"""
        
        metier = self.kb_loader.rechercher_metier(carriere_envisagee)
        
        if metier:
            return {
                "metier_trouve": True,
                "metier_obj": metier,
                "secteur": metier.secteur_activite,
                "demande_marche": metier.niveau_demande_marche,
                "pertinence_benin": metier.pertinence_realites_africaines_benin,
                "competences_requises": {
                    "techniques": metier.competences_requises_techniques,
                    "transversales": metier.competences_requises_transversales
                },
                "formations_typiques": metier.formations_typiques_generales
            }
        else:
            return {
                "metier_trouve": False,
                "suggestions_similaires": self._chercher_metiers_similaires(carriere_envisagee)
            }
    
    def _recommander_universites(self, profil: Dict) -> List[Dict]:
        """Recommande des universités basées sur le profil et la carrière envisagée"""
        
        carriere = profil["carriere_envisagee"]
        serie_bac = profil.get("serie_bac")
        
        # Rechercher directement dans la base de connaissances
        universites_directes = self.kb_loader.rechercher_universites_pour_metier(carriere, serie_bac)
        
        # Si peu de résultats, élargir la recherche
        if len(universites_directes) < 3:
            # Rechercher des métiers similaires
            metiers_similaires = self._chercher_metiers_similaires(carriere)
            for metier_similaire in metiers_similaires[:3]:
                universites_similaires = self.kb_loader.rechercher_universites_pour_metier(
                    metier_similaire, serie_bac
                )
                universites_directes.extend(universites_similaires)
        
        # Dédoublonner et limiter
        universites_uniques = []
        noms_vus = set()
        
        for univ in universites_directes:
            if univ["nom_universite"] not in noms_vus:
                universites_uniques.append(univ)
                noms_vus.add(univ["nom_universite"])
        
        # Prioriser les universités publiques
        universites_uniques.sort(key=lambda x: (x["statut"] != "Public", x["nom_universite"]))
        
        return universites_uniques[:10]  # Limiter à 10 recommandations
    
    def _proposer_carrieres_alternatives(self, profil: Dict) -> List[Metier]:
        """Propose des carrières alternatives basées sur le profil"""
        
        carriere_principale = profil["carriere_envisagee"]
        serie_bac = profil.get("serie_bac")
        
        alternatives = self.kb_loader.get_metiers_alternatifs(carriere_principale, limite=8)
        
        # Filtrer selon la série de BAC si disponible
        if serie_bac:
            alternatives_filtrees = []
            serie_lettre = serie_bac.split()[0]
            serie_type = self.series_bac_mapping.get(serie_lettre, {}).get("type", "")
            
            for metier in alternatives:
                # Logique simple de compatibilité série-métier
                compatible = self._verifier_compatibilite_serie_metier(serie_type, metier)
                if compatible:
                    alternatives_filtrees.append(metier)
            
            if alternatives_filtrees:
                return alternatives_filtrees[:5]
        
        return alternatives[:5]
    
    def _calculer_compatibilite(self, profil: Dict) -> Dict[str, float]:
        """Calcule des scores de compatibilité pour différents aspects"""
        
        scores = {
            "serie_metier": 0.0,
            "marche_benin": 0.0,
            "formation_disponible": 0.0
        }
        
        metier_analyse = self._analyser_metier_envisage(profil["carriere_envisagee"])
        
        if metier_analyse["metier_trouve"]:
            metier = metier_analyse["metier_obj"]
            
            # Score série-métier
            if profil.get("serie_bac"):
                serie_lettre = profil["serie_bac"].split()[0]
                scores["serie_metier"] = self._calculer_score_serie_metier(serie_lettre, metier)
            
            # Score marché béninois
            if metier.niveau_demande_marche:
                demande_mapping = {
                    "Très élevé": 1.0, "Élevé": 0.8, "Moyen": 0.6, 
                    "Faible": 0.4, "Très faible": 0.2
                }
                scores["marche_benin"] = demande_mapping.get(metier.niveau_demande_marche, 0.5)
            
            # Score formation disponible
            universites = self.kb_loader.rechercher_universites_pour_metier(
                profil["carriere_envisagee"], profil.get("serie_bac")
            )
            if universites:
                scores["formation_disponible"] = min(1.0, len(universites) / 3)  # Normalisé
        
        return scores
    
    def _suggerer_parcours(self, profil: Dict) -> Dict[str, Any]:
        """Suggère un parcours personnalisé"""
        
        parcours = {
            "etapes": [],
            "duree_totale": "À déterminer",
            "competences_a_developper": [],
            "conseils_specifiques": []
        }
        
        if profil["statut"] == "Élève (Futur Bachelier)":
            parcours["etapes"] = [
                "1. Réussir le Baccalauréat avec une mention appropriée",
                "2. S'inscrire dans une université/filière recommandée",
                "3. Compléter la formation initiale",
                "4. Effectuer des stages pratiques",
                "5. Obtenir le diplôme et rechercher un emploi/stage professionnel"
            ]
        else:
            parcours["etapes"] = [
                "1. Terminer la formation actuelle",
                "2. Évaluer les possibilités de spécialisation",
                "3. Considérer une formation complémentaire si nécessaire",
                "4. Développer l'expérience pratique",
                "5. Rechercher des opportunités dans le domaine visé"
            ]
        
        # Analyser le métier pour des conseils spécifiques
        metier_analyse = self._analyser_metier_envisage(profil["carriere_envisagee"])
        if metier_analyse["metier_trouve"]:
            metier = metier_analyse["metier_obj"]
            parcours["competences_a_developper"] = (
                metier.competences_requises_techniques[:3] + 
                metier.competences_requises_transversales[:2]
            )
        
        return parcours
    
    def _extraire_domaine_filiere(self, filiere: str) -> str:
        """Extrait le domaine d'étude d'une filière universitaire"""
        filiere_lower = filiere.lower()
        
        domaines = {
            "médecine": "Santé", "pharmacie": "Santé", "infirmier": "Santé",
            "informatique": "Technologies", "génie": "Ingénierie", "math": "Sciences",
            "droit": "Juridique", "avocat": "Juridique",
            "économie": "Économie", "gestion": "Gestion", "commerce": "Commerce",
            "lettres": "Lettres", "langue": "Langues", "communication": "Communication"
        }
        
        for mot_cle, domaine in domaines.items():
            if mot_cle in filiere_lower:
                return domaine
        
        return "Général"
    
    def _chercher_metiers_similaires(self, carriere: str) -> List[str]:
        """Recherche des métiers avec des noms similaires"""
        if not self.kb_loader.knowledge_base:
            return []
        
        carriere_lower = carriere.lower()
        similaires = []
        
        for metier in self.kb_loader.knowledge_base.metiers:
            nom_metier_lower = metier.nom_metier.lower()
            
            # Recherche de mots communs
            mots_carriere = set(re.findall(r'\w+', carriere_lower))
            mots_metier = set(re.findall(r'\w+', nom_metier_lower))
            
            intersection = mots_carriere & mots_metier
            if intersection:
                similaires.append(metier.nom_metier)
        
        return similaires[:5]
    
    def _verifier_compatibilite_serie_metier(self, serie_type: str, metier: Metier) -> bool:
        """Vérifie la compatibilité entre un type de série et un métier"""
        
        if not serie_type:
            return True  # Si pas de série définie, considérer compatible
        
        secteur_lower = metier.secteur_activite.lower()
        
        # Règles de compatibilité simplifiées
        compatibilites = {
            "scientifique": ["santé", "sciences", "ingénierie", "technique", "médecine", "recherche"],
            "littéraire": ["communication", "education", "langues", "culture", "média", "enseignement"],
            "économique": ["économie", "banque", "finance", "administration", "gestion"],
            "technique": ["technique", "ingénierie", "industrie", "construction", "technologie"],
            "tertiaire": ["commerce", "service", "vente", "administration", "secrétariat"]
        }
        
        mots_cles = compatibilites.get(serie_type, [])
        return any(mot in secteur_lower for mot in mots_cles)
    
    def _calculer_score_serie_metier(self, serie_lettre: str, metier: Metier) -> float:
        """Calcule un score de compatibilité entre série de BAC et métier"""
        
        if serie_lettre not in self.series_bac_mapping:
            return 0.5  # Score neutre si série inconnue
        
        serie_type = self.series_bac_mapping[serie_lettre]["type"]
        
        if self._verifier_compatibilite_serie_metier(serie_type, metier):
            return 0.8  # Bonne compatibilité
        else:
            return 0.3  # Compatibilité faible mais possible
    
    def generer_donnees_pour_llm(self, profil: Dict, recommandations: Dict) -> Dict[str, Any]:
        """Prépare les données pour l'analyse par le LLM"""
        
        return {
            "profil_etudiant": {
                "statut": profil["statut"],
                "serie_bac": profil.get("serie_bac"),
                "filiere_actuelle": profil.get("filiere_actuelle"),
                "carriere_envisagee": profil["carriere_envisagee"],
                "analyse_profil": recommandations["profil_analyse"]
            },
            "analyse_metier": recommandations["metier_analyse"],
            "universites_trouvees": len(recommandations["universites_recommandees"]),
            "universites_details": recommandations["universites_recommandees"][:3],  # Top 3
            "carrieres_alternatives": [
                {
                    "nom": metier.nom_metier,
                    "secteur": metier.secteur_activite,
                    "demande": metier.niveau_demande_marche
                } 
                for metier in recommandations["carrieres_alternatives"][:3]
            ],
            "scores_compatibilite": recommandations["compatibilite_scores"],
            "contexte_benin": True
        }