"""
Backend cible - Système d'authentification avec OTP
Ce backend simule un service d'inscription réel qui envoie des OTP par email.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import string
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Stockage des utilisateurs (simulation CSV)
USERS_FILE = 'users.csv'
OTP_STORAGE = {}  # Stocke les OTP temporaires

def generate_otp():
    """Génère un code OTP à 6 chiffres"""
    return ''.join(random.choices(string.digits, k=6))

def load_users():
    """Charge les utilisateurs depuis le fichier CSV"""
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, 'r') as f:
        lines = f.readlines()[1:]  # Skip header
        users = []
        for line in lines:
            parts = line.strip().split(',')
            if len(parts) >= 3:
                users.append({
                    'email': parts[0],
                    'password': parts[1],
                    'token': parts[2]
                })
        return users

def save_user(email, password, token):
    """Sauvegarde un utilisateur dans le fichier CSV"""
    file_exists = os.path.exists(USERS_FILE)
    with open(USERS_FILE, 'a') as f:
        if not file_exists:
            f.write('email,password,token,created_at\n')
        created_at = datetime.now().isoformat()
        f.write(f'{email},{password},{token},{created_at}\n')

@app.route('/api/register', methods=['POST'])
def register():
    """Endpoint d'inscription - envoie un OTP"""
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email requis'}), 400
    
    # Vérifier si l'utilisateur existe déjà
    users = load_users()
    if any(u['email'] == email for u in users):
        return jsonify({'error': 'Utilisateur déjà existant'}), 400
    
    # Générer et stocker l'OTP
    otp = generate_otp()
    OTP_STORAGE[email] = {
        'code': otp,
        'expires_at': datetime.now() + timedelta(minutes=5)
    }
    
    # Simuler l'envoi d'email via Mailgun (en réalité, on le loggue pour la démo)
    print(f"\n[MAILGUN SIMULATION] Envoi d'OTP à {email}: {otp}")
    
    # Dans une vraie implémentation, on appellerait l'API Mailgun ici
    # Pour cette démo, on simule le routage vers le mock Mailgun
    try:
        with open('../mock_mailgun/incoming_emails.json', 'r') as f:
            emails = json.load(f)
    except:
        emails = []
    
    emails.append({
        'recipient': email,
        'subject': 'Votre code OTP',
        'body': f'Votre code OTP est: {otp}',
        'timestamp': datetime.now().isoformat(),
        'otp_code': otp
    })
    
    with open('../mock_mailgun/incoming_emails.json', 'w') as f:
        json.dump(emails, f, indent=2)
    
    return jsonify({
        'message': 'OTP envoyé',
        'email': email
    }), 200

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    """Vérifie le code OTP et crée le compte"""
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    
    if not email or not otp:
        return jsonify({'error': 'Email et OTP requis'}), 400
    
    # Vérifier l'OTP
    if email not in OTP_STORAGE:
        return jsonify({'error': 'Aucune demande d\'inscription trouvée'}), 404
    
    stored_data = OTP_STORAGE[email]
    
    # Vérifier l'expiration
    if datetime.now() > stored_data['expires_at']:
        del OTP_STORAGE[email]
        return jsonify({'error': 'OTP expiré'}), 400
    
    # Vérifier le code
    if stored_data['code'] != otp:
        return jsonify({'error': 'OTP incorrect'}), 400
    
    # Générer un token et créer le compte
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    # Récupérer le mot de passe (dans une vraie app, il serait haché)
    password = request.json.get('password', 'default_password_' + ''.join(random.choices(string.digits, k=4)))
    
    save_user(email, password, token)
    
    # Nettoyer l'OTP utilisé
    del OTP_STORAGE[email]
    
    return jsonify({
        'message': 'Inscription réussie',
        'token': token,
        'email': email
    }), 200

@app.route('/api/users', methods=['GET'])
def get_users():
    """Liste tous les utilisateurs inscrits"""
    users = load_users()
    return jsonify({
        'count': len(users),
        'users': users
    }), 200

if __name__ == '__main__':
    print("🎯 Backend Cible démarré sur http://localhost:5000")
    print("Endpoints disponibles:")
    print("  POST /api/register - Inscription avec envoi d'OTP")
    print("  POST /api/verify-otp - Vérification de l'OTP")
    print("  GET /api/users - Liste des utilisateurs")
    app.run(host='0.0.0.0', port=5000, debug=True)
