import time
from typing import Dict, Any
class Errors:
    def __init__(self, response) -> None:
        self.error_messages = {
            400: "Bad Request (invalid or missing params, CORS)",
            401: "Invalid credentials (OAuth session expired, disabled/invalid API key)",
            402: "Your account or API key has insufficient credits. Add more credits and retry the request.",
            403: "Your chosen model requires moderation and your input was flagged",
            404: "Your chosen model is not available or BASE URL is invalid",
            408: "Your request timed out",
            429: "You are being rate limited",
            500: "Internal Server Error",
            501: "Your chosen model is not ready yet",
            502: "Your chosen model is down or we received an invalid response from it",
            503: "There is no available model provider that meets your routing requirements"
        }
        self.message: str = ''
        self.response = response
        self.status_code = response.status

    def send_error_headers(self) -> None:
        """Handle different error responses from the API."""
        self.send_response(self.status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def handle_rate_limiting(self, sleep: int = 10) -> None:
        """
        A function to handle rate limiting with a specified time parameter.
        Args:
            sleep (int): The time to sleep, in seconds.
        Returns:
            None
        """
        time.sleep(sleep)

    def handle_error_response(self) -> Dict[str, str]:
        """Handle different error responses from the API."""
        if self.status_code in self.error_messages:
            self.send_error_headers(self.status_code)
            self.message = {"message": self.error_messages[self.status_code]}
            if self.status_code == 429:
                self.handle_rate_limiting()
        elif self.status_code >= 500:
            self.send_error_headers(502)
            self.message = {"message": "Internal Server Error"}
        elif self.status_code != 200:
            self.send_error_headers(400)
            self.message = {"message": "Unknown error"}
        return self.message
