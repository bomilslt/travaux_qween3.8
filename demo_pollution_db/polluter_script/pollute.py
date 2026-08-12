"""
Script pollueur - Génère des inscriptions en boucle
Ce script simule des tentatives d'inscription massives pour démontrer
comment un système peut être saturé.
"""

import requests
import random
import string
import json
import time
from datetime import datetime

# Configuration
TARGET_BACKEND = 'http://localhost:5000'
MOCK_MAILGUN_FILE = '../mock_mailgun/incoming_emails.json'

# Listes de préfixes pour génération aléatoire
PRENOMS = ['Jean', 'Marie', 'Pierre', 'Sophie', 'Luc', 'Emma', 'Thomas', 'Lea', 'Nicolas', 'Chloe',
           'Alexandre', 'Julie', 'Maxime', 'Sarah', 'Antoine', 'Manon', 'Julien', 'Laura', 'David', 'Camille']

NOMS = ['Dupont', 'Martin', 'Bernard', 'Petit', 'Robert', 'Richard', 'Durand', 'Dubois', 'Moreau', 'Laurent',
        'Simon', 'Michel', 'Lefebvre', 'Leroy', 'Garnier', 'Andre', 'Mercier', 'Blanc', 'Guerin', 'Boyer']

DOMAINES = ['gmail.com', 'yahoo.fr', 'hotmail.com', 'outlook.fr', 'mail.com', 
            'protonmail.com', 'icloud.com', 'live.fr', 'wanadoo.fr', 'orange.fr']

def generate_random_prefix(length=6):
    """Génère un préfixe aléatoire"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_identity():
    """Génère une identité complète aléatoire"""
    prenom = random.choice(PRENOMS)
    nom = random.choice(NOMS)
    prefix = generate_random_prefix()
    
    # Génération du nom d'utilisateur (première combinaison disponible)
    username_options = [
        f"{prenom.lower()}{nom.lower()}",
        f"{prenom.lower()}.{nom.lower()}",
        f"{prenom[0]}{nom.lower()}",
        f"{prenom}{generate_random_prefix(3)}",
    ]
    username = random.choice(username_options)
    
    # Génération de l'email avec préfixe aléatoire
    email_prefix = generate_random_prefix(8)
    domaine = random.choice(DOMAINES)
    email = f"{email_prefix}.{prenom.lower()}.{nom.lower()}@{domaine}"
    
    # Génération du mot de passe
    password = 'Pass123!' + generate_random_prefix(4)
    
    return {
        'prenom': prenom,
        'nom': nom,
        'username': username,
        'email': email,
        'password': password
    }

def get_otp_from_mailgun(email):
    """Récupère l'OTP depuis le fichier Mailgun mocké"""
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            with open(MOCK_MAILGUN_FILE, 'r') as f:
                emails = json.load(f)
            
            # Chercher l'email correspondant
            for mail in reversed(emails):  # Commencer par le plus récent
                if mail.get('recipient') == email:
                    otp = mail.get('otp_code')
                    if otp:
                        print(f"  ✓ OTP trouvé: {otp}")
                        return otp
            
            print(f"  ⏳ Attente de l'OTP... (tentative {attempt + 1}/{max_attempts})")
            time.sleep(0.5)
            
        except FileNotFoundError:
            print(f"  ⏳ Fichier non trouvé, attente... (tentative {attempt + 1}/{max_attempts})")
            time.sleep(0.5)
        except json.JSONDecodeError:
            print(f"  ⏳ Fichier en cours d'écriture, attente... (tentative {attempt + 1}/{max_attempts})")
            time.sleep(0.5)
    
    return None

def register_user():
    """Inscrit un utilisateur complet"""
    # Générer une identité
    identity = generate_identity()
    print(f"\n📝 Nouvelle inscription:")
    print(f"   Email: {identity['email']}")
    print(f"   Password: {identity['password']}")
    
    # Étape 1: Demander l'inscription
    try:
        response = requests.post(
            f'{TARGET_BACKEND}/api/register',
            json={'email': identity['email']},
            timeout=5
        )
        
        if response.status_code != 200:
            print(f"   ❌ Erreur registration: {response.json().get('error', 'Unknown')}")
            return False
        
        print(f"   ✓ Registration initiée, OTP envoyé")
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Erreur connexion backend: {e}")
        return False
    
    # Étape 2: Récupérer l'OTP en boucle
    otp = get_otp_from_mailgun(identity['email'])
    
    if not otp:
        print(f"   ❌ OTP non reçu après {max_attempts} tentatives")
        return False
    
    # Étape 3: Vérifier l'OTP et finaliser l'inscription
    try:
        response = requests.post(
            f'{TARGET_BACKEND}/api/verify-otp',
            json={
                'email': identity['email'],
                'otp': otp,
                'password': identity['password']
            },
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Inscription réussie!")
            print(f"      Token: {result.get('token', 'N/A')[:16]}...")
            return True
        else:
            print(f"   ❌ Erreur vérification: {response.json().get('error', 'Unknown')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Erreur connexion backend: {e}")
        return False

def main():
    """Boucle principale de pollution"""
    print("🚀 Script de pollution démarré")
    print(f"   Cible: {TARGET_BACKEND}")
    print(f"   Appuyez sur Ctrl+C pour arrêter\n")
    
    count_success = 0
    count_failure = 0
    start_time = time.time()
    
    try:
        while True:
            print(f"\n{'='*60}")
            print(f"📊 Statistiques: {count_success} succès | {count_failure} échecs")
            print(f"⏱️  Temps écoulé: {time.time() - start_time:.1f}s")
            print(f"{'='*60}")
            
            if register_user():
                count_success += 1
            else:
                count_failure += 1
            
            # Petit délai entre chaque inscription
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Arrêt demandé par l'utilisateur")
        print(f"📊 Bilan final: {count_success} inscriptions réussies, {count_failure} échecs")
        print(f"⏱️  Durée totale: {time.time() - start_time:.1f}s")

if __name__ == '__main__':
    main()
