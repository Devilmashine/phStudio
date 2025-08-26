"""
Health Check API Routes for Database Monitoring
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import logging

from ..core.health import get_database_health, db_health

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Basic health check endpoint
    Returns overall application health status
    """
    try:
        health_data = await get_database_health()
        
        # Return simplified health status for load balancers
        return {
            "status": health_data["overall_status"],
            "timestamp": health_data["timestamp"],
            "environment": health_data["environment"]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@router.get("/health/detailed", response_model=Dict[str, Any])
async def detailed_health_check():
    """
    Detailed health check endpoint for administrators
    Returns comprehensive database health information
    """
    try:
        return await get_database_health()
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@router.get("/health/database", response_model=Dict[str, Any])
async def database_health_check():
    """
    Database-specific health check endpoint
    Returns only database connectivity and performance metrics
    """
    try:
        health_data = await get_database_health()
        
        return {
            "status": health_data["checks"]["connection"]["status"],
            "connection": health_data["checks"]["connection"],
            "pool": health_data["checks"]["connection_pool"],
            "performance": health_data["checks"]["performance"],
            "timestamp": health_data["timestamp"]
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")

@router.get("/health/ready", response_model=Dict[str, str])
async def readiness_check():
    """
    Kubernetes readiness probe endpoint
    Returns 200 if service is ready to accept traffic
    """
    try:
        connection_check = db_health.check_connection()
        tables_check = db_health.check_tables()
        
        if (connection_check["status"] == "healthy" and 
            tables_check["status"] in ["healthy", "warning"]):
            return {"status": "ready"}
        else:
            raise HTTPException(status_code=503, detail="Not ready")
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Not ready")

@router.get("/health/live", response_model=Dict[str, str])
async def liveness_check():
    """
    Kubernetes liveness probe endpoint
    Returns 200 if service is running
    """
    try:
        # Basic check - just verify the service is responding
        return {"status": "alive"}
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        raise HTTPException(status_code=503, detail="Not alive")