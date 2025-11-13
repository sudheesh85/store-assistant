# NL2SQL Chatbot UI Development Prompt

## Project Overview
Build a modern, elegant, and user-friendly Natural Language to SQL (NL2SQL) chatbot application with a ChatGPT-like interface. The application should be **backend-agnostic** and easily pluggable to any NL2SQL API backend.

---

## Core Requirements

### 1. **User Interface Design**
- **ChatGPT-style chat interface** with:
  - User messages aligned to the **right** (with user avatar/icon)
  - Assistant messages aligned to the **left** (with bot avatar/icon)
  - Smooth scrolling to latest messages
  - Clean, modern design with proper spacing between messages
  - Responsive layout that works on desktop and tablet
  - Dark/light theme support (or elegant default theme)

- **Chat Input Box**:
  - Sticky at the bottom of the screen
  - Large, visible text input area (similar to ChatGPT)
  - Placeholder text: "Ask a question about your data..."
  - Send button or Enter key submission
  - Disabled state while processing requests
  - Character counter (optional, for long queries)

- **Message Display**:
  - Markdown support for formatted responses
  - Code blocks with syntax highlighting for SQL queries (if shown)
  - Tables/charts embedded within assistant messages
  - Loading indicator ("Thinking..." or spinner) while processing
  - Error messages displayed clearly
  - Timestamps (optional, can be toggled)

### 2. **Authentication System**
- **Login Page**:
  - Clean, professional login form
  - Username/email and password fields
  - "Remember me" checkbox
  - "Forgot password?" link (optional)
  - Error message display for invalid credentials

- **Authentication Options**:
  - **Option A: Simple API Key Authentication**
    - Login form accepts API key
    - API key stored in session/localStorage
    - Sent as header in all API requests
  
  - **Option B: JWT Token Authentication**
    - Login endpoint returns JWT token
    - Token stored securely (httpOnly cookie preferred, or localStorage)
    - Token refresh mechanism
    - Auto-logout on token expiration
  
  - **Option C: OAuth Integration**
    - Google/Microsoft/GitHub OAuth buttons
    - OAuth callback handling
    - Token management

- **Session Management**:
  - Persistent login (session storage)
  - Logout functionality
  - Protected routes (redirect to login if not authenticated)
  - Session timeout handling

- **User Profile** (optional):
  - Display username/email in header
  - Settings dropdown
  - Logout button

### 3. **Backend Integration (Pluggable)**
- **API Configuration**:
  - Configurable backend API base URL (via environment variables or config file)
  - Support for different API endpoints:
    - `/ask/question` (non-streaming)
    - `/ask/question/stream` (Server-Sent Events streaming)
    - `/health` (health check)
  
- **Request Format**:
  - Accept standard request format:
    ```json
    {
      "question": "string",
      "org_id": "number (optional)",
      "session_id": "string (optional)"
    }
    ```
  
- **Response Handling**:
  - Parse standard response format:
    ```json
    {
      "success": boolean,
      "response": "string",
      "sql": "string (optional)",
      "data": {
        "columns": ["col1", "col2"],
        "rows": [[val1, val2], ...]
      },
      "visualization": "bar|line|pie|table (optional)",
      "error": "string (if error)"
    }
    ```
  
- **Streaming Support**:
  - Handle Server-Sent Events (SSE) for real-time streaming responses
  - Display streaming text word-by-word as it arrives
  - Handle connection errors gracefully
  - Show loading state during streaming

- **Error Handling**:
  - Network errors (connection timeout, server error)
  - API errors (400, 401, 403, 500)
  - User-friendly error messages
  - Retry mechanism (optional)

### 4. **Features & Functionality**

#### Core Features:
- **Chat History**:
  - Persistent chat history (localStorage or backend)
  - Clear chat history button
  - Export chat history (optional)
  - Search through chat history (optional)

- **Data Visualization**:
  - Render charts (bar, line, pie) based on response metadata
  - Display tables with pagination (if large datasets)
  - Download results as CSV/Excel
  - Copy SQL query button (if SQL is shown)

- **Query Management**:
  - Show/hide SQL query toggle
  - Edit and re-run previous queries
  - Favorite/bookmark queries (optional)

#### Advanced Features (Optional):
- **Multi-database support**: Switch between different databases/orgs
- **Query suggestions**: Auto-complete or suggested queries
- **Voice input**: Speech-to-text for questions
- **Export options**: PDF, Excel, JSON export
- **Query history analytics**: Most asked questions, query performance

### 5. **Technical Stack Recommendations**

#### Frontend Framework Options:
- **Option A: React + TypeScript** (Recommended)
  - Next.js for routing and SSR
  - Tailwind CSS or Material-UI for styling
  - React Query for API state management
  - Axios or Fetch for API calls
  - React Markdown for message rendering
  
- **Option B: Vue.js + TypeScript**
  - Nuxt.js for routing
  - Vuetify or Tailwind CSS
  - Vue Query for API state
  
- **Option C: Streamlit** (Simpler, Python-based)
  - Good for rapid prototyping
  - Less customizable but faster to build
  - Already used in current project

#### Key Libraries:
- **HTTP Client**: Axios, Fetch API, or `httpx` (Python)
- **Streaming**: EventSource API (for SSE) or `sse-client` library
- **Charts**: Chart.js, Recharts, Plotly, or Streamlit charts
- **Markdown**: `react-markdown`, `marked`, or Streamlit markdown
- **Authentication**: `react-router` protected routes, or Streamlit session state
- **State Management**: React Context, Redux, Zustand, or Streamlit session state

### 6. **Design Guidelines**

#### Visual Design:
- **Color Scheme**: 
  - Professional, modern palette (e.g., dark blue/gray with accent colors)
  - High contrast for readability
  - Accessible color combinations (WCAG AA compliant)
  
- **Typography**:
  - Clean, readable font (Inter, Roboto, or system fonts)
  - Proper font sizes (16px+ for body text)
  - Clear hierarchy (headings, body, captions)
  
- **Spacing & Layout**:
  - Generous whitespace
  - Consistent padding/margins
  - Max-width container (1200-1400px) for readability
  - Mobile-responsive breakpoints

#### UX Principles:
- **Loading States**: Always show loading indicators
- **Feedback**: Immediate feedback on user actions
- **Error Recovery**: Clear error messages with actionable steps
- **Accessibility**: Keyboard navigation, screen reader support
- **Performance**: Fast initial load, smooth interactions

### 7. **Security Considerations**
- **API Key Security**:
  - Never expose API keys in frontend code
  - Use environment variables for API URLs
  - Store tokens securely (httpOnly cookies preferred)
  
- **Input Validation**:
  - Sanitize user input before sending to backend
  - Prevent XSS attacks in rendered messages
  - Rate limiting on frontend (optional)
  
- **CORS Configuration**:
  - Ensure backend allows frontend origin
  - Handle CORS errors gracefully

### 8. **Performance Requirements**
- **Initial Load**: < 3 seconds
- **Message Rendering**: < 100ms per message
- **Streaming Latency**: Display chunks as soon as received
- **Chat History**: Lazy load or paginate if > 50 messages
- **Optimization**: Code splitting, lazy loading, image optimization

### 9. **Configuration & Deployment**

#### Environment Variables:
```env
# Backend API Configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_API_STREAMING_URL=http://localhost:8000/api/v1/ask/question/stream

# Authentication
VITE_AUTH_TYPE=api_key|jwt|oauth
VITE_AUTH_ENDPOINT=http://localhost:8000/api/v1/auth/login

# Optional
VITE_ENABLE_SQL_PREVIEW=true
VITE_MAX_CHAT_HISTORY=100
VITE_THEME=dark|light|auto
```

#### Build & Deploy:
- Production build optimization
- Docker containerization (optional)
- Static hosting (Vercel, Netlify, AWS S3) or server deployment
- Environment-specific configurations

### 10. **Testing Requirements**
- **Unit Tests**: Component logic, utility functions
- **Integration Tests**: API calls, authentication flow
- **E2E Tests**: Complete user flows (login → ask question → view response)
- **Browser Compatibility**: Chrome, Firefox, Safari, Edge (latest 2 versions)

---

## Example User Flow

1. **User visits application** → Redirected to login if not authenticated
2. **User logs in** → Redirected to chat interface
3. **User types question**: "How many students are in grade 5?"
4. **System shows "Thinking..."** → Sends request to backend API
5. **Backend streams response** → UI displays response word-by-word
6. **Response includes data** → UI renders chart/table
7. **User can download CSV** → Clicks download button
8. **User asks follow-up** → New message added to chat history

---

## Deliverables

1. **Source Code**: Complete, well-documented, production-ready code
2. **README.md**: Setup instructions, configuration guide, API integration guide
3. **Environment Template**: `.env.example` with all required variables
4. **Build Scripts**: Package.json scripts or equivalent for dev/prod builds
5. **Dockerfile** (optional): For containerized deployment
6. **Documentation**: API integration guide for backend developers

---

## Success Criteria

✅ **Functional**:
- Users can authenticate and access the chat interface
- Questions can be asked and responses displayed
- Streaming responses work smoothly
- Charts/tables render correctly
- Chat history persists across sessions

✅ **Design**:
- Interface looks professional and modern
- ChatGPT-like user experience
- Responsive on different screen sizes
- Accessible and user-friendly

✅ **Technical**:
- Code is clean, maintainable, and well-documented
- Easy to integrate with any backend API
- Performance is optimized
- Security best practices followed

✅ **Usability**:
- Intuitive navigation
- Clear error messages
- Fast response times
- Smooth interactions

---

## Additional Notes

- **Backend Agnostic**: The UI should work with any backend that follows the specified API contract
- **Extensibility**: Code should be modular and easy to extend with new features
- **Maintainability**: Follow best practices, use TypeScript if possible, add comments for complex logic
- **Documentation**: Inline code comments and external documentation for API integration

---

## Questions to Clarify (if needed)

1. Preferred frontend framework? (React, Vue, Streamlit, etc.)
2. Authentication method preference? (API key, JWT, OAuth)
3. Should SQL queries be visible to users by default?
4. Any specific design system or brand colors to follow?
5. Deployment target? (Cloud, on-premise, Docker)
6. Multi-language support required?
7. Any specific accessibility requirements?

---

**End of Prompt**

