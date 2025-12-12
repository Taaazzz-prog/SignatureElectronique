# Script de monitoring pour Signature Électronique (Docker Swarm)
# Usage: .\monitor.ps1

$SERVER = "user@votre-serveur.com"
$STACK_NAME = "signature"
$SERVICE_NAME = "${STACK_NAME}_signature-app"
$URL = "https://votre-domaine.com"

Write-Host "📊 Monitoring de Signature Électronique (Swarm)" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Test 1 : Statut du service Swarm
Write-Host "🐳 Statut du service Docker Swarm..." -ForegroundColor Yellow
$serviceStatus = ssh $SERVER "docker service ls --filter name=$SERVICE_NAME --format '{{.Name}} - {{.Replicas}} - {{.Image}}'"

if ($serviceStatus) {
    Write-Host "✅ Service actif : $serviceStatus" -ForegroundColor Green
} else {
    Write-Host "❌ Service non trouvé ou arrêté !" -ForegroundColor Red
}

Write-Host ""

# Test 2 : Liste des tâches (conteneurs) du service
Write-Host "📦 Tâches du service..." -ForegroundColor Yellow
ssh $SERVER "docker service ps $SERVICE_NAME --format 'table {{.Name}}\t{{.CurrentState}}\t{{.Error}}' --no-trunc"

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

# Test 3 : Logs récents du service
Write-Host "📝 Dernières lignes de logs..." -ForegroundColor Yellow
ssh $SERVER "docker service logs --tail 10 $SERVICE_NAME"

Write-Host ""

# Test 4 : Inspection du service
Write-Host "🔍 Informations du service..." -ForegroundColor Yellow
ssh $SERVER "docker service inspect $SERVICE_NAME --format '{{.Spec.Name}}: {{.Spec.TaskTemplate.ContainerSpec.Image}} (Replicas: {{.Spec.Mode.Replicated.Replicas}})'"

Write-Host ""

# Test 5 : Vérification des volumes
Write-Host "📦 Volumes Docker..." -ForegroundColor Yellow
ssh $SERVER "docker volume ls | grep signature"

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "✅ Monitoring terminé" -ForegroundColor Green
Write-Host ""
