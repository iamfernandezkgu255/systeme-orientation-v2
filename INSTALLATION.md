# Guide d'Installation - Système d'Orientation Bénin

## 🚀 Installation Rapide

### 1. Prérequis
```bash
# Python 3.8 ou plus récent
python --version

# Git (optionnel)
git --version
```

### 2. Installation des dépendances
```bash
# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration des secrets (optionnelle)

Pour utiliser l'IA DeepSeek via OpenRouter:

1. Créez un compte sur [OpenRouter.ai](https://openrouter.ai)
2. Générez une clé API
3. Copiez le fichier de configuration:
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```
4. Éditez `.streamlit/secrets.toml` avec votre clé API:
```toml
[openrouter]
api_key = "sk-or-votre_vraie_cle_api"
```

### 4. Lancement de l'application
```bash
streamlit run app_student.py
```

L'application sera accessible à l'adresse: `http://localhost:8501`

## 🔧 Fonctionnalités

✅ **Sans configuration API:**
- Analyse de base des profils
- Recommandations d'universités
- Suggestions de carrières alternatives
- Parcours personnalisés

✅ **Avec API OpenRouter:**
- Analyse IA avancée
- Conseils personnalisés
- Recommandations contextualisées au Bénin

## 🧪 Test de l'installation

1. Lancez l'application
2. Utilisez les "Outils de diagnostic" dans la barre latérale
3. Testez avec un profil d'exemple:
   - Statut: Élève (Futur Bachelier)
   - Série BAC: C (Mathématiques-Sciences Physiques)
   - Carrière: Médecin

## 📊 Base de données incluse

- **10 métiers** représentatifs du Bénin
- **5 universités** publiques et privées agréées
- **6 secteurs porteurs** de l'économie béninoise
- **25+ filières** avec conditions d'admission

## 🚨 Dépannage

### Problème: "Erreur lors de l'initialisation"
**Solution:** Vérifiez que le fichier `knowledge_base_benin_v2.json` existe et est valide.

### Problème: "Clé API non trouvée"
**Solution:** L'application fonctionne sans API. Pour l'IA, configurez `.streamlit/secrets.toml`

### Problème: Port déjà utilisé
**Solution:** Lancez avec un port différent:
```bash
streamlit run app_student.py --server.port 8502
```

## 📈 Performance

- **Démarrage:** ~2-5 secondes
- **Analyse complète:** ~3-10 secondes (selon API)
- **Mode dégradé:** ~1-2 secondes