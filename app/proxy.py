# app/proxy.py
"""
This module provides functionality for handling proxy operations.
"""

import json
import os
import signal
import sys
import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, Optional, List, Any, Tuple, Final
from dotenv import load_dotenv

load_dotenv()

API_URL: Optional[str] = os.getenv("OPENROUTER_API_BASE_URL")
REFERER: Optional[str] = os.getenv("REFERER")
TITLE: Optional[str] = os.getenv("TITLE")

MODELS: Final[List[str]] = [
    "google/gemma-7b-it:free",
    "mistralai/mistral-7b-instruct:free",
    "openchat/openchat-7b:free",
]

FAKE_MODEL: Final[str] = "fake_repo/fake_model"
current_model_index: int = 0


class ProxyHandler(BaseHTTPRequestHandler):
    """
    Handles the incoming HTTP requests and forwards them to the specified API_URL.
    Attributes:
        API_URL: The base URL of the API to which the requests are forwarded.
        REFERER: The HTTP Referer header for outgoing requests.
        TITLE: The X-Title header for outgoing requests.
        MODELS: The models used for processing the requests 
        which are changed when 429 error is received.
        FAKE_MODELS: The fake model used for processing the responses.
    Methods:
        create_headers: Creates the headers for the outgoing requests.
        forward_response: Forwards the response from the API to the client.
        do_POST: Handles the incoming POST requests.
    """

    def handle_error_response(self, response : Any)-> Dict[str, str]:
        """Handle different error responses from the API."""

        global current_model_index

        if response.status == 400:
            self.send_error_headers(400)
            message =  {
                "message": "Bad Request (invalid or missing params, CORS)"
            }
        if response.status == 401:
            self.send_error_headers(401)
            message =  {
                "message": "Invalid credentials (OAuth session expired, disabled/invalid API key)"
            }
        if response.status == 402:
            self.send_error_headers(402)
            message =  {
                "message": "Your account or API key has insufficient credits. Add more credits and retry the request."
            }
        if response.status == 403:
            self.send_error_headers(403)
            message =  {
                "message": "Your chosen model requires moderation and your input was flagged"
            }
        if response.status == 408:
            self.send_error_headers(408)
            message =  {
                "message": "Your request timed out"
            }
        if response.status == 429:
            current_model_index = (current_model_index + 1) % len(MODELS)
            message =  {
                "message": "You are being rate limited"
            }
        if response.status == 502:
            self.send_error_headers(502)
            message =  {
                "message": "Your chosen model is down or we received an invalid response from it"
            }
        if response.status == 503:
            self.send_error_headers(503)
            message =  {
                "message": "There is no available model provider that meets your routing requirements"
            }
        return message

    def send_error_headers(self, status_code : int) -> None:
        """Handle different error responses from the API."""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def create_headers(self, additional_headers: List[str] = None) -> Dict[str, str]:
        """
        Create headers with additional headers
        if provided and return the resulting headers dictionary.
        Args:
            additional_headers (list, optional): Additional headers 
            to be added to the headers dictionary. Defaults to an empty list.
        Returns:
            dict: The resulting headers dictionary.
        """
        headers = {
            "HTTP-Referer": REFERER,
            "X-Title": TITLE,
        }
        for header in additional_headers:
            if header in self.headers:
                headers[header] = self.headers[header]
        return headers

    def forward_response(self, response : Any) -> None:
        """
        Send a custom JSON response with optional content length header.
        :param response: The response object to read and process.
        :type response: object
        :return: None
        """
        response_data = response.read().decode("utf-8")
        json_data = json.loads(response_data)
        json_data["model"] = FAKE_MODEL
        json_response = json.dumps(json_data)
        content_length = len(json_response.encode("utf-8"))

        self.send_response(response.status)
        if content_length:
            self.send_header("Content-Length", content_length)
        self.end_headers()

        self.wfile.write(json_response.encode("utf-8"))

    def do_POST(self) -> None:
        """Handle the incoming POST requests."""
        global current_model_index

        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        post_data = json.loads(post_data.decode("utf-8"))
        post_data["model"] = MODELS[current_model_index]
        print(f"\033[92m==> CURRENT MODEL: {post_data["model"]}\033[0m")
        post_data["temperature"] = 0
        post_data = json.dumps(post_data)
        headers = self.create_headers(["Accept", "User-Agent", "Authorization", "Content-Type"])

        try:
            connection = http.client.HTTPSConnection("openrouter.ai", "https")
            connection.request("POST", f"{API_URL}{self.path}", body=post_data, headers=headers)
            response = connection.getresponse()

            # Check if we should switch to another model
            if response.status == 429:  # Status code 429 means rate limit exceeded
                self.handle_error_response(response)

            if response.status != 200:
                error = self.handle_error_response(response)
                print(f"\033[91m==> ERROR number: {response.status}: {error["message"]}\033[0m" )
            else:
                self.forward_response(response)
        except Exception as e:
            print("\033[91m==> ERROR: \033[0m", e )
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"error": "Internal Server Error"}')


def exit_handler(signal: int, frame: Any) -> None:
    """
    Handle the exit signal by printing a farewell message and exiting the program.
    :param signal: The signal number or name
    :param frame: The current stack frame at the point where the signal was raised
    :return: None
    """
    print('\033[92m\n\n==> Bye!\033[0m\n\n')
    sys.exit(0)

def run(
    server_class: Any = HTTPServer,
    handler_class: Any = ProxyHandler,
    port: int = int(os.getenv("PORT")),
) -> None:
    """
    This function starts a server with the given server class, handler class, and port.
    It then prints the address the server is running on, before serving forever.
    """

    signal.signal(signal.SIGINT, exit_handler)

    server_address: Tuple[str, int] = ("localhost", port)
    httpd: Any = server_class(server_address, handler_class)
    server_info: str = f"\033[92m\n\n==> Starting PROXY SERVER on {server_address[0]}:{server_address[1]}.\n    Happy coding!\033[0m\n\n"
    print(server_info)
    httpd.serve_forever()


if __name__ == "__main__":
    run()
