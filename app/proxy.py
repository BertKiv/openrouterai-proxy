import requests
import json
import os
import signal
import sys
import time
import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, Optional, List, Any, Tuple, Final, Literal
from errors import Errors
from dotenv import load_dotenv

load_dotenv()



class ProxyHandler(BaseHTTPRequestHandler):
    """
    Handles the incoming HTTP requests and forwards them to the specified API_URL.
    """

    API_URL: Optional[str] = os.environ["OPENROUTER_API_BASE_URL"]
    REFERER: Optional[str] = os.environ["REFERER"]
    TITLE: Optional[str] = os.environ["TITLE"]

    MODELS: Final[List[str]] = [
        "google/gemma-7b-it:free",
        "mistralai/mistral-7b-instruct:free",
        "openchat/openchat-7b:free",
        "nousresearch/nous-capybara-7b:free",
        "gryphe/mythomist-7b:free",
        "huggingfaceh4/zephyr-7b-beta:free",
    ]

    FAKE_MODEL: Final[str] = "fake_repo/fake_model"


    def create_headers(self, additional_headers: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Create headers with additional headers
        if provided and return the resulting headers dictionary.
        Args:
            additional_headers (list, optional): Additional headers 
            to be added to the headers dictionary. Defaults to an empty list.
        Returns:
            dict: The resulting headers dictionary.
        """
        if additional_headers is None:
            additional_headers = []
        headers = {
            "HTTP-Referer": self.REFERER,
            "X-Title": self.TITLE,
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
        json_data["model"] = self.FAKE_MODEL
        json_response = json.dumps(json_data)
        content_length = len(json_response.encode("utf-8"))

        self.send_response(response.status)
        if content_length:
            self.send_header("Content-Length", content_length)
        self.end_headers()

        self.wfile.write(json_response.encode("utf-8"))

    def do_POST(self) -> None:
        """Handle the incoming POST requests."""

        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        post_data = json.loads(post_data.decode("utf-8"))
        post_data["model"] = self.MODELS[self.current_model_index]
        print(f"\033[92m==> CURRENT MODEL: {post_data['model']}\033[0m")
        post_data["temperature"] = 0
        post_data = json.dumps(post_data)
        headers = self.create_headers(["Accept", "User-Agent", "Authorization", "Content-Type"])

        response = requests.post(f"{self.API_URL}{self.path}", json=post_data, headers=headers)
        errors = Errors(response).handle_error_response()

        # Check if we should switch to another model
        if response.status_code == 429:  # Status code 429 means rate limit exceeded
            errors.handle_error_response()
        if response.status_code != 200:
            error_message = errors.handle_error_response()
            print(f"\033[91m==> ERROR number: {response.status_code}: {error_message['message']}\033[0m" )
            self.wfile.write(f'{{"error": "{error_message['message']}"}}'.encode())
        else:    
            self.forward_response(response)

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
    port: int = int(os.environ["PORT"]),
) -> None:
    """
    This function starts a server with the given server class, handler class, and port.
    It then prints the address the server is running on, before serving forever.
    """

    signal.signal(signal.SIGINT, exit_handler)

    server_address: Tuple[str, int] = ("0.0.0.0", port)
    httpd: Any = server_class(server_address, handler_class)
    server_info: str = f"\033[92m\n\n==> Starting PROXY SERVER on {server_address[0]}:{server_address[1]}.\n    Happy coding!\033[0m\n\n"
    print(server_info)
    httpd.serve_forever()


if __name__ == "__main__":
    run()
