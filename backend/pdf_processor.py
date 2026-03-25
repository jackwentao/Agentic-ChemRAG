"""
PDF Multi-Modal Document Parser & Chunker (PDF多模态文档解析与切分器)

此脚本主要用于大模型 RAG (Retrieval-Augmented Generation) 数据预处理。
功能演进说明：
- [v1.0] 纯文本提取：实现基础的 PDF 文本解析。
- [v2.0] 图像截取：增加对文档内图像的提取与本地保存功能。
- [v3.0] 图文混排：将提取的图像转换为 Markdown 格式的 URL ( ![Image](path) ) 并无缝插入文本流，保留原始排版上下文。
- [v4.0] 精准页码追踪：通过全局偏移量映射（Offset Mapping）结合 LangChain 切分器，完美解决跨页 Chunking 导致页码元数据丢失的技术难题。
"""

import glob
import os
import fitz  # PyMuPDF 底层引擎，性能优异
import re
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def process_chemistry_pdf(pdf_path: str, image_output_dir: str) -> list[Document]:
    """
    解析单个 PDF 文件，提取图文信息，并返回带有精确页码元数据的文本块 (Chunks)。

    Args:
        pdf_path (str): PDF 文件的绝对或相对路径。
        image_output_dir (str): 提取出的图片保存目录。

    Returns:
        list[Document]: LangChain 标准格式的 Document 列表，每个块附带精确的 metadata。
    """
    if not os.path.isfile(pdf_path):
        print(f"❌ 错误: 文件 {pdf_path} 不存在！")
        return []

    if not os.path.exists(image_output_dir):
        os.makedirs(image_output_dir)

    doc = fitz.open(pdf_path)

    full_text = ""
    total_img_count = 0
    pdf_filename = os.path.basename(pdf_path).replace('.pdf', '')

    # 核心映射表：用于记录每一页文本在全局 full_text 字符串中的字符起止索引
    page_mapping = []

    for i in range(len(doc)):
        page = doc[i]
        page_elements = []
        page_text = ""

        # ==========================================
        # 步骤 1: 提取页面元素并按物理坐标排序，还原阅读顺序
        # ==========================================
        for block in page.get_text("blocks"):
            if block[6] == 0:  # 0 表示文本块
                page_elements.append({"type": "text", "y0": block[1], "x0": block[0], "content": block[4]})

        for img_info in page.get_image_info(xrefs=True):
            page_elements.append(
                {"type": "image", "y0": img_info["bbox"][1], "x0": img_info["bbox"][0], "xref": img_info["xref"]}
            )

        # 按照 Y 坐标主导、X 坐标辅助进行排序 (从上到下，从左到右)
        page_elements.sort(key=lambda e: (e["y0"], e["x0"]))

        # ==========================================
        # 步骤 2: 拼接单页图文内容 (Markdown 化)
        # ==========================================
        for elem in page_elements:
            if elem["type"] == "text":
                content = elem["content"]
                # 数据清洗：消除 PDF 提取时中文之间的多余空格，并处理异常换行
                clean_content = re.sub(r'(?<=[\u4e00-\u9fa5])\s+(?=[\u4e00-\u9fa5])', '', content)
                clean_content = re.sub(r'(?<!\n)\n(?!\n)', ' ', clean_content)
                page_text += clean_content + " "
            elif elem["type"] == "image":
                try:
                    base_image = doc.extract_image(elem["xref"])
                    if not base_image: continue
                    image_bytes, image_ext = base_image["image"], base_image["ext"]
                except Exception:
                    continue

                # 动态生成图片名并持久化
                image_name = f"{pdf_filename}_page{i + 1}_img{total_img_count}.{image_ext}"
                image_path = os.path.join(image_output_dir, image_name)
                with open(image_path, "wb") as f:
                    f.write(image_bytes)

                total_img_count += 1
                # 将图片占位符作为 Markdown 插入文本，实现多模态信息的对齐
                page_text += f"此处有图片![Image]({image_path})"

        # ==========================================
        # 步骤 3: 记录全局索引，构建页码映射花名册
        # ==========================================
        start_index = len(full_text)
        full_text += page_text + " "  # 将单页内容追加到全局上下文
        end_index = len(full_text)

        # 登记该页在全局文本流中的势力范围
        page_mapping.append({
            "page_num": i + 1,
            "start": start_index,
            "end": end_index
        })

    doc.close()

    # 将全文伪装成单个 LangChain Document，准备进行全局切分
    single_doc = [Document(
        page_content=full_text,
        metadata={"source": pdf_path, "pdf_filename": pdf_filename}
    )]

    # ==========================================
    # 步骤 4: 带有坐标感知的递归字符切分
    # ==========================================
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "。", "，", "！", ",", "!", ". ", " ", "", "？", "\n"],
        keep_separator=True,
        add_start_index=True  # 关键参数：保留每个 chunk 在原始长文本中的绝对起始位置
    )

    chunks = text_splitter.split_documents(single_doc)

    # ==========================================
    # 步骤 5: 元数据找回 (解决跨页 Chunk 的页码归属问题)
    # ==========================================
    page_idx = 0
    total_pages = len(page_mapping)

    for chunk in chunks:
        chunk_start = chunk.metadata.get("start_index", 0)

        # 【核心逻辑】：只要当前 chunk 的起始位置已经超过了当前页的管辖范围 (end)，
        # 页面指针就果断向后移动，绝不回头！
        while page_idx < total_pages and chunk_start >= page_mapping[page_idx]["end"]:
            page_idx += 1

        # 安全赋值与防御性边界处理
        if page_idx < total_pages:
            chunk.metadata["page"] = page_mapping[page_idx]["page_num"]
        else:
            # 应对极端的越界脏数据，兜底为最后一页或默认页
            chunk.metadata["page"] = page_mapping[-1]["page_num"] if page_mapping else 1

    print(f"✂️ [{pdf_filename}] 分割完成，共生成 {len(chunks)} 个携带精确页码的文本块。")
    return chunks


def process_multi_pdf(folder_path: str, image_output_dir: str = "../data/extracted_images") -> list[Document]:
    """
    批量处理文件夹下的所有 PDF 文件。

    Args:
        folder_path (str): 存放 PDF 的目标文件夹路径。
        image_output_dir (str): 提取图片的统一存放路径。

    Returns:
        list[Document]: 包含所有 PDF 解析结果的 Document 列表。
    """
    all_chunks = []
    search_pattern = os.path.join(folder_path, "*.pdf")
    pdf_files = glob.glob(search_pattern)
    print(f"📂 在文件夹 {folder_path} 中找到了 {len(pdf_files)} 个 PDF 文件。")

    for pdf_file in pdf_files:
        try:
            chunks = process_chemistry_pdf(pdf_file, image_output_dir)
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"❌ 处理文件 {pdf_file} 时发生错误: {e}")
            continue

    print(f"🎉 批处理完成！系统总共生成了 {len(all_chunks)} 个高质量图文文本块。")
    return all_chunks


if __name__ == "__main__":
    # 示例执行入口
    # 确保本地存在 data/pdf 目录并放入测试文件
    final_chunks = process_multi_pdf("data/pdf", "data/extracted_images")

