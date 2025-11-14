"""
Script de test pour l'API avec authentification
"""
import requests
import json

BASE_URL = "http://localhost:5000"

print("="*60)
print("TEST DE L'API SIGNATURE ELECTRONIQUE AVEC AUTHENTIFICATION")
print("="*60)

# Test 1: Inscription
print("\n1. Test d'inscription...")
try:
    response = requests.post(f"{BASE_URL}/api/register", json={
        "email": "bruno@taaazzz.com",
        "password": "testpass123",
        "name": "Bruno Taaazzz"
    })
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Reponse: {json.dumps(data, indent=2)}")
    
    if response.status_code == 200:
        token = data.get('token')
        print(f"   ✓ Token recu: {token[:20]}...")
    else:
        print(f"   × Erreur: {data.get('error')}")
except Exception as e:
    print(f"   × Exception: {e}")

# Test 2: Connexion
print("\n2. Test de connexion...")
try:
    response = requests.post(f"{BASE_URL}/api/login", json={
        "email": "bruno@taaazzz.com",
        "password": "testpass123"
    })
    print(f"   Status: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        token = data.get('token')
        user = data.get('user')
        print(f"   ✓ Connexion reussie!")
        print(f"   ✓ Utilisateur: {user.get('name')} ({user.get('email')})")
        print(f"   ✓ Token: {token[:20]}...")
        
        # Sauvegarder le token pour les tests suivants
        AUTH_TOKEN = token
    else:
        print(f"   × Erreur: {data.get('error')}")
        AUTH_TOKEN = None
except Exception as e:
    print(f"   × Exception: {e}")
    AUTH_TOKEN = None

# Test 3: Informations utilisateur
if AUTH_TOKEN:
    print("\n3. Test recuperation infos utilisateur...")
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{BASE_URL}/api/me", headers=headers)
        print(f"   Status: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            print(f"   ✓ ID: {data.get('id')}")
            print(f"   ✓ Email: {data.get('email')}")
            print(f"   ✓ Nom: {data.get('name')}")
            print(f"   ✓ Cree le: {data.get('created_at')}")
        else:
            print(f"   × Erreur: {data.get('error')}")
    except Exception as e:
        print(f"   × Exception: {e}")

# Test 4: Sauvegarde d'une signature
if AUTH_TOKEN:
    print("\n4. Test sauvegarde signature...")
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        fake_signature = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        response = requests.post(f"{BASE_URL}/api/signatures/save", 
                                headers=headers,
                                json={
                                    "name": "Ma signature pro",
                                    "signature": fake_signature
                                })
        print(f"   Status: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            print(f"   ✓ Signature sauvegardee! ID: {data.get('signature_id')}")
        else:
            print(f"   × Erreur: {data.get('error')}")
    except Exception as e:
        print(f"   × Exception: {e}")

# Test 5: Liste des signatures
if AUTH_TOKEN:
    print("\n5. Test liste signatures...")
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{BASE_URL}/api/signatures", headers=headers)
        print(f"   Status: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            signatures = data.get('signatures', [])
            print(f"   ✓ Nombre de signatures: {len(signatures)}")
            for sig in signatures:
                print(f"     - {sig['name']} (ID: {sig['id']})")
        else:
            print(f"   × Erreur: {data.get('error')}")
    except Exception as e:
        print(f"   × Exception: {e}")

# Test 6: Historique
if AUTH_TOKEN:
    print("\n6. Test historique...")
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(f"{BASE_URL}/api/history", headers=headers)
        print(f"   Status: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            history = data.get('history', [])
            print(f"   ✓ Nombre d'entrees: {len(history)}")
            for entry in history:
                print(f"     - {entry['original_filename']} -> {entry['signed_filename']}")
        else:
            print(f"   × Erreur: {data.get('error')}")
    except Exception as e:
        print(f"   × Exception: {e}")

# Test 7: Deconnexion
if AUTH_TOKEN:
    print("\n7. Test deconnexion...")
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.post(f"{BASE_URL}/api/logout", headers=headers)
        print(f"   Status: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            print(f"   ✓ {data.get('message')}")
        else:
            print(f"   × Erreur: {data.get('error')}")
    except Exception as e:
        print(f"   × Exception: {e}")

print("\n" + "="*60)
print("TESTS TERMINES")
print("="*60)
