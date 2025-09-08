from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from contextlib import contextmanager
from typing import Generator
import json
import os

from app.database.models import get_db
from app.ask_question.tokenizer import HanLPTokenizer
from app.ask_question.vectorization import EmbeddingClient
from app.ask_question.search_chroma import ChromaSearcher
from app.ask_question.sentence_splitter import SentenceSplitter
from app.ask_question.answerer import Answerer
from app.Conversation.conversation_manager import ConversationManager
# from Config.config import api_key

router = APIRouter(prefix="/api", tags=["ask"])

api_key = os.getenv("API_KEY")

# 初始化工具
tokenizer = HanLPTokenizer()
embed_client = EmbeddingClient(api_key=api_key)
searcher = ChromaSearcher(persist_dir="./chroma_db", collection_name="thuc_news")
answerer = Answerer(api_key=api_key)

# Pydantic模型类
class Question(BaseModel):
    question: str
    owner_id: int
    is_user: bool = True
    conversation_id: int = None

@contextmanager
def get_new_session() -> Generator[Session, None, None]:
    """获取新的数据库会话上下文管理器"""
    from app.database.models import SessionLocal
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()

@router.post("/ask")
def ask_question(q: Question, request: Request, db: Session = Depends(get_db)):
    """问答接口"""
    # 1. 分句
    sentences = SentenceSplitter.split(q.question)

    retrieved_contexts = []
    # 2. 每个句子：分词 -> 向量化 -> 检索数据库
    for sent in sentences:
        seg_text = tokenizer.cut_for_embedding(sent)
        vec = embed_client.embed_text(seg_text)
        results = searcher.query(query_vector=vec, top_k=3)
        retrieved_contexts.extend(results)

    # 去重（避免多个句子搜到重复片段）
    retrieved_contexts = list(dict.fromkeys(retrieved_contexts))

    # 3. 获取对话历史（如果提供了对话ID）
    conversation_history = []
    if q.conversation_id:
        # 获取对话的所有消息
        conversation_messages = ConversationManager.get_conversation_messages(db, q.conversation_id)
        
        # 构建对话历史列表，只保留最近的几轮对话
        max_history_turns = 100  # 限制最多100轮对话历史
        start_idx = max(0, len(conversation_messages) - max_history_turns)
        for i in range(start_idx, len(conversation_messages)):
            conversation_history.append({
                "question": conversation_messages[i]["question"],
                "answer": conversation_messages[i]["answer"]
            })

    # 4. 流式回答：构造生成器
    # 如果没有提供对话ID，则创建新的对话记录
    conversation = None
    if not q.conversation_id:
        # 创建新的对话记录
        if q.is_user:
            conversation = ConversationManager.create_conversation(db, q.owner_id, organization_id=None)
        else:
            conversation = ConversationManager.create_conversation(db, user_id=None, organization_id=q.owner_id)
        conversation_id = conversation.id
    else:
        conversation_id = q.conversation_id

    def event_stream():
        full_answer = ""
        try:
            for chunk in answerer.stream_answer(q.question, retrieved_contexts, conversation_history):
                if chunk == "[END]":
                    # 保存最终答案（新开 session）
                    try:
                        with get_new_session() as new_db:
                            if q.is_user:
                                ConversationManager.update_conversation(new_db, conversation_id, q.question, full_answer, user_id=q.owner_id, organization_id=None)
                            else:
                                ConversationManager.update_conversation(new_db, conversation_id, q.question, full_answer, user_id=None, organization_id=q.owner_id)
                    except Exception as e:
                        print("保存失败:", e)
                    yield f"event: done\ndata: {json.dumps({'done': True})}\n\n"
                    break

                full_answer += chunk
                yield f"event: message\ndata: {json.dumps({'chunk': chunk})}\n\n"

        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    headers = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
        "Content-Type": "text/event-stream; charset=utf-8",
        "Connection": "keep-alive"
    }
    return StreamingResponse(event_stream(), headers=headers)
