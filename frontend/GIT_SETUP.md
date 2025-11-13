# Git Repository Setup Guide

Your code is already in a local Git repository! Here's how to push it to a remote repository (GitHub, GitLab, etc.).

## Current Status

✅ Local Git repository initialized  
✅ All files are committed  
✅ Working on `master` branch

## Option 1: Push to GitHub (Recommended)

### Step 1: Create a New Repository on GitHub

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right → **"New repository"**
3. Fill in the details:
   - **Repository name**: `nl2sql-chatbot` (or any name you prefer)
   - **Description**: "Modern NL2SQL Chatbot UI - Backend Agnostic"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click **"Create repository"**

### Step 2: Connect Your Local Repository to GitHub

Run these commands in your terminal:

```bash
cd /Users/sudheeshmadathil/Documents/chatbot

# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/nl2sql-chatbot.git

# Or if you prefer SSH:
# git remote add origin git@github.com:YOUR_USERNAME/nl2sql-chatbot.git

# Push your code to GitHub
git push -u origin master
```

### Step 3: Verify

Visit your repository on GitHub to see your code!

---

## Option 2: Push to GitLab

### Step 1: Create a New Project on GitLab

1. Go to [GitLab.com](https://gitlab.com) and sign in
2. Click **"New project"** → **"Create blank project"**
3. Fill in the details:
   - **Project name**: `nl2sql-chatbot`
   - **Visibility**: Choose Public, Internal, or Private
   - **DO NOT** initialize with README
4. Click **"Create project"**

### Step 2: Connect and Push

```bash
cd /Users/sudheeshmadathil/Documents/chatbot

# Add the remote repository
git remote add origin https://gitlab.com/YOUR_USERNAME/nl2sql-chatbot.git

# Push your code
git push -u origin master
```

---

## Option 3: Push to Bitbucket

### Step 1: Create a New Repository on Bitbucket

1. Go to [Bitbucket.org](https://bitbucket.org) and sign in
2. Click **"Create"** → **"Repository"**
3. Fill in the details and click **"Create repository"**

### Step 2: Connect and Push

```bash
cd /Users/sudheeshmadathil/Documents/chatbot

# Add the remote repository
git remote add origin https://bitbucket.org/YOUR_USERNAME/nl2sql-chatbot.git

# Push your code
git push -u origin master
```

---

## Quick Commands Reference

### Check Current Status
```bash
git status
```

### View Remote Repositories
```bash
git remote -v
```

### Add All Changes (if you make edits)
```bash
git add .
git commit -m "Your commit message"
git push
```

### Create a New Branch
```bash
git checkout -b feature/your-feature-name
```

### Switch Back to Master
```bash
git checkout master
```

---

## Troubleshooting

### If you get "remote origin already exists"
```bash
# Remove existing remote
git remote remove origin

# Add new remote
git remote add origin YOUR_REPO_URL
```

### If you need to change the remote URL
```bash
git remote set-url origin YOUR_NEW_REPO_URL
```

### If push is rejected
```bash
# Pull first, then push
git pull origin master --allow-unrelated-histories
git push -u origin master
```

---

## Next Steps After Pushing

1. **Add a README badge** (optional) - Update README.md with repository badges
2. **Set up CI/CD** - Add GitHub Actions, GitLab CI, etc.
3. **Add issues template** - Create `.github/ISSUE_TEMPLATE.md`
4. **Add pull request template** - Create `.github/pull_request_template.md`
5. **Deploy** - Connect to Vercel, Netlify, or your hosting service

---

**Your code is ready to be shared! 🚀**

