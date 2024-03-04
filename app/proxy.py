import requests
import os
from typing import Dict, Optional, List, Final
from errors import ErrorsHandler
from fastapi import Request
from fastapi.responses import JSONResponse


class ProxyHandler:
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


    def create_headers(self, request: Request, additional_headers: Optional[List[str]] = None) -> Dict[str, str]:
        if additional_headers is None:
            additional_headers = []
        headers = {
            "HTTP-Referer": self.REFERER,
            "X-Title": self.TITLE,
        }
        for header in additional_headers:
            if header in request.headers:
                headers[header] = request.headers[header]
        return headers

    async def do_POST(self, request: Request) -> JSONResponse:
        post_data = await request.json()
        model = post_data.get("model")
        if post_data["model"] == self.FAKE_MODEL:
            post_data["model"] = model if model != self.FAKE_MODEL else self.MODELS[0]
        print(f"\033[92m==> CURRENT MODEL: {post_data["model"]}\033[0m")
        headers = self.create_headers(request, ["Accept", "User-Agent", "Authorization", "Content-Type"])
        response = requests.post(f"{self.API_URL}{request.url.path}", json=post_data, headers=headers)
        handleErrors = ErrorsHandler(response).handle_error_response()

        # Check if we should wait because of rate limiting
        if response.status_code == 429:  # Status code 429 means rate limit exceeded
            error_message = handleErrors        
        elif response.status_code != 200:
            error_message = handleErrors
            print(f"\033[91m==> ERROR number: {response.status_code}: {error_message['message']}\033[0m" )
            return JSONResponse(content={"error": error_message['message']}, status_code=response.status_code)
        else:    
            response_data = response.json()
            return JSONResponse(content=response_data)
