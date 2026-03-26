from operator import itemgetter
from typing import List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_deepseek import ChatDeepSeek
from pydantic import BaseModel
from pydantic import Field
from retriever_engine import get_reranked_retriever


# 明确告诉前端：我会传给你一张图的路径和描述
class ImageInfo(BaseModel):
    image_path: str = Field(description="从资料中提取出的图片本地相对路径，如 data/extracted_images/xxx.jpeg")
    image_desc: str = Field(description="这段资料中对该图片的描述或图号说明")


# 明确告诉前端：我会传给你参考文献的来源
class SourceInfo(BaseModel):
    file_name: str = Field(description="参考的文献来源文件名")
    page: str = Field(description="文献所在的页码")


# 这是系统最终输出的总结构！前端直接拿这个解析！
class ChemResponse(BaseModel):
    answer: str = Field(
        description="对用户化学问题的详细文字解答。如果资料中查不到，请输出'无相关资料，无法回答'。注意：回答中不要包含任何图片的 Markdown 链接，纯文字即可。")
    images: List[ImageInfo] = Field(default_factory=list, description="相关图片的列表，如果没有查到图片则为空列表 []")
    sources: List[SourceInfo] = Field(default_factory=list, description="参考资料的来源列表")


def format_docs(docs):
    return "\n\n".join(
        f"内容：{doc.page_content}\n页码：{doc.metadata.get('page', '未知')}\n文件名：{doc.metadata.get('source', '未知')}"
        for doc in docs
    )


def get_rag_chain():
    """
    构建 RAG 链路，包含问题重写，回答问题，格式化输出
    :return: 返回构建好的链路
    """
    # TODO 重写问题链路
    rewrite_prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个无情的“指代消解”机器。你的唯一任务是根据对话历史，把用户最新问题中的代词（如“它”、“前者”、“后者”、“这个”）替换成具体的专有名词。

        【最高指令 / 绝对禁令】：
        1. 绝对不允许回答问题！不允许输出任何解释、分析或常识！
        2. 你的输出必须且只能是一句简短的疑问句！
        3. 如果用户问题没有代词，或者不需要改写，请原样输出用户的问题！

        【标准示例】：
        历史：用户问"卟啉是什么"，AI答"是一种有机物..."
        用户最新问题："那它和ZnO结合有什么用？"
        你的输出："卟啉和ZnO结合有什么用？"
    """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}绝对不允许回答问题！不允许输出任何解释、分析或常识！")
    ])
    rewrite_llm = ChatDeepSeek(model="deepseek-chat", temperature=0.1)
    rewrite_chain = rewrite_prompt | rewrite_llm | StrOutputParser()

    # TODO 回答问题链路
    # 使模型结构化输出
    answer_llm = ChatDeepSeek(model="deepseek-chat").with_structured_output(ChemResponse)
    # 采用工业级 ChatML 格式，严格区分“系统纪律”、“上下文记忆”和“用户诉求”
    answer_prompt = ChatPromptTemplate.from_messages([
        # 👑 1. System 角色 (最高指令层)：确立人设、铁律和知识库
        # 无论用户怎么使坏，模型都会死守这一层的规则
        ("system", """你是一个极其严谨的材料化学专家。
    你的唯一任务是：严格根据下方【检索到的资料】来回答问题。

    【强制执行的铁律】：
    1. 必须精准提取出资料中所有相关的图片路径（Markdown格式）、来源文件名和页码。
    2. 必须按要求的结构输出（或严格遵守用户指定的 JSON/格式要求）。
    3. 绝不能捏造数据。如果【检索到的资料】完全无法回答问题，你必须将 answer 字段直接填为：“无相关资料，无法回答”。

    【检索到的资料】：
    {retriever}
    """),

        # 🧠 2. 记忆占位符 (预留扩展层)：为了未来 5 分钟内能快速升级为 Agent 做准备
        # 如果将来你想让系统记住多轮对话，只需传入 chat_history 变量，它就会自动在这里展开
        # MessagesPlaceholder(variable_name="chat_history", optional=True),

        # 👤 3. Human 角色 (操作执行层)：用户当下的具体问题
        ("human", "{question}")
    ])
    retriever = get_reranked_retriever()
    # answer_chain = [retriever,question] | answer_prompt | answer_llm

    # TODO 构建完整链路
    chain = (
        # 1. 拦截原始输入字典，插入新的key-value对
            RunnablePassthrough.assign(
                standalone_question=rewrite_chain
            )
            | {
                # 2. 检索与询问
                "retriever": itemgetter("standalone_question") | retriever | format_docs,
                "question": itemgetter("standalone_question")
            }
            | answer_prompt | answer_llm
    )
    return chain




