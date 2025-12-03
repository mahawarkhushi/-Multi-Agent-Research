# 🚀 Multi-Agent Research & Reporting Platform

A production-grade **multi-agent research system** built with a secure Python backend, LLM-powered job processing, robust RBAC authentication, and a Streamlit-based admin dashboard. The system ingests documents, runs analysis via agents & tools, and generates explainable reports.

---

## 🔐 Authentication & RBAC

* JWT-based **access + refresh token** flow.
* Secure login, signup, logout, token refresh.
* **Role-Based Access Control (RBAC)**:

  * **Admin** — full access to users, agents, jobs.
  * **User** — can run their own jobs and view results.
* Session persistence on refresh using refresh-token API.

---

## 🧠 Multi-Agent System (Agents + Tools)

Each Agent contains:

* **Tools** (internal/external) like LLM inference, document chunking, search tool, summarizer.
* Tool execution pipelines.
* Configurable workflows.

Agents allow:

* Reusable logic
* Modular research workflows
* LLM-backed reporting

Jobs run via:

* LLM Tools → Agent Pipeline → Report Output
* Supports: PDF, TXT, DOCX ingestion + raw JSON data.

---

## 📑 LLM-Powered Job Processing

* File input or JSON input.
* Background job execution using agents.
* Output stored as JSON (report, summary, errors, progress).
* Fully modular — replace HuggingFace/LLM models anytime.

---

## 🖥️ Streamlit Dashboard (Frontend)

* Authentication (Login, Signup).
* Token display (for debugging).
* Create Job (file upload or JSON).
* View Jobs (auto-filtered by role).
* Agent manager + Tools manager.
* Admin-only actions: cancel job, view all jobs.

---

## 🐳 Docker Compose

`docker-compose.yml` manages:

* **Backend (FastAPI)**
* **PostgreSQL database**
* **Kafka** (optional, for background job queue or event pipeline)
* **Streamlit frontend**

Ensures:

* One-command start
* Consistent dev/prod environment
* Easy deployment

---

## 🛢️ PostgreSQL Database (Why not MySQL?)

The system uses **PostgreSQL** because:

1. **Native JSONB support** — perfect for storing:

   * job input/output
   * agent configs
   * tool metadata
2. Better handling of **semi-structured LLM data**.
3. Superior indexing for search and analytics.
4. Stronger transactional guarantees.
5. Plays well with async Python frameworks and SQLAlchemy.

MySQL struggles with JSON workloads and complex relations, making Postgres the ideal choice.

---

## ⚡ Backend (Python + FastAPI)

Features:

* Fully typed, modular API.
* JWT auth system.
* Models, migrations, and schemas with SQLAlchemy.
* Agents, Tools, Jobs modules.
* Seamless file processing pipeline.
* Configurable to plug in real LLMs (OpenAI, HF, etc.).

---

## 📬 Kafka (Optional)

Kafka is integrated for:

* Background job queue
* Event-based processing
* Scalable multi-agent execution

Can be enabled/disabled via compose.

---

## 📦 Tech Stack Summary

| Layer            | Technologies           |
| ---------------- | ---------------------- |
| **Frontend**     | Streamlit              |
| **Backend**      | FastAPI, Python        |
| **Database**     | PostgreSQL             |
| **Queue**        | Kafka (optional)       |
| **ORM**          | SQLAlchemy             |
| **Auth**         | JWT (access + refresh) |
| **Infra**        | Docker Compose         |
| **Agents/Tools** | Modular LLM pipeline   |

---

## ▶️ Run Locally

```
docker-compose up --build
```

Backend → `http://localhost:8000`
Frontend → `http://localhost:8501`

---

## 📚 Summary

This platform gives you:

* Secure login + RBAC
* Multi-agent LLM research workflows
* File-based or JSON-based job processing
* Dashboard for real-time monitoring
* Production backend with PostgreSQL + Kafka
* Modular, scalable architecture

Perfect foundation for AI research tools, automation, and enterprise-grade agent systems.
