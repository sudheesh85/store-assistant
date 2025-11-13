# Quick Start Guide

Get your NL2SQL Chatbot up and running in 5 minutes!

## Prerequisites

- Node.js 18+ installed
- npm, yarn, or pnpm
- A backend NL2SQL API (or use the mock setup below)

## Installation Steps

```bash
cd <repository-folder>/frontend
```

### 1. Install Dependencies

```bash
npm install
```

### 2. Create Environment File

Create a `.env.local` file in this `frontend/` directory:

```bash
# Copy this content to .env.local

# Backend API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_API_STREAMING_URL=http://localhost:8000/api/v1/ask/question/stream

# Authentication
NEXT_PUBLIC_AUTH_TYPE=api_key
NEXT_PUBLIC_AUTH_ENDPOINT=http://localhost:8000/api/v1/auth/login

# Optional Settings
NEXT_PUBLIC_ENABLE_SQL_PREVIEW=false
NEXT_PUBLIC_MAX_CHAT_HISTORY=100
NEXT_PUBLIC_THEME=light
```

### 3. Start Development Server

```bash
npm run dev
```

### 4. Open in Browser

Navigate to [http://localhost:3000](http://localhost:3000)

### 5. Login

- Use **API Key** authentication (default)
- Enter any API key (your backend should validate it)
- Or use email/password if you've configured JWT authentication

## Testing Without a Backend

If you don't have a backend yet, you can test the UI by:

1. Using the login page (it will accept any API key for now)
2. The chat interface will show connection errors, but you can see the UI
3. To fully test, you'll need to set up a backend API

## Next Steps

1. **Configure Your Backend**: See `API_INTEGRATION.md` for API requirements
2. **Customize**: Update query examples in `lib/queryExamples.ts`
3. **Deploy**: See deployment section in `README.md`

## Common Issues

### Port Already in Use

If port 3000 is busy, Next.js will automatically use the next available port (3001, 3002, etc.)

### Module Not Found

Run `npm install` again to ensure all dependencies are installed.

### API Connection Errors

- Verify your backend is running
- Check `NEXT_PUBLIC_API_BASE_URL` in `.env.local`
- Ensure CORS is configured on your backend

## Need Help?

- Check the full `README.md` for detailed documentation
- See `API_INTEGRATION.md` for backend integration
- Review the requirements in `req.md`

---

**Happy Querying! 🚀**

