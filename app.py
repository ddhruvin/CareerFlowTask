from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import smtplib
import sqlite3
import hashlib
import uuid
import time
import threading
import logging

app = FastAPI()
security = HTTPBasic()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Database Setup ---
def get_db():
    conn = sqlite3.connect("emails.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id TEXT PRIMARY KEY,
                        email TEXT UNIQUE,
                        password TEXT,
                        token TEXT,
                        plan TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS emails (
                        id TEXT PRIMARY KEY,
                        user_id TEXT,
                        to_email TEXT,
                        subject TEXT,
                        body TEXT,
                        send_at TEXT,
                        status TEXT)''')
    db.commit()
    db.close()

init_db()

# --- Pydantic Models ---
class SignupModel(BaseModel):
    email: EmailStr
    password: str
    plan: str  # e.g., 'free' or 'pro'

class LoginModel(BaseModel):
    email: EmailStr
    password: str

class EmailScheduleModel(BaseModel):
    to_email: EmailStr
    subject: str
    body: str
    send_at: datetime  # when to send the email

# --- Helper Functions ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (credentials.username,))
    user = cursor.fetchone()
    if not user or user['password'] != hash_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return user

def is_quota_exceeded(user_id, plan):
    db = get_db()
    cursor = db.cursor()
    today = datetime.now().date()
    cursor.execute("SELECT COUNT(*) FROM emails WHERE user_id=? AND date(send_at)=?", (user_id, today))
    count = cursor.fetchone()[0]
    daily_limit = 10 if plan.lower() == 'free' else 100
    return count >= daily_limit

# --- API Routes ---
@app.post("/signup")
def signup(data: SignupModel):
    token = str(uuid.uuid4())
    db = get_db()
    try:
        db.execute("INSERT INTO users (id, email, password, token, plan) VALUES (?, ?, ?, ?, ?)",
                   (str(uuid.uuid4()), data.email, hash_password(data.password), token, data.plan))
        db.commit()
        logger.info(f"New user signed up: {data.email}")
        return {"message": "Welcome aboard! Here's your token.", "token": token}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Looks like that email is already registered.")

@app.post("/login")
def login(data: LoginModel):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (data.email,))
    user = cursor.fetchone()
    if not user or user['password'] != hash_password(data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials, please try again.")
    return {"token": user['token']}

@app.post("/schedule")
def schedule_email(data: EmailScheduleModel, user=Depends(authenticate)):
    if is_quota_exceeded(user['id'], user['plan']):
        raise HTTPException(status_code=403, detail="You've hit your daily email limit. Try again tomorrow or upgrade.")

    db = get_db()
    cursor = db.cursor()
    email_id = str(uuid.uuid4())
    send_time = data.send_at.isoformat()  # make sure it's in ISO format

    cursor.execute("""
        INSERT INTO emails (id, user_id, to_email, subject, body, send_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (email_id, user['id'], data.to_email, data.subject, data.body, send_time, 'pending'))
    db.commit()

    logger.info(f"Scheduled email {email_id} to {data.to_email} at {send_time}")
    return {"message": "Your email has been scheduled successfully!"}

# --- Background Email Sender ---
def send_pending_emails():
    while True:
        db = get_db()
        now = datetime.utcnow().isoformat()  # NOTE: make sure to use UTC consistently
        cursor = db.cursor()
        cursor.execute("SELECT * FROM emails WHERE send_at<=? AND status='pending'", (now,))
        emails = cursor.fetchall()

        for email in emails:
            try:
                # Replace these credentials with env vars or secrets manager in production
                with smtplib.SMTP("smtp.mailtrap.io", 2525) as server:
                    server.login("username", "password")
                    message = f"Subject: {email['subject']}\n\n{email['body']}"
                    server.sendmail("from@example.com", email['to_email'], message)

                cursor.execute("UPDATE emails SET status='sent' WHERE id=?", (email['id'],))
                db.commit()
                logger.info(f"Sent email: {email['id']}")

            except Exception as e:
                logger.error(f"Failed to send email {email['id']}: {e}")

        db.close()
        time.sleep(60)  # check every 60 seconds

# Start background sender thread
threading.Thread(target=send_pending_emails, daemon=True).start()

@app.get("/")
def root():
    return {"message": "📬 FastAPI Email Scheduler is live!"}  # A little emoji never hurts ;)

# TODO: Add support for CC/BCC in future
# FIXME: SMTP error handling needs retry logic
12