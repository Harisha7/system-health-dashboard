import os
import psutil
import psycopg2
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="System Health Dashboard")
templates = Jinja2Templates(directory="templates")

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "healthdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "postgres123")

def check_db_health():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            connect_timeout=3
        )
        conn.close()
        return "Connected (Healthy)"
    except Exception as e:
        return f"Disconnected ({e.__class__.__name__})"

@app.get("/api/health")
def health_metrics():
    cpu = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    db_status = check_db_health()

    return {
        "status": "healthy" if "Connected" in db_status and cpu < 90 else "degraded",
        "cpu_usage_pct": cpu,
        "memory_usage_pct": memory.percent,
        "memory_used_gb": round(memory.used / (1024 ** 3), 2),
        "memory_total_gb": round(memory.total / (1024 ** 3), 2),
        "disk_usage_pct": disk.percent,
        "database_status": db_status
    }

@app.get("/", response_class=HTMLResponse)
def dashboard_view(request: Request):
    metrics = health_metrics()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"metrics": metrics}
    )