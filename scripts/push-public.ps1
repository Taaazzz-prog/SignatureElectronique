# 🌐 Push vers le repository PUBLIC
# Usage: .\push-public.ps1 [-Message "commit message"]

param(
    [string]$Message = "Update code"
)

$ErrorActionPreference = "Stop"

Write-Host "`n🌐 PUSH VERS LE REPOSITORY PUBLIC" -ForegroundColor Cyan
Write-Host "=========================================`n" -ForegroundColor Cyan

# 1. Sauvegarder le .gitignore actuel
Write-Host "1️⃣ Configuration pour le public..." -ForegroundColor Yellow
if (Test-Path ".gitignore") {
    Copy-Item ".gitignore" ".gitignore.backup" -Force
}

# 2. Utiliser le .gitignore public
Copy-Item ".gitignore-public" ".gitignore" -Force
Write-Host "   ✅ .gitignore public activé`n" -ForegroundColor Green

# 3. Afficher ce qui sera commité
Write-Host "2️⃣ Fichiers qui seront pushés (CODE uniquement):" -ForegroundColor Yellow
git status --short
Write-Host ""

# 4. Confirmation
$confirm = Read-Host "Continuer le push vers PUBLIC? (o/N)"
if ($confirm -ne "o") {
    Write-Host "`n❌ Annulé" -ForegroundColor Red
    # Restaurer le .gitignore
    if (Test-Path ".gitignore.backup") {
        Move-Item ".gitignore.backup" ".gitignore" -Force
    }
    exit 0
}

# 5. Add, commit, push
Write-Host "`n3️⃣ Commit et push..." -ForegroundColor Yellow
try {
    git add .
    git commit -m "🌐 $Message"
    git push public main
    Write-Host "`n✅ Push vers PUBLIC réussi !" -ForegroundColor Green
    Write-Host "   https://github.com/Taaazzz-prog/SignatureElectronique`n" -ForegroundColor Gray
} catch {
    Write-Host "`n⚠️ Erreur lors du push: $_" -ForegroundColor Red
}

# 6. Restaurer le .gitignore original
if (Test-Path ".gitignore.backup") {
    Move-Item ".gitignore.backup" ".gitignore" -Force
}

Write-Host "=========================================`n" -ForegroundColor Cyan
