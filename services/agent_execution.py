"""Agent execution service."""

from typing import Optional
from models import ChatGPTResponse
from services.agent_setup import AgentSetup


class AgentExecution:
    """Handles agent execution and result processing following SRP."""

    def __init__(self, setup: AgentSetup) -> None:
        """Initialize with agent setup dependency."""
        self.setup = setup

    async def execute(self, prompt: str) -> Optional[ChatGPTResponse]:
        """Execute the agent and return structured output.

        Args:
            prompt: The prompt to process through ChatGPT

        Returns:
            Optional[ChatGPTResponse]: Structured response or None if failed
        """
        llm = self.setup.create_llm()
        browser = self.setup.create_browser()
        task = self.setup.create_task(prompt)
        agent = self.setup.create_agent(task, llm, browser)

        history = await agent.run()
        return history.structured_output if history.structured_output else None
