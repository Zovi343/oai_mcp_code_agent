import json
import os

from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
)

from src.mcp_code_agent.custom_types.tool import CustomOpenAITool

load_dotenv()

class MCPAgent:
    """Agent class that supports MCP tool calling with the OpenAI."""
    TEMPERATURE = 0
    SYSTEM_PROMPT = """
    You are an expert assistant who can solve any task using tool calls. 
    You will be given a task to solve as best you can. Call a tool only when needed.
    """

    def __init__(self, tools: dict[str, CustomOpenAITool] ):
        """Initialize the agent with the provided tools.

        Args:
            tools (Dict[str, CustomOpenAITool]): The tools to use.

        Raises:
            ValueError: If no tools are provided.
        """
        self.client = AsyncAzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_LLM_MODEL_DEPLOYMENT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("OPENAI_API_VERSION"),
        )
        
        self.model = os.getenv("AZURE_OPENAI_LLM_MODEL")

        self.messages: list[dict] = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT,
            },
        ]

        if not tools:
            raise ValueError("No tools provided!")

        self.tools = tools
        self.tool_list = [tool["schema"] for tool in self.tools.values()]

    async def send_massages(self) -> ChatCompletion:
        """Send messages to the agent and get a response.

        Returns:
            ChatCompletion: The response from the agent.
        """
        return await self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tool_list,
            temperature=self.TEMPERATURE,
        )

    async def evaluate_tool(self, tool_call: ChatCompletionMessageToolCall):
        """Evaluate a tool call and append the result to the messages.

        Args:
            tool_call (ChatCompletionMessageToolCall): The tool call to evaluate.
        """
        arguments = (
            json.loads(tool_call.function.arguments)
            if isinstance(tool_call.function.arguments, str)
            else tool_call.function.arguments
        )

        tool_result = await self.tools[tool_call.function.name]["callable"](**arguments)
        self.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": json.dumps(tool_result),
            }
        )
        
            
    async def query_agent(self, query: str) -> str:
        """Query the agent with a given string.

        Args:
            query (str): The query to send to the agent.

        Returns:
            str: The response from the agent.
        """
        self.messages.append({"role": "user", "content": query})

        first_response = await self.send_massages()

        self.messages.append(first_response.choices[0].message)

        tools_calls = first_response.choices[0].message.tool_calls
        requested_tools_evaluation =  tools_calls is not None

        if requested_tools_evaluation:
            for tool_call in tools_calls:
                await self.evaluate_tool(tool_call)

            response_aware_of_tool_result = await self.send_massages()

            return response_aware_of_tool_result.choices[0].message.content
        else:
            return first_response.choices[0].message.content