# ♻️ EcoCollect

### E-Waste Collection & Recycling Management System

EcoCollect is a full-stack web application developed as a Database Management Systems (DBMS) mini-project using **React, FastAPI, and MySQL**.

The application allows users to submit electronic waste collection requests, track their recycling status, and manage e-waste collection activities through an administrator dashboard.

## 🌐 Live Website

**[Explore EcoCollect](https://ecocollect-7vd.pages.dev)**

## ✨ Features

**User Features**
- User registration and secure login
- Submit e-waste collection requests
- Add multiple electronic items to a request
- Track collection and recycling status
- View request history

**Administrator Features**
- Dashboard with collection statistics
- Manage collection requests
- Schedule pickups
- Assign recycling centres
- Update collection and recycling status
- View reports and analytics

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, Tailwind CSS |
| Backend | Python, FastAPI |
| Database | MySQL |
| ORM | SQLAlchemy |
| Authentication | JWT, Argon2 |
| Frontend Hosting | Cloudflare Pages |
| Backend Hosting | Render |
| Database Hosting | Aiven |
| Version Control | Git & GitHub |

## 🗄️ Database

EcoCollect uses six relational tables:

- `users`
- `ewaste_categories`
- `collection_requests`
- `request_items`
- `recycling_centres`
- `status_history`

The project demonstrates primary keys, foreign keys, relationships, SQL queries, constraints, database normalisation, and transaction management.

## 🔄 Recycling Workflow

`Pending → Scheduled → Collected → Recycled`

Each status update is recorded in the database.

## 💻 Run Locally

**Prerequisites:** Python 3.12+, Node.js, and MySQL 8.4.

Clone the repository:

```bash
git clone https://github.com/soumyajit-mandal-swe/EcoCollect.git
cd EcoCollect
```

Install backend dependencies:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
```

Configure your local MySQL database and environment variables (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, and `JWT_SECRET`). Never commit credentials to GitHub.

Initialize the database:

```powershell
.\.venv\Scripts\python.exe -m backend.init_db
```

Install frontend dependencies:

```powershell
cd frontend
npm install
cd ..
```

Start EcoCollect:

```powershell
.\Start-EcoCollect.cmd
```

Open the local URL displayed in the terminal.

## 👨‍💻 Developer

**Soumyajit Mandal**

GitHub: [@soumyajit-mandal-swe](https://github.com/soumyajit-mandal-swe)

---

*EcoCollect is an educational project developed to demonstrate DBMS concepts and full-stack web development. The demonstration recycling records do not represent actual recycling operations.*