# FamilyHuddle Streamlit Cloud Deployment Guide

This guide provides step-by-step instructions for deploying FamilyHuddle to Streamlit Community Cloud.

## Prerequisites

- [GitHub](https://github.com) account (public or private repository)
- [Supabase](https://supabase.com) project (production database)
- [Streamlit Community Cloud](https://share.streamlit.io) account

## 🚀 Quick Deployment Steps

### 1. Prepare Repository

```bash
# Generate requirements.txt for Streamlit
make requirements

# Verify app.py is the main entry point (already configured)
ls app.py

# Commit all changes
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 2. Configure Supabase Production Database

#### Apply Database Schema
1. Open [Supabase Dashboard](https://supabase.com/dashboard)
2. Navigate to your production project
3. Go to **SQL Editor**
4. Copy and paste the contents of `supabase/migrations/20250705_family_huddle_schema.sql`
5. Click **Run** to create all tables and policies

#### Initialize Sample Data (Optional)
```bash
# Switch to production environment locally
make use-production

# Add your service key to .env.production (temporarily)
echo "SUPABASE_SERVICE_KEY=your-service-key-here" >> .env.production

# Run production initialization
uv run python scripts/init_production.py

# Remove service key from file (security)
sed -i '' '/SUPABASE_SERVICE_KEY/d' .env.production
```

### 3. Deploy to Streamlit Cloud

1. Visit [Streamlit Community Cloud](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **Create app**
4. Configure deployment:
   - **Repository**: `your-username/FamilyHuddle`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: Choose a custom URL

### 4. Configure Secrets

In the Streamlit Cloud app settings, add these secrets:

```toml
[supabase]
url = "https://your-project-id.supabase.co"
anon_key = "your-anon-key-here"
```

**Where to find these values:**
- **URL**: Supabase Dashboard → Settings → API → Project URL
- **Anon Key**: Supabase Dashboard → Settings → API → Project API keys → anon/public

### 5. Deploy!

Click **Deploy** and wait for the app to build. The deployment typically takes 2-5 minutes.

## 📁 File Structure Requirements

Your repository must include:

```
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies (auto-generated)
├── .streamlit/
│   └── secrets.toml.template      # Template for local secrets
├── src/family_huddle/             # Application code
├── supabase/migrations/           # Database schema
└── CLAUDE.md                      # Development instructions
```

## 🔐 Environment Variables & Secrets

### Local Development
```bash
# .env.local (for local Supabase)
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_ANON_KEY=your-local-anon-key

# .env.production (for production Supabase)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-production-anon-key
```

### Streamlit Cloud Secrets
Configure in app settings dashboard:
```toml
[supabase]
url = "https://your-project-id.supabase.co"
anon_key = "your-anon-key-here"
# service_key = "your-service-key"  # Only if needed for admin ops
```

## 🗄️ Database Setup

### Required Tables
The application requires these tables in your Supabase database:
- `users` - User accounts and authentication
- `profiles` - User profiles (multiple per user)
- `nfl_teams` - NFL team data
- `nfl_seasons` - Season information
- `nfl_weeks` - Weekly schedule data
- `pools` - Football pools
- `pool_participants` - Pool membership
- `team_selections` - User team choices
- `pool_scores` - Scoring data
- `team_performance` - Team statistics

### Schema Migration
Apply the schema by running the SQL in `supabase/migrations/20250705_family_huddle_schema.sql` in your Supabase SQL Editor.

### Sample Data
Use `scripts/init_production.py` to populate with sample data:
- NFL teams (32 teams with realistic point values)
- Current season and 18 weeks
- Test users (email: test@example.com, password: password)
- Sample football pool

## 🔧 Build Process

### Requirements Generation
```bash
# Automatically generates clean requirements.txt
make requirements
```

The Makefile automatically:
1. Exports dependencies from `uv.lock`
2. Removes hashes (unsupported by Streamlit)
3. Excludes development dependencies
4. Creates Streamlit-compatible format

### App Configuration
The app automatically detects the deployment environment:
- **Local**: Uses `.env` files
- **Streamlit Cloud**: Uses `st.secrets` configuration

## 🧪 Testing Deployment

### Local Testing
```bash
# Test with production data
make use-production
make run

# Test with local data
make use-local
make run
```

### Production Testing
1. Check app loads without errors
2. Test user registration and login
3. Verify pool creation and joining
4. Test team selection functionality
5. Check leaderboard displays

## 🔍 Troubleshooting

### Common Issues

**1. Import Errors**
- Ensure all dependencies are in `requirements.txt`
- Run `make requirements` to regenerate

**2. Database Connection Errors**
- Verify Supabase secrets are correctly configured
- Check that database schema is applied
- Ensure RLS policies allow app operations

**3. Missing Tables**
- Apply the database migration in Supabase SQL Editor
- Run `scripts/init_production.py` for sample data

**4. Authentication Issues**
- Verify RLS policies are configured correctly
- Check user table has proper permissions

### Logs and Debugging
- Check Streamlit Cloud logs in the app dashboard
- Use `st.write()` for debugging in development
- Monitor Supabase logs for database issues

## 📊 Resource Limits

### Streamlit Community Cloud Limits
- **Storage**: Limited (use external database)
- **Memory**: 1GB RAM
- **CPU**: Shared resources
- **Bandwidth**: Fair use policy
- **Apps**: 3 public apps per account

### Optimization Tips
- Use `@st.cache_data` for expensive operations
- Minimize database queries
- Optimize images and assets
- Use lazy loading for large datasets

## 🔒 Security Considerations

### Secrets Management
- ✅ **Do**: Store secrets in Streamlit Cloud settings
- ❌ **Don't**: Commit secrets to repository
- ❌ **Don't**: Use service keys unless absolutely necessary

### Database Security
- RLS (Row Level Security) is enabled
- Public read access for reference data only
- Application-level authentication for user data

### Best Practices
- Use HTTPS for production (automatic with Streamlit Cloud)
- Validate all user inputs
- Hash passwords with bcrypt
- Follow principle of least privilege

## 🔄 Continuous Deployment

### Automatic Updates
Streamlit Cloud automatically redeploys when you push to the main branch:

```bash
# Make changes and deploy
git add .
git commit -m "Update feature"
git push origin main
# App automatically redeploys
```

### Version Management
- Use semantic versioning in your commits
- Tag releases for major updates
- Maintain a changelog for tracking changes

## 📞 Support

### Resources
- [Streamlit Community Cloud Docs](https://docs.streamlit.io/deploy/streamlit-community-cloud)
- [Supabase Documentation](https://supabase.com/docs)
- [UV Package Manager](https://docs.astral.sh/uv/)

### Getting Help
- Check application logs in Streamlit dashboard
- Review Supabase project logs
- Open issues in the GitHub repository

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Generate `requirements.txt` with `make requirements`
- [ ] Verify `app.py` is the main entry point
- [ ] Test locally with production database
- [ ] Apply database schema to production Supabase
- [ ] Initialize production data (optional)
- [ ] Commit all changes to GitHub

### Streamlit Cloud Setup
- [ ] Create Streamlit Cloud account
- [ ] Connect GitHub repository
- [ ] Configure app settings (repository, branch, main file)
- [ ] Add Supabase secrets configuration
- [ ] Deploy application

### Post-Deployment
- [ ] Verify app loads successfully
- [ ] Test core functionality (login, pools, team selection)
- [ ] Check database connectivity
- [ ] Validate user registration and authentication
- [ ] Monitor performance and errors

### Production Readiness
- [ ] Remove any debug code or test data
- [ ] Verify secrets are not committed to repository
- [ ] Test with multiple users and pools
- [ ] Confirm responsive design on mobile
- [ ] Set up monitoring and alerting (optional)

🎉 **Your FamilyHuddle app is now live on Streamlit Cloud!**