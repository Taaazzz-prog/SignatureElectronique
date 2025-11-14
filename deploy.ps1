# Script de déploiement automatique pour Signature Électronique
# Usage: .\deploy.ps1

$SERVER = "taaazzz@51.75.55.185"
$REMOTE_PATH = "/home/taaazzz/SignatureElectronique"
$LOCAL_PATH = "d:\WEB API\SignatureElectronique"

Write-Host "🚀 Déploiement de Signature Électronique sur OVH" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
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

# Étape 3 : Reconstruction et déploiement Docker
Write-Host "🐳 Étape 3/3 : Déploiement Docker..." -ForegroundColor Yellow
ssh $SERVER "cd $REMOTE_PATH && docker-compose down && docker-compose build && docker-compose up -d"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Déploiement réussi !" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur lors du déploiement Docker" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "✨ Déploiement terminé avec succès !" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Application disponible sur :" -ForegroundColor Cyan
Write-Host "   https://signatureelectronique.taaazzz-prog.fr" -ForegroundColor White
Write-Host ""
Write-Host "📋 Commandes utiles :" -ForegroundColor Cyan
Write-Host "   Voir les logs  : ssh $SERVER 'docker logs -f signature_electronique_app'" -ForegroundColor Gray
Write-Host "   Redémarrer     : ssh $SERVER 'cd $REMOTE_PATH && docker-compose restart'" -ForegroundColor Gray
Write-Host "   Arrêter        : ssh $SERVER 'cd $REMOTE_PATH && docker-compose down'" -ForegroundColor Gray
Write-Host ""
