# 🐳 Dockerfile pour Signature Électronique PDF
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code de l'application
COPY . .

# Créer les dossiers nécessaires pour les uploads et la base de données
RUN mkdir -p uploads signed signatures data

# Exposer le port 5000
EXPOSE 5000

# Installer Gunicorn globalement
RUN pip install --no-cache-dir gunicorn

# Créer un utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Commande de démarrage
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
