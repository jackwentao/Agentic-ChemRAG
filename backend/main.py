import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict
from langchain_core.messages import HumanMessage, AIMessage

# 导入你刚刚完美封装的链
from rag_chain import get_rag_chain

app = FastAPI(title="Agentic-ChemRAG API")

# ==========================================
# 1. 解决前端跨域问题 (CORS)
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段允许所有前端访问
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 2. 挂载静态文件目录 (动态计算绝对路径)
# ==========================================
# 获取当前 main.py 所在的 backend 目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 从 backend 退到上一级 (Agentic-ChemRAG)，再进入 data
DATA_DIR = os.path.join(BASE_DIR, "../data")
ABSOLUTE_DATA_DIR = os.path.abspath(DATA_DIR)

print(f"📦 正在挂载静态文件目录: {ABSOLUTE_DATA_DIR}")

# 用绝对路径挂载，确保前端能拿到图片
app.mount("/data", StaticFiles(directory=ABSOLUTE_DATA_DIR), name="data")

# ==========================================
# 3. 初始化 RAG 引擎与状态管理
# ==========================================
rag_chain = get_rag_chain()

# 内存级状态管理（模拟 Redis Session）
SESSION_STORE: Dict[str, List] = {}
MAX_ROUNDS = 3  # 滑动窗口截断：只记最近3轮


# 定义前端传过来的请求体格式
class ChatRequest(BaseModel):
    session_id: str
    question: str


# ==========================================
# 4. 核心对话接口
# ==========================================
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # 获取该用户的专属历史记录，如果没有则初始化
        chat_history = SESSION_STORE.get(request.session_id, [])

        # 执行终极拷问
        print(f"收到请求，Session: {request.session_id}, 问题: {request.question}")
        result = rag_chain.invoke({
            "question": request.question,
            "chat_history": chat_history
        })

        # 滑动窗口维护历史记录
        chat_history.extend([
            HumanMessage(content=request.question),
            AIMessage(content=result.answer)
        ])

        # 截断超长记忆
        max_messages = MAX_ROUNDS * 2
        if len(chat_history) > max_messages:
            chat_history = chat_history[-max_messages:]

        # 存回内存
        SESSION_STORE[request.session_id] = chat_history

        # ==========================================
        # 💥 核心清洗逻辑：消灭 Windows 反斜杠刺客！
        # 把所有的 "\\" 全部替换成 Web 标准的 "/"
        # ==========================================
        for img in result.images:
            img.image_path = img.image_path.replace("\\", "/")

        for src in result.sources:
            src.file_name = src.file_name.replace("\\", "/")

        # FastAPI 会自动把 Pydantic 对象转成完美的 JSON 返回给前端！
        return result

    except Exception as e:
        print(f"❌ 系统报错: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # 启动服务器！
    print("🚀 Agentic-ChemRAG 后端服务已启动！API 地址: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)