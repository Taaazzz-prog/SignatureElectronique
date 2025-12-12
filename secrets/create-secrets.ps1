# 🔐 Création des Docker Secrets - PRODUCTION
# Usage: .\create-secrets.ps1

# ==============================================================================
# 🎯 Ce script crée les Docker Secrets sur le serveur de production
# ==============================================================================

$SERVER = "taaazzz@51.75.55.185"

Write-Host "`n🔐 Création des Docker Secrets" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que le fichier .env existe
if (-not (Test-Path "$PSScriptRoot\..\.env")) {
    Write-Host "❌ Fichier .env introuvable !" -ForegroundColor Red
    Write-Host "Créez d'abord le fichier .env avec vos secrets" -ForegroundColor Yellow
    exit 1
}

Write-Host "📋 Lecture des secrets depuis .env..." -ForegroundColor Yellow

# Lire les secrets depuis .env
$envContent = Get-Content "$PSScriptRoot\..\.env" -Raw
$secrets = @{}

# Parser le fichier .env
$envContent -split "`n" | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
        $parts = $line -split "=", 2
        $key = $parts[0].Trim()
        $value = $parts[1].Trim()
        $secrets[$key] = $value
    }
}

# Extraire les secrets nécessaires
$SECRET_KEY = $secrets["SECRET_KEY"]
$RECAPTCHA_SECRET_KEY = $secrets["RECAPTCHA_SECRET_KEY"]
$GOODFLAG_API_TOKEN = $secrets["GOODFLAG_API_TOKEN"]

# Vérifier que les secrets obligatoires sont présents
if (-not $SECRET_KEY -or $SECRET_KEY -like "*VOTRE_VRAIE*") {
    Write-Host "❌ SECRET_KEY manquant ou non configuré dans .env !" -ForegroundColor Red
    exit 1
}

if (-not $RECAPTCHA_SECRET_KEY -or $RECAPTCHA_SECRET_KEY -like "*VOTRE_VRAIE*") {
    Write-Host "⚠️  RECAPTCHA_SECRET_KEY manquant - utilisation d'une valeur vide" -ForegroundColor Yellow
    $RECAPTCHA_SECRET_KEY = ""
}

if (-not $GOODFLAG_API_TOKEN) {
    Write-Host "⚠️  GOODFLAG_API_TOKEN vide - OK pour démarrer" -ForegroundColor Yellow
    $GOODFLAG_API_TOKEN = ""
}

Write-Host "✅ Secrets chargés depuis .env" -ForegroundColor Green
Write-Host ""

# Confirmation
Write-Host "⚠️  Les secrets vont être créés sur : $SERVER" -ForegroundColor Yellow
$confirm = Read-Host "Continuer? (o/N)"
if ($confirm -ne "o") {
    Write-Host "❌ Annulé" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "🚀 Création des secrets sur le serveur..." -ForegroundColor Cyan
Write-Host ""

# Créer signature_secret_key
Write-Host "  📝 signature_secret_key..." -ForegroundColor Gray
$result = ssh $SERVER "echo '$SECRET_KEY' | docker secret create signature_secret_key - 2>&1"
if ($LASTEXITCODE -eq 0) {
    Write-Host "     ✅ Créé" -ForegroundColor Green
} else {
    if ($result -like "*already exists*") {
        Write-Host "     ⚠️  Existe déjà" -ForegroundColor Yellow
    } else {
        Write-Host "     ❌ Erreur: $result" -ForegroundColor Red
    }
}

# Créer signature_recaptcha_key
Write-Host "  📝 signature_recaptcha_key..." -ForegroundColor Gray
$result = ssh $SERVER "echo '$RECAPTCHA_SECRET_KEY' | docker secret create signature_recaptcha_key - 2>&1"
if ($LASTEXITCODE -eq 0) {
    Write-Host "     ✅ Créé" -ForegroundColor Green
} else {
    if ($result -like "*already exists*") {
        Write-Host "     ⚠️  Existe déjà" -ForegroundColor Yellow
    } else {
        Write-Host "     ❌ Erreur: $result" -ForegroundColor Red
    }
}

# Créer signature_goodflag_token
Write-Host "  📝 signature_goodflag_token..." -ForegroundColor Gray
$result = ssh $SERVER "echo '$GOODFLAG_API_TOKEN' | docker secret create signature_goodflag_token - 2>&1"
if ($LASTEXITCODE -eq 0) {
    Write-Host "     ✅ Créé" -ForegroundColor Green
} else {
    if ($result -like "*already exists*") {
        Write-Host "     ⚠️  Existe déjà" -ForegroundColor Yellow
    } else {
        Write-Host "     ❌ Erreur: $result" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ Terminé !" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Vérifier les secrets créés:" -ForegroundColor Cyan
Write-Host "   ssh $SERVER 'docker secret ls'" -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 Prochaine étape:" -ForegroundColor Cyan
Write-Host "   .\deploy-swarm-prod.ps1" -ForegroundColor Gray
Write-Host ""
