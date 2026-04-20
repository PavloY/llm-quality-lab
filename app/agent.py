import json

from openai import OpenAI

from app.config import settings
from app.llm import LLMProvider
from app.schemas import AgentResponse, AgentStep, RetrievalResult
from app.tools import TOOLS_DESCRIPTION, ToolKit

AGENT_SYSTEM_PROMPT = """You are a technical support agent for FastAPI documentation.
You have access to tools to search knowledge bases.

Rules:
1. Use tools to find information before answering
2. If the question is a greeting or off-topic, use no_search_needed
3. You can call multiple tools if needed
4. Always base your answer on the search results
5. If search returns nothing relevant, say you don't have this information
6. Respond in the same language as the question"""

MAX_STEPS = 5


class Agent:
    """ReAct agent: think → act → observe → repeat until answer."""

    def __init__(self, toolkit: ToolKit, llm_provider: LLMProvider) -> None:
        self._toolkit = toolkit
        self._tools = toolkit.get_tools()
        self._client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )

    def query(self, question: str) -> AgentResponse:
        """Run the ReAct loop for a given question."""
        steps: list[AgentStep] = []
        tools_used: list[str] = []
        sources: list[str] = []

        messages = [
            {"role": "system", "content": AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]

        for _ in range(MAX_STEPS):
            response = self._client.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                tools=TOOLS_DESCRIPTION,
                tool_choice="auto",
                temperature=0.0,
            )

            message = response.choices[0].message

            if not message.tool_calls:
                return AgentResponse(
                    steps=steps,
                    final_answer=message.content or "I couldn't generate an answer.",
                    sources=list(set(sources)),
                    total_steps=len(steps),
                    tools_used=list(set(tools_used)),
                )

            messages.append(message)

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    tool_args = {}

                if tool_name in self._tools:
                    result = self._tools[tool_name](**tool_args)
                    tools_used.append(tool_name)
                else:
                    result = [
                        RetrievalResult(
                            text=f"Unknown tool: {tool_name}", source="error", score=0.0
                        )
                    ]

                if isinstance(result, list):
                    observation = "\n\n".join([r.text for r in result])
                    sources.extend([r.source for r in result if r.source != "agent_knowledge"])
                else:
                    observation = str(result)

                steps.append(
                    AgentStep(
                        thought=f"Calling {tool_name} with {tool_args}",
                        action=tool_name,
                        action_input=tool_args,
                        observation=observation[:500],
                    )
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": observation,
                    }
                )

        return AgentResponse(
            steps=steps,
            final_answer="I reached the maximum number of reasoning steps.",
            sources=list(set(sources)),
            total_steps=len(steps),
            tools_used=list(set(tools_used)),
        )
