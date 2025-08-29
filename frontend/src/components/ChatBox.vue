<template>
  <McLayout class="container">
    <McHeader :title="'InfoPoP Chat'">
      <template #operationArea>
        <div class="operations">
          <select v-model="selectedModel" class="model-selector" title="选择AI模型">
            <option v-for="model in availableModels" :key="model.name" :value="model.name">
              {{ model.display_name }}
            </option>
          </select>
          <Button 
            icon="op-upload" 
            variant="outline" 
            color="common" 
            title="文件上传"
            size="md"
            @click="goToUpload"
          >
            文件上传
          </Button>
          <i class="icon-helping"></i>
        </div>
      </template>
    </McHeader>
    <McLayoutContent
      style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px"
      v-if="messages.length === 0"
    >
      <McIntroduction
        :title="'InfoPoP Chat'"
        :subTitle="'Hi，欢迎使用 InfoPoP AI 聊天助手'"
        :description="description"
      ></McIntroduction>
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </McLayoutContent>
    <McLayoutContent class="content-container" v-else>
      <template v-for="(msg, idx) in messages" :key="idx">
        <McBubble
          v-if="msg.from === 'user'"
          :content="msg.content"
          :align="'right'"
          :avatarConfig="{ imgSrc: 'https://matechat.gitcode.com/png/demo/userAvatar.svg' }"
        >
        </McBubble>
        <McBubble v-else :content="msg.content" :avatarConfig="{ imgSrc: 'https://matechat.gitcode.com/logo.svg' }"> </McBubble>
      </template>
      
      <!-- Loading indicator -->
      <div v-if="isLoading" class="loading-message">
        <McBubble content="AI正在思考中..." :avatarConfig="{ imgSrc: 'https://matechat.gitcode.com/logo.svg' }"> </McBubble>
      </div>
    </McLayoutContent>
    <div class="shortcut" style="display: flex; align-items: center; gap: 8px">
      <Button
        style="margin-left: auto"
        icon="add"
        shape="circle"
        title="新建对话"
        size="md"
        @click="newConversation"
      ></Button>
    </div>
    <McLayoutSender>
      <McInput 
        :value="inputValue" 
        :maxLength="2000" 
        :disabled="isLoading"
        @change="(e: string) => (inputValue = e)" 
        @submit="onSubmit"
        placeholder="输入您的问题..."
      >
        <template #extra>
          <div class="input-foot-wrapper">
            <div class="input-foot-left">
              <span v-for="(item, index) in inputFootIcons" :key="index">
                <i :class="item.icon"></i>
                {{ item.text }}
              </span>
              <span class="input-foot-dividing-line"></span>
              <span class="input-foot-maxlength">{{ inputValue.length }}/2000</span>
            </div>
            <div class="input-foot-right">
              <Button 
                icon="op-clearup" 
                shape="round" 
                :disabled="!inputValue || isLoading" 
                @click="inputValue = ''"
              >
                <span class="demo-button-content">清空输入</span>
              </Button>
            </div>
          </div>
        </template>
      </McInput>
    </McLayoutSender>
  </McLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Button } from 'vue-devui/button';
import 'vue-devui/button/style.css';

// Types
interface Message {
  from: 'user' | 'model';
  content: string;
  timestamp?: string;
}

interface ModelConfig {
  name: string;
  display_name: string;
  api_key_env: string;
  base_url?: string;
  model_type: string;
}

// Configuration
const API_BASE_URL = 'http://localhost:8001';

const description = [
  'InfoPoP 可以辅助研发人员编码、查询知识和相关作业信息、编写文档等。',
  '作为AI模型，InfoPoP 提供的答案可能不总是确定或准确的，但您的反馈可以帮助 InfoPoP 做的更好。',
];

// Reactive state
const inputValue = ref('');
const messages = ref<Message[]>([]);
const isLoading = ref(false);
const conversationId = ref<string>('');
const selectedModel = ref('gpt-3.5-turbo');
const availableModels = ref<ModelConfig[]>([]);
const errorMessage = ref('');

// Router
const router = useRouter();

const inputFootIcons = [
  { icon: 'icon-at', text: '智能体' },
  { icon: 'icon-standard', text: '词库' },
  { icon: 'icon-add', text: '附件' },
];

// API functions
const fetchAvailableModels = async () => {
  try {
    console.log('Fetching models from:', `${API_BASE_URL}/models`);
    const response = await fetch(`${API_BASE_URL}/models`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    const models = await response.json();
    console.log('Received models:', models);
    availableModels.value = models;
    errorMessage.value = ''; // Clear any previous errors
  } catch (error) {
    console.error('Error fetching models:', error);
    errorMessage.value = `Failed to load available models: ${error instanceof Error ? error.message : '未知错误'}`;
    // Add default models as fallback
    availableModels.value = [
      { name: 'gpt-3.5-turbo', display_name: 'GPT-3.5 Turbo', api_key_env: 'OPENAI_API_KEY', model_type: 'openai' },
      { name: 'gpt-4', display_name: 'GPT-4', api_key_env: 'OPENAI_API_KEY', model_type: 'openai' }
    ];
  }
};

const sendMessageToAPI = async (message: string): Promise<string> => {
  try {
    console.log('Sending message:', { message, model: selectedModel.value, conversation_id: conversationId.value });
    
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        conversation_id: conversationId.value || undefined,
        model_name: selectedModel.value,
      }),
    });

    console.log('Response status:', response.status);
    
    if (!response.ok) {
      const errorData = await response.json();
      console.error('API error response:', errorData);
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    console.log('Received response:', data);
    
    // Update conversation ID if it's a new conversation
    if (!conversationId.value) {
      conversationId.value = data.conversation_id;
    }
    
    return data.message;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

// Event handlers
const newConversation = () => {
  messages.value = [];
  conversationId.value = '';
  errorMessage.value = '';
};

const goToUpload = () => {
  router.push('/upload');
};

const onSubmit = async (evt: any) => {
  const messageContent = typeof evt === 'string' ? evt : inputValue.value;
  
  if (!messageContent.trim()) return;
  
  // Clear input and error
  inputValue.value = '';
  errorMessage.value = '';
  isLoading.value = true;
  
  // Add user message
  messages.value.push({
    from: 'user',
    content: messageContent,
    timestamp: new Date().toLocaleTimeString(),
  });

  try {
    // Send message to API and get response
    const aiResponse = await sendMessageToAPI(messageContent);
    
    // Add AI response
    messages.value.push({
      from: 'model',
      content: aiResponse,
      timestamp: new Date().toLocaleTimeString(),
    });
  } catch (error) {
    // Add error message
    messages.value.push({
      from: 'model',
      content: `抱歉，发生了错误：${error instanceof Error ? error.message : '未知错误'}`,
      timestamp: new Date().toLocaleTimeString(),
    });
    errorMessage.value = error instanceof Error ? error.message : '未知错误';
  } finally {
    isLoading.value = false;
  }
};

// Lifecycle
onMounted(() => {
  fetchAvailableModels();
});
</script>

<style>
.container {
  width: calc(100vw - 200px);
  max-width: 1200px;
  margin: 20px auto;
  height: calc(100vh - 150px);
  padding: 20px;
  gap: 8px;
}

.operations {
  display: flex;
  align-items: center;
  gap: 12px;
}

.model-selector {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  font-size: 14px;
  min-width: 150px;
}

.error-message {
  color: #e74c3c;
  background: #ffeaea;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #e74c3c;
  max-width: 400px;
  text-align: center;
}

.loading-message {
  opacity: 0.7;
}

.content-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow: auto;
}

.input-foot-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 100%;
  margin-right: 8px;

  .input-foot-left {
    display: flex;
    align-items: center;
    gap: 8px;

    span {
      font-size: 14px;
      line-height: 18px;
      color: #252b3a;
      cursor: pointer;
    }

    .input-foot-dividing-line {
      width: 1px;
      height: 14px;
      background-color: #d7d8da;
    }

    .input-foot-maxlength {
      font-size: 14px;
      color: #71757f;
    }
  }

  .input-foot-right {
    .demo-button-content {
      font-size: 14px;
    }

    & > *:not(:first-child) {
      margin-left: 8px;
    }
  }
}
</style>