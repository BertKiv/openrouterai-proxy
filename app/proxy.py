# app/proxy.py

import json
import os
import signal
import sys
import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("OPENROUTER_API_BASE_URL")
REFERER = os.getenv("REFERER")
TITLE = os.getenv("TITLE")

# The models used for processing the requests which are changed when 429 error is received
# You can add more models here or change the models in the MODELS variable
MODELS = [
    "google/gemma-7b-it:free",
    "mistralai/mistral-7b-instruct:free",
    "openchat/openchat-7b:free",
]

# The fake model used by the client for processing the responses
FAKE_MODEL = "fake_repo/fake_model"
# Index of the currently used model
current_model_index = 0


class ProxyHandler(BaseHTTPRequestHandler):
    """
    Handles the incoming HTTP requests and forwards them to the specified API_URL.
    Attributes:
        API_URL: The base URL of the API to which the requests are forwarded.
        REFERER: The HTTP Referer header for outgoing requests.
        TITLE: The X-Title header for outgoing requests.
        MODELS: The models used for processing the requests which are changed when 429 error is received.
        FAKE_MODELS: The fake model used for processing the responses.
    Methods:
        create_headers: Creates the headers for the outgoing requests.
        forward_response: Forwards the response from the API to the client.
        do_POST: Handles the incoming POST requests.
    """

    def handle_error_response(self, response):
        global current_model_index

        if response.status == 400:
            self.send_error_headers(400)
            return {"message": "Bad Request (invalid or missing params, CORS)"}
        elif response.status == 401:
            self.send_error_headers(401)
            return {"message": "Invalid credentials (OAuth session expired, disabled/invalid API key)"}
        elif response.status == 402:
            self.send_error_headers(402)
            return {"message": "Your account or API key has insufficient credits. Add more credits and retry the request."}
        elif response.status == 403:
            self.send_error_headers(403)
            return {"message": "Your chosen model requires moderation and your input was flagged"}
        elif response.status == 408:
            self.send_error_headers(408)
            return {"message": "Your request timed out"}
        elif response.status == 429:
            current_model_index = (current_model_index + 1) % len(MODELS)  # Switch to the next model
            return {"message": "You are being rate limited"}
        elif response.status == 502:
            self.send_error_headers(502)
            return {"message": "Your chosen model is down or we received an invalid response from it"}
        elif response.status == 503:
            self.send_error_headers(503)
            return {"message": "There is no available model provider that meets your routing requirements"}
        else:
            self.send_error_headers(500)
            return {"message": "Unhandled error"}
        
    def send_error_headers(self, status_code):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def create_headers(self, additional_headers=[]):
        """
        Create headers with additional headers if provided and return the resulting headers dictionary.
        Args:
            additional_headers (list, optional): Additional headers to be added to the headers dictionary. Defaults to an empty list.
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

    def forward_response(self, response):
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

    def do_POST(self):
        """
        A method to handle POST requests. It reads the request data, processes it, sends a POST request to the specified API URL with the modified data, and handles the response.
        """
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


def exit_handler(signal, frame):
    """
    Handle the exit signal by printing a farewell message and exiting the program.
    :param signal: The signal number or name
    :param frame: The current stack frame at the point where the signal was raised
    :return: None
    """
    print(f'\033[92m\n\n==> Bye!\033[0m\n\n')
    sys.exit(0)

def run(
    server_class=HTTPServer,
    handler_class=ProxyHandler,
    port=int(os.getenv("PORT", 8000)),
):
    """
    This function starts a server with the given server class, handler class, and port.
    It then prints the address the server is running on, before serving forever.
    """
    signal.signal(signal.SIGINT, exit_handler)

    server_address = ("localhost", port)
    httpd = server_class(server_address, handler_class)
    print(f"\033[92m\n\n==> Starting PROXY SERVER on {server_address[0]} : {server_address[1]}.\n    Happy coding!\033[0m\n\n" )
    httpd.serve_forever()


if __name__ == "__main__":
    run()
