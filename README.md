# ChatGPT Browser Agent

A Python application using the [Browser Use](https://github.com/browser-use/browser-use) library to interact with ChatGPT programmatically. The agent operates exclusively on chatgpt.com, submits prompts, and retrieves complete responses with full formatting preservation.

## Features

- **ChatGPT-Only Operation**: Strictly operates within chatgpt.com - no external sites or web searches
- **Precise 6-Step Execution**: Structured workflow from navigation to response retrieval
- **Complete Response Capture**: Preserves all markdown, code blocks, line breaks, and formatting
- **Automatic Retry Logic**: Up to 3 retry attempts for failed operations
- **Structured Output**: Pydantic-validated JSON responses with success/error handling
- **No Modification**: Returns ChatGPT responses exactly as displayed, without summarization
- **Error Handling**: Graceful failure reporting with detailed error messages
- **Response Validation**: Ensures complete response loading before extraction

## Requirements

- Python >= 3.11
- OpenAI API key (for the LLM that controls the browser agent)
- Active internet connection

## Installation

### 1. Clone or Download the Repository

```bash
git clone <repository-url>
cd YC
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e .
```

This will install:
- `browser-use>=0.9.4` - Browser automation framework
- `python-dotenv>=1.0.0` - Environment variable management
- `langchain-openai>=0.2.0` - OpenAI LLM integration
- `pydantic>=2.0.0` - Data validation and structured output

### 4. Configure Environment Variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required: OpenAI API key for the browser control LLM
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional: Browser Use API key (if using Browser Use Cloud)
BROWSER_USE_API_KEY=your_browser_use_api_key_here

# Optional: Browser settings
HEADLESS_MODE=false
BROWSER_TIMEOUT=60000
```

**Getting API Keys:**
- OpenAI API Key: https://platform.openai.com/api-keys
- Browser Use API Key: https://browser-use.com (optional, for cloud features)

## Usage

### Basic Usage

Run the ChatGPT agent with your prompt defined in `main.py`:

```bash
python main.py
```

Edit the `prompt` variable in `main.py` to change what you want to ask ChatGPT:

```python
prompt = """
I need a new ERP that use AI
"""
```

### How It Works

The agent will:
1. Navigate to https://chatgpt.com
2. Locate the prompt input field
3. Submit your prompt exactly as written
4. Wait for ChatGPT's complete response
5. Extract the entire response with all formatting
6. Return the response in a structured format

### Customizing Your Prompt

You can ask ChatGPT anything you normally would:

```python
# Technical questions
prompt = "Explain how React hooks work with code examples"

# Creative tasks
prompt = "Write a short story about a robot learning to paint"

# Analysis requests
prompt = "Compare the pros and cons of microservices vs monolithic architecture"

# Code generation
prompt = "Create a Python function that validates email addresses using regex"
```

## Output Format

The agent returns structured data validated by Pydantic:

### Structured Response

```json
{
  "prompt": "I need a new ERP that use AI",
  "response": "When looking for an AI-powered ERP system, here are some top options to consider:\n\n1. **SAP S/4HANA Cloud**\n   - Features advanced AI and machine learning capabilities\n   - Intelligent automation for business processes\n   - Predictive analytics and insights\n\n2. **Oracle Fusion Cloud ERP**\n   - Built-in AI and ML for intelligent process automation\n   - Adaptive intelligence for personalized experiences\n   - Advanced analytics and forecasting\n\n3. **Microsoft Dynamics 365**\n   - AI-powered insights and automation\n   - Integration with Azure AI services\n   - Copilot assistance for enhanced productivity\n\nEach offers strong AI capabilities with different strengths depending on your specific business needs.",
  "success": true,
  "error_message": null
}
```

### Console Output

```
================================================================================
🤖 CHATGPT AGENT - STARTING
================================================================================
Target: https://chatgpt.com
Prompt to submit: I need a new ERP that use AI
================================================================================

[Agent navigates to ChatGPT and submits prompt...]

================================================================================
✅ CHATGPT INTERACTION COMPLETED
================================================================================

📊 STRUCTURED OUTPUT:
{
  "prompt": "I need a new ERP that use AI",
  "response": "When looking for an AI-powered ERP system...",
  "success": true,
  "error_message": null
}

================================================================================
📋 RESULT SUMMARY:
================================================================================
Status: ✅ Success
Prompt Submitted: I need a new ERP that use AI

📝 CHATGPT RESPONSE:
--------------------------------------------------------------------------------
When looking for an AI-powered ERP system, here are some top options to consider:

1. **SAP S/4HANA Cloud**
   - Features advanced AI and machine learning capabilities
   - Intelligent automation for business processes
   - Predictive analytics and insights

2. **Oracle Fusion Cloud ERP**
   - Built-in AI and ML for intelligent process automation
   - Adaptive intelligence for personalized experiences
   - Advanced analytics and forecasting

3. **Microsoft Dynamics 365**
   - AI-powered insights and automation
   - Integration with Azure AI services
   - Copilot assistance for enhanced productivity

Each offers strong AI capabilities with different strengths depending on your specific business needs.
--------------------------------------------------------------------------------
================================================================================

📊 EXECUTION STATS:
  - Steps taken: 8
  - Duration: 32.15s
  - Pages visited: 1
  - Errors: 0
================================================================================
```

## Project Structure

```
YC/
├── .env                    # Environment variables (create from .env.example)
├── .env.example           # Environment variable template
├── main.py                # Main application entry point
├── chatgpt_agent.py       # Browser Use agent implementation
├── source_extractor.py    # Source parsing and extraction logic
├── config.py              # Configuration management
├── pyproject.toml         # Project dependencies and metadata
└── README.md              # This file
```

## How It Works

### Architecture Overview

The agent follows a precise 6-step ChatGPT interaction process:

#### STEP 1: Navigate to ChatGPT.com
- Opens browser and navigates to https://chatgpt.com
- Waits for page to fully load
- Verifies correct URL in address bar
- Retries up to 3 times if page fails to load
- Stops with error if all retries fail

#### STEP 2: Locate the Prompt Input Area
- Finds the main text input field on ChatGPT
- Typically appears at bottom of page with placeholder text
- Ensures input field is visible and interactive
- Waits until input area is ready for interaction

#### STEP 3: Insert and Submit the Prompt
- Clicks into the prompt input area to focus it
- Inserts the EXACT prompt text without modification
- Submits the prompt (Enter key or Send button)
- Confirms successful submission

#### STEP 4: Wait for ChatGPT Response to Fully Load
- Monitors for response streaming to begin
- Waits for response generation to complete
- Looks for completion indicators (copy button appears, etc.)
- Allows up to 60 seconds for response
- Retries up to 3 times if no response received

#### STEP 5: Retrieve the Complete Response Text
- Locates ChatGPT's response in the conversation thread
- Extracts ENTIRE response text exactly as displayed
- Preserves ALL formatting (markdown, code blocks, line breaks)
- No summarization, filtering, or modification

#### STEP 6: Return the Structured Response
- Populates Pydantic model with:
  - `prompt`: Original prompt text submitted
  - `response`: Complete ChatGPT response with formatting
  - `success`: true/false based on operation result
  - `error_message`: Error description if failed, otherwise null
- Returns JSON-validated structured output

### Key Components

**ChatGPT System Prompt** (`CHATGPT_SYSTEM_PROMPT`)
- Enforces strict chatgpt.com-only operation
- Prohibits web searches and external navigation
- Defines error handling and retry behavior
- Ensures response preservation without modification

**Execution Plan** (`CHATGPT_EXECUTION_PLAN`)
- Provides detailed 6-step interaction sequence
- Includes retry logic for failures (up to 3 attempts)
- Specifies timeout behavior (60 seconds for response)
- Ensures systematic and reliable ChatGPT interaction

**Structured Output Model** (`ChatGPTResponse`)
- Pydantic model for guaranteed schema compliance
- Fields: prompt, response, success, error_message
- Validates all output automatically
- Provides type safety and programmatic access

## Advanced Usage

### Customizing System Prompts

Modify `CHATGPT_SYSTEM_PROMPT` to adjust agent behavior:

```python
CHATGPT_SYSTEM_PROMPT = """
🚨 CRITICAL BEHAVIORAL CONSTRAINTS:

1. SITE RESTRICTION:
   - You MUST operate ONLY on chatgpt.com
   - Add custom navigation rules if needed

2. RESPONSE HANDLING:
   - Preserve ALL formatting
   - Add custom extraction rules
   - Define specific timeout behaviors

... add your custom requirements
"""
```

### Modifying the Execution Plan

Customize the interaction sequence by editing `CHATGPT_EXECUTION_PLAN`:

```python
CHATGPT_EXECUTION_PLAN = """
📋 PRECISE EXECUTION SEQUENCE:

STEP 1: NAVIGATE TO CHATGPT.COM
- Add custom page load verification
- Adjust retry attempts

STEP 2: LOCATE INPUT AREA
- Add custom selectors
- Handle different ChatGPT UI versions

... add your custom steps
"""
```

### Extending the Output Model

Add additional fields to the structured output:

```python
class ChatGPTResponse(BaseModel):
    """Enhanced ChatGPT response with additional metadata."""
    prompt: str
    response: str
    success: bool
    error_message: str | None

    # New fields
    response_length: int = Field(description="Character count of response")
    response_time: float = Field(description="Time taken to generate response (seconds)")
    model_used: str = Field(description="ChatGPT model that generated response")
    timestamp: str = Field(description="ISO timestamp when response was received")
```

### Batch Processing Multiple Prompts

Use the agent to process multiple prompts:

```python
import asyncio
from main import ChatGPTResponse, prompt
from browser_use import Agent, ChatOpenAI, Browser

async def ask_chatgpt_batch(prompts: list[str]) -> list[ChatGPTResponse]:
    """Submit multiple prompts to ChatGPT and return all responses."""
    results = []

    llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
    browser = Browser(headless=True)

    for prompt_text in prompts:
        # Update the task for each prompt
        task = f"Submit this prompt to ChatGPT: {prompt_text}"

        agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
            output_model_schema=ChatGPTResponse,
            max_failures=3,
            max_steps=25,
        )

        history = await agent.run()
        if history.structured_output:
            results.append(history.structured_output)

    return results

# Usage
prompts = [
    "Explain quantum computing in simple terms",
    "Write a haiku about programming",
    "List 5 tips for better Python code"
]
responses = asyncio.run(ask_chatgpt_batch(prompts))

for resp in responses:
    print(f"\nPrompt: {resp.prompt}")
    print(f"Response: {resp.response[:100]}...")
```

## Troubleshooting

### Common Issues

**"OPENAI_API_KEY not found in environment variables"**
- Make sure you've created a `.env` file with your API key
- Check that the file is named exactly `.env` (not `.env.txt`)
- Verify the API key is valid at https://platform.openai.com/api-keys

**Browser doesn't open or chatgpt.com doesn't load**
- Try running with `headless=False` to see what's happening
- Check your internet connection
- Verify you can access https://chatgpt.com in a regular browser
- The agent will automatically retry 3 times before failing

**ChatGPT login required**
- chatgpt.com may require authentication
- Run with `headless=False` and manually log in when prompted
- The browser session will maintain the login for subsequent runs
- Consider using browser session persistence for automation

**Response not fully captured**
- Increase wait time in the execution plan if responses are long
- Check that response streaming completed before extraction
- Look for completion indicators (copy button, etc.)
- The agent waits up to 60 seconds by default

**Agent navigates away from chatgpt.com**
- This should not happen with the strict constraints
- If it does, check the system prompt enforcement
- Review agent logs to see what triggered external navigation
- File an issue if this persists

**Rate limiting or request blocking**
- ChatGPT may rate limit automated requests
- Add delays between batch operations
- Consider using a logged-in session
- Respect ChatGPT's terms of service

### Debug Mode

To see detailed agent execution logs, the Browser Use library provides built-in logging. You can enable it by setting the logging level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Configuration Options

### Agent Parameters

```python
agent = Agent(
    task=task,
    llm=llm,
    browser=browser,
    extend_system_message=ENHANCED_SYSTEM_PROMPT,  # Custom instructions
    output_model_schema=ResearchResult,             # Pydantic model
    max_failures=5,                                 # Retry limit
    max_steps=50,                                   # Maximum execution steps
)
```

### Browser Configuration

```python
browser = Browser(
    headless=True,              # Run without UI
    window_size={"width": 1920, "height": 1080},
    minimum_wait_page_load_time=0.5,
    wait_between_actions=1.0,
)
```

### LLM Configuration

```python
llm = ChatOpenAI(
    model="gpt-4o-mini",        # or "gpt-4o" for better accuracy
    temperature=0.1,            # Low for consistency
)
```

## Behavioral Constraints

The agent enforces strict operational rules:

### What the Agent WILL Do
- Navigate to chatgpt.com and stay there exclusively
- Locate and interact with the ChatGPT prompt input field
- Submit prompts exactly as provided without modification
- Wait for complete response generation (up to 60 seconds)
- Extract and preserve the full response with all formatting
- Retry failed operations up to 3 times
- Return structured output with success/error status

### What the Agent WILL NOT Do
- Navigate to any site other than chatgpt.com
- Perform web searches on Google, DuckDuckGo, Bing, etc.
- Visit external URLs or documentation sites
- Modify, summarize, or filter ChatGPT responses
- Attempt workarounds beyond the 3-retry limit
- Follow links outside of chatgpt.com
- Access ChatGPT API directly (uses browser automation only)

## Limitations

- Operates exclusively on chatgpt.com - no web search or external research
- ChatGPT may require login/authentication for access
- Response quality depends entirely on ChatGPT's output
- Browser automation requires stable internet connection
- Execution time varies based on ChatGPT response length (typically 20-60 seconds)
- Requires browser to be installed (Chrome/Chromium)
- Subject to ChatGPT's rate limits and terms of service
- Does not work with ChatGPT Plus features unless logged in

## Security & Privacy

- API keys are stored in `.env` (ensure it's in `.gitignore`)
- Browser sessions are isolated and can be made persistent
- Data is sent to OpenAI (for LLM control) and ChatGPT (for prompt submission)
- No external sites are accessed - strictly chatgpt.com only
- Consider using headless mode to avoid screen recording concerns
- Be mindful of sensitive information in prompts
- Review ChatGPT's privacy policy and terms of service

## Contributing

Contributions are welcome! Areas for improvement:

- **Session Persistence**: Save and reuse browser sessions to avoid repeated logins
- **Response Streaming**: Capture responses as they stream for real-time processing
- **Multi-Model Support**: Allow selection of different ChatGPT models (GPT-3.5, GPT-4, etc.)
- **Conversation Context**: Maintain conversation history for follow-up prompts
- **Parallel Processing**: Execute multiple prompts concurrently in separate browser tabs
- **Response Caching**: Cache responses to avoid duplicate API calls
- **Screenshot Capture**: Take screenshots of ChatGPT responses for verification
- **Export Formats**: Save responses to PDF, Markdown, or plain text files
- **API Wrapper**: REST API for programmatic ChatGPT interaction
- **Error Recovery**: More sophisticated retry strategies and error handling
- **Proxy Support**: Route traffic through proxies for privacy/access
- **Custom CSS Selectors**: Handle different ChatGPT UI versions automatically

## License

MIT License - See LICENSE file for details

## Acknowledgments

- [Browser Use](https://github.com/browser-use/browser-use) - Browser automation framework
- [LangChain](https://github.com/langchain-ai/langchain) - LLM integration
- OpenAI - GPT models for browser control

## Resources

- **Browser Use Documentation**: https://docs.browser-use.com/
- **Browser Use GitHub**: https://github.com/browser-use/browser-use
- **OpenAI Platform**: https://platform.openai.com/

## Support

For issues related to:
- **This project**: Open an issue in this repository
- **Browser Use library**: https://github.com/browser-use/browser-use/issues
- **OpenAI API**: https://help.openai.com/
