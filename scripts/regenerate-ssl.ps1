# Script de régénération de certificat SSL (Docker Swarm)
# Usage: .\regenerate-ssl.ps1

$SERVER = "user@votre-serveur.com"
$REMOTE_PATH = "/home/user/SignatureElectronique"
$STACK_NAME = "signature"
$SERVICE_NAME = "${STACK_NAME}_signature-app"

Write-Host "🔐 Régénération du certificat SSL (Docker Swarm)" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Étape 1 : Trouver le nom exact du conteneur Traefik
Write-Host "🔍 Recherche du conteneur Traefik..." -ForegroundColor Yellow
$traefikContainer = ssh $SERVER "docker ps | grep traefik | awk '{print `$NF}' | head -n 1"

if ($traefikContainer) {
    Write-Host "✅ Conteneur Traefik trouvé : $traefikContainer" -ForegroundColor Green
} else {
    Write-Host "❌ ERREUR : Aucun conteneur Traefik trouvé !" -ForegroundColor Red
    Write-Host "   Vérifiez que Traefik est bien démarré" -ForegroundColor Yellow
    Write-Host "   Commande : ssh $SERVER 'docker ps | grep traefik'" -ForegroundColor Gray
    exit 1
}

Write-Host ""

# Étape 2 : Vérifier les certificats actuels
Write-Host "📋 Certificats actuels..." -ForegroundColor Yellow
ssh $SERVER "docker exec $traefikContainer cat /letsencrypt/acme.json 2>/dev/null | grep -o 'signatureelectronique' | head -5 || echo '   Aucun certificat pour signatureelectronique'"

Write-Host ""

# Étape 3 : Redémarrer le service pour forcer la demande de certificat
Write-Host "🔄 Redémarrage du service Swarm..." -ForegroundColor Yellow
ssh $SERVER "docker service update --force $SERVICE_NAME"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Service redémarré avec succès" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur lors du redémarrage" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Étape 4 : Surveiller la génération du certificat (30 secondes)
Write-Host "⏳ Surveillance de la génération du certificat (30 secondes)..." -ForegroundColor Yellow
Write-Host "   Appuyez sur Ctrl+C pour arrêter" -ForegroundColor Gray
Write-Host ""

for ($i = 1; $i -le 6; $i++) {
    Start-Sleep -Seconds 5
    $certCheck = ssh $SERVER "docker exec $traefikContainer cat /letsencrypt/acme.json 2>/dev/null | grep 'signatureelectronique'"
    
    if ($certCheck) {
        Write-Host "✅ CERTIFICAT GÉNÉRÉ AVEC SUCCÈS !" -ForegroundColor Green
        Write-Host "   Détails : $certCheck" -ForegroundColor Gray
        break
    } else {
        Write-Host "   [$i/6] En attente de génération..." -ForegroundColor Gray
    }
}

Write-Host ""

# Étape 5 : Afficher les logs Traefik
Write-Host "📝 Derniers logs Traefik..." -ForegroundColor Yellow
ssh $SERVER "docker logs $traefikContainer --tail 20 2>&1 | grep -i 'signatureelectronique\|certificate\|error' || echo '   Aucune erreur détectée'"

Write-Host ""

# Étape 6 : Test final
Write-Host "🧪 Test de connexion HTTPS..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://votre-domaine.com" -Method Head -TimeoutSec 10 -UseBasicParsing -SkipCertificateCheck
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Site accessible !" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Code HTTP : $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    $errorMsg = $_.Exception.Message
    if ($errorMsg -match "ERR_CERT") {
        Write-Host "⚠️ Certificat encore invalide. Attendez 2-5 minutes supplémentaires." -ForegroundColor Yellow
        Write-Host "   Let's Encrypt peut prendre du temps pour la première génération." -ForegroundColor Gray
    } else {
        Write-Host "❌ Erreur : $errorMsg" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "📋 Prochaines étapes :" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Attendre 2-5 minutes pour la génération complète" -ForegroundColor White
Write-Host "2. Tester l'accès : https://votre-domaine.com" -ForegroundColor White
Write-Host "3. En cas d'échec, vérifier les logs Traefik :" -ForegroundColor White
Write-Host "   ssh $SERVER 'docker logs $traefikContainer -f | grep signatureelectronique'" -ForegroundColor Gray
Write-Host "4. Vérifier les logs du service :" -ForegroundColor White
Write-Host "   ssh $SERVER 'docker service logs -f $SERVICE_NAME'" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 Si le problème persiste après 10 minutes :" -ForegroundColor Yellow
Write-Host "   - Vérifier que les ports 80 et 443 sont ouverts" -ForegroundColor Gray
Write-Host "   - Vérifier la configuration Traefik (certresolver letsencrypt)" -ForegroundColor Gray
Write-Host "   - Consulter la limite de taux Let's Encrypt (5 certificats/domaine/semaine)" -ForegroundColor Gray
Write-Host ""

