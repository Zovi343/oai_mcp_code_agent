import json
import os

from dotenv import load_dotenv
from mcp_clients.tool_types import CustomOpenAITool
from openai import AsyncAzureOpenAI
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
)

load_dotenv()

class MCPAgent:
    """Agent class that supports MCP tool calling with the OpenAI."""
    TEMPERATURE = 0
    SYSTEM_PROMPT = """
    You are an expert assistant who can solve any task using tool calls.
    You will be given a task to solve as best you can. Call a tool only when needed.
    """

    def __init__(self)-> None:
        """Initialize the agent with the provided tools."""
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

        self.tools: dict[str, CustomOpenAITool] | None = None

    def add_tools(self, tools: dict[str, CustomOpenAITool]):
        """Configure the tools for the agent.

        Args:
            tools (dict[str, CustomOpenAITool]): The tools to configure.

        Raises:
            ValueError: If no tools are provided.
        """
        if not tools:
            raise ValueError("No tools provided!")

        if self.tools:
            self.tools | tools
        else:
            self.tools = tools
        self.tool_list = [tool["schema"] for tool in self.tools.values()]


    async def send_messages(self) -> ChatCompletion:
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

    async def query(self, message: str) -> tuple[str, list[dict]]:
        """Query the agent with a given string.

        Args:
            message (str): The query to send to the agent.

        Returns:
            str: The response from the agent.

        Raises:
            ValueError: If no tools are not configured.
        """
        if not self.tools:
            raise ValueError("Tools are not configured!")

        self.messages.append({"role": "user", "content": message})

        first_response = await self.send_messages()

        self.messages.append(first_response.choices[0].message)

        tool_calls = first_response.choices[0].message.tool_calls
        requested_tools_evaluation =  tool_calls is not None

        if requested_tools_evaluation:
            return None, tool_calls
        else:
            return first_response.choices[0].message.content, None


    async def evaluate_tool(self, tool_call: ChatCompletionMessageToolCall) -> str:
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
        parsed_tool_result = json.dumps(tool_result)
        self.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": parsed_tool_result,
            }
        )

        return parsed_tool_result


    async def tool_aware_query(self):
        """Queries the agents with all the existing messages.

        Should be called after the tools have been evaluated.

        Returns:
            _type_: The response from the agent.
        """
        response_aware_of_tool_result = await self.send_messages()
        return response_aware_of_tool_result.choices[0].message.content
