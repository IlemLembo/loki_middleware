import json
import os
import time
from uuid import uuid4

from geocoder import ip

from ..utils.loggers import ConsoleLogger, LokiLogger
from ..utils.notifications import notify_on_telegram


class DjangoLokiMiddleware:
    """
    Simple Django middleware for structured logging to Loki.
    Captures request/response and sends to Loki.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = LokiLogger("DjangoLokiMiddleware")
        self.console_logger = ConsoleLogger("DjangoConsoleLogger")

        # Define a message template for structured logging
        self.message_template = {
            "level": "INFO",
            "severity": "info",
            "request_id": None,
            "request_origin": None,
            "request_user_agent": None,
            "request_referer": None,
            "request_method": None,
            "request_path": None,
            "request_complete_path": None,
            "request_query_string": None,
            "request_ip": None,
            "request_location": None,
            "request_host": None,
            "request_content_type": None,
            "request_body": None,
            "x_frontend_real_ip": None,
            "response_status": None,
            "response_status_code": None,
            "response_time": None,
            "response_type": None,
            "response_content_type": None,
            "response_content_length": None,
            "response_body": None,
            "exception": None,
        }

        # Paths to exclude from logging (e.g., health checks, static files)
        ## To control later with settings or environment variables
        self.excluded_paths = os.getenv("LOKI_EXCLUDED_PATHS", "/health,/static").split(
            ","
        )

    def __call__(self, request):
        if self._should_not_log(request.path):
            try:
                return self.get_response(request)
            except Exception as e:
                if os.getenv("ENABLE_TELEGRAM_NOTIFICATION", "false").lower() == "true":
                    environment = os.getenv("LOKI_ENVIRONMENT", "unknown")
                    message = f'<b>ENVIRONNEMENT :</b> <pre language="text">{environment}</pre><b>MODULE:</b> <pre language="text">{request.method} {request.path_info}</pre><b>FONCTIONNALITE :</b> <pre language="text">{request.method} {request.path_info}</pre><b>DETAILS :</b> Internal server error : <pre language="error">{e!s}</pre>'
                    notify_on_telegram(
                        message=message,
                        bot_token=str(os.getenv("TELEGRAM_BOT_TOKEN")),
                        chat_id=str(os.getenv("TELEGRAM_CHAT_ID")),
                    )
                raise

        # Process the request here (e.g., log it to Loki)
        start_time = time.time()
        request_id = self._generate_request_id()

        response = self.get_response(request)
        request_data = self._extract_request(request)
        execution_time = time.time() - start_time

        # I now extract the response and build the log entry
        response_data = self._extract_response(response)
        log_entry = self._build_log_entry(
            request_data, response_data, execution_time, request_id=request_id
        )

        if (
            os.getenv("ENABLE_TELEGRAM_NOTIFICATION", "false").lower() == "true"
            and response_data.get("response_status_code", 0) >= 500
        ):
            environment = os.getenv("LOKI_ENVIRONMENT", "unknown")
            message = f'<b>ENVIRONNEMENT :</b> <pre language="text">{environment}</pre><b>MODULE:</b> <pre language="text">{request_data.get("request_method")} {request_data.get("request_complete_path")}</pre><b>FONCTIONNALITE :</b> <pre language="text">{request_data.get("request_method")} {request_data.get("request_complete_path")}</pre><b>DETAILS :</b> Internal server error : <pre language="error">{response_data.get("exception")}</pre>'
            notify_on_telegram(
                message=message,
                bot_token=str(os.getenv("TELEGRAM_BOT_TOKEN")),
                chat_id=str(os.getenv("TELEGRAM_CHAT_ID")),
            )
        self.logger.info(log_entry)
        return response

    def _extract_request(self, request):
        """Extract relevant request data"""
        request_data = {
            "request_origin": request.META.get("HTTP_ORIGIN", "unknown"),
            "request_referer": request.META.get("HTTP_REFERER", "unknown"),
            "request_location": self._get_location(self._get_client_ip(request))[0],
            "request_host": request.get_host(),
            "request_content_type": request.content_type,
            "request_method": request.method,
            "request_path": request.path_info,
            "request_complete_path": request.path
            + ("?" + request.GET.urlencode() if request.GET else ""),
            "request_query_string": request.GET.urlencode() if request.GET else None,
            "request_ip": self._get_client_ip(request),
            "request_user_agent": request.META.get("HTTP_USER_AGENT", "unknown"),
            "request_body": self._parse_request_body(request),
        }
        # self.console_logger.info(f"Extracted request data: {request_data}")
        return request_data

    def _extract_response(self, response):
        """Extract relevant response data safely without repeating dictionary structures."""
        content_type = response.get("Content-Type", "")

        content_length = 0
        if hasattr(response, "content") and response.content:
            content_length = len(response.content)

        response_data = {
            "response_status_code": response.status_code,
            "response_status": self._get_severity(response.status_code),
            "response_type": self._get_response_type(content_type),
            "response_content_type": content_type,
            "response_content_length": content_length,
            "response_body": self._parse_response_body(response),
        }

        if hasattr(response, "exception"):
            response_data["exception"] = str(response.exception)

        return response_data

    def _parse_request_body(self, request):
        if request.content_type == "application/json" and request.body:
            return json.loads(request.body.decode())
        elif request.content_type == "text/plain" or request.content_type.startswith(
            "application/x-www-form-urlencoded"
        ):
            return request.body.decode()
        elif request.content_type.startswith("multipart/form-data"):
            return {k: v for k, v in request.body.decode().split("&")}
        return None

    def _parse_response_body(self, response):
        """Parse the response body based on content type, with error handling"""
        content_type = response.get("Content-Type", "")
        # uf
        if content_type.startswith("application/json"):
            return json.loads(response.content.decode("utf-8"))
        elif content_type.startswith(("text/plain", "text/html")):
            return f"<Text content of length {len(response.content)}>"
        elif content_type.startswith("application/x-www-form-urlencoded"):
            return response.content.decode("utf-8")
        elif content_type.startswith("multipart/form-data"):
            return {k: v for k, v in response.content.decode("utf-8").split("&")}
        elif "application/octet-stream" in content_type:
            return f"<Binary data of length {len(response.content)}>"
        else:
            return str(response.content)  # Fallback to string representation

    def _should_not_log(self, path):
        # Simple check to exclude certain paths from logging
        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                return True
        return False

    def _generate_request_id(self):
        return str(uuid4())

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    # @lru_cache(maxsize=1000)
    def _get_location(self, ip_address):
        """Get location information for a given IP address using geocoder. if env variable LOKI_ENABLE_GEOLOCATION is set to true and API_KEY is provided, otherwise return None."""
        if os.getenv("LOKI_ENABLE_GEOLOCATION", "false").lower() != "true":
            return None, None
        try:
            g = ip(ip_address)
            if g.ok:
                return f"{g.city}, {g.state}, {g.country}", [g.lat, g.lng]
        except ValueError as e:
            self.console_logger.error(
                f"Error getting location for IP {ip_address}: {e!s}"
            )
        return None, None

    def _get_severity(self, status_code):
        if 200 <= status_code < 300:
            return "success"
        elif 400 <= status_code < 500:
            return "warning"
        elif status_code >= 500:
            return "error"
        return "info"

    def _get_log_level(self, severity):
        if severity == "success":
            return "SUCCESS"
        elif severity == "error":
            return "ERROR"
        elif severity == "warning":
            return "WARNING"
        return "INFO"

    def _get_response_type(self, content_type):
        # Essentially categorizes response types for better log analysis in Loki
        if content_type.startswith("application/json"):
            return "json"
        elif content_type.startswith("text/html"):
            return "html"
        elif content_type.startswith("text/plain"):
            return "text"
        return "other"

    def _build_log_entry(
        self, request_data, response_data, execution_time=None, request_id=None
    ):
        log_entry = {
            **self.message_template,
            **request_data,
            **response_data,
            "level": self._get_log_level(response_data.get("response_status", "info")),
            "severity": self._get_severity(
                response_data.get("response_status_code", 0)
            ),
            "response_time": f"{execution_time:0.4f}s",
        }
        log_entry["request_id"] = request_id
        return log_entry
