from browser_use import Agent, ChatAnthropic, Browser, Tools
from browser_use.controller import Controller
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import asyncio
import json
from typing import List, Optional

load_dotenv()

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================
CHATGPT_URL = "https://chatgpt.com"
ALLOWED_DOMAINS = ["chatgpt.com"]
LLM_MODEL = "claude-sonnet-4-0"
LLM_TEMPERATURE = 0.0
MAX_FAILURES = 3
MAX_STEPS = 25
HEADLESS_MODE = False  # Set to True for production

# Input query to process
DEFAULT_PROMPT = """
necesito validar la informacion del pasado judicial de mis conductores
"""

# ============================================================================
# TOOLS SETUP
# ============================================================================
tools = Tools()

@tools.action('Navigate to a specific URL')
async def navigate_to_url(url: str, new_tab: bool = False, controller: Optional[Controller] = None) -> str:
    """
    Navigate to a specific URL in the browser.
    
    Args:
        url: The URL to navigate to (must include protocol, e.g., https://)
        new_tab: Whether to open the URL in a new tab (default: False)
        controller: Browser controller instance (automatically injected)
    
    Returns:
        Success or error message
    """
    try:
        from browser_use.browser import BrowserSession
        
        # Get the browser session from the controller
        if not controller or not controller.browser_session:
            return "Error: Browser session not available"
        
        browser_session: BrowserSession = controller.browser_session
        
        # Dispatch navigation event
        from browser_use.browser.events import NavigateToUrlEvent
        event = browser_session.event_bus.dispatch(
            NavigateToUrlEvent(url=url, new_tab=new_tab)
        )
        await event
        await event.event_result(raise_if_any=True, raise_if_none=False)
        
        if new_tab:
            msg = f'🔗 Opened new tab with URL {url}'
        else:
            msg = f'🔗 Navigated to {url}'
        
        return msg
        
    except RuntimeError as e:
        if 'CDP client not initialized' in str(e):
            return f'Browser connection error: {str(e)}'
        return f'Navigation failed: {str(e)}'
    except Exception as e:
        error_msg = str(e)
        # Check for network-related errors
        if any(err in error_msg for err in [
            'ERR_NAME_NOT_RESOLVED',
            'ERR_INTERNET_DISCONNECTED', 
            'ERR_CONNECTION_REFUSED',
            'ERR_TIMED_OUT',
            'net::'
        ]):
            return f'Navigation failed - site unavailable: {url}'
        return f'Navigation failed: {error_msg}'


@tools.action('Enable ChatGPT web search feature before sending query')
async def enable_chatgpt_search(controller: Optional[Controller] = None) -> str:
    """
    Automatically enables ChatGPT's web search by clicking the Search button.
    Checks current state and only clicks if search is disabled.
    
    Args:
        controller: Browser controller instance (automatically injected)
    
    Returns:
        Status message indicating action taken or any errors
    """
    try:
        from browser_use.browser import BrowserSession
        
        # Get the browser session from the controller
        if not controller or not controller.browser_session:
            return "Error: Browser session not available"
        
        browser_session: BrowserSession = controller.browser_session
        page = await browser_session.must_get_current_page()
        
        # Locate the Search button using data-testid attribute
        search_button_selector = '[data-testid="composer-button-search"]'
        
        try:
            # Wait for button to be available (max 5 seconds)
            await page.wait_for_selector(search_button_selector, timeout=5000)
        except Exception:
            return "⚠️ Search button not found - may not be available on this page"
        
        # Get the button element
        search_button = await page.query_selector(search_button_selector)
        
        if not search_button:
            return "⚠️ Search button not found - may not be available on this page"
        
        # Check current state of the button
        aria_pressed = await search_button.get_attribute('aria-pressed')
        
        if aria_pressed == 'true':
            return "✅ Search is already enabled"
        
        # Click the button to enable search
        await search_button.click()
        
        # Wait for the button state to update (max 5 seconds)
        try:
            await page.wait_for_function(
                f'document.querySelector("{search_button_selector}").getAttribute("aria-pressed") === "true"',
                timeout=5000
            )
            return "✅ Search feature enabled successfully"
        except Exception:
            return "⚠️ Search button clicked but state change timeout - search may still be enabled"
        
    except RuntimeError as e:
        if 'CDP client not initialized' in str(e):
            return f'❌ Browser connection error: {str(e)}'
        return f'❌ Failed to enable search: {str(e)}'
    except Exception as e:
        return f'❌ Failed to enable search: {str(e)}'


@tools.action('Submit the prompt by clicking the send button')
async def submit_chatgpt_prompt(controller: Optional[Controller] = None) -> str:
    """
    Automatically submits the ChatGPT prompt by clicking the submit/send button.
    This should be called immediately after the prompt is written in the text input.
    
    Args:
        controller: Browser controller instance (automatically injected)
    
    Returns:
        Status message indicating action taken or any errors
    """
    try:
        from browser_use.browser import BrowserSession
        
        # Get the browser session from the controller
        if not controller or not controller.browser_session:
            return "Error: Browser session not available"
        
        browser_session: BrowserSession = controller.browser_session
        page = await browser_session.must_get_current_page()
        
        # Locate the submit button using data-testid attribute
        submit_button_selector = '[data-testid="send-button"]'
        
        try:
            # Wait for button to be available (max 5 seconds)
            await page.wait_for_selector(submit_button_selector, timeout=5000)
        except Exception:
            return "⚠️ Submit button not found - may not be available on this page"
        
        # Get the button element
        submit_button = await page.query_selector(submit_button_selector)
        
        if not submit_button:
            return "⚠️ Submit button not found - may not be available on this page"
        
        # Check if button is disabled
        is_disabled = await submit_button.get_attribute('disabled')
        if is_disabled is not None:
            return "⚠️ Submit button is disabled - prompt may be empty or invalid"
        
        # Click the button to submit the prompt
        await submit_button.click()
        
        # Wait a moment for the submission to register
        try:
            # After clicking, the button typically becomes disabled or disappears
            await page.wait_for_timeout(1000)
            return "✅ Prompt submitted successfully"
        except Exception:
            return "✅ Submit button clicked (confirmation timeout but likely submitted)"
        
    except RuntimeError as e:
        if 'CDP client not initialized' in str(e):
            return f'❌ Browser connection error: {str(e)}'
        return f'❌ Failed to submit prompt: {str(e)}'
    except Exception as e:
        return f'❌ Failed to submit prompt: {str(e)}'


# Input query to process
prompt = """
necesito validar la informacion del pasado judicial de mis conductores
"""

# ============================================================================
# DATA MODELS
# ============================================================================
class Source(BaseModel):
    """Model for a source citation."""
    url: str = Field(description="The URL of the source")
    order: int = Field(description="The order of appearance of the source")

class ChatGPTResponse(BaseModel):
    """Structured output model for ChatGPT responses."""
    response: str = Field(description="The complete ChatGPT response text, preserving all formatting, markdown, line breaks, etc.")
    sources: List[Source] = Field(description="An ordered list of the sources cited in the answer, preserving their order of appearance. Empty array if no sources provided.")

# ============================================================================
# CONFIGURATION CLASSES
# ============================================================================
class ChatGPTConfig:
    """Configuration for ChatGPT interaction."""

    def __init__(self) -> None:
        self.url = CHATGPT_URL
        self.allowed_domains = ALLOWED_DOMAINS
        self.system_prompt = """
You operate exclusively on chatgpt.com. Use navigate_to_url tool to reach https://chatgpt.com.

Task sequence:
1. Navigate to chatgpt.com
2. Use enable_chatgpt_search tool to activate web search feature
3. Enter user prompt in textbox exactly as provided (without modification)
4. Use submit_chatgpt_prompt tool to submit the prompt immediately after writing it
5. Wait for complete response (60s timeout, retry up to 3 times if needed)
6. Scroll to response end
7. Click 'Sources' button in citations panel
8. Extract all source URLs in order with their position

Response handling:
- Preserve all formatting (markdown, line breaks, code blocks)
- Return complete text without modification
- Extract sources from citations panel only (not inline links)
- For each source, include the URL and its order of appearance (1-based index)
- Return empty sources array if no Sources button exists

On error: Retry failed operations up to 3 times total, then return error message.
"""


# ============================================================================
# BUSINESS LOGIC CLASSES
# ============================================================================
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
            temperature=LLM_TEMPERATURE
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
            prompt: The prompt to submit to ChatGPT

        Returns:
            str: Formatted task string with instructions
        """
        return f"""
Submit this prompt to ChatGPT: "{prompt}.retrive sources"

Steps:
1. Use navigate_to_url to go to https://chatgpt.com
2. Use enable_chatgpt_search tool to enable web search
3. Enter the prompt exactly as shown above (without modification)
4. Use submit_chatgpt_prompt tool to submit the prompt immediately after writing it
5. Wait for complete response
6. Scroll to end, click 'Sources' button
7. Extract all source URLs from citations panel in order

Output structured data:
- response: Complete ChatGPT output (preserve all formatting)
- sources: Array of objects with 'url' and 'order' fields (1-based index). Empty array if no sources.

Example sources format:
[
  {{"url": "https://example.com", "order": 1}},
  {{"url": "https://example2.com", "order": 2}}
]
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


class OutputHandler:
    """Handles output formatting and display following SRP."""

    @staticmethod
    def display_result(result: Optional[ChatGPTResponse]) -> None:
        """Display the execution result in a formatted manner.

        Args:
            result: The structured response to display, or None if no result
        """
        if not result:
            print("⚠️  No structured output available")
            return

        print("📊 STRUCTURED OUTPUT:")
        print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))

        print(f"\n{'='*80}")
        print("📋 RESULT SUMMARY:")
        print(f"{'='*80}")

        print(f"\n📝 CHATGPT RESPONSE:")
        print(f"{'-'*80}")
        print(result.response)
        print(f"{'-'*80}")

        if result.sources:
            print(f"\n🔗 SOURCES FOUND ({len(result.sources)}):")
            for source in result.sources:
                print(f"  {source.order}. {source.url}")
        else:
            print("\n🔗 SOURCES: None found in response")

        print(f"{'='*80}\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================
async def main() -> None:
    """Main execution function following KISS principles.

    Orchestrates the ChatGPT interaction workflow using dependency injection
    and separation of concerns for maintainability and testability.
    """
    # Initialize dependencies following DIP
    config = ChatGPTConfig()
    setup = AgentSetup(config)
    execution = AgentExecution(setup)
    handler = OutputHandler()

    # Execute workflow
    result = await execution.execute(DEFAULT_PROMPT)
    handler.display_result(result)


if __name__ == "__main__":
    asyncio.run(main())