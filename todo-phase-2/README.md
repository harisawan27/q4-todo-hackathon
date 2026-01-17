# Multi-User Web Todo Application (Phase II)

A robust, full-stack task management application designed for individual productivity. This project represents Phase II of the Todo Hackathon, evolving from a CLI tool into a modern web and mobile-responsive application with secure multi-user support.

## 🚀 Features

### Core Task Management
*   **Smart Prioritization**: Organize tasks by urgency with color-coded priority levels (Urgent 🔴, High 🟠, Medium 🔵, Low ⚪).
*   **Deadline Tracking**: Never miss a deadline with real-time status indicators:
    *   **Overdue** alerts for missed tasks.
    *   **Today** highlights for immediate focus.
    *   **Countdown** timers for tasks due within 24 hours.
*   **Rich Details**: Add comprehensive descriptions and tags to keep your tasks context-aware and organized.

### User Experience
*   **Seamless Interaction**: Quick-toggle completion status, expandable task details, and safe deletion with confirmation dialogs.
*   **Secure Authentication**: Robust user registration and sign-in powered by Better Auth, including **Google OAuth** for a seamless experience, and JWT security.
*   **Profile Customization**: Personalize your account by uploading a profile picture on your account page.
*   **Data Privacy**: Strict data isolation ensures your tasks remain private and accessible only to you.

### Platform Support
*   **Responsive Design**: A fluid interface that adapts perfectly to Desktop, Tablet, and Mobile screens.
*   **Mobile Ready**: Native-like experience on Android via Capacitor integration.
*   **Dark Mode Support**: (Implicit support via Tailwind classes observed in codebase).

## 📊 Analytics & Notifications

The application provides powerful tools to track your productivity and stay informed about your tasks:

### Dedicated Statistics Dashboard
Access a comprehensive overview of your task management journey at `/dashboard/stats` (via the "Stats" link in the sidebar). This dashboard offers detailed insights, including:
*   **Key Performance Indicators**: Total, Completed, In Progress tasks, and your overall Completion Rate.
*   **Due Date Overview**: Categorization of tasks that are Overdue, Due Today, Due This Week, or tasks without a set due date.
*   **Priority Breakdown**: Visual representation of tasks across different priority levels (Urgent, High, Medium, Low) and their completion status.
*   **Weekly Progress**: Track your task completion trends with a comparison of tasks completed this week versus last week.
*   **Top Tags**: Discover your most frequently used tags for better organization.

### Real-time Notifications System
Stay updated with important task events through the integrated notifications system. Notifications are accessible via the **Bell Icon** in the header and a dedicated page at `/dashboard/notifications`.
*   **Event-Driven Alerts**: Receive announcements for events such as:
    *   New tasks being created.
    *   Tasks being completed or deleted.
    *   Deadlines approaching or passed.
*   **Full Control**:
    *   View all notifications, with an option to filter for unread messages.
    *   Mark individual notifications or all notifications as read.
    *   Clear specific notifications or all of them.

## 🛠️ Tech Stack

### Frontend
*   **Framework**: [Next.js](https://nextjs.org/) (App Router)
*   **Language**: TypeScript
*   **Styling**: Tailwind CSS
*   **Auth**: Better Auth
*   **Mobile**: Capacitor (Android)

### Backend
*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
*   **Language**: Python 3.10+
*   **ORM**: SQLModel
*   **Database**: PostgreSQL (Neon)

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
*   [Node.js](https://nodejs.org/) (v20 or higher)
*   [Python](https://www.python.org/) (v3.10 or higher)
*   [PostgreSQL](https://www.postgresql.org/) (or a Neon database instance)

## ⚡ Getting Started

### 1. Backend Setup

Navigate to the backend directory and set up the Python environment.

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Configuration:**
Copy `.env.example` to `.env` and update the values with your database credentials and secret keys.

```bash
cp .env.example .env
```

**Database Migration:**
Run the migration script to set up your database schema.

```bash
python migrations/run_migration.py
```

**Start Server:**
```bash
uvicorn app.main:app --reload
```
The backend API will be available at `http://localhost:8000`.

### 2. Frontend Setup

Open a new terminal, navigate to the frontend directory, and install dependencies.

```bash
cd frontend

# Install dependencies
npm install
```

**Configuration:**
Copy `.env.example` to `.env.local` and configure the necessary environment variables (API URL, Auth Secret, etc.).

```bash
cp .env.example .env.local
```

**Start Development Server:**
```bash
npm run dev
```
The application will be running at `http://localhost:3000`.

## 📱 Mobile (Android)

To build and run the application on an Android device or emulator:

```bash
cd frontend
npm run android:build
```
*Note: This requires Android Studio to be installed and configured.*

## 🤝 Contributing

We welcome contributions! Please see the `CONTRIBUTING.md` file for details on how to get involved.

1.  Fork the repository
2.  Create a feature branch (`git checkout -b feature/amazing-feature`)
3.  Commit your changes (`git commit -m 'Add some amazing feature'`)
4.  Push to the branch (`git push origin feature/amazing-feature`)
5.  Open a Pull Request

## 🆘 Support

If you encounter any issues or have questions, please check the existing issues or file a new one in the issue tracker.
