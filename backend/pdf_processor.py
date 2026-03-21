import glob
import os
import fitz  # 直接使用底层引擎
import re
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def process_chemistry_pdf(pdf_path: str, image_output_dir: str) -> list[Document]:
    """
    进化版：图文双提的化学 PDF 处理器
    """
    if not os.path.isfile(pdf_path):
        print(f"❌ 错误: 文件 {pdf_path} 不存在！")
        return []

    if not os.path.exists(image_output_dir):
        os.makedirs(image_output_dir)

    print(f"📄 正在加载并双提 PDF: {pdf_path}")

    # 1. 破局核心：直接用 fitz 打开文档，彻底掌控全局
    doc = fitz.open(pdf_path)
    print(f"✅ 加载完成，共读取了 {len(doc)} 页。")

    full_text = ""
    img_count = 0
    pdf_filename = os.path.basename(pdf_path).replace('.pdf', '')  # 提取文件名用于图片命名

    # 2. 遍历每一页：左手拿文本，右手拿图片
    for i in range(len(doc)):
        page = doc[i]

        # --- [左手：提取并清洗文本] ---
        content = page.get_text("text")
        # 清理中文空格
        clean_content = re.sub(r'(?<=[\u4e00-\u9fa5])\s+(?=[\u4e00-\u9fa5])', '', content)
        # 清理硬换行
        clean_content = re.sub(r'(?<!\n)\n(?!\n)', ' ', clean_content)
        full_text += clean_content + " "

        # --- [右手：提取并保存图片] ---
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            # 保存图片 (加上原 PDF 的名字，防止多篇文献图片同名覆盖)
            image_name = f"{pdf_filename}_page{i + 1}_img{img_index}.{image_ext}"
            with open(os.path.join(image_output_dir, image_name), "wb") as f:
                f.write(image_bytes)
            img_count += 1

    doc.close()
    print(f"🖼️ 提取完成！共截获了 {img_count} 张核心图表。")

    # 3. 把洗干净的纯文本，伪装成 LangChain 的 Document 对象
    # 这里我们把提取到的图片数量也偷偷塞进 metadata 里，方便以后做统计
    single_doc = [Document(
        page_content=full_text,
        metadata={
            "source": pdf_path,
            "extracted_images_count": img_count
        }
    )]

    # 4. 文本切分 (保持你原本优秀的中文策略)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "。", "，", "！", ",", "!", ". ", " ", "", "？", "\n"],
        keep_separator=True
    )

    chunks = text_splitter.split_documents(single_doc)
    print(f"✂️ 分割完成，共生成了 {len(chunks)} 个文本块。")
    return chunks


def process_muti_pdf(folder_path: str, image_output_dir: str = "data/extracted_images") -> list[Document]:
    all_chunks = []
    search_pattern = os.path.join(folder_path, "*.pdf")
    pdf_files = glob.glob(search_pattern)
    print(f"📂 在文件夹 {folder_path} 中找到了 {len(pdf_files)} 个 PDF 文件。")

    for pdf_file in pdf_files:
        try:
            # 修复了这里的传参问题，加上了图片输出路径
            chunks = process_chemistry_pdf(pdf_file, image_output_dir)
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"❌ 处理文件 {pdf_file} 时发生错误: {e}")
            continue

    print(f"🎉 所有处理完成！系统总共接管了 {len(all_chunks)} 个文本块。")
    return all_chunks


if __name__ == "__main__":
    # 假设你的 PDF 放在 data/pdf 目录下，图片想存到 data/extracted_images
    final_chunks = process_muti_pdf("data/pdf", "data/extracted_images")
