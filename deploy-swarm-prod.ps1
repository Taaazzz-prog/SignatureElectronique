# 🚀 Script de déploiement Swarm - PRODUCTION
# Usage: .\deploy-swarm-prod.ps1

param(
    [switch]$SkipPull,
    [switch]$Force
)

# ==============================================================================
# 🔐 CONFIGURATION PRODUCTION - VRAIES VALEURS
# ==============================================================================

$SERVER = "taaazzz@51.75.55.185"
$REMOTE_PATH = "/home/taaazzz/SignatureElectronique"
$STACK_NAME = "signature"
$IMAGE_NAME = "ghcr.io/taaazzz-prog/signatureelectronique:latest"

Write-Host "`n🚀 Déploiement Swarm - PRODUCTION" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "Serveur: $SERVER" -ForegroundColor Gray
Write-Host "Stack: $STACK_NAME" -ForegroundColor Gray
Write-Host ""

# Confirmation
if (-not $Force) {
    Write-Host "⚠️  Déploiement en PRODUCTION" -ForegroundColor Yellow
    $confirm = Read-Host "Continuer? (o/N)"
    if ($confirm -ne "o") {
        Write-Host "❌ Annulé" -ForegroundColor Red
        exit 0
    }
    Write-Host ""
}

# Étape 1 : Transfert du docker-compose.prod.yml
Write-Host "📦 Transfert du docker-compose.yml..." -ForegroundColor Yellow
scp "$PSScriptRoot\docker-compose.prod.yml" "${SERVER}:${REMOTE_PATH}/docker-compose.yml"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Fichier transféré" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur lors du transfert" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Étape 2 : Pull de l'image depuis GHCR
if (-not $SkipPull) {
    Write-Host "🐳 Pull de l'image depuis GHCR..." -ForegroundColor Yellow
    Write-Host "Image: $IMAGE_NAME" -ForegroundColor Gray
    
    ssh $SERVER "docker pull $IMAGE_NAME"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Image récupérée" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Erreur lors du pull" -ForegroundColor Yellow
        Write-Host "L'image publique peut nécessiter une authentification GHCR" -ForegroundColor Gray
    }
    
    Write-Host ""
}

# Étape 3 : Déploiement de la stack
Write-Host "🚀 Déploiement de la stack Swarm..." -ForegroundColor Yellow
ssh $SERVER "cd $REMOTE_PATH && docker stack deploy -c docker-compose.yml $STACK_NAME"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Stack déployée !" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur lors du déploiement" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Étape 4 : Vérification
Write-Host "🔍 Vérification du déploiement..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

ssh $SERVER "docker service ls | grep $STACK_NAME"
Write-Host ""
ssh $SERVER "docker service ps ${STACK_NAME}_signature-app --no-trunc | head -n 5"

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "✨ Déploiement terminé !" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Commandes utiles:" -ForegroundColor Cyan
Write-Host "  Logs en temps réel:" -ForegroundColor White
Write-Host "    ssh $SERVER 'docker service logs -f ${STACK_NAME}_signature-app'" -ForegroundColor Gray
Write-Host ""
Write-Host "  URL de l'application:" -ForegroundColor White
Write-Host "    https://signatureelectronique.taaazzz-prog.fr" -ForegroundColor Gray
Write-Host ""
Write-Host "  Vérifier les secrets:" -ForegroundColor White
Write-Host "    ssh $SERVER 'docker secret ls'" -ForegroundColor Gray
Write-Host ""
