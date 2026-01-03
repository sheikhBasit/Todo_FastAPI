# ToDo API with FastAPI

A robust, asynchronous **FastAPI** application for managing tasks and groups. This project features **AI-driven task suggestions**, secure **JWT authentication**, and a "Default Inbox" strategy to ensure seamless organization for every user.



## 🚀 Live Demo

* **API Home:** [https://todo-fast-api-alpha.vercel.app](https://todo-fast-api-alpha.vercel.app)
* **Interactive Swagger Docs:** [/docs](https://todo-fast-api-alpha.vercel.app/docs)
* **ReDoc Interface:** [/redoc](https://todo-fast-api-alpha.vercel.app/redoc)



## ✨ Key Features

* **Automatic Inbox:** Every new user gets an "Inbox" group automatically via SQLAlchemy event listeners upon registration.
* **Smart Indexing:** Composite unique constraints ensure task titles are unique **within a group** per user, preventing messy duplicates while allowing flexibility across different groups.
* **AI Integration:** Powered by **Groq/LLM** to provide intelligent task descriptions and planning suggestions.
* **Security & Performance:** Protected by **SlowAPI** rate limiting and organized with custom middlewares for logging and GZip compression.



## 🛠 Setup & Execution

### 1. Environment Configuration

Copy the template file and update it with your **Postgres URL** (Neon.tech recommended), **Secret Key**, and **Groq API Key**:


cp .env.example .env



### 2. 🐳 Running with Docker (Recommended)

This is the fastest way to get the API running with all system dependencies (like `libpq-dev`) pre-configured.


docker-compose up --build



### 3. 🐍 Local Development (For IDE Support)

If you want local IntelliSense and linting in your editor:


python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt





## 🗄 Database & Migrations

### Configuration

The app uses `create_engine` with `pool_pre_ping=True` to handle the "cold starts" associated with serverless databases like Neon.

### Schema Management

* **Auto-Creation:** The app is configured to run `Base.metadata.create_all(bind=engine)` on startup.
* **Alembic (Optional):** If you wish to use versioned migrations:

alembic revision --autogenerate -m "Initial migration"
alembic upgrade head







## 🚀 Deployment & CI/CD

### Makefile (Hypercorn)

We use **Hypercorn** as our ASGI server for high-performance throughput and HTTP/2 support.


make run      # Start the production server
make test     # Run the pytest suite using an in-memory SQLite DB



### Vercel

This project is optimized for deployment as **Vercel Serverless Functions**.

* The `vercel.json` file handles routing to `app/main.py`.
* Deployment is triggered automatically on every `git push` to the main branch.



## 🧪 Testing

The test suite uses `httpx` and `pytest`. It overrides the production database with an **in-memory SQLite** instance for total isolation.

# Inside Docker
docker-compose exec web pytest -v
