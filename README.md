# CareerFlowTask: Email Scheduler API

This project is a FastAPI-based email scheduler that allows users to:

- Sign up and receive a unique token
- Log in to receive authentication
- Schedule emails to be sent at a specific time (uses background tasks)

## 🚀 Features

- **User Authentication**: Secure login and signup endpoints
- **Email Scheduling**: Schedule emails with a specific send time
- **Token-based Authorization**: Protect scheduling endpoint with credentials
- **SQLite Database**: Store user and scheduling information persistently

## 📦 Tech Stack

- **Backend Framework**: FastAPI
- **Database**: SQLite
- **Email Delivery**: (Configured via SMTP – e.g., Gmail)
- **Testing Tool**: FastAPI Swagger UI at `/docs`

## 📁 Project Structure

```
CareerFlowTask/
├── main.py               # FastAPI app and routes
├── models.py             # Pydantic models for validation
├── database.py           # SQLite DB connection and ORM (if used)
├── utils.py              # Email utility functions
├── scheduler.py          # Background task handler
├── .env                  # Environment variables (for secrets)
└── README.md             # You're reading it
```

## 🔐 Authentication

- Sign up with your email and password to receive a token.
- Use your credentials in Basic Auth to access the `/schedule` endpoint.

## ✅ API Endpoints

| Method | Endpoint     | Description              |
|--------|--------------|--------------------------|
| POST   | `/signup`    | Register a new user      |
| POST   | `/login`     | Log in with credentials  |
| POST   | `/schedule`  | Schedule an email (auth) |
| GET    | `/`          | Welcome message          |

## 🧪 How to Test

1. Run the server:

```bash
uvicorn main:app --reload
```

2. Go to Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

3. Test all endpoints directly from the browser.

## 📬 Email Format

When calling `/schedule`, provide:

```json
{
  "to_email": "example@gmail.com",
  "subject": "Hello",
  "body": "Your scheduled email is here!",
  "send_at": "2025-04-04T17:21:11.752Z"
}
```

Emails are sent asynchronously in the background.

## 🛠️ Setup Instructions

1. Clone the repo:
```bash
git clone https://github.com/ddhruvin/CareerFlowTask.git
```

2. Create a virtual environment and install dependencies:
```bash
pip install -r requirements.txt
```

3. Add `.env` for email config (SMTP credentials, etc.):
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_password
```

4. Run the app:
```bash
uvicorn main:app --reload
```

## 📌 Notes

- Make sure to allow "Less secure apps" or App Passwords in Gmail settings.
- This app is not meant for production use without proper security measures.

## 🙌 Acknowledgements

- Built as a task for CareerFlow
- Powered by FastAPI + SQLite + SMTP

---

**Made with ❤️ by Dhruvin Dholakia**

