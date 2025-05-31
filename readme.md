# 🎓 Système d'Aide à l'Orientation Professionnelle pour Étudiants au Bénin (Version 2)

Une application web développée avec Streamlit pour aider les élèves et étudiants béninois à faire des choix d'orientation éclairés en fonction de leur profil et des opportunités disponibles au Bénin.

## 🌟 Fonctionnalités

- **Analyse personnalisée** : Évaluation du profil étudiant et de ses choix de carrière
- **Recommandations d'universités** : Suggestions d'établissements publics et privés agréés
- **Carrières alternatives** : Proposition de métiers connexes adaptés au profil
- **Intelligence artificielle** : Analyse avancée via l'API DeepSeek d'OpenRouter
- **Base de données locale** : Métiers, universités et filières du Bénin
- **Interface intuitive** : Application web simple et accessible

## 🏗️ Architecture du Projet

```
orientation_benin_v2/
├── app_student.py                    # Application Streamlit principale
├── knowledge_base_loader.py          # Chargeur de base de connaissances
├── recommendation_logic_student.py   # Moteur de recommandation
├── llm_interface.py                  # Interface API DeepSeek/OpenRouter
├── requirements.txt                  # Dépendances Python
├── knowledge_base_benin_v2.json     # Base de données (à créer)
├── README.md                        # Documentation
└── .streamlit/
    └── secrets.toml                 # Configuration des secrets (à créer)
```

## 🚀 Installation et Configuration

### 1. Prérequis

- Python 3.8 ou plus récent
- Compte OpenRouter.ai (pour l'API DeepSeek)
- Git (optionnel)

### 2. Installation des dépendances

```bash
# Cloner ou télécharger le projet
git clone <url_du_projet>
cd orientation_benin_v2

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration de l'API OpenRouter

#### a) Obtenir une clé API

1. Créez un compte sur [OpenRouter.ai](https://openrouter.ai)
2. Générez une clé API dans votre dashboard
3. Notez votre clé API (elle commence généralement par `sk-or-`)

#### b) Configuration des secrets Streamlit

Créez un dossier `.streamlit` et un fichier `secrets.toml` :

```bash
mkdir .streamlit
```

Créez le fichier `.streamlit/secrets.toml` avec le contenu suivant :

```toml
[openrouter]
api_key = "sk-or-votre_clé_api_ici"
```

**⚠️ Important :** 
- Ne committez jamais ce fichier dans Git
- Ajoutez `.streamlit/secrets.toml` à votre `.gitignore`

### 4. Configuration de la base de connaissances

#### Option A : Utilisation du fichier exemple

L'application créera automatiquement un fichier `knowledge_base_benin_v2.json` exemple au premier lancement.

#### Option B : Création manuelle complète

Créez le fichier `knowledge_base_benin_v2.json` avec la structure suivante :

```json
{
  "metiers": [
    {
      "nom_metier": "Médecin",
      "description": "Professionnel de santé qui diagnostique et traite les maladies",
      "secteur_activite": "Santé",
      "competences_requises_techniques": ["Anatomie", "Physiologie", "Pharmacologie"],
      "competences_requises_transversales": ["Communication", "Empathie"],
      "formations_typiques_generales": ["Doctorat en Médecine"],
      "niveau_demande_marche": "Très élevé",
      "perspectives_croissance": true,
      "pertinence_realites_africaines_benin": "Très pertinent"
    }
  ],
  "secteurs_porteurs": [
    {
      "nom_secteur": "Santé",
      "description": "Secteur des soins de santé",
      "croissance_prevue": "Forte",
      "metiers_cles": ["Médecin", "Infirmier"]
    }
  ],
  "competences": [
    {
      "nom_competence": "Communication",
      "description": "Capacité à communiquer efficacement",
      "type_competence": "Transversale"
    }
  ],
  "formations_generales": [
    {
      "nom_formation_generale": "Doctorat en Médecine",
      "description": "Formation médicale complète",
      "metiers_prepares": ["Médecin"],
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
              "metiers_vises_typiques": ["Médecin généraliste"]
            }
          ]
        }
      ]
    }
  ]
}
```

## 🔧 Utilisation

### Lancement local

```bash
streamlit run app_student.py
```

L'application sera accessible à l'adresse : `http://localhost:8501`

### Déploiement sur Streamlit Community Cloud

1. Pushez votre code sur GitHub
2. Connectez-vous à [share.streamlit.io](https://share.streamlit.io)
3. Déployez votre application
4. Configurez les secrets dans l'interface Streamlit Cloud :
   - Allez dans les paramètres de votre app
   - Section "Secrets"
   - Ajoutez votre configuration TOML

## 📊 Utilisation de l'Application

### Pour les Élèves (Futurs Bacheliers)

1. **Sélectionnez** "Élève (Futur Bachelier)"
2. **Choisissez** votre série de BAC (A1, A2, B, C, D, E, EA, F1-F4, G1-G3)
3. **Indiquez** la carrière que vous envisagez
4. **Cliquez** sur "Analyser mon profil"

### Pour les Étudiants Universitaires

1. **Sélectionnez** "Étudiant Universitaire"
2. **Renseignez** votre filière actuelle
3. **Indiquez** la carrière que vous envisagez
4. **Cliquez** sur "Analyser mon profil"

### Résultats Fournis

- **Analyse personnalisée** de votre choix de carrière
- **Liste d'universités** adaptées à votre profil
- **Filières recommandées** avec conditions d'admission
- **Carrières alternatives** à considérer
- **Parcours personnalisé** avec étapes concrètes

## 🛠️ Structure des Données

### Séries de BAC Supportées

| Série | Domaine | Type |
|-------|---------|------|
| A1 | Lettres-Langues | Littéraire |
| A2 | Lettres-Sciences Sociales | Littéraire |
| B | Sciences Sociales | Économique |
| C | Mathématiques-Sciences Physiques | Scientifique |
| D | Mathématiques-Sciences Naturelles | Scientifique |
| E | Mathématiques-Techniques | Technique |
| EA | Économie-Administration | Économique |
| F1-F4 | Techniques diverses | Technique |
| G1-G3 | Tertiaire | Tertiaire |

### Statuts d'Universités

- **Public** : Universités publiques du Bénin
- **Privé Agréé** : Établissements privés reconnus par l'État

## 🔍 Fonctionnalités Avancées

### Système de Recommandation

- **Filtrage par compatibilité** série BAC / métier
- **Analyse de la demande** sur le marché béninois
- **Suggestions alternatives** basées sur le secteur et les compétences
- **Scores de compatibilité** multidimensionnels

### Intelligence Artificielle

- **Analyse contextuelle** adaptée au Bénin
- **Conseils personnalisés** selon le profil
- **Parcours suggérés** avec étapes concrètes
- **Fallback intelligent** en cas de problème API

## 🚨 Dépannage

### Problèmes Fréquents

#### "Clé API non trouvée"
- Vérifiez que le fichier `.streamlit/secrets.toml` existe
- Confirmez que la clé API est correcte
- Redémarrez l'application

#### "Fichier de base de connaissances non trouvé"
- L'application créera un fichier exemple automatiquement
- Vous pouvez populer ce fichier avec vos propres données

#### "Erreur de connexion API"
- Vérifiez votre connexion internet
- Confirmez que votre compte OpenRouter est actif
- Vérifiez les quotas de votre clé API

### Mode Dégradé

L'application fonctionne même sans API :
- **Analyse de base** sans IA
- **Recommandations** basées sur la base de données locale
- **Fonctionnalités** de recherche et filtrage

## 🤝 Contribution

### Ajouter des Données

Pour enrichir la base de connaissances :

1. **Éditez** `knowledge_base_benin_v2.json`
2. **Respectez** la structure de données
3. **Testez** l'application après modifications
4. **Validez** avec la fonction de validation intégrée

### Améliorer le Code

1. **Forkez** le projet
2. **Créez** une branche pour vos modifications
3. **Testez** vos changements
4. **Soumettez** une pull request

## 📈 Métriques et Suivi

L'application fournit des statistiques sur :
- Nombre de métiers dans la base
- Nombre d'universités référencées
- Nombre de filières disponibles
- Taux de compatibilité des profils

## 🔐 Sécurité et Confidentialité

- **Aucune donnée personnelle** n'est stockée
- **Les analyses** sont effectuées en temps réel
- **Les clés API** sont sécurisées via Streamlit Secrets
- **Respect** de la vie privée des utilisateurs

## 📄 Licence

Ce projet est développé pour l'aide à l'orientation au Bénin. Consultez le fichier LICENSE pour plus de détails.

## 🆘 Support

Pour obtenir de l'aide :
1. Consultez cette documentation
2. Vérifiez les problèmes fréquents ci-dessus
3. Contactez l'équipe de développement

---

**Développé avec ❤️ pour l'éducation au Bénin**
