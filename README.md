# Openrouter.ai Proxy

## Description

This Python FastAPI application acts as a proxy server for [openrouter.ai](https://openrouter.ai), facilitating the forwarding of incoming HTTP requests to a specified API URL and managing the responses. Notably, it incorporates a feature enabling the automatic waiting in response to a 429 error, effectively bypassing rate limits and enabling the utilization of free-of-charge models for programming and testing purposes without incurring any expenses.

## Installation

To install the application using Poetry, use the following steps:

1. Make sure Poetry is installed on your system. If not, you can install it using the instructions from [Poetry's official documentation](https://python-poetry.org/docs/).
2. Create a `.env` file in the root directory of the application. You can use the provided `env-example` file as a template.
3. Update the environment variables in the `.env` file with the necessary configuration for your environment, including the API_URL, REFERER, TITLE, and other relevant settings.
4. Navigate to the directory containing the `pyproject.toml` file.
5. Run the following command to install the application and its dependencies:

```bash
poetry install --no-root --only main
```

## Docker Integration

This application can also be run using Docker, which can simplify the setup process and ensure consistent execution across different environments. Here are the steps to run the application using Docker:

1. Make sure Docker is installed on your system.
If not, you can install it using the instructions from Docker's [official documentation](https://docs.docker.com/install/).

2. Run the Docker Compose Stack for the application by running the following command in the directory containing the docker-compose.yml file:

```bash
docker compose up -d --build
```

## Usage

To use the application, simply run docker compose and set BASE URL of free openrouter model in Base URL field or environment variable like that:

```bash
http(s)://[IP ADDRESS or domain.tld or localhost]:[PORT or 9999]
```

Here is an example for the AutoGen Studio model where proxy is running on OrbStack on localhost:

![autoGen](./example.png)

## TODO

- [ ]&nbsp;&nbsp; Authorization via Bearer Token

- [ ]&nbsp;&nbsp; Logging

- [ ]&nbsp;&nbsp; Statistics

- [ ]&nbsp;&nbsp; Multiuser

- [ ]&nbsp;&nbsp; UI


## License

This application is distributed under the MIT license.

The MIT License (MIT)
Copyright © 2024 <copyright Wojciech Kiwerski>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
