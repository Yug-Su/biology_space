# 🚀 SpaceBio AI Intelligence Platform

AI-powered research platform for NASA space biology publications. Built for the **NASA Space Apps Challenge 2025**.

## ✨ Features

* **🔍 Enhanced Search** – Advanced search across titles, abstracts, and authors with year filtering
* **💬 AI Chat Assistant** – Conversational AI for research questions
* **✍️ Article Generator** – Generate comprehensive scientific articles
* **📊 Analytics Dashboard** – Track searches and AI generations
* **572 Research Articles** indexed from NASA PMC database

## 🏗️ Tech Stack

* **Backend:** Django 5.0 + SQLite
* **Frontend:** TailwindCSS + Alpine.js + HTMX
* **AI:** OpenRouter + Groq APIs
* **Search:** Multi-field text search with intelligent ranking

## 🚀 Quick Start

### 1. API Key Configuration

Create a `.env` file at the project root:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# OpenRouter API (https://openrouter.ai/)
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Groq API (https://console.groq.com/)
GROQ_API_KEY=gsk_xxxxx
```

**Where to get the keys:**

* **OpenRouter:** [https://openrouter.ai/keys](https://openrouter.ai/keys) (free with starter credits)
* **Groq:** [https://console.groq.com/](https://console.groq.com/) (free with starter credits)

### 2. Installation

```bash
# Activate virtual environment
source venv/Scripts/activate   # Windows Git Bash
# or
.\venv\Scripts\activate         # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Apply migrations (already done)
# python manage.py migrate

# Load articles (already done - 572 articles)
# python manage.py load_articles
```

### 3. Run the Server

```bash
python manage.py runserver
```

Open your browser at [http://localhost:8000](http://localhost:8000)

## 📁 Project Structure

```
007/
├── core/                       # Main Django app
│   ├── models.py               # Models (Article, Embedding, Chat)
│   ├── views.py                # Views (search, chat, generate)
│   ├── services/
│   │   ├── ai_providers.py     # OpenRouter + Groq logic
│   │   └── embeddings.py       # Embedding service
│   ├── management/commands/
│   │   ├── load_articles.py    # Load CSV data
│   │   └── generate_embeddings.py
│   └── templates/core/         # HTML templates
├── Data/
│   └── SB_publication_PMC.csv  # 608 NASA articles
├── db.sqlite3                  # Database
└── manage.py
```

## 🎯 Core Features

### 1. Enhanced Search

* **Multi-field Search** – Search across titles, abstracts, and authors
* **Smart Filtering** – Filter by publication year
* **Intelligent Ranking** – Sort results by popularity and relevance

### 2. AI Chat Assistant

* Chat with an AI trained on space biology topics
* Maintains conversation context
* Powered by **OpenRouter (GPT-4)** with **Groq fallback**

### 3. Article Generator

Automatically generate scientific articles:

* **Types:** Review, Research, Protocol
* **Length:** Short (500w), Medium (1000w), Long (2000w)
* **Style:** Academic, Executive, Technical

### 4. Django Admin

Access: [http://localhost:8000/admin](http://localhost:8000/admin)

Create a superuser:

```bash
python manage.py createsuperuser
```

## 💰 API Cost Estimate

**100% FREE:**

* ✅ Advanced search: **FREE** (no paid APIs)
* ✅ Article browsing: **FREE**
* ✅ Django Admin: **FREE**

**With API keys:**

* Chat AI: **$0.01–$0.05** per conversation (OpenRouter/Groq)
* Article generation: **$0.05–$0.20** per article

**Recommended budget for hackathon testing:** **$5–10**

## 🔧 Useful Commands

```bash
# Reload articles
python manage.py load_articles

# Open Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser
```

## 📊 Database

**Articles:** 572 (36 duplicates ignored)

Structure:

* `Article` – NASA scientific publications
* `ChatSession` – AI chat history
* `SearchQuery` – Search tracking
* `GeneratedArticle` – AI-generated scientific papers

## 🐛 Troubleshooting

**Error "No module named 'httpx'"**

```bash
pip install httpx
```

**API Error "Invalid key"**

* Ensure `.env` file is in the root directory
🚀 SpaceBio AI Intelligence Platform

AI-powered research platform for NASA space biology publications. Built for the**NASA Space Apps Challenge 2025**.

## ✨ Features

* **🔍 Enhanced Search** – Advanced search across titles, abstracts, and authors with year filtering
* **💬 AI Chat Assistant** – Conversational AI for research questions
* **✍️ Article Generator** – Generate comprehensive scientific articles
* **📊 Analytics Dashboard** – Track searches and AI generations
* **572 Research Articles** indexed from NASA PMC database

## 🏗️ Tech Stack

* **Backend:** Django 5.0 + SQLite
* **Frontend:** TailwindCSS + Alpine.js + HTMX
* **AI:** OpenRouter + Groq APIs
* **Search:** Multi-field text search with intelligent ranking

## 🚀 Quick Start

### 1. API Key Configuration

Create a `.env` file at the project root:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# OpenRouter API (https://openrouter.ai/)
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Groq API (https://console.groq.com/)
GROQ_API_KEY=gsk_xxxxx
```

**Where to get the keys:**

* **OpenRouter:** [https://openrouter.ai/keys](https://openrouter.ai/keys) (free with starter credits)
* **Groq:** [https://console.groq.com/](https://console.groq.com/) (free with starter credits)

### 2. Installation

```bash
# Activate virtual environment
source venv/Scripts/activate   # Windows Git Bash
# or
.\venv\Scripts\activate         # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Apply migrations (already done)
# python manage.py migrate

# Load articles (already done - 572 articles)
# python manage.py load_articles
```

### 3. Run the Server

```bash
python manage.py runserver
```

Open your browser at [http://localhost:8000](http://localhost:8000)

## 📁 Project Structure

```
spacebio/
├── core/                       # Main Django app
│   ├── models.py               # Models (Article, Embedding, Chat)
│   ├── views.py                # Views (search, chat, generate)
│   ├── services/
│   │   ├── ai_providers.py     # OpenRouter + Groq logic
│   │   └── embeddings.py       # Embedding service
│   ├── management/commands/
│   │   ├── load_articles.py    # Load CSV data
│   │   └── generate_embeddings.py
│   └── templates/core/         # HTML templates
├── Data/
│   └── SB_publication_PMC.csv  # 608 NASA articles
├── db.sqlite3                  # Database
└── manage.py
```

## 🎯 Core Features

### 1. Enhanced Search

* **Multi-field Search** – Search across titles, abstracts, and authors
* **Smart Filtering** – Filter by publication year
* **Intelligent Ranking** – Sort results by popularity and relevance

### 2. AI Chat Assistant

* Chat with an AI trained on space biology topics
* Maintains conversation context
* Powered by **OpenRouter (GPT-4)** with **Groq fallback**

### 3. Article Generator

Automatically generate scientific articles:

* **Types:** Review, Research, Protocol
* **Length:** Short (500w), Medium (1000w), Long (2000w)
* **Style:** Academic, Executive, Technical

### 4. Django Admin

Access: [http://localhost:8000/admin](http://localhost:8000/admin)

Create a superuser:

```bash
python manage.py createsuperuser
```

## 💰 API Cost Estimate

**100% FREE:**

* ✅ Advanced search: **FREE** (no paid APIs)
* ✅ Article browsing: **FREE**
* ✅ Django Admin: **FREE**

**With API keys:**

* Chat AI: **$0.01–$0.05** per conversation (OpenRouter/Groq)
* Article generation: **$0.05–$0.20** per article

**Recommended budget for hackathon testing:** **$5–10**

## 🔧 Useful Commands

```bash
# Reload articles
python manage.py load_articles

# Open Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser
```

## 📊 Database

**Articles:** 572 (36 duplicates ignored)

Structure:

* `Article` – NASA scientific publications
* `ChatSession` – AI chat history
* `SearchQuery` – Search tracking
* `GeneratedArticle` – AI-generated scientific papers

## 🐛 Troubleshooting

**Error "No module named 'httpx'"**

```bash
pip install httpx
```

**API Error "Invalid key"**

* Ensure `.env` file is in the root directory
* Double-check OpenRouter/Groq API keys

**Chat AI not responding**

* Verify `OPENROUTER_API_KEY` or `GROQ_API_KEY` is set
* Check console logs for detailed error messages

**Search returns no results**

* Check spelling
* Try broader terms (e.g., use "microgravity" instead of "microgravity effects")

## 🚀 Deployment

> 🧠 **Note from the team:**
> Initially, the README suggested using platforms like **Vercel**, **Railway**, or **PythonAnywhere**.
> However, **we did not deploy on these platforms** for our hackathon version.
> The current deployment and testing were done **locally** for demo purposes.

*(Original suggestion retained for reference)*

* **Vercel** – Frontend + Django (serverless)
* **Railway** – Django backend hosting
* **PythonAnywhere** – Full free hosting solution

## 📝 License

**MIT License** – NASA Space Apps Challenge 2025

## 👥 Team

**Hackathon NASA Space Apps Challenge 2025 – Team SpaceBio** 
