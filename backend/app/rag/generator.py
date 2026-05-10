"""RAG answer generator with Agentic capabilities."""

import logging
import os
import time
from typing import Any, List, Tuple, Set, Optional

from langchain_core.agents import AgentAction
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, ToolMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_community.retrievers import BM25Retriever
from sentence_transformers import CrossEncoder

from app.rag.retriever import HybridRetriever
from app.tools.search import create_search_tool

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

API_ERROR_MESSAGE = "ขออภัย ระบบประมวลผลหนาแน่น (API Error) กรุณาลองใหม่อีกครั้ง"
INSUFFICIENT_INFO_MESSAGE = "ขออภัย ไม่พบข้อมูลในเอกสารอ้างอิง"


class RAGAgent:
    """Agentic RAG assistant that uses a HybridRetriever to answer questions."""

    def __init__(
        self,
        retriever: HybridRetriever,
        model_name: str = "typhoon-v2.5-30b-a3b-instruct",
        temperature: float = 0.1,
        max_retries: int = 3,
        recursion_limit: int = 10,
    ):
        self.retriever = retriever
        self.max_retries = max_retries
        self.recursion_limit = recursion_limit
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=os.environ.get("TYPHOON_API_KEY", ""),
            base_url="https://api.opentyphoon.ai/v1",
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
        return SystemMessage(content=(
            "คุณคือ AI ผู้ช่วยเชี่ยวชาญด้าน 'คู่มือสำนักทะเบียนและประมวลผล มหาวิทยาลัยเชียงใหม่' (CMU Registrar Assistant)\n"
            "หน้าที่หลักของคุณคือการตอบคำถามเกี่ยวกับกฎระเบียบ การลงทะเบียน และบริการต่างๆ ของสำนักทะเบียนและประมวลผล มหาวิทยาลัยเชียงใหม่ โดยใช้ข้อมูลจากระบบค้นหาเอกสาร (search_knowledge_base) เท่านั้น\n\n"
            "=== กฎที่ต้องปฏิบัติตามอย่างเคร่งครัด (STRICT RULES) ===\n"
            "1. ค้นหาข้อมูลก่อนตอบเสมอ: ใช้เครื่องมือ search_knowledge_base เพื่อดึงข้อมูลที่เกี่ยวข้อง หากข้อมูลไม่เพียงพอ ให้ค้นหาด้วยคำค้นใหม่ (Search again)\n"
            "2. ห้ามคิดเอง: ห้ามแต่งข้อมูลขึ้นมาเองเด็ดขาด ตอบเฉพาะสิ่งที่มีปรากฏในเอกสารที่ค้นพบเท่านั้น\n"
            "3. กรณีไม่พบข้อมูล: หากค้นหาแล้วไม่พบคำตอบในเอกสาร หรืออยู่นอกเหนือจากเอกสาร ให้ตอบว่า 'ขออภัย ไม่พบข้อมูลในคู่มือสำนักทะเบียนฯ' เท่านั้น ห้ามตอบด้วยข้อมูลอื่นที่คุณรู้เด็ดขาด\n"
            "4. การขอความชัดเจน (Clarification): หากคำถามจากผู้ใช้สั้นเกินไป กำกวม หรือไม่ชัดเจน (เช่น พิมพ์มาแค่คำเดียวว่า 'เกรด' หรือ 'ลา') ห้ามเดาความหมาย ให้ถามกลับอย่างสุภาพเพื่อขอรายละเอียดเพิ่มเติม\n"
            "5. อ้างอิงแหล่งที่มา: หากตอบคำถามได้ ให้สรุปคำตอบให้กระชับ เข้าใจง่าย และระบุชื่อเอกสารต้นทาง (Source) เสมอ\n"
            "6. กฎการอ้างอิง: ห้ามสมมติหรือสร้างชื่อเอกสารขึ้นมาเองเด็ดขาด (ZERO Fake Source) ชื่อ Source ที่อ้างอิงต้องมาจากฟิลด์ (Source: [ชื่อไฟล์]) ในผลลัพธ์ของ search_knowledge_base เท่านั้น\n"
            "=================================================="
        ))

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
            logger.warning("Agent execution error (attempt %d/%d): %s", attempt + 1, self.max_retries, exception)
            if "recursion limit" in str(exception).lower():
                return "ขออภัย ระบบทำการค้นหาหลายขั้นตอนเกินไป กรุณาระบุคำถามให้เจาะจงมากขึ้น", []
            
            if attempt == self.max_retries - 1:
                logger.error("All %d retries exhausted", self.max_retries)
                return API_ERROR_MESSAGE, []
            
            time.sleep(2 ** attempt)
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
    bm25_retriever: Optional[BM25Retriever],
    chat_history: str = "",
    reranker: Optional[CrossEncoder] = None,
    tenant_id: Optional[str] = None,
) -> Tuple[str, List[Document], List[Tuple[AgentAction, str]]]:
    hybrid_retriever = HybridRetriever(vectorstore, bm25_retriever, reranker, tenant_id=tenant_id)
    rag_agent = RAGAgent(hybrid_retriever)
    return rag_agent.generate(query, chat_history)