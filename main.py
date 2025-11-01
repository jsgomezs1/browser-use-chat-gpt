"""
ChatGPT Browser Agent API - Main Entry Point

A FastAPI-based service that automates ChatGPT interactions with web search
and citation extraction capabilities.
"""

import sys
import uvicorn
from dotenv import load_dotenv
from api import app

# Load environment variables
load_dotenv()


def run_api(host: str = "0.0.0.0", port: int = 8000):
    """
    Run the FastAPI application server.

    Args:
        host: Host to bind to (default: 0.0.0.0)
        port: Port to bind to (default: 8000)
    """
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    # Get port from command line argument or use default
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

    print(f"🚀 Starting FastAPI server on http://0.0.0.0:{port}")
    print(f"📚 API docs available at http://localhost:{port}/docs")
    print(f"📍 POST endpoint: http://localhost:{port}/execute")
    print(f"💚 Health check: http://localhost:{port}/health")

    run_api(port=port)
