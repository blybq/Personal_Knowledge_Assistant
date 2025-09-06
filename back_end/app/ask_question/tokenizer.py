
# 分词器
import hanlp

class HanLPTokenizer:
    def __init__(self, model=hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH):
        """
        初始化分词器
        :param model: HanLP 提供的多任务模型，默认 ELECTRA 中文模型
        """
        self.pipeline = hanlp.load(model)

    def cut(self, text: str, coarse=False):
        """
        获取分词结果
        :param text: 输入文本
        :param coarse: 是否使用粗粒度分词（默认False，使用精细分词）
        :return: list[str]
        """
        result = self.pipeline(text)
        return result['tok/coarse'] if coarse else result['tok/fine']

    def cut_batch(self, texts: list, coarse=False):
        """
        批量分词
        """
        results = self.pipeline(texts)
        key = 'tok/coarse' if coarse else 'tok/fine'
        return [r[key] for r in results]

    def cut_for_embedding(self, text: str):
        """
        获取适合传给 embedding API 的分词结果（默认使用精细分词）
        """
        return " ".join(self.cut(text))  # 拼成空格分隔的字符串，embedding常用格式

    def cut_with_pos(self, text: str):
        """
        获取分词 + 词性标注（CTB体系）
        """
        result = self.pipeline(text)
        words = result['tok/fine']
        pos_tags = result['pos/ctb']
        return list(zip(words, pos_tags))


if __name__ == "__main__":
    tokenizer = HanLPTokenizer()
    text = "今天天气如何呢，你现在怎么样"

    print("精细分词：", tokenizer.cut(text))
    print("粗分词：", tokenizer.cut(text, coarse=True))
    print("适合Embedding的输入：", tokenizer.cut_for_embedding(text))
    print("分词+词性标注：", tokenizer.cut_with_pos(text))
