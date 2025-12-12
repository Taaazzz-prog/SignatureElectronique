"""
Helper pour lire les secrets Docker Swarm
Supporte aussi les variables d'environnement pour développement local
"""
import os


def read_secret(secret_name, env_var_name=None):
    """
    Lit un secret Docker depuis /run/secrets/ ou variable d'environnement
    
    Args:
        secret_name: Nom du secret Docker (fichier dans /run/secrets/)
        env_var_name: Nom de la variable d'environnement (si différent)
    
    Returns:
        str: Valeur du secret ou None
    """
    # 1. Essayer de lire depuis Docker Secrets (production Swarm)
    secret_path = f'/run/secrets/{secret_name}'
    if os.path.exists(secret_path):
        try:
            with open(secret_path, 'r') as f:
                value = f.read().strip()
                if value:
                    return value
        except Exception as e:
            print(f"⚠️  Erreur lecture secret {secret_name}: {e}")
    
    # 2. Fallback sur variable d'environnement (dev local)
    env_name = env_var_name or secret_name.upper().replace('-', '_')
    env_value = os.environ.get(env_name)
    if env_value:
        return env_value
    
    return None


def get_secret_or_default(secret_name, default_value='', env_var_name=None):
    """
    Lit un secret avec valeur par défaut
    
    Args:
        secret_name: Nom du secret Docker
        default_value: Valeur par défaut si secret introuvable
        env_var_name: Nom de la variable d'environnement alternative
    
    Returns:
        str: Valeur du secret ou valeur par défaut
    """
    value = read_secret(secret_name, env_var_name)
    return value if value is not None else default_value


def is_using_docker_secrets():
    """Vérifie si on utilise Docker Secrets (mode production)"""
    return os.path.exists('/run/secrets/')
