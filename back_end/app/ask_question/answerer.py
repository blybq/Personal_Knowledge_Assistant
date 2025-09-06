# ask_question/answerer.py
from zhipuai import ZhipuAI
from typing import List, Generator, Optional, Tuple, Any
import time
import traceback


class Answerer:
    def __init__(self, api_key: str, model: str = "glm-4"):
        self.client = ZhipuAI(api_key=api_key)
        self.model = model

    def build_prompt(self, question: str, context: List[str], conversation_history: List[dict] = None) -> str:
        """
        构建提示词，包含问题、检索到的上下文和对话历史摘要
        """
        # 构建检索到的参考资料
        context_text = "\n".join([f"- {c}" for c in context]) if context else "无相关参考资料"
        
        # 构建对话历史摘要
        history_summary = ""
        if conversation_history:
            history_summary = self.generate_summary(conversation_history)
        
        # 构建完整的提示词
        prompt = f"""你是一个智能助手。请基于以下参考资料和对话历史来回答用户的问题。

参考资料:
{context_text}

对话历史摘要:
{history_summary if history_summary else "无对话历史"}

当前问题: {question}

请给出简洁且有条理的回答。如果参考资料或对话历史与当前问题无关，请仅基于你的知识回答问题。
"""
        return prompt

    def generate_summary(self, conversation_history: List[dict]) -> str:
        """
        为对话历史生成摘要
        """
        if not conversation_history:
            return ""
        
        # 只取最近几轮对话进行摘要
        recent_history = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
        
        summary_parts = []
        for turn in recent_history:
            if "question" in turn and "answer" in turn:
                summary_parts.append(f"Q: {turn['question']}")
                summary_parts.append(f"A: {turn['answer']}")
        
        return "\n".join(summary_parts)

    def stream_answer(self, question: str, context: List[str], conversation_history: List[dict] = None) -> Generator[str, None, None]:
        """
        使用 SDK 的流式接口生成回答，包含问题、检索到的上下文和对话历史摘要
        yield 的片段都是字符串；在流结束前会 yield "[END]"。
        """
        prompt = self.build_prompt(question, context, conversation_history)
        messages = [
            {"role": "system", "content": "你是一个有用的助手"},
            {"role": "user", "content": prompt},
        ]

        resp_iterable = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
        )
        
        # 处理流式响应
        for chunk in resp_iterable:
            # print(f"[DEBUG] chunk={repr(chunk)}", flush=True)
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                choice = chunk.choices[0]
                if hasattr(choice, 'delta') and hasattr(choice.delta, 'content'):
                    content = choice.delta.content
                    if content:
                        yield content
                if hasattr(choice, 'finish_reason') and choice.finish_reason is not None:
                    yield "[END]"
                    return
        
        # 如果没有明确的结束信号，也发送结束标记
        yield "[END]"