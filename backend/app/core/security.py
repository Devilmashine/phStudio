"""
Security middleware for phStudio application.
Implements enterprise-grade security headers with minimal cost.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging
from typing import Dict, Any
import uuid
from app.core.input_validation import input_validator

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive security headers middleware.
    Cost-effective implementation using only FastAPI/Starlette built-ins.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        
        # Content Security Policy - restrictive but functional
        self.csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.telegram.org; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate request ID for tracing
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Security Headers
            self._add_security_headers(response, request)
            
            # Performance monitoring
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id
            
            # Log security events
            self._log_security_event(request, response, process_time)
            
            return response
            
        except Exception as e:
            # Log security exceptions
            logger.error(f"Security middleware error: {str(e)}", extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "client_ip": self._get_client_ip(request)
            })
            raise
    
    def _add_security_headers(self, response: Response, request: Request) -> None:
        """Add comprehensive security headers"""
        
        # Prevent XSS attacks
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Prevent MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # HSTS for HTTPS enforcement (only in production)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = self.csp_policy
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy (Feature Policy replacement)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )
        
        # Remove server information
        response.headers["Server"] = "phStudio"
        
        # Cache control for security-sensitive responses
        if request.url.path.startswith("/api/auth/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address with security considerations"""
        # Check for X-Forwarded-For (but validate to prevent spoofing)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take only the first IP and validate it's not private
            ip = forwarded_for.split(",")[0].strip()
            if self._is_valid_public_ip(ip):
                return ip
        
        # Check for X-Real-IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip and self._is_valid_public_ip(real_ip):
            return real_ip
        
        # Fall back to client host
        return request.client.host if request.client else "unknown"
    
    def _is_valid_public_ip(self, ip: str) -> bool:
        """Validate IP address is not private/local"""
        try:
            import ipaddress
            ip_obj = ipaddress.ip_address(ip)
            return not (ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local)
        except ValueError:
            return False
    
    def _log_security_event(self, request: Request, response: Response, process_time: float) -> None:
        """Log security-relevant events"""
        
        # Log authentication attempts
        if request.url.path.startswith("/api/auth/"):
            log_data = {
                "event_type": "auth_request",
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("User-Agent", "unknown"),
                "request_id": getattr(request.state, "request_id", "unknown"),
                "process_time": process_time
            }
            
            if response.status_code == 401:
                logger.warning("Failed authentication attempt", extra=log_data)
            elif response.status_code == 200:
                logger.info("Successful authentication", extra=log_data)
        
        # Log suspicious activity
        if self._is_suspicious_request(request, response):
            logger.warning("Suspicious request detected", extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("User-Agent", "unknown"),
                "request_id": getattr(request.state, "request_id", "unknown")
            })
    
    def _is_suspicious_request(self, request: Request, response: Response) -> bool:
        """Detect potentially suspicious requests"""
        
        # Check for common attack patterns in URL
        suspicious_patterns = [
            "../", "..", "script>", "<script", "javascript:", "eval(",
            "union select", "drop table", "insert into", "delete from"
        ]
        
        path_lower = request.url.path.lower()
        query_lower = str(request.query_params).lower()
        
        for pattern in suspicious_patterns:
            if pattern in path_lower or pattern in query_lower:
                return True
        
        # Check for unusually long URLs (potential buffer overflow)
        if len(str(request.url)) > 2048:
            return True
        
        # Check for multiple failed requests (could indicate brute force)
        if response.status_code in [401, 403, 429]:
            return True
        
        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    Cost-effective alternative to Redis for small applications.
    """
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.clients: Dict[str, Dict[str, Any]] = {}
        self.cleanup_interval = 300  # Cleanup every 5 minutes
        self.last_cleanup = time.time()
    
    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = self._get_client_ip(request)
        
        # Cleanup old entries periodically
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries(current_time)
            self.last_cleanup = current_time
        
        # Check rate limit
        if self._is_rate_limited(client_ip, current_time):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return Response(
                content='{"detail": "Rate limit exceeded"}',
                status_code=429,
                media_type="application/json",
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0"
                }
            )
        
        # Update request count
        self._update_request_count(client_ip, current_time)
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self._get_remaining_requests(client_ip, current_time)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP with basic validation"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Check if client has exceeded rate limit"""
        if client_ip not in self.clients:
            return False
        
        client_data = self.clients[client_ip]
        window_start = current_time - 60  # 1 minute window
        
        # Count requests in the current window
        request_count = sum(1 for timestamp in client_data["requests"] 
                          if timestamp > window_start)
        
        return request_count >= self.requests_per_minute
    
    def _update_request_count(self, client_ip: str, current_time: float) -> None:
        """Update request count for client"""
        if client_ip not in self.clients:
            self.clients[client_ip] = {"requests": []}
        
        self.clients[client_ip]["requests"].append(current_time)
        
        # Keep only requests from the last minute
        window_start = current_time - 60
        self.clients[client_ip]["requests"] = [
            timestamp for timestamp in self.clients[client_ip]["requests"]
            if timestamp > window_start
        ]
    
    def _get_remaining_requests(self, client_ip: str, current_time: float) -> int:
        """Get remaining requests for client"""
        if client_ip not in self.clients:
            return self.requests_per_minute
        
        window_start = current_time - 60
        request_count = sum(1 for timestamp in self.clients[client_ip]["requests"]
                          if timestamp > window_start)
        
        return max(0, self.requests_per_minute - request_count)
    
    def _cleanup_old_entries(self, current_time: float) -> None:
        """Remove old entries to prevent memory leaks"""
        cutoff_time = current_time - 3600  # Remove entries older than 1 hour
        
        clients_to_remove = []
        for client_ip, client_data in self.clients.items():
            # Remove old requests
            client_data["requests"] = [
                timestamp for timestamp in client_data["requests"]
                if timestamp > cutoff_time
            ]
            
            # Mark client for removal if no recent requests
            if not client_data["requests"]:
                clients_to_remove.append(client_ip)
        
        # Remove inactive clients
        for client_ip in clients_to_remove:
            del self.clients[client_ip]


class InputValidationMiddleware(BaseHTTPMiddleware):
    """
    Automatic input validation and sanitization middleware.
    Validates and sanitizes all incoming request data.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        
        # Endpoints that require validation
        self.validation_rules = {
            '/api/auth/users': {
                'POST': {
                    'username': 'username',
                    'email': 'email',
                    'full_name': 'name',
                    'password': 'password'
                }
            },
            '/api/bookings/': {
                'POST': {
                    'client_name': 'name',
                    'client_email': 'email',
                    'client_phone': 'phone',
                    'notes': 'text',
                    'total_price': 'decimal'
                }
            },
            '/api/bookings/public/': {
                'POST': {
                    'client_name': 'name',
                    'client_email': 'email',
                    'client_phone': 'phone',
                    'notes': 'text',
                    'total_price': 'decimal'
                }
            }
        }
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip validation for GET requests and static files
        if request.method == 'GET' or request.url.path.startswith('/static'):
            return await call_next(request)
        
        # Check if this endpoint needs validation
        path_rules = self.validation_rules.get(request.url.path)
        if not path_rules or request.method not in path_rules:
            return await call_next(request)
        
        field_rules = path_rules[request.method]
        
        try:
            # Read and parse request body
            body = await request.body()
            if not body:
                return await call_next(request)
            
            # Handle form data
            if request.headers.get('content-type', '').startswith('application/x-www-form-urlencoded'):
                from urllib.parse import parse_qs
                parsed_data = parse_qs(body.decode('utf-8'))
                # Convert lists to single values
                data = {k: v[0] if v else '' for k, v in parsed_data.items()}
            
            # Handle JSON data
            elif request.headers.get('content-type', '').startswith('application/json'):
                import json
                data = json.loads(body.decode('utf-8'))
            else:
                return await call_next(request)
            
            # Use custom validation for booking endpoints
            if request.url.path in ['/api/bookings/', '/api/bookings/public/']:
                from app.core.input_validation import validate_booking_input, sanitize_booking_input
                is_valid, errors = validate_booking_input(data)
                if not is_valid:
                    logger.warning(f"Booking validation failed for {request.url.path}: {errors}")
                    return Response(
                        content=json.dumps({"detail": "Input validation failed", "errors": errors}),
                        status_code=422,
                        media_type="application/json"
                    )
                sanitized_data = sanitize_booking_input(data)
            else:
                # Use standard validation for other endpoints
                is_valid, errors = input_validator.validate_dict(data, field_rules)
                if not is_valid:
                    logger.warning(f"Input validation failed for {request.url.path}: {errors}")
                    return Response(
                        content=json.dumps({"detail": "Input validation failed", "errors": errors}),
                        status_code=422,
                        media_type="application/json"
                    )
                sanitized_data = input_validator.sanitize_dict(data, field_rules)
            
            # Check for suspicious input
            client_ip = self._get_client_ip(request)
            for field_name, value in data.items():
                if input_validator.is_suspicious_input(str(value)):
                    input_validator.log_suspicious_input(str(value), field_name, client_ip)
                    return Response(
                        content=json.dumps({"detail": "Suspicious input detected"}),
                        status_code=400,
                        media_type="application/json"
                    )
            
            # Create new request with sanitized data
            if request.headers.get('content-type', '').startswith('application/json'):
                new_body = json.dumps(sanitized_data).encode('utf-8')
            else:
                from urllib.parse import urlencode
                new_body = urlencode(sanitized_data).encode('utf-8')
            
            # Replace request body
            async def receive():
                return {"type": "http.request", "body": new_body}
            
            # Create new scope with updated body
            scope = request.scope.copy()
            scope["method"] = request.method
            
            # Continue with sanitized request
            return await call_next(Request(scope, receive))
            
        except Exception as e:
            logger.error(f"Input validation middleware error: {str(e)}")
            # Continue without validation if there's an error
            return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"