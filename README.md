# 🧠 SafeSpace – AI Mental Health Support Assistant

SafeSpace is an AI-powered mental health support assistant designed to provide empathetic conversations, emotional guidance, and access to helpful resources. The project combines Large Language Models (LLMs), AI Agents, and real-world tools to create a supportive and responsive user experience.

## ✨ Features

- 🤖 AI Agent powered by LangChain and LangGraph
- 💬 Mental health support conversations
- 🏥 Therapist recommendation tool
- 📞 Emergency assistance integration with Twilio
- ⚡ Fast responses using Groq LLMs
- 🌐 FastAPI backend
- 🎨 Streamlit frontend
- 🔧 Tool calling and agent-based decision making

## 🛠️ Tech Stack

### Backend

- Python
- FastAPI
- LangChain
- LangGraph
- Groq
- Twilio

### Frontend

- Streamlit

### AI & Agent Framework

- LangChain Tools
- ReAct Agent Architecture
- Large Language Models (LLMs)

## 🚀 Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd safespace-ai-therapist
```

Install dependencies:

```bash
uv sync
```

## ▶️ Run the Backend

```bash
uv run uvicorn backend.main:app --reload
```

Backend will start at:

```text
http://127.0.0.1:8000
```

## ▶️ Run the Frontend

```bash
uv run streamlit run frontend.py
```

## 📂 Project Structure

```text
safespace-ai-therapist/
│
├── backend/
│   ├── ai_agent.py
│   ├── config.py
│   ├── tools.py
│   └── main.py
│
├── frontend.py
├── pyproject.toml
├── uv.lock
└── README.md
```

## 🔐 Environment Variables

Store API keys securely and never commit them to GitHub.

Example:

```env
GROQ_API_KEY=your_api_key
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_FROM_NUMBER=your_number
EMERGENCY_CONTACT=your_contact
```

## 📌 Future Improvements

- Real therapist search using Google Maps API
- Conversation memory
- WhatsApp integration
- Multi-language support
- Crisis detection and escalation workflows

## 👨‍💻 Author

Abhishek Pathak

B.Tech CSE Student | MERN Stack Developer | AI Enthusiast
