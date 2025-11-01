"""Custom browser tools for ChatGPT interaction."""

from browser_use import Tools
from browser_use.controller import Controller
from typing import Optional

# Initialize tools
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
