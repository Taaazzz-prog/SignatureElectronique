# Script de déploiement automatique pour Signature Électronique (Docker Swarm)
# Usage: .\deploy.ps1

$SERVER = "user@votre-serveur.com"
$REMOTE_PATH = "/home/user/SignatureElectronique"
$LOCAL_PATH = "d:\WEB API\SignatureElectronique"
$STACK_NAME = "signature"

Write-Host "🚀 Déploiement de Signature Électronique sur OVH (Docker Swarm)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

# Étape 1 : Transfert des fichiers
Write-Host "📦 Étape 1/3 : Transfert des fichiers..." -ForegroundColor Yellow
scp -r "$LOCAL_PATH\*" "${SERVER}:${REMOTE_PATH}/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Fichiers transférés avec succès" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur lors du transfert des fichiers" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Étape 2 : Nettoyage des fichiers de test
Write-Host "🧹 Étape 2/3 : Nettoyage des fichiers de test..." -ForegroundColor Yellow
ssh $SERVER "cd $REMOTE_PATH && rm -rf uploads/* signed/* signatures/* .venv/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Nettoyage effectué" -ForegroundColor Green
} else {
    Write-Host "⚠️ Avertissement : Erreur lors du nettoyage" -ForegroundColor Yellow
}

Write-Host ""

# Étape 3 : Construction de l'image et déploiement Swarm
Write-Host "🐳 Étape 3/3 : Construction et déploiement Docker Swarm..." -ForegroundColor Yellow
ssh $SERVER "cd $REMOTE_PATH && docker build -t signature-app:latest . && docker stack deploy -c docker-compose.yml $STACK_NAME"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Déploiement réussi !" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur lors du déploiement Docker" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "✨ Déploiement terminé avec succès !" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Application disponible sur :" -ForegroundColor Cyan
Write-Host "   https://votre-domaine.com" -ForegroundColor White
Write-Host ""
Write-Host "📋 Commandes utiles (Docker Swarm) :" -ForegroundColor Cyan
Write-Host "   Voir les services : ssh $SERVER 'docker service ls | grep $STACK_NAME'" -ForegroundColor Gray
Write-Host "   Voir les logs     : ssh $SERVER 'docker service logs -f ${STACK_NAME}_signature-app'" -ForegroundColor Gray
Write-Host "   Mettre à jour     : ssh $SERVER 'cd $REMOTE_PATH && docker build -t signature-app:latest . && docker service update --image signature-app:latest ${STACK_NAME}_signature-app'" -ForegroundColor Gray
Write-Host "   Supprimer la stack: ssh $SERVER 'docker stack rm $STACK_NAME'" -ForegroundColor Gray
Write-Host ""
