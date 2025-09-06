from zhipuai import ZhipuAI

class EmbeddingClient:
    def __init__(self, api_key: str = "62539744e9ff4883a47762075f58fa14.zjyN4ZeeSZlHzobu", 
                 model_name: str = "embedding-3"):
        self.client = ZhipuAI(api_key=api_key)
        self.model_name = model_name

    def embed_text(self, text: str):
        """
        对单条文本生成向量
        """
        response = self.client.embeddings.create(
            model=self.model_name,
            input=[text]  # 单条文本也需要用列表
        )
        # 返回向量
        return response.data[0].embedding

    def embed_texts(self, texts: list):
        """
        批量文本向量化
        """
        response = self.client.embeddings.create(
            model=self.model_name,
            input=texts
        )
        return [item.embedding for item in response.data]
    
    def embed_response(self, texts: list):
        """
        调试响应报文
        """
        response = self.client.embeddings.create(
            model=self.model_name,
            input=texts
        )
        return response


if __name__ == "__main__":
    API_KEY = "我的API key"
    embed_client = EmbeddingClient(API_KEY)

    text = "我 喜欢 学习 人工 智能"
    vector = embed_client.embed_text(text)
    print(len(vector), vector[:10])  # 打印前10维

    texts = ["我 喜欢 学习 人工 智能", "Python 是 编程 语言"]
    vectors = embed_client.embed_texts(texts)
    print(len(vectors), [v[:5] for v in vectors])

    texts = ["我 喜欢 学习 人工 智能", "Python 是 编程 语言"]
    print(embed_client.embed_response(texts))

