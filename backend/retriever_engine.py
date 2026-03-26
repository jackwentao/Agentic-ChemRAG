"""
Agentic-ChemRAG Dual-Tower Retriever Engine (双塔检索引擎)

此脚本是大模型获取外部化学知识的核心枢纽，负责从海量底库中精准定位上下文。
功能演进说明：
- [v1.0] 基础召回：实现基于 Chroma 的原生单路向量检索。
- [v2.0] 双阶段精排与防幻觉 (Anti-Hallucination)：引入 bge-small (Bi-encoder) 粗排撒网与 bge-reranker (Cross-encoder) 交叉注意力精排。结合 score_threshold (>=0.5) 阈值硬拦截，构建了防止大模型面对无关问题时产生知识幻觉的物理防线。
- [v3.0] 读写对称与状态解耦 (架构规范)：针对底层的 IP 内积空间，在检索端严格执行 L2 归一化，保证了 Query 向量与底库向量数学维度的绝对对称。
"""
from langchain_chroma import Chroma
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_huggingface import HuggingFaceEmbeddings


def get_reranked_retriever():
    """
    构建双阶段检索器: 召回 (Top-10 且达标) -> 重排 (Top-3)
    :return: 带有精排功能的高级检索器
    """
    embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5", encode_kwargs={'normalize_embeddings': True})

    # 1. 挂载本地数据库
    chroma_db = Chroma(
        persist_directory="../data/chroma_db",
        embedding_function=embedding,
    )

    # 2. 粗排阶段：撒大网捞 10 个，但必须过 0.5 的及格线（防极度不相关幻觉）
    base_retriever = chroma_db.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 10, "score_threshold": 0.5}
    )

    # 3. 精排阶段：交叉注意力逐字审讯，选出最精华的 3 个
    cross_encoder = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3")
    reranker = CrossEncoderReranker(model=cross_encoder, top_n=3)

    # 4. 拼装流水线
    advanced_retriever = ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=base_retriever
    )
    return advanced_retriever
