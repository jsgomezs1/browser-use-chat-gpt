"""FastAPI routes for ChatGPT Browser Agent API."""

from fastapi import FastAPI, HTTPException, status
from config import ChatGPTConfig
from models import ChatGPTResponse, PromptRequest
from services import AgentSetup, AgentExecution


app = FastAPI(
    title="ChatGPT Browser Agent API",
    description="API for executing prompts through ChatGPT with web search and citation extraction",
    version="1.0.0"
)


@app.post(
    "/execute",
    response_model=ChatGPTResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute a prompt through ChatGPT",
    response_description="The ChatGPT response with sources"
)
async def execute_prompt(request: PromptRequest) -> ChatGPTResponse:
    """
    Execute a prompt through ChatGPT with web search enabled.

    This endpoint:
    - Navigates to ChatGPT
    - Enables web search
    - Submits the provided prompt
    - Waits for the response
    - Extracts citations and sources

    Args:
        request: JSON payload containing the prompt field

    Returns:
        ChatGPTResponse: Structured response with the ChatGPT output and sources

    Raises:
        HTTPException: If execution fails or returns no result
    """
    try:
        # Initialize dependencies
        config = ChatGPTConfig()
        setup = AgentSetup(config)
        execution = AgentExecution(setup)

        # Execute the prompt
        result = await execution.execute(request.prompt)

        # Validate result
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Agent execution failed to produce a structured output. Please try again."
            )

        return result

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the error and return a generic error response
        error_message = str(e)
        print(f"Error executing prompt: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during execution: {error_message}"
        )


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ChatGPT Browser Agent API"}
