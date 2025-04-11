# ✅ Task Manager App (FastAPI + Firebase + Firestore)

This cloud-based Task Manager application is designed for collaborative task tracking across multiple users. It enables authenticated users to create task boards, assign tasks, and manage team-based workflows in real time. The backend is built using Python's FastAPI framework, Firebase Authentication for secure login, and Google Firestore as the primary NoSQL database.

---

## 📌 Features Implemented

### 🔹 Group 1: Authentication & Board Setup
- Firebase Authentication (Sign Up, Login, Logout)
- User identity validation via Firebase Admin SDK
- Create task boards with metadata
- View boards where user is creator or member

### 🔹 Group 2: Collaboration Features
- Add user to board via UID
- Create, assign, and complete tasks
- Shared boards visible to all members

### 🔹 Group 3: Task/Board Operations
- Edit and delete tasks
- Rename board (creator only)
- Remove user and reassign tasks automatically
- Highlight unassigned tasks in red

### 🔹 Group 4: Final Polish
- Remove red highlight if reassigned
- Task counters: total, active, completed
- Board deletion only if empty
- Clean UI with Bootstrap styling and modals

---

## 🧱 Technologies Used

- **FastAPI** – RESTful backend framework
- **Firebase Authentication** – Secure sign-in with token validation
- **Google Firestore** – Scalable document-based database
- **HTML/CSS/JS** – Frontend (not discussed in backend scope)
- **Python 3.10+** – Core language
- **Uvicorn** – ASGI server for FastAPI