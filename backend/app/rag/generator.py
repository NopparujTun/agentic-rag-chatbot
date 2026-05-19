"""RAG answer generator with Agentic capabilities."""

import os
import time
import structlog
from typing import Any, List, Tuple, Set, Optional

from langchain_core.agents import AgentAction
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, ToolMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from sentence_transformers import CrossEncoder

from app.rag.retriever import PineconeRetriever
from app.tools.search import create_search_tool
from app.rag.prompts import get_registrar_assistant_prompt

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

API_ERROR_MESSAGE = "ขออภัย ระบบประมวลผลหนาแน่น (API Error) กรุณาลองใหม่อีกครั้ง"
INSUFFICIENT_INFO_MESSAGE = "ขออภัย ไม่พบข้อมูลในเอกสารอ้างอิง"
BASE_RETRY_DELAY_SECONDS = 2


class RAGAgent:
    """Agentic RAG assistant that uses a Pinecone retriever to answer questions."""

    def __init__(
        self,
        retriever: PineconeRetriever,
        model_name: str = "deepseek-chat",
        temperature: float = 0.1,
        max_retries: int = 3,
        recursion_limit: int = 10,
    ):
        self.retriever = retriever
        self.max_retries = max_retries
        self.recursion_limit = recursion_limit
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
            base_url="https://api.deepseek.com/v1",
            temperature=temperature,
            max_tokens=2048,
        )
        self.retrieved_documents: List[Document] = []
        self._seen_document_contents: Set[str] = set()

    def _get_tools(self) -> List[Any]:
        """Define and return tools available for the agent."""
        search_knowledge_base = create_search_tool(
            self.retriever,
            self.retrieved_documents,
            self._seen_document_contents
        )
        return [search_knowledge_base]

    def _get_system_message(self) -> SystemMessage:
        """Retrieves the system message defining the agent's persona and rules."""
        return get_registrar_assistant_prompt()

    def _parse_intermediate_steps(self, messages: List[Any]) -> List[Tuple[AgentAction, str]]:
        intermediate_steps = []
        for i, message in enumerate(messages):
            if isinstance(message, AIMessage) and getattr(message, 'tool_calls', []):
                for tool_call in message.tool_calls:
                    observation_text = ""
                    for next_message in messages[i + 1:]:
                        if isinstance(next_message, ToolMessage) and getattr(next_message, 'tool_call_id', '') == tool_call.get("id"):
                            observation_text = str(next_message.content)
                            break

                    action_item = AgentAction(
                        tool=tool_call.get("name", "unknown_tool"),
                        tool_input=tool_call.get("args", {}),
                        log=""
                    )
                    intermediate_steps.append((action_item, observation_text))
        return intermediate_steps

    def _invoke_agent(self, agent: Any, input_content: str, attempt: int) -> Tuple[Optional[str], List[Tuple[AgentAction, str]]]:
        try:
            state = agent.invoke(
                {"messages": [("user", input_content)]},
                {"recursion_limit": self.recursion_limit}
            )

            messages = state["messages"]
            intermediate_steps = self._parse_intermediate_steps(messages)
            final_output = str(messages[-1].content)
            return final_output, intermediate_steps

        except Exception as exception:
            import traceback
            logger.warning("Agent execution error (attempt %d/%d): %s\n%s", attempt + 1, self.max_retries, exception, traceback.format_exc())
            if "recursion limit" in str(exception).lower():
                return "ขออภัย ระบบทำการค้นหาหลายขั้นตอนเกินไป กรุณาระบุคำถามให้เจาะจงมากขึ้น", []

            if attempt == self.max_retries - 1:
                logger.error("All %d retries exhausted", self.max_retries)
                return API_ERROR_MESSAGE, []

            time.sleep(BASE_RETRY_DELAY_SECONDS ** attempt)
            return None, []

    def generate(
        self,
        query: str,
        chat_history: str = ""
    ) -> Tuple[str, List[Document], List[Tuple[AgentAction, str]]]:
        self.retrieved_documents = []
        self._seen_document_contents = set()

        agent_tools = self._get_tools()
        system_message = self._get_system_message()

        compiled_agent = create_react_agent(self.llm, agent_tools, prompt=system_message)

        input_content = query
        if chat_history:
            input_content = f"ประวัติการสนทนาที่ผ่านมา:\n{chat_history}\n\nคำถามปัจจุบัน: {query}"

        for attempt in range(self.max_retries):
            output, intermediate_steps = self._invoke_agent(compiled_agent, input_content, attempt)
            if output is not None:
                return output, self.retrieved_documents, intermediate_steps

        return API_ERROR_MESSAGE, [], []


def generate_answer(
    query: str,
    vectorstore: Any,
    chat_history: str = "",
    reranker: Optional[CrossEncoder] = None,
) -> Tuple[str, List[Document], List[Tuple[AgentAction, str]]]:
    """Generate an answer using the agentic RAG pipeline.

    Args:
        query: The user's question.
        vectorstore: The Pinecone vector store instance.
        chat_history: Formatted string of prior conversation turns.
        reranker: Optional cross-encoder model for precision reranking.

    Returns:
        A tuple of (answer, retrieved_documents, intermediate_steps).
    """
    retriever = PineconeRetriever(vectorstore, reranker)
    rag_agent = RAGAgent(retriever)
    return rag_agent.generate(query, chat_history)
