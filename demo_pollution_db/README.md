# Démonstration de Pollution de Base de Données

Ce projet éducatif montre comment un système d'authentification par OTP peut être saturé par des inscriptions automatisées.

## ⚠️ Avertissement

Ce code est fourni **uniquement à des fins éducatives**. Ne l'utilisez jamais sur des systèmes que vous ne possédez pas ou sans autorisation explicite.

## Architecture

```
┌─────────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  Polluter Script    │────▶│  Target Backend  │────▶│  Mock Mailgun       │
│  (pollute.py)       │     │  (app.py:5000)   │     │  (incoming_emails)  │
└─────────────────────┘     └──────────────────┘     └─────────────────────┘
         ▲                         │
         │                         ▼
         └─────────────────  users.csv  ────────────────┘
```

## Installation

```bash
cd /workspace/demo_pollution_db
pip install -r requirements.txt
```

## Démarrage

### Terminal 1 - Lancer le backend cible
```bash
cd target_backend
python app.py
```

Le backend sera disponible sur `http://localhost:5000`

### Terminal 2 - Lancer le script pollueur
```bash
cd polluter_script
python pollute.py
```

## Fonctionnement

1. **Génération d'identité**: Le script crée des identités aléatoires avec:
   - Prénoms et noms français aléatoires
   - Préfixes aléatoires pour les emails
   - Domaines variés (gmail, yahoo, hotmail, etc.)

2. **Inscription**: 
   - Appel à `/api/register` avec l'email généré
   - Le backend génère un OTP et le stocke dans le mock Mailgun

3. **Récupération de l'OTP**:
   - Le script pollue en boucle le fichier `incoming_emails.json`
   - Il extrait l'OTP correspondant à l'email

4. **Validation**:
   - Envoi de l'OTP à `/api/verify-otp`
   - Création du compte et stockage dans `users.csv`

## Fichiers générés

- `target_backend/users.csv`: Base de données des utilisateurs inscrits
- `mock_mailgun/incoming_emails.json`: Simulation des emails reçus

## Endpoints API

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/register` | POST | Initie une inscription avec envoi d'OTP |
| `/api/verify-otp` | POST | Vérifie l'OTP et finalise l'inscription |
| `/api/users` | GET | Liste tous les utilisateurs inscrits |

## Mesures de protection recommandées

Pour protéger votre système contre ce type d'attaque:

1. **Rate limiting**: Limiter le nombre de requêtes par IP
2. **CAPTCHA**: Ajouter une vérification humaine
3. **Validation d'email**: Confirmer la propriété de l'email avant inscription
4. **Cooldown entre tentatives**: Délai minimum entre deux inscriptions
5. **Surveillance**: Détecter les patterns d'inscription automatisée

## Auteur

Créé à des fins éducatives pour comprendre les vulnérabilités des systèmes d'authentification.
