# Script to help push your code to GitHub
# Run this after installing Git and creating a GitHub repository

Write-Host "=== Pushing to GitHub ===" -ForegroundColor Cyan

# Check if git is available
try {
    git --version | Out-Null
    Write-Host "✓ Git is installed" -ForegroundColor Green
} catch {
    Write-Host "✗ Git is not installed. Please install from https://git-scm.com/download/win" -ForegroundColor Red
    exit 1
}

# Initialize repository if not already done
if (-not (Test-Path .git)) {
    Write-Host "Initializing git repository..." -ForegroundColor Yellow
    git init
} else {
    Write-Host "✓ Git repository already initialized" -ForegroundColor Green
}

# Check if files are already staged/committed
$status = git status --porcelain
if ($status) {
    Write-Host "Adding files to git..." -ForegroundColor Yellow
    git add .
    
    Write-Host "Creating initial commit..." -ForegroundColor Yellow
    git commit -m "Initial commit: Dark Eden RPG game"
    Write-Host "✓ Files committed" -ForegroundColor Green
} else {
    Write-Host "✓ Files already committed" -ForegroundColor Green
}

# Check for remote
$remote = git remote get-url origin 2>$null
if ($remote) {
    Write-Host "✓ Remote repository already configured: $remote" -ForegroundColor Green
    Write-Host "`nTo push, run: git push -u origin main" -ForegroundColor Cyan
} else {
    Write-Host "`n=== Next Steps ===" -ForegroundColor Cyan
    Write-Host "1. Create a new repository on GitHub (https://github.com/new)" -ForegroundColor Yellow
    Write-Host "2. Copy the repository URL (e.g., https://github.com/username/repo-name.git)" -ForegroundColor Yellow
    Write-Host "3. Run the following commands:" -ForegroundColor Yellow
    Write-Host "   git remote add origin <YOUR_REPO_URL>" -ForegroundColor White
    Write-Host "   git branch -M main" -ForegroundColor White
    Write-Host "   git push -u origin main" -ForegroundColor White
}

