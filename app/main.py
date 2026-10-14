import os
from pathlib import Path
import psutil
import psycopg2
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="System Health Dashboard")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "healthdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "postgres123")

def check_db_health() -> str:
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
    except Exception as exc:
        return f"Disconnected ({exc.__class__.__name__})"

@app.get("/api/health")
def health_metrics():
    cpu = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    db_status = check_db_health()
    is_healthy = ("Connected" in db_status) and (cpu < 95.0)

    return {
        "status": "healthy" if is_healthy else "degraded",
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