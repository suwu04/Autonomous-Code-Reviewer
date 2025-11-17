# Autonomous AI Code Reviewer
A complete, end-to-end system that uses an autonomous AI agent (built with CrewAI) to review GitHub pull requests. The system is served via a FastAPI frontend, processed asynchronously using Celery workers, and is fully containerized with Docker.

---

## 🚀 Core Features
* **Simple Web Interface:** A clean, single-page HTML frontend to submit PRs and view results.
* **Asynchronous Processing:** Uses a Celery task queue so the AI can take its time reviewing code without blocking the user.
* **Intelligent AI Agent:** A CrewAI agent with a specific role (Senior Code Quality Reviewer) analyzes code diffs for bugs, style issues, performance, and best practices.
* **Reliable LLM Integration:** Uses LiteLLM to reliably connect to the Hugging Face API, using the powerful Llama-3-8B-Instruct model.
* **Structured Output:** The AI's findings are parsed and validated using Pydantic into a clean, predictable JSON format.
* **Graceful Error Handling:** The system can handle network errors or malformed AI responses and report them cleanly to the user.
* **Fully Containerized:** The entire 3-part application (web, worker, redis) is managed in one `docker-compose.yml` file for simple, one-command setup.

---

## 🏗️ System Architecture
This project is built as a three-part microservice, much like a restaurant:

* **`web` (The Waiter):** This is the FastAPI service. It serves the HTML frontend to the user and takes their "order" (the PR details). It doesn't do the review itself; it just creates a "job ticket" and puts it on the order wheel.
* **`redis` (The Order Wheel):** This is a high-speed Redis database. It holds the queue of "job tickets" created by the `web` service.
* **`worker` (The Chef):** This is the Celery service. It's a background worker constantly watching the `redis` queue for new jobs. When it sees one, it:
    1.  Fetches the PR diff from GitHub.
    2.  Uses the CrewAI agent to perform the complex AI analysis (the "cooking").
    3.  Saves the final, structured JSON review back to Redis.

The user interacts with the `web` service to check the status, which in turn checks `redis` to see if the `worker` has finished the job.

---

## 🛠️ Technology Stack
* **API:** FastAPI
* **Web Server:** Uvicorn (for development) & Gunicorn (for production)
* **Asynchronous Task Queue:** Celery
* **Broker / Result Backend:** Redis
* **AI Agent Framework:** CrewAI
* **LLM Provider:** LiteLLM (to connect to Hugging Face)
* **LLM:** `huggingface/meta-llama/Meta-Llama-3-8B-Instruct`
* **Data Validation:** Pydantic
* **Containerization:** Docker & Docker Compose
* **Frontend:** Plain HTML, CSS, and JavaScript
* **Git Client:** `requests` (to call the GitHub API)

---

## 🚀 How to Run Locally
This entire application is containerized, so you do not need to install Python or Redis on your machine. You only need Docker.

### 1. Prerequisites
* Docker Desktop (This is all you need to run the app)
* Git (To download the code)

### 2. Clone the Repository
Open your terminal (like PowerShell) and clone the project:
```bash
git clone [https://github.com/suwu04/Autonomous-Code-Reviewer.git](https://github.com/suwu04/Autonomous-Code-Reviewer.git)
cd Autonomous-Code-Reviewer
```

## 4. Build and Run the Application

This single command builds the Docker images and starts all three services (web, worker, and redis) at the same time.

```bash
docker-compose up --build
```
## 5.Use the App!
Your AI Code Reviewer is now running!
Open your web browser and go to: http://localhost:8000
You can now use the web interface to submit a PR for analysis and see the results appear on the page.

## 6. (Optional) View the API Docs
FastAPI automatically generates an interactive API (Swagger) documentation page. You can view it here: http://localhost:8000/docs

###In Action
##Review in Progress
<img width="943" height="595" alt="image" src="https://github.com/user-attachments/assets/794afb22-53df-49e1-866b-2e61428811be" />

While the AI agent is busy analyzing your pull request, the system displays a clear indication that the task is underway. This ensures you're always aware of the review's status.


##Review Results
<img width="1906" height="920" alt="Screenshot 2025-11-17 212151" src="https://github.com/user-attachments/assets/4f5790c1-a205-468e-8828-39dbc7e9f3a9" />

Once the AI has completed its analysis, the detailed findings are presented in an easy-to-understand format. Issues are ranked by severity, color-coded for quick identification, and each finding includes a clear explanation of the problem and a suggested fix.
<img width="1906" height="920" alt="Screenshot 2025-11-17 212151" src="https://github.com/user-attachments/assets/4f5790c1-a205-468e-8828-39dbc7e9f3a9" />

