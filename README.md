# GAARD AI – Government AI for Automated Reporting and Detection

GAARD AI is an AI-powered civic issue detection and response system that helps identify public infrastructure problems such as potholes, garbage overflow, and water leakage.

Users can upload an image of a civic issue, and the system analyzes it using AI, determines its category and severity, routes it to the appropriate department, and sends an automated notification.

## Features

- **Image Quality Check:** Detects unclear, blurry, or low-quality images.
- **AI-Based Issue Detection:** Identifies the type of civic issue using computer vision and AI.
- **Severity Analysis:** Classifies issues based on their severity.
- **Automated Department Routing:** Routes reported issues to the appropriate department.
- **Email Notifications:** Sends automated notifications to the concerned department.
- **Agentic Workflow:** Uses multiple AI agents to automate the complete process.

## Tech Stack

- Python
- FastAPI
- Streamlit
- OpenCV
- Gemini Vision API
- LangGraph
- PostgreSQL
- SQLAlchemy
- SMTP
- REST APIs

## Workflow

1. User uploads an image of a civic issue.
2. Image Quality Agent checks image clarity.
3. Vision Agent identifies the issue and its severity.
4. Decision Agent determines the next action.
5. Routing Agent selects the appropriate department.
6. Notification Agent sends an email notification.

## Project Structure

```text
GAARD/
│
├── main.py
├── app.py
├── agents/
├── database/
├── requirements.txt
├── .env
└── README.md
```

*Note: Update the structure above to match your actual project folders.*

## Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd GAARD
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file and add your required API keys and email configuration.

```env
GEMINI_API_KEY=your_api_key
DATABASE_URL=your_database_url
EMAIL_ADDRESS=your_email
EMAIL_PASSWORD=your_app_password
```

Never upload your actual API keys or passwords to GitHub.

### 5. Run Backend

```bash
uvicorn main:app --reload
```

Backend: http://127.0.0.1:8000

API Documentation: http://127.0.0.1:8000/docs

### 6. Run Frontend

Open another terminal:

```bash
source venv/bin/activate
streamlit run app.py
```

Frontend: http://localhost:8501

## Future Improvements

- Real-time civic issue monitoring.
- Interactive map for reported issues.
- Admin dashboard for issue tracking.
- Integration with government complaint management systems.

## Author

**Naladimmi Vijay Kumar Reddy**

B.Tech – Computer Science and Engineering  
RGUKT Ongole
