"""
Module d'intégration API Goodflag (ex-Lex Persona)
Pour signature électronique qualifiée conforme eIDAS
"""

import os
import requests
import json
from datetime import datetime
from secrets_helper import read_secret, get_secret_or_default


class GoodflagAPI:
    """Client API Goodflag pour signature électronique"""
    
    def __init__(self, api_token=None, api_url=None):
        """
        Initialise le client API Goodflag
        
        Args:
            api_token: Token d'authentification API (depuis Docker Secret si non fourni)
            api_url: URL de base de l'API (depuis Docker Secret ou env si non fourni)
        """
        # Lire depuis Docker Secret en priorité, puis env var
        self.api_token = api_token or get_secret_or_default(
            'signature_goodflag_token',
            default_value='',
            env_var_name='GOODFLAG_API_TOKEN'
        )
        self.api_url = api_url or get_secret_or_default(
            'signature_goodflag_url',
            default_value='https://api.goodflag.com/v1',
            env_var_name='GOODFLAG_API_URL'
        )
        
        if not self.api_token:
            print("⚠️  Token API Goodflag non configuré. Utilisez les variables d'environnement.")
        
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def is_configured(self):
        """Vérifie si l'API est correctement configurée"""
        return bool(self.api_token)
    
    def create_signature_workflow(self, document_path, signers, workflow_name=None):
        """
        Crée un circuit de signature sur Goodflag
        
        Args:
            document_path: Chemin du fichier PDF à signer
            signers: Liste des signataires [{'email': 'email@example.com', 'name': 'Nom'}]
            workflow_name: Nom du circuit de signature
            
        Returns:
            (success, result) - result contient workflow_id ou message d'erreur
        """
        if not self.is_configured():
            return False, "API Goodflag non configurée. Vérifiez votre token."
        
        try:
            # Préparer les données du workflow
            workflow_data = {
                'name': workflow_name or f"Signature_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'signers': signers,
                'signature_level': 'advanced',  # simple, advanced, ou qualified
                'auto_download': True
            }
            
            # Créer le workflow
            response = requests.post(
                f'{self.api_url}/workflows',
                headers=self.headers,
                json=workflow_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                workflow = response.json()
                workflow_id = workflow.get('id')
                
                # Uploader le document
                with open(document_path, 'rb') as f:
                    files = {'document': f}
                    upload_response = requests.post(
                        f'{self.api_url}/workflows/{workflow_id}/documents',
                        headers={'Authorization': f'Bearer {self.api_token}'},
                        files=files,
                        timeout=60
                    )
                
                if upload_response.status_code in [200, 201]:
                    return True, {
                        'workflow_id': workflow_id,
                        'message': 'Circuit de signature créé avec succès',
                        'signing_url': workflow.get('signing_url')
                    }
                else:
                    return False, f"Erreur upload document: {upload_response.text}"
            else:
                return False, f"Erreur création workflow: {response.text}"
                
        except requests.exceptions.RequestException as e:
            return False, f"Erreur réseau: {str(e)}"
        except Exception as e:
            return False, f"Erreur: {str(e)}"
    
    def sign_document_server_side(self, document_path, signer_email, signer_name):
        """
        Signature côté serveur (signature automatique avec certificat serveur)
        
        Args:
            document_path: Chemin du PDF à signer
            signer_email: Email du signataire
            signer_name: Nom du signataire
            
        Returns:
            (success, result) - result contient le chemin du PDF signé ou erreur
        """
        if not self.is_configured():
            return False, "API Goodflag non configurée"
        
        try:
            with open(document_path, 'rb') as f:
                files = {'document': f}
                data = {
                    'signer_email': signer_email,
                    'signer_name': signer_name,
                    'signature_level': 'advanced'
                }
                
                response = requests.post(
                    f'{self.api_url}/sign/server',
                    headers={'Authorization': f'Bearer {self.api_token}'},
                    files=files,
                    data=data,
                    timeout=60
                )
            
            if response.status_code == 200:
                # Sauvegarder le PDF signé
                signed_path = document_path.replace('.pdf', '_goodflag_signed.pdf')
                with open(signed_path, 'wb') as f:
                    f.write(response.content)
                
                return True, {
                    'signed_path': signed_path,
                    'message': 'Document signé avec Goodflag',
                    'signature_type': 'goodflag_qualified'
                }
            else:
                return False, f"Erreur signature: {response.text}"
                
        except Exception as e:
            return False, f"Erreur: {str(e)}"
    
    def get_workflow_status(self, workflow_id):
        """
        Récupère le statut d'un circuit de signature
        
        Args:
            workflow_id: ID du workflow
            
        Returns:
            (success, status_data)
        """
        if not self.is_configured():
            return False, "API non configurée"
        
        try:
            response = requests.get(
                f'{self.api_url}/workflows/{workflow_id}',
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Erreur: {response.text}"
                
        except Exception as e:
            return False, f"Erreur: {str(e)}"
    
    def download_signed_document(self, workflow_id, output_path):
        """
        Télécharge un document signé
        
        Args:
            workflow_id: ID du workflow
            output_path: Chemin de sortie du PDF signé
            
        Returns:
            (success, message)
        """
        if not self.is_configured():
            return False, "API non configurée"
        
        try:
            response = requests.get(
                f'{self.api_url}/workflows/{workflow_id}/documents/signed',
                headers=self.headers,
                timeout=60
            )
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True, "Document signé téléchargé"
            else:
                return False, f"Erreur téléchargement: {response.text}"
                
        except Exception as e:
            return False, f"Erreur: {str(e)}"
    
    def test_connection(self):
        """
        Teste la connexion à l'API Goodflag
        
        Returns:
            (success, message)
        """
        if not self.is_configured():
            return False, "Token API non configuré"
        
        try:
            response = requests.get(
                f'{self.api_url}/account',
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                account = response.json()
                return True, f"Connecté: {account.get('name', 'Compte Goodflag')}"
            else:
                return False, f"Erreur authentification: {response.status_code}"
                
        except Exception as e:
            return False, f"Erreur connexion: {str(e)}"


# Instance globale
_goodflag_client = None

def get_goodflag_client():
    """Retourne l'instance unique du client Goodflag"""
    global _goodflag_client
    if _goodflag_client is None:
        _goodflag_client = GoodflagAPI()
    return _goodflag_client
