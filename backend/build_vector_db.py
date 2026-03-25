from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


def build_chroma_persist_db(chunks):
    """
    构建持久化数据库，只需调用一次
    :param chunks: 切分好的文档块列表
    :return: Chroma 向量数据库实例
    """
    print("⏳ [1/2] 正在加载 BGE 向量模型...")
    embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")

    print("🗄️ [2/2] 正在构建并持久化 Chroma 数据库 (空间法则: Cosine)...")
    chromadb = Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory="../data/chroma_db",
        collection_metadata={"hnsw:space": "cosine"}
    )
    print("✅ 数据库构建完成！")
    return chromadb
