# Openrouter.ai Proxy

## Description
This Python application acts as a proxy server for [openrouter.ai](https://openrouter.ai), facilitating the forwarding of incoming HTTP requests to a specified API URL and managing the responses. Notably, it incorporates a feature enabling the automatic switching to alternative models in response to a 429 error, effectively bypassing rate limits and enabling the utilization of free-of-charge models for programming and testing purposes without incurring any expenses.

## Installation
To install the application using Poetry, use the following steps:

1. Make sure Poetry is installed on your system. If not, you can install it using the instructions from [Poetry's official documentation](https://python-poetry.org/docs/).
2. Create a `.env` file in the root directory of the application. You can use the provided `env-example` file as a template.
3. Update the environment variables in the `.env` file with the necessary configuration for your environment, including the API_URL, REFERER, TITLE, and other relevant settings.
4. Navigate to the directory containing the `pyproject.toml` file.
5. Run the following command to install the application and its dependencies:

```bash
poetry install --no-root
```

## Usage
To run the proxy server, use the following command:
```bash
poetry run python app/proxy.py
```

## License
This application is distributed under the MIT license.