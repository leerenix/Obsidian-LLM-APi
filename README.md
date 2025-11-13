# Obsidian LLM Assistant

This project provides a web-based chat interface to an LLM agent that can interact with an Obsidian vault via a pre-existing API helper.

## Features

-   **Chat Interface**: A simple and clean UI for conversing with the LLM agent.
-   **Conversation Management**: Create multiple, persistent conversations.
-   **Note Viewer**: Automatically displays the content of notes that the agent interacts with.
-   **LangChain Agent**: Uses a powerful LangChain agent to perform complex, multi-step tasks on your Obsidian vault.

## Project Structure

```
.
├── .env.example      # Template for environment variables
├── pyproject.toml    # Project definition and dependencies for PDM
├── static/           # All frontend files (HTML, CSS, JS)
│   ├── index.html
│   ├── main.js
│   └── style.css
└── src/              # Python source code
    ├── __init__.py
    ├── agent.py      # Core LangChain agent logic
    ├── config.py     # Environment variable loading
    ├── database.py   # SQLAlchemy database setup and models
    ├── main.py       # FastAPI application, API endpoints, and WebSocket
    └── tools.py      # Tools for the LangChain agent to call the Obsidian API
```

## Setup and Installation

This project uses [PDM](https://pdm.fming.dev/) for dependency management.

### 1. Set Up Environment Variables

You must provide your LLM API key for the application to work.

1.  **Copy the example file:**
    ```bash
    cp .env.example .env
    ```
2.  **Edit the new `.env` file:**
    Open the `.env` file in a text editor and replace `YOUR_LLM_API_KEY_HERE` with your actual secret key for the LLM.

### 2. Install Dependencies

Install all required Python packages using PDM. This will also create a `.venv` virtual environment for the project.

```bash
pdm install
```

## How to Run the Application

Once the setup is complete, you can launch the web server using the `start` script defined in `pyproject.toml`.

Run the following command from the root of the project directory:

```bash
pdm run start
```

The server will start, and you will see output in your console indicating that it is running (by default on `http://0.0.0.0:8000`).

## Accessing the Web UI

Open your web browser and navigate to:

[http://localhost:8000](http://localhost:8000)

You should now see the chat application interface and can begin interacting with your Obsidian assistant.
