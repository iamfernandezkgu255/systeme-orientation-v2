"""
Module pour charger et interroger la base de connaissances knowledge_base_benin_v2.json
"""

import json
import os
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import streamlit as st

class Metier(BaseModel):
    """Modèle de données pour un métier"""
    nom_metier: str
    description: str
    secteur_activite: str
    competences_requises_techniques: List[str] = Field(default_factory=list)
    competences_requises_transversales: List[str] = Field(default_factory=list)
    formations_typiques_generales: List[str] = Field(default_factory=list)
    niveau_demande_marche: str = ""
    perspectives_croissance: Any = None  # boolean ou string
    pertinence_realites_africaines_benin: str = ""

class SecteurPorteur(BaseModel):
    """Modèle de données pour un secteur porteur"""
    nom_secteur: str
    description: str
    croissance_prevue: str = ""
    metiers_cles: List[str] = Field(default_factory=list)

class Competence(BaseModel):
    """Modèle de données pour une compétence"""
    nom_competence: str
    description: str
    type_competence: str = ""  # technique, transversale, etc.

class FormationGenerale(BaseModel):
    """Modèle de données pour une formation générale"""
    nom_formation_generale: str
    description: str
    metiers_prepares: List[str] = Field(default_factory=list)
    type: str = ""

class Filiere(BaseModel):
    """Modèle de données pour une filière d'université"""
    nom_filiere: str
    description_filiere: str = ""
    diplome_delivre: str
    duree_etudes_ans: int
    conditions_admission_texte: str = ""
    series_bac_requises: List[str] = Field(default_factory=list)
    autres_prerequis: str = ""
    metiers_vises_typiques: List[str] = Field(default_factory=list)

class FaculteEcole(BaseModel):
    """Modèle de données pour une faculté ou école"""
    nom_faculte_ecole: str
    filieres: List[Filiere] = Field(default_factory=list)

class Universite(BaseModel):
    """Modèle de données pour une université"""
    nom_universite: str
    sigle: str = ""
    statut: str  # Public, Privé Agréé
    localisation: str = ""
    site_web: str = ""
    facultes_ecoles: List[FaculteEcole] = Field(default_factory=list)

class KnowledgeBase(BaseModel):
    """Modèle de données pour la base de connaissances complète"""
    metiers: List[Metier] = Field(default_factory=list)
    secteurs_porteurs: List[SecteurPorteur] = Field(default_factory=list)
    competences: List[Competence] = Field(default_factory=list)
    formations_generales: List[FormationGenerale] = Field(default_factory=list)
    universites: List[Universite] = Field(default_factory=list)

class KnowledgeBaseLoader:
    """Classe pour charger et interroger la base de connaissances"""
    
    def __init__(self, fichier_path: str = "knowledge_base_benin_v2.json"):
        """Initialise le chargeur avec le fichier de base de connaissances"""
        # Assurer un chemin absolu pour éviter les problèmes de contexte Streamlit
        if not os.path.isabs(fichier_path):
            # Chercher dans le répertoire courant et le répertoire du script
            current_dir = os.getcwd()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            if os.path.exists(os.path.join(current_dir, fichier_path)):
                self.fichier_path = os.path.join(current_dir, fichier_path)
            elif os.path.exists(os.path.join(script_dir, fichier_path)):
                self.fichier_path = os.path.join(script_dir, fichier_path)
            else:
                self.fichier_path = fichier_path  # Garder le chemin original
        else:
            self.fichier_path = fichier_path
            
        self.knowledge_base: Optional[KnowledgeBase] = None
        self.charger_base_connaissances()
    
    def charger_base_connaissances(self) -> None:
        """Charge la base de connaissances depuis le fichier JSON"""
        try:
            if not os.path.exists(self.fichier_path):
                # Créer un fichier exemple si n'existe pas
                self.creer_fichier_exemple()
            
            with open(self.fichier_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Conversion des données en objets Pydantic avec gestion d'erreur
            try:
                self.knowledge_base = KnowledgeBase(**data)
            except Exception as e:
                st.warning(f"Erreur lors de la validation des données : {e}")
                # Fallback: utiliser les données brutes
                self.knowledge_base = self._load_raw_data(data)
                
        except FileNotFoundError:
            try:
                st.error(f"Fichier {self.fichier_path} non trouvé.")
            except:
                print(f"❌ Fichier {self.fichier_path} non trouvé.")
            self.knowledge_base = KnowledgeBase()
        except json.JSONDecodeError as e:
            try:
                st.error(f"Erreur de format JSON : {e}")
            except:
                print(f"❌ Erreur de format JSON : {e}")
            self.knowledge_base = KnowledgeBase()
        except Exception as e:
            try:
                st.error(f"Erreur lors du chargement : {e}")
            except:
                print(f"❌ Erreur lors du chargement : {e}")
            self.knowledge_base = KnowledgeBase()
    
    def _load_raw_data(self, data: Dict) -> KnowledgeBase:
        """Charge les données même si elles ne sont pas parfaitement structurées"""
        kb = KnowledgeBase()
        
        # Chargement avec gestion d'erreur pour chaque section
        if 'metiers' in data:
            for metier_data in data['metiers']:
                try:
                    kb.metiers.append(Metier(**metier_data))
                except Exception:
                    # Ignorer les entrées malformées
                    pass
        
        if 'secteurs_porteurs' in data:
            for secteur_data in data['secteurs_porteurs']:
                try:
                    kb.secteurs_porteurs.append(SecteurPorteur(**secteur_data))
                except Exception:
                    pass
        
        if 'competences' in data:
            for comp_data in data['competences']:
                try:
                    kb.competences.append(Competence(**comp_data))
                except Exception:
                    pass
        
        if 'formations_generales' in data:
            for form_data in data['formations_generales']:
                try:
                    kb.formations_generales.append(FormationGenerale(**form_data))
                except Exception:
                    pass
        
        if 'universites' in data:
            for univ_data in data['universites']:
                try:
                    # Traitement spécial pour les universités avec structure complexe
                    univ = Universite(
                        nom_universite=univ_data.get('nom_universite', ''),
                        sigle=univ_data.get('sigle', ''),
                        statut=univ_data.get('statut', ''),
                        localisation=univ_data.get('localisation', ''),
                        site_web=univ_data.get('site_web', '')
                    )
                    
                    # Traitement des facultés
                    if 'facultes_ecoles' in univ_data:
                        for fac_data in univ_data['facultes_ecoles']:
                            try:
                                faculte = FaculteEcole(nom_faculte_ecole=fac_data.get('nom_faculte_ecole', ''))
                                
                                # Traitement des filières
                                if 'filieres' in fac_data:
                                    for fil_data in fac_data['filieres']:
                                        try:
                                            filiere = Filiere(**fil_data)
                                            faculte.filieres.append(filiere)
                                        except Exception:
                                            pass
                                
                                univ.facultes_ecoles.append(faculte)
                            except Exception:
                                pass
                    
                    kb.universites.append(univ)
                except Exception:
                    pass
        
        return kb
    
    def creer_fichier_exemple(self) -> None:
        """Crée un fichier exemple avec quelques données"""
        exemple_data = {
            "metiers": [
                {
                    "nom_metier": "Médecin",
                    "description": "Professionnel de santé qui diagnostique et traite les maladies",
                    "secteur_activite": "Santé",
                    "competences_requises_techniques": ["Anatomie", "Physiologie", "Pharmacologie"],
                    "competences_requises_transversales": ["Communication", "Empathie", "Gestion du stress"],
                    "formations_typiques_generales": ["Doctorat en Médecine"],
                    "niveau_demande_marche": "Très élevé",
                    "perspectives_croissance": True,
                    "pertinence_realites_africaines_benin": "Très pertinent, forte demande en santé publique"
                }
            ],
            "secteurs_porteurs": [
                {
                    "nom_secteur": "Santé",
                    "description": "Secteur des soins de santé et services médicaux",
                    "croissance_prevue": "Forte croissance",
                    "metiers_cles": ["Médecin", "Infirmier", "Pharmacien"]
                }
            ],
            "competences": [
                {
                    "nom_competence": "Communication",
                    "description": "Capacité à transmettre efficacement des informations",
                    "type_competence": "Transversale"
                }
            ],
            "formations_generales": [
                {
                    "nom_formation_generale": "Doctorat en Médecine",
                    "description": "Formation médicale complète de 7 ans",
                    "metiers_prepares": ["Médecin", "Chirurgien"],
                    "type": "Universitaire"
                }
            ],
            "universites": [
                {
                    "nom_universite": "Université d'Abomey-Calavi",
                    "sigle": "UAC",
                    "statut": "Public",
                    "localisation": "Abomey-Calavi",
                    "site_web": "https://www.uac.bj",
                    "facultes_ecoles": [
                        {
                            "nom_faculte_ecole": "Faculté des Sciences de la Santé",
                            "filieres": [
                                {
                                    "nom_filiere": "Doctorat en Médecine",
                                    "description_filiere": "Formation médicale générale",
                                    "diplome_delivre": "Doctorat",
                                    "duree_etudes_ans": 7,
                                    "conditions_admission_texte": "BAC série D ou C avec mention",
                                    "series_bac_requises": ["D", "C"],
                                    "autres_prerequis": "Concours d'entrée",
                                    "metiers_vises_typiques": ["Médecin généraliste", "Médecin spécialiste"]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        with open(self.fichier_path, 'w', encoding='utf-8') as f:
            json.dump(exemple_data, f, indent=2, ensure_ascii=False)
        
        st.info(f"Fichier exemple créé : {self.fichier_path}")
    
    def rechercher_metier(self, nom_metier: str) -> Optional[Metier]:
        """Recherche un métier par nom (recherche floue)"""
        if not self.knowledge_base:
            return None
        
        nom_metier_lower = nom_metier.lower()
        
        # Recherche exacte d'abord
        for metier in self.knowledge_base.metiers:
            if metier.nom_metier.lower() == nom_metier_lower:
                return metier
        
        # Recherche partielle
        for metier in self.knowledge_base.metiers:
            if nom_metier_lower in metier.nom_metier.lower():
                return metier
        
        return None
    
    def rechercher_metiers_par_secteur(self, secteur: str) -> List[Metier]:
        """Recherche les métiers d'un secteur donné"""
        if not self.knowledge_base:
            return []
        
        secteur_lower = secteur.lower()
        metiers_secteur = []
        
        for metier in self.knowledge_base.metiers:
            if secteur_lower in metier.secteur_activite.lower():
                metiers_secteur.append(metier)
        
        return metiers_secteur
    
    def rechercher_universites_pour_metier(self, nom_metier: str, serie_bac: Optional[str] = None) -> List[Dict]:
        """Recherche les universités et filières pour un métier donné"""
        if not self.knowledge_base:
            return []
        
        resultats = []
        nom_metier_lower = nom_metier.lower()
        
        for universite in self.knowledge_base.universites:
            filieres_compatibles = []
            
            for faculte in universite.facultes_ecoles:
                for filiere in faculte.filieres:
                    # Vérifier si la filière prépare au métier
                    metier_compatible = any(
                        nom_metier_lower in metier_vise.lower() 
                        for metier_vise in filiere.metiers_vises_typiques
                    )
                    
                    if metier_compatible:
                        # Vérifier la compatibilité avec la série de BAC
                        serie_compatible = True
                        if serie_bac and filiere.series_bac_requises:
                            # Extraire la lettre de la série (ex: "D" depuis "D (Mathématiques-Sciences Naturelles)")
                            serie_lettre = serie_bac.split()[0] if serie_bac else ""
                            serie_compatible = (
                                any(serie_lettre in serie_req for serie_req in filiere.series_bac_requises) or
                                "Toutes" in str(filiere.series_bac_requises)
                            )
                        
                        if serie_compatible:
                            filieres_compatibles.append({
                                "faculte": faculte.nom_faculte_ecole,
                                **filiere.dict()
                            })
            
            if filieres_compatibles:
                resultats.append({
                    **universite.dict(),
                    "filieres_recommandees": filieres_compatibles
                })
        
        return resultats
    
    def get_metiers_alternatifs(self, metier_principal: str, limite: int = 5) -> List[Metier]:
        """Propose des métiers alternatifs basés sur le secteur ou les compétences"""
        if not self.knowledge_base:
            return []
        
        metier_obj = self.rechercher_metier(metier_principal)
        if not metier_obj:
            return []
        
        alternatives = []
        
        # Métiers du même secteur
        metiers_meme_secteur = self.rechercher_metiers_par_secteur(metier_obj.secteur_activite)
        for metier in metiers_meme_secteur:
            if metier.nom_metier != metier_obj.nom_metier:
                alternatives.append(metier)
        
        # Métiers avec compétences similaires
        for metier in self.knowledge_base.metiers:
            if metier.nom_metier != metier_obj.nom_metier and metier not in alternatives:
                competences_communes = set(metier_obj.competences_requises_techniques + 
                                         metier_obj.competences_requises_transversales) & \
                                       set(metier.competences_requises_techniques + 
                                         metier.competences_requises_transversales)
                if len(competences_communes) >= 2:  # Au moins 2 compétences en commun
                    alternatives.append(metier)
        
        return alternatives[:limite]
    
    def get_statistics(self) -> Dict[str, int]:
        """Retourne des statistiques sur la base de données"""
        if not self.knowledge_base:
            return {}
        
        nb_filieres = sum(
            len(faculte.filieres) 
            for universite in self.knowledge_base.universites 
            for faculte in universite.facultes_ecoles
        )
        
        return {
            "nb_metiers": len(self.knowledge_base.metiers),
            "nb_universites": len(self.knowledge_base.universites),
            "nb_secteurs": len(self.knowledge_base.secteurs_porteurs),
            "nb_competences": len(self.knowledge_base.competences),
            "nb_formations": len(self.knowledge_base.formations_generales),
            "nb_filieres": nb_filieres
        }
    
    def valider_base_connaissances(self) -> Dict[str, List[str]]:
        """Valide la base de connaissances et retourne les erreurs trouvées"""
        erreurs = {"avertissements": [], "erreurs": []}
        
        if not self.knowledge_base:
            erreurs["erreurs"].append("Base de connaissances non chargée")
            return erreurs
        
        # Vérifications de base
        if not self.knowledge_base.metiers:
            erreurs["avertissements"].append("Aucun métier défini")
        
        if not self.knowledge_base.universites:
            erreurs["avertissements"].append("Aucune université définie")
        
        # Vérifier la cohérence des références
        metiers_references = {metier.nom_metier for metier in self.knowledge_base.metiers}
        
        for universite in self.knowledge_base.universites:
            for faculte in universite.facultes_ecoles:
                for filiere in faculte.filieres:
                    for metier_vise in filiere.metiers_vises_typiques:
                        if metier_vise not in metiers_references:
                            erreurs["avertissements"].append(
                                f"Métier '{metier_vise}' référencé dans {filiere.nom_filiere} "
                                f"mais non défini dans la base"
                            )
        
        return erreurs
