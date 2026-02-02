import ChatInterface from '@/components/ChatInterface';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
      {/* Background content */}
      <div className="flex flex-col items-center justify-center min-h-screen p-8">
        <div className="text-center space-y-4 max-w-md">
          <div className="flex items-center justify-center mb-6">
            <div className="h-16 w-16 flex items-center justify-center rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-600 shadow-lg">
              <svg
                className="h-8 w-8 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                />
              </svg>
            </div>
          </div>
          <h1 className="text-3xl font-bold text-foreground">
            DoneKaro AI
          </h1>
          <p className="text-muted-foreground text-lg">
            Your intelligent task management assistant
          </p>
          <div className="pt-4 space-y-2 text-sm text-muted-foreground">
            <p>✨ Add, complete, and manage tasks with natural language</p>
            <p>🤖 Powered by AI for smarter task handling</p>
            <p>⚡ Fast and intuitive chat interface</p>
          </div>
          <div className="pt-6">
            <p className="text-sm text-muted-foreground animate-pulse">
              Click the chat button in the bottom right corner to get started →
            </p>
          </div>
        </div>
      </div>

      {/* Chat Widget */}
      <ChatInterface />
    </main>
  );
}
