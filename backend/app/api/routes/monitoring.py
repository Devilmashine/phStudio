"""
Monitoring and Metrics API Routes
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from typing import Dict, Any
import logging
import os

from ...core.metrics import metrics_endpoint, get_application_health, metrics_collector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# Get the directory where this file is located
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(CURRENT_DIR)), "templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def monitoring_dashboard():
    """
    Monitoring dashboard HTML page
    Returns the monitoring dashboard interface
    """
    try:
        dashboard_path = os.path.join(TEMPLATES_DIR, "monitoring_dashboard.html")
        with open(dashboard_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)
    except Exception as e:
        logger.error(f"Error serving dashboard: {e}")
        return HTMLResponse(content="<h1>Error loading dashboard</h1>", status_code=500)

@router.get("/metrics", response_model=str)
async def prometheus_metrics(request: Request):
    """
    Prometheus metrics endpoint
    Returns metrics in Prometheus format for monitoring systems
    """
    return await metrics_endpoint(request)

@router.get("/health/application", response_model=Dict[str, Any])
async def application_health():
    """
    Application health check with metrics
    Returns comprehensive health information including performance metrics
    """
    try:
        return get_application_health()
    except Exception as e:
        logger.error(f"Application health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
        }

@router.get("/metrics/summary", response_model=Dict[str, Any])
async def metrics_summary():
    """
    Summary of application metrics
    Returns aggregated metrics for quick overview
    """
    try:
        from prometheus_client import generate_latest, REGISTRY
        import json
        
        # Get endpoint stats
        endpoint_stats = metrics_collector.get_endpoint_stats()
        
        # Get system metrics if available
        system_metrics = {}
        try:
            import psutil
            process = psutil.Process()
            system_metrics = {
                "cpu_percent": process.cpu_percent(),
                "memory_rss": process.memory_info().rss,
                "memory_percent": process.memory_percent(),
                "uptime": metrics_collector.get_uptime()
            }
        except ImportError:
            system_metrics = {"error": "psutil not available"}
        except Exception as e:
            system_metrics = {"error": str(e)}
        
        return {
            "endpoint_stats": endpoint_stats,
            "system_metrics": system_metrics,
            "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Metrics summary failed: {e}")
        return {
            "error": str(e),
            "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
        }

@router.get("/metrics/endpoints", response_model=Dict[str, Any])
async def endpoint_metrics():
    """
    Detailed endpoint performance metrics
    Returns performance statistics for all endpoints
    """
    try:
        return {
            "endpoint_stats": metrics_collector.get_endpoint_stats(),
            "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Endpoint metrics failed: {e}")
        return {
            "error": str(e),
            "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
        }

@router.get("/metrics/business", response_model=Dict[str, Any])
async def business_metrics():
    """
    Business metrics and KPIs
    Returns key business performance indicators
    """
    try:
        # This would typically query the database for real business metrics
        # For now, we'll return a placeholder structure
        return {
            "bookings": {
                "today": 0,
                "this_week": 0,
                "this_month": 0,
                "total": 0
            },
            "revenue": {
                "today": 0,
                "this_week": 0,
                "this_month": 0,
                "total": 0
            },
            "employees": {
                "active": 0,
                "total": 0
            },
            "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Business metrics failed: {e}")
        return {
            "error": str(e),
            "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
        }

@router.get("/status", response_model=Dict[str, str])
async def simple_status():
    """
    Simple status endpoint for quick checks
    Returns basic status information
    """
    return {"status": "ok", "service": "photo-studio-api"}

@router.get("/version", response_model=Dict[str, str])
async def version_info():
    """
    Application version information
    Returns version and build information
    """
    return {
        "version": "1.0.0",
        "name": "phStudio API",
        "environment": "development"  # This would be dynamic in production
    }