// API服务层 - 管理所有与后端的通信
interface ModelConfig {
  name: string;
  display_name: string;
  api_key_env: string;
  base_url?: string;
  model_type: string;
}

interface ChatMessage {
  content: string;
  from_user: boolean;
  timestamp?: string;
}

interface ChatRequest {
  message: string;
  conversation_id?: string;
  model_name?: string;
}

interface ChatResponse {
  message: string;
  conversation_id: string;
  model_used: string;
  timestamp: string;
}

class ApiService {
  private baseURL: string;

  constructor(baseURL: string = 'http://localhost:8001') {
    this.baseURL = baseURL;
  }

  // 通用请求方法
  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        
        // 根据不同的HTTP状态码提供更详细的错误信息
        let errorMessage = errorData.detail || `HTTP ${response.status}: ${response.statusText}`;
        
        switch (response.status) {
          case 400:
            errorMessage = `请求参数错误: ${errorData.detail || '请检查输入内容'}`;
            break;
          case 401:
            errorMessage = `API密钥无效: ${errorData.detail || '请检查API密钥是否正确'}`;
            break;
          case 402:
            errorMessage = `账户余额不足或需要付费: ${errorData.detail || '请检查DeepSeek账户余额或付费状态'}`;
            break;
          case 403:
            errorMessage = `访问被拒绝: ${errorData.detail || '请检查API权限'}`;
            break;
          case 429:
            errorMessage = `请求频率过高: ${errorData.detail || '请稍后再试'}`;
            break;
          case 500:
            errorMessage = `服务器内部错误: ${errorData.detail || '请稍后重试'}`;
            break;
          case 502:
          case 503:
          case 504:
            errorMessage = `服务暂时不可用: ${errorData.detail || '请稍后重试'}`;
            break;
        }
        
        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      console.error(`API请求失败 [${endpoint}]:`, error);
      throw error;
    }
  }

  // 获取可用模型
  async getModels(): Promise<ModelConfig[]> {
    return this.request<ModelConfig[]>('/models');
  }

  // 发送聊天消息
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    return this.request<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // 获取对话历史
  async getConversationHistory(conversationId: string): Promise<ChatMessage[]> {
    return this.request<ChatMessage[]>(`/conversation/${conversationId}`);
  }

  // 清除对话
  async clearConversation(conversationId: string): Promise<{message: string}> {
    return this.request<{message: string}>(`/conversation/${conversationId}`, {
      method: 'DELETE',
    });
  }

  // 健康检查
  async healthCheck(): Promise<{status: string; timestamp: string}> {
    return this.request<{status: string; timestamp: string}>('/health');
  }

  // 测试模型
  async testModel(modelName: string): Promise<any> {
    return this.request<any>(`/test-model/${modelName}`);
  }
}

// 导出单例实例
export const apiService = new ApiService();
export type { ModelConfig, ChatMessage, ChatRequest, ChatResponse };
