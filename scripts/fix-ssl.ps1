# Script de correction SSL pour Signature Électronique
# Usage: .\fix-ssl.ps1

$SERVER = "user@votre-serveur.com"
$REMOTE_PATH = "/home/user/SignatureElectronique"

Write-Host "🔧 Diagnostic et correction SSL" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Étape 1 : Vérification de Traefik
Write-Host "🔍 Étape 1/5 : Vérification de Traefik..." -ForegroundColor Yellow
$traefikStatus = ssh $SERVER "docker ps | grep traefik"

if ($traefikStatus) {
    Write-Host "✅ Traefik est actif" -ForegroundColor Green
    Write-Host "$traefikStatus" -ForegroundColor Gray
} else {
    Write-Host "❌ PROBLÈME : Traefik n'est pas actif !" -ForegroundColor Red
    Write-Host "   Solution : Vérifier la configuration Traefik" -ForegroundColor Yellow
}

Write-Host ""

# Étape 2 : Vérification du réseau Docker
Write-Host "🔍 Étape 2/5 : Vérification du réseau Docker..." -ForegroundColor Yellow
$networkStatus = ssh $SERVER "docker network ls | grep faildaily-ssl-network"

if ($networkStatus) {
    Write-Host "✅ Réseau faildaily-ssl-network existe" -ForegroundColor Green
} else {
    Write-Host "❌ PROBLÈME : Le réseau n'existe pas !" -ForegroundColor Red
    Write-Host "   Solution : Créer le réseau ou vérifier le nom exact" -ForegroundColor Yellow
}

Write-Host ""

# Étape 3 : Vérification des certificats Let's Encrypt
Write-Host "🔍 Étape 3/5 : Vérification des certificats..." -ForegroundColor Yellow
ssh $SERVER "docker exec faildaily-traefik-ssl cat /letsencrypt/acme.json 2>/dev/null | grep signatureelectronique || echo 'Aucun certificat trouvé pour signatureelectronique'"

Write-Host ""

# Étape 4 : Logs Traefik pour erreurs SSL
Write-Host "🔍 Étape 4/5 : Logs Traefik (erreurs SSL)..." -ForegroundColor Yellow
ssh $SERVER "docker logs faildaily-traefik-ssl --tail 50 2>&1 | grep -i 'error\|certificate\|signatureelectronique' || echo 'Aucune erreur récente trouvée'"

Write-Host ""

# Étape 5 : Test DNS
Write-Host "🔍 Étape 5/5 : Vérification DNS..." -ForegroundColor Yellow
$dnsResult = Resolve-DnsName -Name "votre-domaine.com" -Type A -ErrorAction SilentlyContinue

if ($dnsResult) {
    Write-Host "✅ DNS résolu : $($dnsResult.IPAddress)" -ForegroundColor Green
    if ($dnsResult.IPAddress -eq "VOTRE.IP.DU.SERVEUR") {
        Write-Host "✅ L'IP correspond au serveur" -ForegroundColor Green
    } else {
        Write-Host "⚠️ L'IP ne correspond PAS au serveur (VOTRE.IP.DU.SERVEUR)" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ PROBLÈME : DNS non résolu !" -ForegroundColor Red
}

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "📋 Actions recommandées :" -ForegroundColor Cyan
Write-Host ""
Write-Host "Si Traefik n'est pas actif :" -ForegroundColor Yellow
Write-Host "  1. Démarrer Traefik sur le serveur" -ForegroundColor Gray
Write-Host "  2. Redéployer l'application avec .\deploy.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "Si le certificat est manquant :" -ForegroundColor Yellow
Write-Host "  1. Forcer la régénération : ssh $SERVER 'cd $REMOTE_PATH && docker stack rm signature && docker stack deploy -c docker-compose.yml signature'" -ForegroundColor Gray
Write-Host "  2. Attendre 2-3 minutes pour la génération" -ForegroundColor Gray
Write-Host "  3. Vérifier les logs : ssh $SERVER 'docker logs faildaily-traefik-ssl -f'" -ForegroundColor Gray
Write-Host ""
Write-Host "Si le DNS ne pointe pas vers le serveur :" -ForegroundColor Yellow
Write-Host "  1. Mettre à jour le DNS pour pointer vers l'IP de votre serveur" -ForegroundColor Gray
Write-Host "  2. Attendre la propagation (jusqu'à 24h)" -ForegroundColor Gray
Write-Host ""

