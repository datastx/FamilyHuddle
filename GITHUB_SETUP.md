# GitHub Repository Setup for Streamlit Deployment

## Pre-Deployment Checklist

### 1. Repository Structure
Ensure your repository has the correct structure:

```
├── app.py                      # ✅ Main Streamlit app
├── requirements.txt            # ✅ Dependencies (auto-generated)
├── .gitignore                  # ✅ Excludes secrets and cache
├── DEPLOYMENT.md               # ✅ Deployment instructions
├── CLAUDE.md                   # ✅ Development guide
├── pyproject.toml              # ✅ Project configuration
├── Makefile                    # ✅ Development commands
├── src/family_huddle/          # ✅ Application code
├── supabase/migrations/        # ✅ Database schema
├── scripts/                    # ✅ Utility scripts
└── .streamlit/
    ├── secrets.toml.template   # ✅ Secrets template
    └── secrets.toml            # ❌ Should be in .gitignore
```

### 2. Generate Dependencies
```bash
# Generate clean requirements.txt for Streamlit
make requirements
```

### 3. Verify .gitignore
Check that sensitive files are excluded:
```bash
# These should be in .gitignore:
.env*
.streamlit/secrets.toml
.venv/
__pycache__/
*.pyc
.cache/
```

### 4. Test Locally
```bash
# Test with production database
make use-production
streamlit run app.py

# Test with local database
make use-local
streamlit run app.py
```

### 5. Commit and Push
```bash
git add .
git commit -m "🚀 Prepare for Streamlit Cloud deployment

- Add requirements.txt for Streamlit
- Update database service for secrets compatibility
- Add comprehensive deployment documentation
- Include production initialization script"
git push origin main
```

## Repository Settings

### Visibility
- ✅ **Public**: Free Streamlit Community Cloud
- ✅ **Private**: Requires Streamlit account with GitHub access

### Branch Protection (Optional)
```bash
# Protect main branch
git checkout -b develop
git push -u origin develop
# Use develop for development, main for production
```

### Repository Topics
Add these topics to help with discovery:
- `streamlit`
- `football-pool`
- `supabase`
- `python`
- `web-app`

## Files Status Check

Run this before deployment:

```bash
# Check required files exist
ls -la app.py requirements.txt .gitignore DEPLOYMENT.md

# Verify no secrets in repo
git log --oneline -p | grep -i "secret\|key\|password" | head -10

# Check requirements.txt is clean (no hashes)
grep -c "hash=" requirements.txt || echo "✅ Clean requirements.txt"

# Verify .env files are gitignored
git status --porcelain | grep ".env" || echo "✅ No .env files tracked"
```

## Ready for Deployment

Once all items are checked:

1. 🔗 **Repository URL**: `https://github.com/your-username/FamilyHuddle`
2. 📄 **Main file**: `app.py`
3. 🌿 **Branch**: `main`
4. 📦 **Dependencies**: `requirements.txt`
5. 🔐 **Secrets**: Configure in Streamlit Cloud dashboard

Your repository is now ready for Streamlit Community Cloud deployment!