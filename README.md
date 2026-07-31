<div align="center">

# 🎓 CollegeAI

### Intelligent AI-Powered Campus Companion

<p>
An AI assistant that helps students interact with academic documents using Retrieval Augmented Generation (RAG), semantic search, and Large Language Models.
</p>

<p>

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-Backend-black?style=for-the-badge)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-red?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-Database-green?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-LLM-purple?style=for-the-badge)
![RAG](https://img.shields.io/badge/RAG-Enabled-orange?style=for-the-badge)

</p>

---

### 🚀 AI Powered • Semantic Search • Document Chat • Study Planner

</div>

---

# 📖 Overview

CollegeAI is a full-stack AI-powered academic assistant built to help students understand, search, and interact with their study materials.

Instead of manually reading lengthy PDFs, students can upload documents and ask questions in natural language. The application retrieves relevant information using semantic search and generates context-aware responses using Large Language Models.

The project combines modern AI techniques such as Retrieval Augmented Generation (RAG), vector databases, embeddings, and conversational AI into a single academic platform.

---

# ✨ Features

## 🤖 AI Assistant

- AI powered academic chatbot
- Multiple assistant personas
- Interactive conversation history
- Context-aware responses

---

## 📄 Smart PDF Processing

- Upload PDF documents
- Automatic text extraction
- Intelligent chunking
- Semantic indexing
- Multiple document support

---

## 🧠 Retrieval Augmented Generation (RAG)

- Sentence Transformer embeddings
- FAISS vector database
- Semantic similarity search
- Context retrieval
- Accurate grounded responses

---

## 🎓 Student Dashboard

- User authentication
- Document statistics
- Chat analytics
- Recent activity
- Theme switching

---

## 📚 Academic Tools

- Study Planner
- Syllabus Analyzer
- AI Mentor
- General Chat
- Academic Tutor

---

## 🔐 Authentication

- Login
- Registration
- Session management

---

# 🖼️ Application Preview

## Login Page

![](screenshots/login-dark.png)

---

## Dashboard

![](screenshots/dashboard-dark.png)

---

## AI Chat

![](screenshots/chat-dark.png)

---

## Document Analysis

![](screenshots/document-chat.png)

---

## Light Theme

![](screenshots/dashboard-light.png)

---

# 🏗️ System Architecture

```
                Student

                   │

                   ▼

             Upload PDF

                   │

                   ▼

          Text Extraction

                   │

                   ▼

             Text Chunking

                   │

                   ▼

     Sentence Transformers

                   │

                   ▼

         FAISS Vector Store

                   │

                   ▼

      Relevant Context Search

                   │

                   ▼

            Groq LLM API

                   │

                   ▼

          AI Generated Answer
```

---

# 🛠 Technology Stack

## Backend

- Python
- Flask
- SQLAlchemy
- SQLite

---

## Artificial Intelligence

- Groq API
- FAISS
- Sentence Transformers
- Retrieval Augmented Generation
- Semantic Search

---

## Frontend

- HTML5
- CSS3
- JavaScript

---

## Database

- SQLite

---

## Project Structure

```
CollegeAI

├── app.py
├── config.py
├── requirements.txt
│
├── database
│   ├── db.py
│   └── models.py
│
├── src
│   ├── auth
│   ├── chat
│   ├── rag
│   ├── services
│   └── syllabus
│
├── templates
│
├── static
│
├── uploads
│
├── instance
│
└── screenshots
```

---

# ⚙️ Installation

Clone repository

```bash
git clone https://github.com/sauru2007/CollegeAI.git
```

Move into directory

```bash
cd CollegeAI
```

Create virtual environment

```bash
python -m venv .venv
```

Activate

Windows

```bash
.venv\Scripts\activate
```

Linux

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run application

```bash
python app.py
```

Open

```
http://127.0.0.1:5000
```

---

# Environment Variables

Create

```
.env
```

Example

```env
SECRET_KEY=your_secret_key
GROQ_API_KEY=your_api_key
```

---

# AI Pipeline

```
User Question

↓

Embedding Generation

↓

Semantic Search

↓

Relevant Chunks

↓

Prompt Construction

↓

Groq LLM

↓

Generated Answer
```

---

# Current Modules

| Module | Status |
|----------|----------|
| Authentication | ✅ |
| Dashboard | ✅ |
| PDF Upload | ✅ |
| AI Chat | ✅ |
| RAG Pipeline | ✅ |
| FAISS Search | ✅ |
| Study Planner | ✅ |
| Syllabus Analyzer | ✅ |

---

# Future Enhancements

- Voice Assistant
- OCR Support
- Campus Navigation
- Attendance Prediction
- Assignment Generator
- AI Resume Builder
- Mobile Application
- Multi-language Support
- Calendar Integration
- Teacher Dashboard
- Cloud Deployment
- Docker Support

---

# Author

## Sidharth Pandey

BCA Student

AI | Machine Learning | Software Development

GitHub

https://github.com/sauru2007

---

# License

MIT License

---

# Support

If you found this project useful,

⭐ Star this repository.
