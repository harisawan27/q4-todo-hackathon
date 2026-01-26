# Todo AI Chatbot - Frontend

Next.js chat interface for the Todo AI Chatbot application.

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env.local
```

Edit `.env.local` with your values:

```env
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_USER_ID=your-user-id
```

### 3. Run the Development Server

```bash
npm run dev
```

The application will be available at http://localhost:3000

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx       # Main page (renders ChatInterface)
│   │   ├── layout.tsx     # Root layout with metadata
│   │   └── globals.css    # Global styles
│   ├── components/
│   │   └── ChatInterface.tsx  # Main chat component
│   └── lib/
│       └── api.ts         # API client for backend
├── package.json
├── .env.example
└── .env.local             # Local environment (not committed)
```

## Features

- Real-time chat interface
- Conversation persistence via conversation_id
- Loading indicators
- Error handling with user feedback
- Responsive design with Tailwind CSS
- Welcome message with available commands

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8001` |
| `NEXT_PUBLIC_USER_ID` | User ID for API calls | Required |

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |

## Usage

1. Ensure the backend is running on port 8001
2. Start the frontend with `npm run dev`
3. Open http://localhost:3000
4. Start chatting with the AI assistant

### Example Commands

- "Show me my tasks"
- "Add a task: Buy groceries"
- "Mark 'Buy groceries' as done"
- "Delete the task 'Buy groceries'"
- "What's on my todo list?"
