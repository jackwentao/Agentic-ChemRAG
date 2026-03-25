import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// 定义类型接口
interface ImageInfo {
  image_path: string;
  image_desc: string;
}

interface SourceInfo {
  file_name: string;
  page: string;
}

interface ChatResponse {
  answer: string;
  images: ImageInfo[];
  sources: SourceInfo[];
}

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  response?: ChatResponse;
}

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => `session-${Date.now()}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      isUser: true,
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    const question = input;
    setInput('');

    try {
      const response = await axios.post<ChatResponse>('/api/chat', {
        session_id: sessionId,
        question: question,
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.data.answer,
        isUser: false,
        response: response.data,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: '抱歉，发生错误。请检查后端服务是否运行。',
        isUser: false,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const formatFileName = (fileName: string) => {
    // 移除路径，只显示文件名
    return fileName.split(/[\\/]/).pop() || fileName;
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🔬 Agentic-ChemRAG 化学问答系统</h1>
        <p>基于材料科学与化学工程的高级检索增强生成系统</p>
      </header>

      <main className="app-main">
        <div className="chat-container">
          <div className="messages-container">
            {messages.length === 0 ? (
              <div className="empty-state">
                <h2>欢迎使用化学问答系统</h2>
                <p>请输入您的化学相关问题，系统将从专业文献中检索并回答。</p>
                <div className="example-questions">
                  <p>例如：</p>
                  <ul>
                    <li>卟啉是什么？</li>
                    <li>二氧化钛纳米复合材料如何制备？</li>
                    <li>共价有机框架有哪些应用？</li>
                  </ul>
                </div>
              </div>
            ) : (
              messages.map(message => (
                <div key={message.id} className={`message ${message.isUser ? 'user-message' : 'assistant-message'}`}>
                  <div className="message-content">
                    <div className="message-text">{message.text}</div>

                    {!message.isUser && message.response && (
                      <div className="response-details">
                        {/* 图片展示 */}
                        {message.response.images.length > 0 && (
                          <div className="images-section">
                            <h3>相关图片</h3>
                            <div className="images-grid">
                              {message.response.images.map((img, index) => (
                                <div key={index} className="image-card">
                                  <div className="image-container">
                                    <img
                                      src={`/${img.image_path}`}
                                      alt={img.image_desc}
                                      onError={(e) => {
                                        (e.target as HTMLImageElement).src = 'https://via.placeholder.com/300x200?text=Image+Not+Found';
                                      }}
                                    />
                                  </div>
                                  <div className="image-desc">{img.image_desc}</div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* 参考资料 */}
                        {message.response.sources.length > 0 && (
                          <div className="sources-section">
                            <h3>参考资料</h3>
                            <div className="sources-list">
                              {message.response.sources.map((source, index) => (
                                <div key={index} className="source-item">
                                  <a
                                    href={`http://localhost:8000/data/pdf/${encodeURIComponent(formatFileName(source.file_name))}#page=${source.page}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="source-link"
                                  >
                                    <span className="source-file">{formatFileName(source.file_name)}</span>
                                    <span className="source-page">第 {source.page} 页</span>
                                  </a>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}

            {loading && (
              <div className="message assistant-message">
                <div className="message-content">
                  <div className="message-text">
                    <div className="loading-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <form className="input-form" onSubmit={handleSubmit}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="请输入您的化学问题..."
              disabled={loading}
            />
            <button type="submit" disabled={loading || !input.trim()}>
              {loading ? '处理中...' : '发送'}
            </button>
          </form>
        </div>

        <div className="info-panel">
          <h2>系统信息</h2>
          <div className="info-section">
            <h3>📚 系统功能</h3>
            <ul>
              <li>复杂学术 PDF 解析</li>
              <li>实验数据精准溯源</li>
              <li>化学概念细粒度区分</li>
              <li>完整回答展示</li>
            </ul>
          </div>

          <div className="info-section">
            <h3>🔍 数据源</h3>
            <p>系统基于专业化学文献数据库，包括：</p>
            <ul>
              <li>无机基底改性研究</li>
              <li>共价有机框架合成</li>
              <li>复合工艺实验数据</li>
            </ul>
          </div>

          <div className="info-section">
            <h3>📊 会话信息</h3>
            <p>会话 ID: <code>{sessionId}</code></p>
            <p>消息数: {messages.length}</p>
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <p>Agentic-ChemRAG &copy; 2026 | 材料科学与化学工程垂直领域 RAG 系统</p>
      </footer>
    </div>
  );
}

export default App
