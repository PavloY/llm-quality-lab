import time

from app.llm import LLMProvider
from app.logging_config import get_logger
from app.schemas import AgentResponse, AgentStep, RetrievalResult
from app.tools import TOOLS_DESCRIPTION, ToolKit

logger = get_logger(__name__)

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
        self._llm = llm_provider

    def query(self, question: str) -> AgentResponse:
        """Run the ReAct loop for a given question."""
        query_start = time.perf_counter()
        logger.info("agent_start question='%s'", question)
        steps: list[AgentStep] = []
        tools_used: list[str] = []
        sources: list[str] = []

        messages: list[dict] = [
            {"role": "system", "content": AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]

        for _ in range(MAX_STEPS):
            response = self._llm.generate_with_tools(
                messages=messages,
                tools=TOOLS_DESCRIPTION,
                temperature=0.0,
            )

            # Capture model's reasoning when mixed content (text + tool_use) is returned
            llm_thought = (response.message.content or "").strip()
            if llm_thought and response.message.tool_calls:
                logger.debug("llm_reasoning content='%s'", llm_thought[:200])

            # Terminal states: no tool calls → final answer
            if not response.message.tool_calls:
                latency_ms = round((time.perf_counter() - query_start) * 1000, 1)
                final = response.message.content or "I couldn't generate an answer."
                if response.stop_reason == "max_tokens":
                    logger.warning("agent_truncated stop_reason=max_tokens")
                logger.info(
                    "agent_done steps=%d tools=%s latency_ms=%s",
                    len(steps),
                    list(set(tools_used)),
                    latency_ms,
                )
                return AgentResponse(
                    steps=steps,
                    final_answer=final,
                    sources=list(set(sources)),
                    total_steps=len(steps),
                    tools_used=list(set(tools_used)),
                )

            # Append the assistant message (text + tool_calls) to history in OpenAI format
            assistant_msg: dict = {"role": "assistant", "content": response.message.content}
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": _json_dumps(tc.arguments)},
                }
                for tc in response.message.tool_calls
            ]
            messages.append(assistant_msg)

            # Execute each tool call
            for tc in response.message.tool_calls:
                tool_name = tc.name
                tool_args = tc.arguments or {}

                if tool_name in self._tools:
                    tool_start = time.perf_counter()
                    result = self._tools[tool_name](**tool_args)
                    tool_ms = round((time.perf_counter() - tool_start) * 1000, 1)
                    logger.info("tool_call tool='%s' latency_ms=%s", tool_name, tool_ms)
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
                        thought=llm_thought or f"Calling {tool_name} with {tool_args}",
                        action=tool_name,
                        action_input=tool_args,
                        observation=observation[:500],
                    )
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
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


def _json_dumps(obj: dict) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False)
