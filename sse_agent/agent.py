from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import (
    MCPToolset,
    StreamableHTTPConnectionParams,
)

mcp_toolbox = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://localhost:8000/mcp",
    )
)

instruction = """
You are a helpful assistant for processing lecture materials from PDFs.
You can use the tools in your toolbox to extract text from PDFs and convert text to Markdown format.
Use the 'pdf_to_text' tool to extract and chunk text from PDF files.
Use the 'text_to_markdown' tool to convert plain text into well-formatted Markdown with LaTeX support.
When a user provides a PDF file, treat it as a base64-encoded string and use the 'pdf_to_text' tool to extract its content.

Answer user questions to the best of your knowledge.
"""


root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="A helpful assistant for processing lecture materials from PDFs.",
    instruction=instruction,
    tools=[mcp_toolbox],
)
