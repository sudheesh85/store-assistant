# Push to GitHub - Step by Step

## Error: Repository Not Found

The repository `https://github.com/sudheesh85/nl2sql-chatbot.git` doesn't exist yet. Follow these steps:

## Step 1: Create the Repository on GitHub

### Option A: Using GitHub Website (Easiest)

1. Go to: https://github.com/new
2. Fill in:
   - **Repository name**: `nl2sql-chatbot`
   - **Description**: "Modern NL2SQL Chatbot UI - Backend Agnostic"
   - **Visibility**: Choose Public or Private
   - **IMPORTANT**: Do NOT check "Add a README file"
   - **IMPORTANT**: Do NOT check "Add .gitignore"
   - **IMPORTANT**: Do NOT check "Choose a license"
3. Click **"Create repository"**

### Option B: Using GitHub CLI (if installed)

```bash
gh repo create nl2sql-chatbot --public --description "Modern NL2SQL Chatbot UI - Backend Agnostic"
```

## Step 2: Push Your Code

After creating the repository, run:

```bash
cd /Users/sudheeshmadathil/Documents/chatbot

# Remove the old remote if it exists
git remote remove origin

# Add the correct remote
git remote add origin https://github.com/sudheesh85/nl2sql-chatbot.git

# Push your code
git push -u origin master
```

## Step 3: If You Get Authentication Errors

If GitHub asks for authentication:

### Option A: Use Personal Access Token
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name like "nl2sql-chatbot"
4. Select scopes: `repo` (full control of private repositories)
5. Click "Generate token"
6. Copy the token
7. When git asks for password, paste the token instead

### Option B: Use SSH (Recommended for future)

1. Generate SSH key (if you don't have one):
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. Add SSH key to GitHub:
```bash
cat ~/.ssh/id_ed25519.pub
# Copy the output and add it to GitHub Settings > SSH and GPG keys
```

3. Use SSH URL instead:
```bash
git remote set-url origin git@github.com:sudheesh85/nl2sql-chatbot.git
git push -u origin master
```

## Alternative: Create Repository with Different Name

If `nl2sql-chatbot` is taken, use a different name:

```bash
# Create repo with different name on GitHub first, then:
git remote set-url origin https://github.com/sudheesh85/YOUR_REPO_NAME.git
git push -u origin master
```

---

**After creating the repository on GitHub, come back and run the push command!**

