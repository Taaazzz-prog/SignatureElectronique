# 🚀 Script de déploiement Swarm avec Secrets Docker + GHCR
# Usage: .\deploy-swarm.ps1

param(
    [switch]$CreateSecrets,
    [switch]$UpdateSecrets,
    [switch]$SkipPull
)

$SERVER = "user@votre-serveur.com"
$REMOTE_PATH = "/home/user/SignatureElectronique"
$STACK_NAME = "signature"
$IMAGE_NAME = "ghcr.io/taaazzz-prog/signatureelectronique:latest"

Write-Host "`n🚀 Déploiement Swarm avec Docker Secrets + GHCR" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Étape 1 : Créer les secrets Docker (première fois uniquement)
if ($CreateSecrets) {
    Write-Host "🔐 Étape 1 : Création des secrets Docker..." -ForegroundColor Yellow
    Write-Host "⚠️  ATTENTION: Vous devez fournir les valeurs réelles !" -ForegroundColor Red
    Write-Host ""
    
    $secretKey = Read-Host "SECRET_KEY (32+ caractères aléatoires)" -MaskInput
    $recaptchaKey = Read-Host "RECAPTCHA_SECRET_KEY (optionnel, appuyez sur Enter si vide)"
    $goodflagToken = Read-Host "GOODFLAG_API_TOKEN (optionnel, appuyez sur Enter si vide)"
    
    Write-Host "`nCréation des secrets sur le serveur..." -ForegroundColor Yellow
    
    ssh $SERVER "echo '$secretKey' | docker secret create signature_secret_key - 2>&1"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ signature_secret_key créé" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  signature_secret_key existe déjà ou erreur" -ForegroundColor Yellow
    }
    
    if ($recaptchaKey) {
        ssh $SERVER "echo '$recaptchaKey' | docker secret create signature_recaptcha_key - 2>&1"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ signature_recaptcha_key créé" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  signature_recaptcha_key existe déjà ou erreur" -ForegroundColor Yellow
        }
    } else {
        ssh $SERVER "echo '' | docker secret create signature_recaptcha_key - 2>&1"
    }
    
    if ($goodflagToken) {
        ssh $SERVER "echo '$goodflagToken' | docker secret create signature_goodflag_token - 2>&1"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ signature_goodflag_token créé" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  signature_goodflag_token existe déjà ou erreur" -ForegroundColor Yellow
        }
    } else {
        ssh $SERVER "echo '' | docker secret create signature_goodflag_token - 2>&1"
    }
    
    Write-Host ""
}

# Étape 2 : Mise à jour des secrets (rotation)
if ($UpdateSecrets) {
    Write-Host "🔄 Étape 2 : Rotation des secrets..." -ForegroundColor Yellow
    Write-Host "Cette opération supprime et recrée les secrets (service redémarré)" -ForegroundColor Yellow
    Write-Host ""
    
    $confirm = Read-Host "Continuer? (o/N)"
    if ($confirm -ne "o") {
        Write-Host "❌ Annulé" -ForegroundColor Red
        exit 0
    }
    
    # TODO: Implémenter la rotation avec suffixes _v2, etc.
    Write-Host "⚠️  Fonctionnalité en cours de développement" -ForegroundColor Yellow
    Write-Host "Pour l'instant, supprimez manuellement les secrets et recréez-les:" -ForegroundColor Gray
    Write-Host "  ssh $SERVER 'docker secret rm signature_secret_key signature_recaptcha_key signature_goodflag_token'" -ForegroundColor Gray
    Write-Host "  .\deploy-swarm.ps1 -CreateSecrets" -ForegroundColor Gray
    exit 0
}

# Étape 3 : Transfert du docker-compose.yml
Write-Host "📦 Transfert du docker-compose.yml..." -ForegroundColor Yellow
scp "$PSScriptRoot\docker-compose.yml" "${SERVER}:${REMOTE_PATH}/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Fichier transféré" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur lors du transfert" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Étape 4 : Pull de l'image depuis GHCR
if (-not $SkipPull) {
    Write-Host "🐳 Pull de l'image depuis GHCR..." -ForegroundColor Yellow
    Write-Host "Image: $IMAGE_NAME" -ForegroundColor Gray
    
    ssh $SERVER "docker pull $IMAGE_NAME"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Image récupérée" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Erreur lors du pull (vérifiez que l'image est publique ou que vous êtes authentifié)" -ForegroundColor Yellow
        Write-Host "Pour vous authentifier: docker login ghcr.io -u VOTRE_USERNAME" -ForegroundColor Gray
    }
    
    Write-Host ""
}

# Étape 5 : Déploiement de la stack
Write-Host "🚀 Déploiement de la stack Swarm..." -ForegroundColor Yellow
ssh $SERVER "cd $REMOTE_PATH && docker stack deploy -c docker-compose.yml $STACK_NAME"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Stack déployée !" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur lors du déploiement" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Étape 6 : Vérification
Write-Host "🔍 Vérification du déploiement..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

ssh $SERVER "docker service ls | grep $STACK_NAME"
Write-Host ""
ssh $SERVER "docker service ps ${STACK_NAME}_signature-app --no-trunc"

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "✨ Déploiement terminé !" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Commandes utiles:" -ForegroundColor Cyan
Write-Host "  Logs en temps réel:" -ForegroundColor White
Write-Host "    ssh $SERVER 'docker service logs -f ${STACK_NAME}_signature-app'" -ForegroundColor Gray
Write-Host ""
Write-Host "  Mettre à jour uniquement l'image:" -ForegroundColor White
Write-Host "    ssh $SERVER 'docker service update --image $IMAGE_NAME ${STACK_NAME}_signature-app'" -ForegroundColor Gray
Write-Host ""
Write-Host "  Lister les secrets:" -ForegroundColor White
Write-Host "    ssh $SERVER 'docker secret ls'" -ForegroundColor Gray
Write-Host ""
Write-Host "  Supprimer la stack:" -ForegroundColor White
Write-Host "    ssh $SERVER 'docker stack rm $STACK_NAME'" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 Pour créer les secrets la première fois:" -ForegroundColor Yellow
Write-Host "    .\deploy-swarm.ps1 -CreateSecrets" -ForegroundColor Gray
Write-Host ""
