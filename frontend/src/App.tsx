import React, { useState } from 'react';
import Chat, { Bubble, useMessages, MessageProps } from '@chatui/core';
import '@chatui/core/dist/index.css';
import axios from 'axios';

// 使用正确的后端地址
const API_BASE_URL = 'http://localhost:8000';

// 配置axios默认值
axios.defaults.headers.post['Content-Type'] = 'application/json';
axios.defaults.withCredentials = true;  // 允许发送凭证
axios.defaults.timeout = 180000; // 3分钟超时

interface SearchResult {
  title: string;
  snippet: string;
  url: string;
}

interface CustomMessageContent {
  text: string;
  searchResults?: SearchResult[];
}

function App() {
  const { messages, appendMsg, setTyping } = useMessages([]);
  const [sessionId, setSessionId] = useState<number | null>(null);

  const handleSend = async (type: string, val: string) => {
    if (type === 'text' && val.trim()) {
      appendMsg({
        type: 'text',
        content: { text: val },
        position: 'right',
      });

      setTyping(true);

      try {
        console.log('Sending request to:', `${API_BASE_URL}/chat/`);
        const response = await axios.post(`${API_BASE_URL}/chat/`, {
          message: val,
          session_id: sessionId,
        });
        console.log('Response:', response.data);

        const { response: aiResponse, search_results: searchResults, session_id: newSessionId } = response.data;

        if (!sessionId) {
          setSessionId(newSessionId);
        }

        appendMsg({
          type: 'text',
          content: {
            text: aiResponse,
            searchResults,
          },
          position: 'left',
        });
      } catch (error: any) {
        console.error('Error details:', error);
        const errorMessage = error.response?.data?.detail || error.message || '未知错误';
        appendMsg({
          type: 'text',
          content: { text: `抱歉，发生了错误：${errorMessage}` },
          position: 'left',
        });
      }

      setTyping(false);
    }
  };

  const renderMessageContent = (message: MessageProps) => {
    const content = message.content as CustomMessageContent;
    const { text, searchResults } = content;

    return (
      <div>
        <Bubble content={text} />
        {searchResults && searchResults.length > 0 && (
          <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
            <div style={{ marginBottom: '4px' }}>相关搜索结果：</div>
            {searchResults.map((result, index) => (
              <div key={index} style={{ marginBottom: '8px' }}>
                <a
                  href={result.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: '#1890ff', textDecoration: 'none' }}
                >
                  {result.title}
                </a>
                <div>{result.snippet}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{ height: '100vh' }}>
      <Chat
        navbar={{ title: '个人知识助手' }}
        messages={messages}
        renderMessageContent={renderMessageContent}
        onSend={handleSend}
        placeholder="请输入您的问题..."
      />
    </div>
  );
}

export default App; 