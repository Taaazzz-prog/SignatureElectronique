# Script de monitoring pour Signature Électronique
# Usage: .\monitor.ps1

$SERVER = "taaazzz@51.75.55.185"
$CONTAINER = "signature_electronique_app"
$URL = "https://signatureelectronique.taaazzz-prog.fr"

Write-Host "📊 Monitoring de Signature Électronique" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1 : Statut du conteneur
Write-Host "🐳 Statut du conteneur Docker..." -ForegroundColor Yellow
$containerStatus = ssh $SERVER "docker ps --filter name=$CONTAINER --format '{{.Status}}'"

if ($containerStatus -match "Up") {
    Write-Host "✅ Conteneur actif : $containerStatus" -ForegroundColor Green
} else {
    Write-Host "❌ Conteneur arrêté ou problème détecté !" -ForegroundColor Red
}

Write-Host ""

# Test 2 : Test HTTP
Write-Host "🌐 Test de connectivité HTTP..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $URL -Method Head -TimeoutSec 10 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Application accessible (HTTP 200)" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Code HTTP inattendu : $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Erreur de connexion : $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3 : Logs récents
Write-Host "📝 Dernières lignes de logs..." -ForegroundColor Yellow
ssh $SERVER "docker logs --tail 10 $CONTAINER"

Write-Host ""

# Test 4 : Utilisation des ressources
Write-Host "💾 Utilisation des ressources..." -ForegroundColor Yellow
ssh $SERVER "docker stats $CONTAINER --no-stream --format 'CPU: {{.CPUPerc}} | RAM: {{.MemUsage}} | NET: {{.NetIO}}'"

Write-Host ""

# Test 5 : Espace disque des volumes
Write-Host "📦 Volumes Docker..." -ForegroundColor Yellow
ssh $SERVER "docker volume ls | grep signature"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Monitoring terminé" -ForegroundColor Green
Write-Host ""
