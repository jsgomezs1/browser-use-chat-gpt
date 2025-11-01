from browser_use import Agent, ChatOpenAI, Browser
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import asyncio
import json

load_dotenv()

# Input query to process
prompt = """
I need a new ERP that use AI
"""

# ============================================================================
# STRUCTURED OUTPUT MODEL
# ============================================================================
class ChatGPTResponse(BaseModel):
    """Structured output model for ChatGPT responses."""
    prompt: str = Field(description="The original prompt that was submitted to ChatGPT")
    response: str = Field(description="The complete ChatGPT response text, preserving all formatting, markdown, line breaks, etc.")
    success: bool = Field(description="Whether the response was successfully retrieved from ChatGPT")
    error_message: str | None = Field(description="Error message if the operation failed, otherwise null")

# ============================================================================
# SYSTEM PROMPT - CHATGPT.COM ONLY OPERATION
# ============================================================================
CHATGPT_SYSTEM_PROMPT = """
🚨 CRITICAL BEHAVIORAL CONSTRAINTS:

1. SITE RESTRICTION:
   - You MUST operate ONLY on chatgpt.com
   - You are FORBIDDEN from visiting any other websites
   - You are FORBIDDEN from using search engines (Google, DuckDuckGo, Bing, etc.)
   - You are FORBIDDEN from navigating to external URLs
   - If you accidentally navigate away from chatgpt.com, immediately return to chatgpt.com

2. SINGLE PURPOSE:
   - Your ONLY task is to interact with ChatGPT on chatgpt.com
   - Submit the provided prompt to ChatGPT
   - Retrieve the complete response from ChatGPT
   - Return the response exactly as displayed

3. NO EXTERNAL ACTIONS:
   - Do NOT search the web
   - Do NOT visit external documentation
   - Do NOT follow links outside chatgpt.com
   - Do NOT perform research or gather information from other sources

4. RESPONSE HANDLING:
   - Preserve ALL formatting (markdown, line breaks, code blocks, etc.)
   - Do NOT summarize or modify the ChatGPT response
   - Do NOT filter or truncate the response
   - Return the complete text exactly as ChatGPT outputs it

5. ERROR HANDLING:
   - If chatgpt.com fails to load, retry up to 3 times
   - If ChatGPT doesn't respond after 60 seconds, retry
   - If maximum retries are exhausted, return an error message
   - Do NOT attempt alternative solutions or workarounds beyond retries
"""

# ============================================================================
# EXECUTION PLAN - CHATGPT INTERACTION SEQUENCE
# ============================================================================
CHATGPT_EXECUTION_PLAN = """
📋 PRECISE EXECUTION SEQUENCE - Follow these 6 steps exactly:

STEP 1: NAVIGATE TO CHATGPT.COM
- Open the browser and navigate directly to: https://chatgpt.com
- Wait for the page to fully load
- Verify you are on chatgpt.com (check the URL in the address bar)
- If the page fails to load, retry (up to 3 total attempts)
- If all retries fail, return error message and stop

STEP 2: LOCATE THE PROMPT INPUT AREA
- Find the main text input area where prompts are entered
- This is typically a text box at the bottom of the page
- It may have placeholder text like "Message ChatGPT" or similar
- Ensure the input field is visible and interactive
- Do NOT proceed until you've confirmed the input area is ready

STEP 3: INSERT AND SUBMIT THE PROMPT
- Click into the prompt input area to focus it
- Type or paste the EXACT text from the 'prompt' variable
- Do NOT modify, summarize, or alter the prompt text in any way
- After inserting the prompt, submit it (usually by pressing Enter or clicking Send button)
- Confirm the prompt was successfully submitted

STEP 4: WAIT FOR CHATGPT RESPONSE TO FULLY LOAD
- Wait for ChatGPT to begin generating a response
- Monitor the response area for streaming text
- Wait until the response is COMPLETELY finished (no more text being generated)
- Look for indicators that generation is complete (e.g., stop button becomes disabled, copy button appears)
- Allow up to 60 seconds for the response to complete
- If no response after 60 seconds, retry from STEP 3 (up to 3 total attempts)

STEP 5: RETRIEVE THE COMPLETE RESPONSE TEXT
- Locate the ChatGPT response in the conversation thread
- Extract the ENTIRE response text exactly as it appears
- Preserve ALL formatting: markdown, code blocks, line breaks, bullet points, etc.
- Do NOT summarize, filter, truncate, or modify the response in any way
- Ensure you capture the complete response from start to finish

STEP 6: RETURN THE STRUCTURED RESPONSE
- Populate the output model with:
  * prompt: The original prompt text that was submitted
  * response: The complete ChatGPT response (preserving all formatting)
  * success: true (if response retrieved successfully)
  * error_message: null (if successful)
- If any step failed after all retries:
  * success: false
  * error_message: Description of what failed
  * response: Empty string

🚨 CRITICAL REMINDERS:
- NEVER leave chatgpt.com during this entire process
- NEVER search the web or visit external URLs
- NEVER modify or summarize the ChatGPT response
- Retry failed steps up to 3 times before reporting failure
- Return the response EXACTLY as ChatGPT displays it
"""

# ============================================================================
# MAIN EXECUTION
# ============================================================================
async def main():
    # Initialize LLM with optimal settings for ChatGPT interaction
    llm = ChatOpenAI(
        model="gpt-4o",  # Using more capable model for accurate browser control
        temperature=0.0  # Zero temperature for maximum consistency
    )

    # Configure browser with extended timeout for ChatGPT responses
    browser = Browser(
        headless=False,  # Set to True for production
    )

    # Construct the complete task with strict ChatGPT-only instructions
    task = f"""
{CHATGPT_EXECUTION_PLAN}

📝 PROMPT TO SUBMIT TO CHATGPT:
"{prompt}"

🎯 YOUR MISSION:
Submit the above prompt to ChatGPT on chatgpt.com and retrieve the complete response.

🚨 STRICT OPERATIONAL RULES:
1. ONLY navigate to and operate on chatgpt.com - NO OTHER SITES ALLOWED
2. Do NOT search the web, use Google, DuckDuckGo, or any search engine
3. Do NOT visit any external URLs or documentation sites
4. Do NOT perform any research outside of chatgpt.com
5. Submit the prompt EXACTLY as provided above (do not modify it)
6. Retrieve the COMPLETE ChatGPT response with ALL formatting preserved
7. Do NOT summarize, filter, or modify the ChatGPT response
8. If chatgpt.com fails to load, retry up to 3 times total
9. If ChatGPT doesn't respond within 60 seconds, retry (up to 3 times)
10. Return structured output with the full response or error message

FINAL OUTPUT REQUIREMENTS:
Populate the structured output model with:
- prompt: The exact prompt text that was submitted
- response: The complete ChatGPT response (preserving markdown, line breaks, all formatting)
- success: true if response retrieved successfully, false otherwise
- error_message: null if successful, otherwise description of the failure

⚠️ REMEMBER: Stay on chatgpt.com for the ENTIRE session. Begin now.
"""

    # Create agent with ChatGPT-specific configuration
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        extend_system_message=CHATGPT_SYSTEM_PROMPT,
        output_model_schema=ChatGPTResponse,
        max_failures=3,  # Allow 3 retries as specified
        max_steps=25,  # Fewer steps needed for single-site operation
    )

    print(f"\n{'='*80}")
    print(f"🤖 CHATGPT AGENT - STARTING")
    print(f"{'='*80}")
    print(f"Target: https://chatgpt.com")
    print(f"Prompt to submit: {prompt.strip()}")
    print(f"{'='*80}\n")

    # Execute the agent
    history = await agent.run()

    # Extract and display structured output
    print(f"\n{'='*80}")
    print(f"{'✅ CHATGPT INTERACTION COMPLETED' if history.structured_output and history.structured_output.success else '❌ CHATGPT INTERACTION FAILED'}")
    print(f"{'='*80}\n")

    if history.structured_output:
        result = history.structured_output
        print("📊 STRUCTURED OUTPUT:")
        print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))

        print(f"\n{'='*80}")
        print(f"📋 RESULT SUMMARY:")
        print(f"{'='*80}")
        print(f"Status: {'✅ Success' if result.success else '❌ Failed'}")
        print(f"Prompt Submitted: {result.prompt}")

        if result.success:
            print(f"\n📝 CHATGPT RESPONSE:")
            print(f"{'-'*80}")
            print(result.response)
            print(f"{'-'*80}")
        else:
            print(f"\n⚠️  Error: {result.error_message}")

        print(f"{'='*80}\n")
    else:
        print("⚠️  No structured output available")
        print(f"Final result: {history.final_result()}")

    # Display execution statistics
    print(f"📊 EXECUTION STATS:")
    print(f"  - Steps taken: {history.number_of_steps()}")
    print(f"  - Duration: {history.total_duration_seconds():.2f}s")
    print(f"  - Pages visited: {len(history.urls())}")
    print(f"  - Errors: {sum(1 for e in history.errors() if e is not None)}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    asyncio.run(main())