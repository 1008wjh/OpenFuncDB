"""
轻量级 RAG 检索引擎
- 无需 GPU / 外部 API
- 纯 Python 实现 TF-IDF 向量化 + 余弦相似度
- 启动时构建索引，支持实时刷新
"""

import math
import re
from collections import Counter
from typing import Optional


# ── 中文 + 英文分词 ──
def tokenize(text: str) -> list[str]:
    """简单但有效的分词：保留中文字符、英文单词、数字"""
    if not text:
        return []
    # 提取中文连续字符
    cn = re.findall(r'[\u4e00-\u9fff]+', text)
    # 提取英文单词
    en = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', text)
    return [t.lower() for t in cn + en]


class RAGEngine:
    """轻量级 RAG 搜索引擎"""

    def __init__(self):
        self._docs: list[dict] = []           # 文档列表 {id, text, ...}
        self._vocab: dict[str, int] = {}      # 词 → id
        self._idf: dict[str, float] = {}       # 词 → IDF
        self._vectors: list[list[float]] = []  # 每个文档的 TF-IDF 向量
        self._built = False

    # ── 构建索引 ──
    def build_index(self, docs: list[dict], text_field: str = "text"):
        """从文档列表构建 TF-IDF 索引"""
        self._docs = docs
        N = len(docs)
        if N == 0:
            self._built = True
            return

        # 1) 分词 + 统计 DF
        tokenized = []
        df = Counter()
        for doc in docs:
            tokens = tokenize(doc.get(text_field, ""))
            tokenized.append(tokens)
            for t in set(tokens):
                df[t] += 1

        # 2) 构建词表
        self._vocab = {word: i for i, word in enumerate(df.keys())}

        # 3) 计算 IDF
        self._idf = {
            word: math.log((N + 1) / (cnt + 1)) + 1.0
            for word, cnt in df.items()
        }

        # 4) 计算每个文档的 TF-IDF 向量 (L2 归一化)
        self._vectors = []
        for tokens in tokenized:
            vec = [0.0] * len(self._vocab)
            tf = Counter(tokens)
            for word, freq in tf.items():
                if word in self._vocab:
                    idx = self._vocab[word]
                    vec[idx] = (1 + math.log(freq)) * self._idf[word]
            # L2 归一化
            norm = math.sqrt(sum(v * v for v in vec)) or 1.0
            self._vectors.append([v / norm for v in vec])

        self._built = True

    # ── 搜索 ──
    def search(self, query: str, top_k: int = 5,
               func_type: Optional[str] = None) -> list[dict]:
        """
        语义搜索
        返回: [{doc, score}]
        """
        if not self._built or not self._vocab:
            return []

        # 查询向量
        q_tokens = tokenize(query)
        q_tf = Counter(q_tokens)
        q_vec = [0.0] * len(self._vocab)
        for word, freq in q_tf.items():
            if word in self._vocab:
                idx = self._vocab[word]
                q_vec[idx] = (1 + math.log(freq)) * self._idf.get(word, 1.0)
        q_norm = math.sqrt(sum(v * v for v in q_vec)) or 1.0
        q_vec = [v / q_norm for v in q_vec]

        # 余弦相似度
        scores = []
        for i, dvec in enumerate(self._vectors):
            if func_type and self._docs[i].get("func_type") != func_type:
                continue
            sim = sum(a * b for a, b in zip(q_vec, dvec))
            if sim > 0.001:
                scores.append((sim, i))

        scores.sort(key=lambda x: x[0], reverse=True)
        top = scores[:top_k]

        return [
            {**self._docs[i], "score": round(score, 4)}
            for score, i in top
        ]


# 全局单例
rag_engine = RAGEngine()
