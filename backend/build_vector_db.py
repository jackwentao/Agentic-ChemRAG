"""
Agentic-ChemRAG Vector Database Builder (向量数据库构建引擎)

此脚本负责将清洗后的多模态文本块进行 Embedding 向量化，并持久化至 Chroma 数据库。
功能演进说明：
- [v1.0] 基础向量化：实现文本块到 Chroma 数据库的原生接入与持久化存储。
- [v2.0] 极速检索优化 (极致性能)：在 Embedding 阶段引入 L2 归一化 (normalize_embeddings=True)，并在底层 HNSW 索引强制替换空间法则为内积 (ip)。通过数学等价转换，彻底抛弃了高算力消耗的 Cosine 余弦计算。在保证召回精度 100% 一致的前提下，利用 CPU/GPU 对矩阵乘加的硬件级优化，极大地降低了高维向量的计算延迟。
"""
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from pdf_processor import process_multi_pdf
from config import CHROMA_DIR, EMBEDDING_MODEL, IMAGE_DIR, PDF_DIR


def build_chroma_persist_db(chunks):
    """
    构建持久化数据库，只需调用一次
    :param chunks: 切分好的文档块列表
    :return: Chroma 向量数据库实例
    """
    print("⏳ [1/2] 正在加载 BGE 向量模型...")
    embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, encode_kwargs={'normalize_embeddings': True})

    print("🗄️ [2/2] 正在构建并持久化 Chroma 数据库 (空间法则: ip)...")
    chromadb = Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory=str(CHROMA_DIR),
        collection_metadata={"hnsw:space": "ip"}
    )
    print("✅ 数据库构建完成！")
    return chromadb


if __name__ == "__main__":
    all_chunks = process_multi_pdf(str(PDF_DIR), str(IMAGE_DIR))
    build_chroma_persist_db(all_chunks)

