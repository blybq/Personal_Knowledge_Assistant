import os
import re
from typing import List, Tuple
from zhipuai import ZhipuAI
import chromadb


class ChromaTrainer:
    def __init__(
        self,
        api_key: str,
        chroma_path: str = "./chroma_db",
        collection_name: str = "thuc_news",
        distance: str = "cosine",   # 余弦相似度
    ):
        # Zhipu client
        self.embed_client = ZhipuAI(api_key=api_key)

        # —— 新版 Chroma：使用 PersistentClient —— #
        # 老式写法 chromadb.Client(Settings(...)) 已废弃，会触发你看到的报错
        self.client = chromadb.PersistentClient(path=chroma_path)

        # 若你手动传 embeddings（我们就是这么做的），可以不传 embedding_function
        # metadata 里设置索引度量（可选）
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": distance}
        )

    # ============== 数据读取 ==============

    def read_texts_from_dir(
        self,
        root_dir: str,
        max_bytes_per_category: int = 2 * 1024 * 1024,
    ) -> List[Tuple[str, str]]:
        """
        从每个子目录（类别）中累计读取约 max_bytes_per_category 字节的文本。
        返回 [(category, concatenated_text), ...]
        """
        results: List[Tuple[str, str]] = []
        # 按名称排序，保证可复现
        subfolders = sorted(
            [f for f in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, f))]
        )

        for folder in subfolders:
            folder_path = os.path.join(root_dir, folder)
            accumulated = 0
            buf: List[str] = []

            # 深度遍历该类别下的所有 .txt
            for r, _, files in os.walk(folder_path):
                for file in sorted(files):
                    if not file.lower().endswith(".txt"):
                        continue
                    path = os.path.join(r, file)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        # 避免编码问题卡住
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()

                    # 计算本文件字节数
                    content_bytes = content.encode("utf-8")
                    need = max_bytes_per_category - accumulated
                    if need <= 0:
                        break

                    if len(content_bytes) <= need:
                        buf.append(content)
                        accumulated += len(content_bytes)
                    else:
                        # 截断到还需要的字节数
                        piece = content_bytes[:need].decode("utf-8", errors="ignore")
                        buf.append(piece)
                        accumulated += len(piece.encode("utf-8"))
                        break
                if accumulated >= max_bytes_per_category:
                    break

            merged = "".join(buf).strip()
            if merged:
                results.append((folder, merged))
        return results

    # ============== 文本切句 ==============

    def split_into_sentences(self, text: str, max_chars_per_item: int = 2000) -> List[str]:
        """
        简单按中英文句末标点切分；太长的句子再按长度切块以避免超出 embedding-3 的 token 限制。
        embedding-3 单条上限 ~3072 tokens，这里保守用 2000 字符。
        """
        # 先按句末标点切：保留标点
        parts = re.split(r"(?<=[。！？!?\.])\s*", text)
        parts = [p.strip() for p in parts if p and p.strip()]

        # 对超长句子再切块
        chunks: List[str] = []
        for p in parts:
            if len(p) <= max_chars_per_item:
                chunks.append(p)
            else:
                # 优先按逗号、分号再切，仍然超长再按定长切
                subparts = re.split(r"(?<=[，；;、])", p)
                buf = ""
                for sp in subparts:
                    if len(buf) + len(sp) <= max_chars_per_item:
                        buf += sp
                    else:
                        if buf:
                            chunks.append(buf)
                        if len(sp) <= max_chars_per_item:
                            buf = sp
                        else:
                            # 兜底定长切
                            for i in range(0, len(sp), max_chars_per_item):
                                chunk = sp[i:i + max_chars_per_item]
                                chunks.append(chunk)
                            buf = ""
                if buf:
                    chunks.append(buf)
        return chunks

    # ============== 向量化 ==============

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量向量化。embedding-3：每次最多 64 条；单条不超过 ~3072 tokens。
        """
        if not texts:
            return []
        resp = self.embed_client.embeddings.create(
            model="embedding-3",
            input=texts
            # 如需自定义维度可加：dimensions=1024
        )
        return [item.embedding for item in resp.data]

    # ============== 训练（入库） ==============

    def train_chroma(
        self,
        root_dir: str,
        max_bytes_per_category: int = 2 * 1024 * 1024,
        batch_size: int = 64,
    ):
        """
        主流程：每类取 ~2MB 文本 -> 切句 -> 批量向量化 -> 写入 Chroma
        """
        cat_texts = self.read_texts_from_dir(root_dir, max_bytes_per_category)
        for category, big_text in cat_texts:
            print(f"[INFO] Category '{category}': preparing sentences...")
            sentences = self.split_into_sentences(big_text)
            print(f"[INFO] Category '{category}': {len(sentences)} sentences")

            # 批量调用 embedding 并写入
            idx = 0
            while idx < len(sentences):
                batch = sentences[idx: idx + batch_size]
                vectors = self.embed_batch(batch)

                ids = [f"{category}_{idx + i}" for i in range(len(batch))]
                metas = [{"category": category} for _ in batch]

                self.collection.add(
                    ids=ids,
                    documents=batch,
                    embeddings=vectors,
                    metadatas=metas,
                )
                idx += batch_size
                print(f"  -> inserted {min(idx, len(sentences))}/{len(sentences)}")

        print("[OK] Done. Data persisted under your PersistentClient path.")


if __name__ == "__main__":
    # ==== 配置区 ====
    API_KEY = "62539744e9ff4883a47762075f58fa14.zjyN4ZeeSZlHzobu"
    ROOT_DIR = "../training_for_chromadb/THUCNews"         # 你的 THUCNews 根目录
    CHROMA_PATH = "./chroma_db"                  # Chroma 持久化目录
    BYTES_PER_CATEGORY = 2 * 1024 * 1024         # 每类约 2MB
    # ==============

    trainer = ChromaTrainer(
        api_key=API_KEY,
        chroma_path=CHROMA_PATH,
        collection_name="thuc_news",
        distance="cosine",
    )
    trainer.train_chroma(
        root_dir=ROOT_DIR,
        max_bytes_per_category=BYTES_PER_CATEGORY,
        batch_size=64,   # embedding-3 每次最多 64 条
    )
