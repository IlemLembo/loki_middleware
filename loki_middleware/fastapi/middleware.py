from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import ClientDisconnect
from fastapi import FastAPI, Request, Response
from typing import Callable
from uuid import uuid4
import time
import os
import json
from geocoder import ip
from ..utils.loki_logger import LokiLogger

class LokiLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, 
        app: FastAPI, 
        *,
        exclude_paths: list = []
    ) -> None:
        # Defining the LokiLogger instance
        self.logger = LokiLogger("loki_middleware_logger")
        # Default paths to exclude from logging
        self.exclude_paths = exclude_paths or [
            "/health",
            "/docs",
            "/healthcheck",
            "/metrics",
        ]
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if the request path should be excluded from logging
        if self._should_exclude_logging(request):
            response = await call_next(request)
            return response

        request_id: str = str(uuid4())
        try:
            await self.set_body(request)
            response, response_dict = await self._log_response(call_next, request, request_id)
            request_dict = await self._log_request(request)

        except ClientDisconnect:
            error_log = {
                "level": "ERROR",
                "event": "logging_middleware_client_disconnect",
                "message": "A connection from a client got cut off.",
                "request_path": request.url.path,
                "request_method": request.method
            }
            self.logger.error(json.dumps(error_log, default=str))
            response = await call_next(request)
            return response
        except Exception as e:
            error_log = {
                "level": "ERROR",
                "event": "logging_middleware_error",
                "message": "An unexpected error occurred.",
                "exception": str(e),
                "request_path": request.url.path,
                "request_method": request.method
            }
            self.logger.error(json.dumps(error_log, default=str))
        """ # Get current trace context for correlation
        current_span = trace.get_current_span()
        trace_id = None
        span_id = None
        current_span = trace.get_current_span()
        trace_id = None
        span_id = None
        
        if current_span and current_span.is_recording():
            span_context = current_span.get_span_context()
            if span_context.trace_id != 0:  # Valid trace
                trace_id = format(span_context.trace_id, "032x")
                span_id = format(span_context.span_id, "016x") """
    
        # Determine log level based on status code
        status_code = response_dict.get("status_code", 200)
        log_level = self._get_log_level_from_status_code(status_code)

        # Create a flattened log structure with trace correlation
        logging_dict = {
            "level": log_level,
            "severity": self._get_log_severity(status_code),  # Additional field for filtering
            "request_id": request_id,
            'request_origin': request_dict.get("origin"),
            'request_user_agent': request_dict.get("user_agent"),
            'request_referer': request_dict.get("referer"),
            'x_frontend_real_ip': request_dict.get("x_frontend_real_ip"),
            "request_method": request_dict.get("method"),
            "request_path": request_dict.get("path"),
            "request_ip": request_dict.get("ip"),
            "request_location": request_dict.get("location"),
            "request_location_latlng": request_dict.get("location_latlng"),
            "request_host": os.getenv("REQUEST_HOST", "localhost"),
            "request_body": request_dict.get("body"),
            "response_status": response_dict.get("status"),
            "response_status_code": response_dict.get("status_code"),
            "response_time": response_dict.get("time_taken"),
            "response_type": response_dict.get("response_type"),  # Add this line
            "response_content_type": response_dict.get("content_type"),  # Add this line
            "response_content_length": response_dict.get("content_length"),  # Add this line
            "response_body": response_dict.get("body"),
        }

        # Log with structured fields including trace context
        log_message = json.dumps(logging_dict, default=str)
        # Use appropriate logging method based on status code
        if status_code >= 500:
            self.logger.error(log_message)
        elif status_code >= 400:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

        return response

    def _get_log_level_from_status_code(self, status_code: int) -> str:
        """Map HTTP status codes to log levels for better visualization"""
        if status_code >= 500:
            return "ERROR"      # Red in Grafana
        elif status_code >= 400:
            return "WARNING"    # Yellow/Orange in Grafana
        elif status_code >= 300:
            return "INFO"       # Blue in Grafana
        elif status_code >= 200:
            return "SUCCESS"    # Green (custom level)
        else:
            return "DEBUG"      # Gray in Grafana

    def _get_log_severity(self, status_code: int) -> str:
        """Get severity for better filtering"""
        if status_code >= 500:
            return "critical"
        elif status_code >= 400:
            return "error"
        elif status_code >= 300:
            return "warning"
        else:
            return "success"

    def _should_exclude_logging(self, request: Request) -> bool:
        """Check if the request path should be excluded from logging"""
        path = request.url.path.rstrip('/')  # Remove trailing slash for comparison
        
        for exclude_path in self.exclude_paths:
            exclude_path = exclude_path.rstrip('/')  # Remove trailing slash for comparison
            if path == exclude_path or path.startswith(f"{exclude_path}/"):
                return True
        
        return False

    async def set_body(self, request: Request):
        """Stores the request body for later logging while preserving it for the actual endpoint.
        
        Arguments:
        - request: Request
        """
        try:
            # Read the body once and store it
            body = await request.body()
            
            # Store the body in request state for later use
            request.state.body = body
            
            # Create a new receive function that returns the stored body
            async def receive():
                return {
                    "type": "http.request", 
                    "body": body,
                    "more_body": False
                }
            
            # Replace the request's receive function
            request._receive = receive
        except ClientDisconnect:
            # In case of any error, log it and proceed without body logging
            self.logger.error(f"Error reading request body, Probably from the client side")
            request.state.body = b""

    async def _log_request(self, request: Request) -> dict:
        """Logs request part

        Arguments:
            - request: Request

        Returns:
            dict: Dictionary containing method, path, ip, and body of the request, origin, user-agent
        """
        path = request.url.path
        if request.query_params:
            path += f"?{request.query_params}"

        origin = request.headers.get("origin", "unknown")
        referer = request.headers.get("referer", "unknown")
        xFrontend_IP = request.headers.get("x-frontend-real-ip", "unknown") 

        user_agent = request.headers.get("user-agent", "unknown")

        location = ip(request.headers.get("x-real-ip", request.headers.get("x-forwarded-for", request.client.host)))
        request_logging = {
            "method": request.method,
            "path": path,
            "origin": origin,
            "referer": referer,
            "user_agent": user_agent,
            "x_frontend_real_ip": xFrontend_IP if origin != "unknown" else "same as request_ip",
            #"ip": request.client.host,
            "ip": request.headers.get("x-real-ip", request.headers.get("x-forwarded-for", request.client.host)),
            "location": f"{location.city}, {location.state}, {location.country}",
            "location_latlng": location.latlng,
        }

        # Get the stored body from request state
        if hasattr(request.state, 'body'):
            body_bytes = request.state.body
            
            if body_bytes:
                try:
                    # Try to parse as JSON
                    body_str = body_bytes.decode('utf-8')
                    if body_str.strip():
                        if request.headers.get('content-type', '').startswith('application/json'):
                            try:
                                request_logging["body"] = json.loads(body_str)
                            except json.JSONDecodeError as e:
                                request_logging["body"] = f"<invalid JSON: {str(e)}>"
                        elif request.headers.get('content-type', '').startswith('application/x-www-form-urlencoded'):
                            # Parse form data
                            from urllib.parse import parse_qs
                            parsed = parse_qs(body_str)
                            request_logging["body"] = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
                        else:
                            request_logging["body"] = body_str
                    else:
                        request_logging["body"] = None
                except (UnicodeDecodeError, json.JSONDecodeError) as e:
                    request_logging["body"] = f"<error parsing body: {str(e)}>"
            else:
                request_logging["body"] = None
        else:
            request_logging["body"] = None

        return request_logging

    async def _log_response(self, call_next: Callable, request: Request, request_id: str) -> tuple:
        """Logs response part with proper body extraction"""
        
        start_time = time.perf_counter()
        response = await self._execute_request(call_next, request, request_id)
        finish_time = time.perf_counter()

        overall_status = "successful" if response.status_code < 400 else "failed"
        execution_time = finish_time - start_time

        response_logging = {
            "status": overall_status,
            "status_code": response.status_code,
            "time_taken": f"{execution_time:0.4f}s",
            "response_type": type(response).__name__,  # Add response type
            "content_type": response.headers.get("content-type", "unknown"),
            "content_length": response.headers.get("content-length", "unknown")
        }

        # Enhanced response body extraction for different response types
        try:
            response_body = None
            
            # Handle StreamingResponse (most common in FastAPI)
            if hasattr(response, 'body_iterator'):
                # Consume the iterator and rebuild it
                body_parts = []
                async for chunk in response.body_iterator:
                    if isinstance(chunk, bytes):
                        body_parts.append(chunk)
                    else:
                        body_parts.append(str(chunk).encode())
                
                # Reconstruct the body
                full_body = b''.join(body_parts)
                
                # Create new iterator for the actual response
                async def new_body_iterator():
                    yield full_body
                
                response.body_iterator = new_body_iterator()
                
                # Parse the captured body
                if full_body:
                    try:
                        body_str = full_body.decode('utf-8')
                        if response.headers.get("content-type", "").startswith("application/json"):
                            response_body = json.loads(body_str)
                        else:
                            response_body = body_str[:1000] + "..." if len(body_str) > 1000 else body_str
                    except (UnicodeDecodeError, json.JSONDecodeError) as e:
                        response_body = f"<error parsing body: {str(e)}>"
        
            # Handle Response objects with direct body access
            elif hasattr(response, 'body') and response.body:
                body_content = response.body
                if isinstance(body_content, bytes):
                    body_str = body_content.decode('utf-8')
                else:
                    body_str = str(body_content)
                
                try:
                    response_body = json.loads(body_str)
                except json.JSONDecodeError:
                    response_body = body_str[:1000] + "..." if len(body_str) > 1000 else body_str
            
            # Handle PlainTextResponse and other text responses
            elif hasattr(response, 'content'):
                content = response.content
                if isinstance(content, bytes):
                    response_body = content.decode('utf-8')
                else:
                    response_body = str(content)
            
            # Fallback for other response types - provide metadata
            else:
                response_body = None
                
            response_logging["body"] = response_body
            
        except Exception as e:
            response_logging["body"] = f"<error extracting response body: {str(e)}>"

        return response, response_logging

    async def _execute_request(self, call_next: Callable, request: Request, request_id: str ) -> Response:
        """Executes the actual path function using call_next.
            It also injects "X-API-Request-ID" header to the response.

            Arguments:
            - call_next: Callable (To execute the actual path function
                        and get response back)
            - request: Request
            - request_id: str (uuid)
            Returns:
            - response: Response
        """
        try:
            response: Response = await call_next(request)

            # Kickback X-Request-ID
            response.headers["X-API-Request-ID"] = request_id
            return response

        except Exception as e:
            error_log = {
                "request_id": request_id,
                "error": "Internal server error",
                "exception": str(e),
                "request_path": request.url.path,
                "request_method": request.method,
                "response_status": "failed",
                "response_status_code": 500
            }
            
            error_message = json.dumps(error_log, default=str)
            self.logger.error(error_message)
            
            #######################
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "error": str(e)},
                headers={"X-API-Request-ID": request_id}
            )

class AsyncIteratorWrapper:
    """The following is a utility class that transforms a
        regular iterable to an asynchronous one.

        link: https://www.python.org/dev/peps/pep-0492/#example-2
    """

    def __init__(self, obj):
        self._it = iter(obj)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            value = next(self._it)
        except StopIteration:
            raise StopAsyncIteration
        return value


