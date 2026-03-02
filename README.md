# AstroLogic AI  
### AI-Powered Vedic Astrology Platform

AstroLogic AI is a full-stack Vedic astrology platform built using **FastAPI, Swiss Ephemeris, and AI LLM integration**.  
It provides Kundali generation, Panchang, Daily Horoscope with caching, AI-based Predictions, Chat module, and Admin Blog CMS.

---

## 🚀 Features

### 🪐 Kundali Generation
- Lagna calculation
- Planetary positions
- Houses & strengths
- Scoring engine (Career, Finance, Relationship, Health)

### 📅 Panchang
- Tithi
- Nakshatra
- Yoga
- Karana
- City-based calculation

### 🔮 AI Predictions
- Marriage prediction
- Career prediction
- Structured astrological interpretation
- LLM-powered analysis

### 💬 Astrology Chat
- Context-aware AI chat
- Uses generated birth chart
- Structured astrological responses

### 🌞 Daily Horoscope
- 12 zodiac signs
- API-based horoscope
- Daily caching (1 call per sign per day)

### 📝 Blog CMS
- Create blog
- Edit blog
- Delete blog
- Admin authentication protected panel

---

## 🛠 Tech Stack

**Backend**
- FastAPI
- Pydantic
- SQLAlchemy
- Session Middleware
- Swiss Ephemeris

**AI Layer**
- LLM Integration
- Structured Prompt Builder
- Context-aware prediction engine

**Frontend**
- HTML
- Bootstrap 5
- Custom Glass UI Theme
- JavaScript Fetch API

**Database**
- SQLite (can be upgraded to PostgreSQL)

---

## 📂 Project Structure


AstroLogic-AI/
  - main.py
  - api/
  - astro_engine/
  - models/
  - services/
  - templates/
  - static/
  - database/
  - requirements.txt
  - .gitignore
  - README.md


---

## ⚙️ Installation

### 1️⃣ Clone Repository


git clone https://github.com/yourusername/AstroLogic-AI.git

cd AstroLogic-AI


### 2️⃣ Create Virtual Environment


python -m venv venv
venv\Scripts\activate


### 3️⃣ Install Dependencies


pip install -r requirements.txt


### 4️⃣ Create .env File


SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_api_key


### 5️⃣ Run Server


uvicorn main:app --reload


Visit:


http://127.0.0.1:8000


---

## 🔐 Admin Panel

Admin panel includes:

- Secure authentication
- Blog creation
- Blog editing
- Blog deletion

Access:

/admin


---

## 📊 Prediction Engine

The prediction engine uses:

- Planet strengths
- House activation
- Dasha timeline
- Yogas
- Functional nature
- Dispositor logic

Scores are generated for:
- Career
- Marriage
- Finance
- Mental Strength
- Overall Strength

---

## 🧠 AI Integration

AstroLogic uses structured prompts to:
- Generate prediction summaries
- Provide analytical responses
- Maintain astrological context in chat

---

## 📈 Future Improvements

- Deployment on cloud (Render / AWS)
- JWT-based authentication
- Multi-user accounts
- Paid premium prediction module
- Advanced Dasha timeline visualizer

---

## 👨‍💻 Author

**Atharv Kulkarni**  
Computer Engineering Student  
AI + Full Stack Developer  

---

## 📜 License

MIT License

---

## 🌟 If you like this project

Star ⭐ the repository and support development.
