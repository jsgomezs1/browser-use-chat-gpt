"""Agent setup and configuration service."""

from browser_use import Agent, ChatAnthropic, Browser
from config import ChatGPTConfig, LLM_MODEL, LLM_TEMPERATURE, HEADLESS_MODE, MAX_FAILURES, MAX_STEPS
from models import ChatGPTResponse
from tools import tools


class AgentSetup:
    """Handles agent configuration and setup following SRP."""

    def __init__(self, config: ChatGPTConfig) -> None:
        """Initialize with configuration."""
        self.config = config

    def create_llm(self) -> ChatAnthropic:
        """Initialize LLM with optimal settings for ChatGPT interaction.

        Returns:
            ChatAnthropic: Configured language model instance
        """
        return ChatAnthropic(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
        )

    def create_browser(self) -> Browser:
        """Configure browser with extended timeout for ChatGPT responses.

        Returns:
            Browser: Configured browser instance
        """
        return Browser(
            allowed_domains=self.config.allowed_domains,
            headless=HEADLESS_MODE
        )

    def create_task(self, prompt: str) -> str:
        """Construct the complete task with strict ChatGPT-only instructions.

        Args:
            prompt: The prompt to submit to ChatGPT (sources retrieval instruction will be automatically appended)

        Returns:
            str: Formatted task string with instructions
        """
        # Always append instruction to retrieve sources
        full_prompt = f"{prompt.strip()}. Retrieve sources"

        return f"""
Submit this prompt to ChatGPT: "{full_prompt}"

IMPORTANT: The prompt above ALREADY includes the instruction to retrieve sources. Submit it exactly as shown without adding or modifying anything.
"""

    def create_agent(self, task: str, llm: ChatAnthropic, browser: Browser) -> Agent:
        """Create agent with ChatGPT-specific configuration.

        Args:
            task: The task description for the agent
            llm: Configured language model
            browser: Configured browser instance

        Returns:
            Agent: Configured agent instance
        """
        return Agent(
            task=task,
            llm=llm,
            browser=browser,
            tools=tools,
            extend_system_message=self.config.system_prompt,
            output_model_schema=ChatGPTResponse,
            max_failures=MAX_FAILURES,
            max_steps=MAX_STEPS
        )
