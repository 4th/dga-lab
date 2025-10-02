# GitHub Deployment Guide

This repo includes a CI workflow that:
- Builds Docker images for each service
- Pushes them to **GitHub Container Registry (GHCR)**
- Runs a simple **docker compose** end-to-end smoke test

## 1) Initialize git & first commit (Windows PowerShell)
```powershell
cd C:\EXAMPLES\dga-lab
git init
git add .
git commit -m "Initial commit: dga-lab"
```

## 2) Create the GitHub repo (using GitHub CLI)
```powershell
# Login once (follow prompts)
gh auth login

# Create a new private repo and push
gh repo create dga-lab --private --source . --remote origin --push
```

> No GitHub CLI? Create a repo in the UI, then:
```powershell
git remote add origin https://github.com/<you>/dga-lab.git
git branch -M main
git push -u origin main
```

## 3) CI/CD details
- Workflow file: `.github/workflows/ci.yml`
- Images are pushed to: `ghcr.io/<your-account>/<service>:latest` (and `:sha-<shortsha>`)
- Permissions are already set in the workflow (`packages: write`)

### View packages
https://github.com/users/<your-account>/packages?repo_name=dga-lab

## 4) Optional tweaks
- Rename services or images? Edit `SERVICES` in `ci.yml`.
- Want to pin Python/Docker versions? Add build args to your Dockerfiles and pass them in the workflow.
- Want Trivy scans or Hadolint? Add extra jobs to the workflow.

## 5) Local dev
```powershell
docker compose up --build
.\run-dga-direct.ps1
```

Happy shipping! 🚀
