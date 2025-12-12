# 🏗️ Build local et push vers GitHub Container Registry
# Usage: .\build-and-push.ps1

param(
    [string]$Tag = "latest",
    [switch]$SkipBuild,
    [switch]$SkipPush
)

$IMAGE_REPO = "ghcr.io/taaazzz-prog/signatureelectronique"
$IMAGE_TAG = "${IMAGE_REPO}:${Tag}"

Write-Host "`n🏗️ Build et Push vers GHCR" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# Étape 1 : Vérifier l'authentification GHCR
Write-Host "🔐 Vérification de l'authentification GHCR..." -ForegroundColor Yellow

$authTest = docker images $IMAGE_REPO 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Vous n'êtes peut-être pas authentifié à GHCR" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Pour vous authentifier:" -ForegroundColor White
    Write-Host "  1. Créer un Personal Access Token GitHub avec scope 'write:packages'" -ForegroundColor Gray
    Write-Host "     https://github.com/settings/tokens/new?scopes=write:packages" -ForegroundColor Gray
    Write-Host "  2. Exécuter: echo VOTRE_TOKEN | docker login ghcr.io -u VOTRE_USERNAME --password-stdin" -ForegroundColor Gray
    Write-Host ""
    
    $continue = Read-Host "Continuer quand même? (o/N)"
    if ($continue -ne "o") {
        exit 0
    }
}

Write-Host ""

# Étape 2 : Build de l'image
if (-not $SkipBuild) {
    Write-Host "🏗️ Build de l'image Docker..." -ForegroundColor Yellow
    Write-Host "Tag: $IMAGE_TAG" -ForegroundColor Gray
    Write-Host ""
    
    docker build -t $IMAGE_TAG .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Image buildée avec succès" -ForegroundColor Green
    } else {
        Write-Host "❌ Erreur lors du build" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    
    # Tag aussi comme latest si ce n'est pas déjà le cas
    if ($Tag -ne "latest") {
        Write-Host "🏷️ Tag additionnel: latest" -ForegroundColor Yellow
        docker tag $IMAGE_TAG "${IMAGE_REPO}:latest"
    }
} else {
    Write-Host "⏭️ Build ignoré (-SkipBuild)" -ForegroundColor Gray
    Write-Host ""
}

# Étape 3 : Push vers GHCR
if (-not $SkipPush) {
    Write-Host "☁️ Push vers GitHub Container Registry..." -ForegroundColor Yellow
    Write-Host "Repository: $IMAGE_REPO" -ForegroundColor Gray
    Write-Host ""
    
    docker push $IMAGE_TAG
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Image $Tag poussée" -ForegroundColor Green
    } else {
        Write-Host "❌ Erreur lors du push" -ForegroundColor Red
        exit 1
    }
    
    # Push latest aussi
    if ($Tag -ne "latest") {
        Write-Host ""
        Write-Host "☁️ Push de latest..." -ForegroundColor Yellow
        docker push "${IMAGE_REPO}:latest"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Image latest poussée" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Erreur lors du push de latest" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "⏭️ Push ignoré (-SkipPush)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "✨ Terminé !" -ForegroundColor Green
Write-Host ""
Write-Host "📦 Image disponible:" -ForegroundColor Cyan
Write-Host "   $IMAGE_TAG" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Voir sur GitHub:" -ForegroundColor Cyan
Write-Host "   https://github.com/Taaazzz-prog/SignatureElectronique/pkgs/container/signatureelectronique" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Pour déployer sur le serveur:" -ForegroundColor Cyan
Write-Host "   .\deploy-swarm.ps1" -ForegroundColor White
Write-Host ""
Write-Host "💡 Pour rendre l'image publique:" -ForegroundColor Yellow
Write-Host "   1. Aller sur https://github.com/Taaazzz-prog/SignatureElectronique/pkgs/container/signatureelectronique/settings" -ForegroundColor Gray
Write-Host "   2. Changer 'Package visibility' en 'Public'" -ForegroundColor Gray
Write-Host ""
