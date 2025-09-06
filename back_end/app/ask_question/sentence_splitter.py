import re
from typing import List

class SentenceSplitter:
    @staticmethod
    def split(text: str, max_chars: int = 200):
        """
        简单的中文分句器，按句号/问号/叹号/英文句号等切分
        长句可按 max_chars 再切一刀
        """
        parts = re.split(r"(?<=[。！？!?\.])\s*", text)
        parts = [p.strip() for p in parts if p.strip()]

        results: List[str] = []
        for p in parts:
            if len(p) <= max_chars:
                results.append(p)
            else:
                for i in range(0, len(p), max_chars):
                    results.append(p[i:i+max_chars])
        return results
