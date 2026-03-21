import glob
import os

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re


def process_chemistry_pdf(pdf_path: str) -> list[Document]:
    """
        处理化学PDF文献的函数，包含以下步骤：
        1. 加载PDF文件并提取文本内容 PyMuPDFLoader
        2. 清理文本内容，解决PDF文档的特殊格式问题（如硬换行、中文空格等）
        3. 使用RecursiveCharacterTextSplitter将文本分割成适合后续处理的小块，考虑中文标点作为分隔符

        接下来目标，调用底层PyMuPDF库，引入多模态技术，保存里面图片等非文本内容，增强文献的表达能力。
    :param pdf_path: 文献路径
    :return: 分割好的文献块列表，每个块都是一个Document对象，包含文本内容和元数据（来源路径）
    """
    print(f"正在加载pdf: {pdf_path}")
    # TODO 加载PDF文件
    loader = PyMuPDFLoader(pdf_path)
    # load() 会将PDF按页读取， 返回一个Document对象列表
    pages = loader.load()
    print(f"加载完成，共读取了 {len(pages)} 页。")

    # 打破页面壁垒 & 清晰PDF空格 & 使用正则表达式只删除中文空格
    full_text = ""
    for page in pages:
        content = page.page_content
        # 将中文间的空格替换为空字符串，保留其他类型的空格
        clean_content = re.sub(r'(?<=[\u4e00-\u9fa5])\s+(?=[\u4e00-\u9fa5])', '', content)
        # 解决PDF文档的硬换黄问题，将单行文本中的换行符替换为空格，但保留段落之间的双换行
        clean_content = re.sub(r'(?<!\n)\n(?!\n)', ' ', clean_content)
        full_text += clean_content + " "

    # 将拼好的全文重新包装成一个单一的 Document
    single_doc = [Document(page_content=full_text, metadata={"source": pdf_path})]
    # print(full_text)

    # TODO 分割文本（Chunking）
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        # 针对中文文献，加入中文标点作为分隔符，防止一句话被硬生生切断
        separators=["\n\n", "。", "，", "！", ",", "!", ". ", " ", "", "？", "\n"],
        # 保留分隔符在文本块的末尾，方便后续处理时能更自然地连接文本块
        keep_separator=True
    )

    # 开始分割
    chunks = text_splitter.split_documents(single_doc)
    print(f"分割完成，共生成了 {len(chunks)} 个文本块。")
    for i in range(len(chunks)):
        print(f"--- 文本块 {i+1} ---")
        print(chunks[i].page_content[0: 500])
        print(f"内容来自{chunks[i].metadata['source']}")
    return chunks


def process_muti_pdf(folder_path: str) -> list[Document]:
    """
        读取指定文件夹下的所有路径
    :param folder_path: pdf包路径
    :return list[Document]: 返回切好的所有文献快列表
    """
    # 扁平化的一维列表，用来装载所有PDF文献块
    all_chunks = []
    # 自动扫描文件夹下所有以 .pdf 结尾的文件（忽略大小写的话可以使用更复杂的匹配）
    # os.path.join 会自动处理 Windows(\) 和 Linux(/) 的路径斜杠差异
    search_pattern = os.path.join(folder_path, "*.pdf")
    pdf_files = glob.glob(search_pattern)
    print(f"在文件夹 {folder_path} 中找到了 {len(pdf_files)} 个PDF文件。")

    if not pdf_files:
        print(f"⚠️ 警告: 在 [{folder_path}] 目录下没有找到任何 PDF 文件！")
        return []

    for pdf_file in pdf_files:
        try:
            print(f"正在处理文件: {pdf_file}")
            chunks = process_chemistry_pdf(pdf_file)
            all_chunks.extend(chunks)
        except Exception as e:
            # 如果某一篇 PDF 损坏了，只跳过它，不要让整个程序崩溃
            print(f"❌ 处理文件 {pdf_file} 时发生错误: {e}")
            continue
    print(f"所有PDF处理完成，共生成了 {len(all_chunks)} 个文本块。")
    return all_chunks


if __name__ == "__main__":
    process_muti_pdf("../data/pdf")
