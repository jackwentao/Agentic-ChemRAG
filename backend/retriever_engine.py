"""
Agentic-ChemRAG Dual-Tower Retriever Engine (双塔检索引擎)

此脚本是大模型获取外部化学知识的核心枢纽，负责从海量底库中精准定位上下文。
功能演进说明：
- [v1.0] 基础召回：实现基于 Chroma 的原生单路向量检索。
- [v2.0] 双阶段精排与防幻觉 (Anti-Hallucination)：引入 bge-small (Bi-encoder) 粗排撒网与 bge-reranker (Cross-encoder) 交叉注意力精排。结合 score_threshold (>=0.5) 阈值硬拦截，构建了防止大模型面对无关问题时产生知识幻觉的物理防线。
- [v3.0] 读写对称与状态解耦 (架构规范)：针对底层的 IP 内积空间，在检索端严格执行 L2 归一化，保证了 Query 向量与底库向量数学维度的绝对对称。
- [v4.0] 引入模块级单例模式。将底层重量级组件（HuggingFaceEmbeddings 编码器、Chroma 向量库连接池、HuggingFaceCrossEncoder 重排模型）的实例化过程抽离至全局作用域。
"""
from langchain_chroma import Chroma
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_huggingface import HuggingFaceEmbeddings
from config import CHROMA_DIR, EMBEDDING_MODEL, RERANKER_MODEL, RERANK_TOP_N, RETRIEVAL_K, RETRIEVAL_SCORE_THRESHOLD

_embedding_model = None
_chroma_db = None
_cross_encoder = None


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embedding_model


def _get_chroma_db():
    global _chroma_db
    if _chroma_db is None:
        _chroma_db = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=_get_embedding_model(),
        )
    return _chroma_db


def _get_cross_encoder():
    global _cross_encoder
    if _cross_encoder is None:
        _cross_encoder = HuggingFaceCrossEncoder(model_name=RERANKER_MODEL)
    return _cross_encoder


def get_reranked_retriever():
    """
    构建双阶段检索器: 召回 (Top-10 且达标) -> 重排 (Top-3)
    :return: 带有精排功能的高级检索器
    """
    base_retriever = _get_chroma_db().as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": RETRIEVAL_K, "score_threshold": RETRIEVAL_SCORE_THRESHOLD}
    )
    reranker = CrossEncoderReranker(model=_get_cross_encoder(), top_n=RERANK_TOP_N)
    advanced_retriever = ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=base_retriever
    )
    return advanced_retriever


def get_similarity_retriever():
    """回退检索器：不做阈值过滤，保证最少返回 K 条候选。"""
    return _get_chroma_db().as_retriever(
        search_type="similarity",
        search_kwargs={"k": RETRIEVAL_K}
    )
