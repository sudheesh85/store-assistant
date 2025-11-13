# NL2SQL Chatbot UI

A modern, user-friendly Natural Language to SQL (NL2SQL) chatbot application with a ChatGPT-like interface. This application is **backend-agnostic** and easily pluggable to any NL2SQL API backend.

## Features

- 🎨 **ChatGPT-style Interface**: Clean, modern chat interface with user and assistant messages
- 🔐 **Flexible Authentication**: Support for API Key, JWT, and OAuth authentication
- 📊 **Data Visualization**: Automatic chart generation (bar, line, pie) and table display
- 💬 **Streaming Responses**: Real-time streaming support via Server-Sent Events (SSE)
- 📝 **Chat History**: Persistent chat history with localStorage
- 🎯 **User-Friendly**: Designed for non-technical users with query examples and plain language
- 📱 **Responsive Design**: Works seamlessly on desktop and tablet devices
- 🌓 **Dark Mode**: Built-in dark mode support
- 📤 **Export Functionality**: Download results as CSV

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Markdown**: React Markdown
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- A backend NL2SQL API that follows the specified API contract

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-folder>/frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
# or
pnpm install
```

3. Create a `.env.local` file in this `frontend/` directory:
```bash
cp .env.example .env.local
```

4. Configure your environment variables in `.env.local`:
```env
# Backend API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_API_STREAMING_URL=http://localhost:8000/api/v1/ask/question/stream

# Authentication
NEXT_PUBLIC_AUTH_TYPE=api_key
# Options: api_key, jwt, oauth
NEXT_PUBLIC_AUTH_ENDPOINT=http://localhost:8000/api/v1/auth/login

# Optional Settings
NEXT_PUBLIC_ENABLE_SQL_PREVIEW=false
NEXT_PUBLIC_MAX_CHAT_HISTORY=100
NEXT_PUBLIC_THEME=light
```

5. Run the development server:
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

6. Open [http://localhost:3000](http://localhost:3000) in your browser.

## API Integration

### Request Format

The application sends requests to your backend in the following format:

```json
{
  "question": "How many students are in grade 5?",
  "org_id": 123,  // optional
  "session_id": "session-1234567890"  // optional
}
```

### Response Format

Your backend should return responses in the following format:

```json
{
  "success": true,
  "response": "There are 45 students in grade 5.",
  "sql": "SELECT COUNT(*) FROM students WHERE grade = 5",  // optional
  "data": {  // optional
    "columns": ["count"],
    "rows": [[45]]
  },
  "visualization": "bar",  // optional: "bar" | "line" | "pie" | "table"
  "error": null  // only present if success is false
}
```

### Streaming Support

For streaming responses, your backend should implement Server-Sent Events (SSE). The application expects responses in the following format:

```
data: {"chunk": "There are "}
data: {"chunk": "45 "}
data: {"chunk": "students"}
data: {"complete": true, "response": "There are 45 students.", "data": {...}}
data: [DONE]
```

### Authentication

#### API Key Authentication

1. Set `NEXT_PUBLIC_AUTH_TYPE=api_key` in your `.env.local`
2. Users will enter their API key on the login page
3. The API key is sent as `X-API-Key` header in all requests

#### JWT Authentication

1. Set `NEXT_PUBLIC_AUTH_TYPE=jwt` in your `.env.local`
2. Configure `NEXT_PUBLIC_AUTH_ENDPOINT` to point to your login endpoint
3. The login endpoint should return a JWT token
4. The token is sent as `Authorization: Bearer <token>` header

### Endpoints

- **Non-streaming**: `POST /ask/question`
- **Streaming**: `POST /ask/question/stream` (SSE)
- **Health Check**: `GET /health` (optional)

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Main chat page
│   ├── login/
│   │   └── page.tsx         # Login page
│   └── globals.css          # Global styles
├── components/
│   ├── ChatContainer.tsx    # Main chat container
│   ├── ChatInput.tsx        # Message input component
│   ├── ChatMessage.tsx      # Individual message component
│   ├── DataVisualization.tsx# Charts and tables
│   └── LoginForm.tsx        # Login form
├── lib/
│   ├── api.ts               # API client
│   ├── auth.ts              # Authentication service
│   ├── storage.ts           # LocalStorage service
│   └── queryExamples.ts     # Query examples
├── types/
│   └── index.ts             # TypeScript types
└── public/                  # Static assets
```

## Building for Production

```bash
npm run build
npm start
```

The application will be optimized and ready for deployment on platforms like Vercel, Netlify, or any Node.js hosting service.

## Configuration Options

### Environment Variables

- `NEXT_PUBLIC_API_BASE_URL`: Base URL for your backend API
- `NEXT_PUBLIC_API_STREAMING_URL`: URL for streaming endpoint
- `NEXT_PUBLIC_AUTH_TYPE`: Authentication type (`api_key`, `jwt`, `oauth`)
- `NEXT_PUBLIC_AUTH_ENDPOINT`: Authentication endpoint URL
- `NEXT_PUBLIC_ENABLE_SQL_PREVIEW`: Show SQL queries by default (default: `false`)
- `NEXT_PUBLIC_MAX_CHAT_HISTORY`: Maximum number of messages to store (default: `100`)
- `NEXT_PUBLIC_THEME`: Default theme (`light`, `dark`, `auto`)

## User Guide

### For End Users

1. **Login**: Enter your API key or credentials on the login page
2. **Ask Questions**: Type your question in plain language (e.g., "How many students are in grade 5?")
3. **View Results**: Results are displayed as charts or tables automatically
4. **Export Data**: Click the "Download CSV" button to export results
5. **View SQL** (optional): Click "Show SQL Query" to see the generated SQL (hidden by default for non-technical users)

### Query Examples

- "How many records are in the database?"
- "Show me the top 10 items by sales"
- "What is the total revenue this month?"
- "List all students in grade 5"
- "Show me the average temperature for each month"

## Security Considerations

- API keys and tokens are stored in browser localStorage (consider using httpOnly cookies in production)
- All API requests include authentication headers
- Input is sanitized before sending to backend
- CORS should be configured on your backend to allow the frontend origin

## Browser Support

- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

## Troubleshooting

### Connection Issues

- Verify your `NEXT_PUBLIC_API_BASE_URL` is correct
- Check that your backend API is running and accessible
- Ensure CORS is properly configured on your backend

### Authentication Issues

- Verify your API key or credentials are correct
- Check that authentication headers are being sent (check browser DevTools Network tab)
- Ensure your backend accepts the authentication method you've configured

### Streaming Not Working

- Verify `NEXT_PUBLIC_API_STREAMING_URL` is correct
- Check that your backend implements SSE correctly
- Ensure your backend sends data in the expected format

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on the repository.

---

**Built with ❤️ for non-technical users who need to query their data easily**

