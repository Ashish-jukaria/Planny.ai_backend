"""
Middleware to log `*/api/*` requests and responses.
"""
import socket
import time
import json
import logging
import uuid

request_logger = logging.getLogger("request_response")


class RequestLogMiddleware:
    """Request Logging Middleware."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        log_data = {
            "log_id": uuid.uuid4().hex,
            "remote_address": request.META["REMOTE_ADDR"],
            "server_hostname": socket.gethostname(),
            "request_method": request.method,
            "request_path": request.get_full_path(),
            "request_sender": request.user,
        }

        # Only logging "*/api/*" patterns
        if "/api/" in str(request.get_full_path()):
            req_body = json.loads(request.body.decode("utf-8")) if request.body else {}
            log_data["request_body"] = req_body

        response = self.get_response(request)

        if (
            response
            and "content-type" in response.headers
            and response.headers["content-type"] == "application/json"
        ):
            response_body = json.loads(response.content.decode("utf-8"))
            log_data["response_body"] = response_body
        log_data["run_time"] = time.time() - start_time

        request_logger.info(msg=log_data)

        return response

    # for logging unhandled exceptions
    def process_exception(self, request, exception):
        try:
            raise exception
        except Exception as e:
            request_logger.exception("Unhandled Exception: " + str(e))
        return exception
