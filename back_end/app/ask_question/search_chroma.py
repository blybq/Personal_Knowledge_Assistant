import chromadb
from chromadb.utils import embedding_functions


class ChromaSearcher:
    def __init__(self, persist_dir="./chroma_db", collection_name="knowledge_base"):
        """
        初始化 Chroma 数据库
        :param persist_dir: 数据库存储路径
        :param collection_name: 集合名称（类似表）
        """
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_texts(self, texts: list, embeddings: list, ids: list = None):
        """
        添加文本和对应向量到数据库
        :param texts: 文本列表
        :param embeddings: 向量列表（长度 = len(texts)）
        :param ids: 可选，文本的唯一 ID 列表
        """
        if ids is None:
            ids = [f"id_{i}" for i in range(len(texts))]
        self.collection.add(documents=texts, embeddings=embeddings, ids=ids)

    def query(self, query_vector: list, top_k: int = 3):
        """
        使用向量检索数据库
        :param query_vector: 输入向量
        :param top_k: 返回最相似的前 k 个文本
        :return: 相似文本片段列表
        """
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k
        )
        return results["documents"][0]  # 返回文本列表


if __name__ == "__main__":
    # 模拟测试
    searcher = ChromaSearcher()

    # ====== Step 1: 添加数据 ======
    dummy_texts = ["我怎么学习人工智能。", "明天天气怎么样。", "c++ 是什么。"]
    dummy_vectors = [
        [0.1] * 1024,  # 假设 embedding-2 向量维度是 1024
        [0.2] * 1024,
        [0.3] * 1024
    ]
    searcher.add_texts(dummy_texts, dummy_vectors)

    # ====== Step 2: 检索 ======
    query_vec = [0.1] * 1024
    results = searcher.query(query_vec, top_k=2)
    print("检索结果：", results)
