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
    embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")

    # 1. 挂载本地数据库
    chroma_db = Chroma(
        persist_directory="../data/chroma_db",
        embedding_function=embedding
    )

    # 2. 粗排阶段：撒大网捞 10 个，但必须过 0.5 的及格线（防极度不相关幻觉）
    base_retriever = chroma_db.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 10, "score_threshold": 0.5}
    )

    # 3. 精排阶段：交叉注意力逐字审讯，选出最精华的 3 个
    cross_encoder = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3")
    # 修复了 model_name -> model
    reranker = CrossEncoderReranker(model=cross_encoder, top_n=3)

    # 4. 拼装流水线
    # 修复了 base_comprossor -> base_compressor
    advanced_retriever = ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=base_retriever
    )
    return advanced_retriever
