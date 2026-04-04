import json
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict
from langchain_core.messages import HumanMessage, AIMessage

# 导入你刚刚完美封装的链
from rag_chain import get_rag_chain
from config import BACKEND_HOST, BACKEND_PORT, CORS_ALLOW_ORIGINS, DATA_DIR, SESSION_MAX_ROUNDS

app = FastAPI(title="Agentic-ChemRAG API")

# ==========================================
# 1. 解决前端跨域问题 (CORS)
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=CORS_ALLOW_ORIGINS != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 2. 挂载静态文件目录 (动态计算绝对路径)
# ==========================================
print(f"📦 正在挂载静态文件目录: {DATA_DIR}")

# 用绝对路径挂载，确保前端能拿到图片
app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")

# ==========================================
# 3. 初始化 RAG 引擎与状态管理
# ==========================================
rag_chain = None


def _get_rag_chain():
    global rag_chain
    if rag_chain is None:
        rag_chain = get_rag_chain()
    return rag_chain

# 内存级状态管理（模拟 Redis Session）
SESSION_STORE: Dict[str, List] = {}
MAX_ROUNDS = SESSION_MAX_ROUNDS  # 滑动窗口截断：只记最近3轮


# 定义前端传过来的请求体格式
class ChatRequest(BaseModel):
    session_id: str
    question: str


def _normalize_result_paths(result):
    # 统一路径分隔符，避免 Windows 反斜杠影响前端 URL
    for img in result.images:
        img.image_path = img.image_path.replace("\\", "/")

    for src in result.sources:
        src.file_name = src.file_name.replace("\\", "/")


def _update_session_history(session_id: str, question: str, answer: str):
    chat_history = SESSION_STORE.get(session_id, [])
    chat_history.extend([
        HumanMessage(content=question),
        AIMessage(content=answer)
    ])

    max_messages = MAX_ROUNDS * 2
    if len(chat_history) > max_messages:
        chat_history = chat_history[-max_messages:]

    SESSION_STORE[session_id] = chat_history


def _sse_payload(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _chunk_text(text: str, chunk_size: int = 8):
    if not text:
        return
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]


# ==========================================
# 4. 核心对话接口
# ==========================================
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        chat_history = SESSION_STORE.get(request.session_id, [])

        # 执行终极拷问
        print(f"收到请求，Session: {request.session_id}, 问题: {request.question}")
        result = await asyncio.to_thread(_get_rag_chain().invoke, {
            "question": request.question,
            "chat_history": chat_history
        })

        _update_session_history(request.session_id, request.question, result.answer)
        _normalize_result_paths(result)

        # FastAPI 会自动把 Pydantic 对象转成完美的 JSON 返回给前端！
        return result

    except Exception as e:
        print(f"❌ 系统报错: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    session_id = request.session_id
    question = request.question

    async def event_generator():
        chat_history = SESSION_STORE.get(session_id, [])
        try:
            yield _sse_payload({"type": "start"})

            result = await asyncio.to_thread(_get_rag_chain().invoke, {
                "question": question,
                "chat_history": chat_history
            })

            _normalize_result_paths(result)

            if hasattr(result, "model_dump"):
                result_payload = result.model_dump()
            elif hasattr(result, "dict"):
                result_payload = result.dict()
            else:
                result_payload = result

            answer_text = result_payload.get("answer", "未生成有效回答") if isinstance(result_payload, dict) else "未生成有效回答"

            # 以小块发送，确保前端能看到连续流式更新
            for chunk in _chunk_text(answer_text):
                yield _sse_payload({"type": "chunk", "content": chunk})
                await asyncio.sleep(0.01)
            yield _sse_payload({"type": "end", **(result_payload if isinstance(result_payload, dict) else {})})

            _update_session_history(session_id, question, answer_text)
        except Exception as e:
            yield _sse_payload({"type": "error", "error": str(e)})
    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    # 启动服务器！
    print(f"🚀 Agentic-ChemRAG 后端服务已启动！API 地址: http://{BACKEND_HOST}:{BACKEND_PORT}")
    uvicorn.run(app, host=BACKEND_HOST, port=BACKEND_PORT)