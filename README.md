Markdown# 🚀 Mini-RAG: Build a Production-Ready RAG Application

**Mini-RAG** is an educational, step-by-step project designed to teach you how to create a fully functional **Retrieval-Augmented Generation (RAG)** application. Perfect for developers diving into advanced AI systems, this minimal implementation combines powerful tools like FastAPI, Celery, Docker, and more to handle document ingestion, vector search, and intelligent question answering.

## 📋 Requirements

- **Python 3.10**

### System Dependencies
```bash
sudo apt update
sudo apt install libpq-dev gcc python3-dev
Install Python with Miniconda

Download and install Miniconda from the official site.
Create and activate the environment:Bashconda create -n mini-rag python=3.10
conda activate mini-rag

Optional: Enhance Your Terminal
Bashexport PS1="$$ \033[01;32m $$\u@\h:\w\n$$ \033[00m $$\$ "
Optional: Run Ollama Locally with Colab + Ngrok
Explore running local LLMs remotely using this Colab Notebook and tutorial video.
⚙️ Installation
Install Packages
Bashpip install -r requirements.txt
Environment Setup
Bashcp .env.example .env
Edit .env with your keys (e.g., OPENAI_API_KEY).
Database Migrations
Bashalembic upgrade head
🐳 Docker Compose Services
Bashcd docker
cp .env.example .env
# Update .env with credentials
cd ..
sudo docker compose up -d
Access Your Services






























ServiceURLNotesFastAPIhttp://localhost:8000API docs at /docsFlowerhttp://localhost:5555Credentials in .envGrafanahttp://localhost:3000Monitoring dashboardsPrometheushttp://localhost:9090Metrics collection
🖥️ Running in Development Mode
Start FastAPI Server
Bashuvicorn main:app --reload --host 0.0.0.0 --port 5000
Celery (Manual for Dev)
Worker (in a new terminal):
Bashpython -m celery -A celery_app worker --queues=default,file_processing,data_indexing --loglevel=info
Beat Scheduler (another terminal):
Bashpython -m celery -A celery_app beat --loglevel=info
Flower Dashboard (optional):
Bashpython -m celery -A celery_app flower --conf=flowerconfig.py
Visit http://localhost:5555 for task monitoring.
📬 API Testing with Postman
Download the ready-to-use collection: mini-rag-app.postman_collection.json
Dive in, experiment, and build smarter AI applications with Mini-RAG! 🔥