<template>
  <div class="chat-view">
    <div class="chat-container">
      <!-- 左侧对话历史栏 -->
      <aside class="conversation-sidebar">
        <div class="sidebar-header">
          <h3>对话历史</h3>
          <button class="new-chat-btn" @click="createNewConversation">
            + 新对话
          </button>
        </div>
        
        <div class="conversation-list">
          <div
            v-for="conversation in conversations"
            :key="conversation.id"
            class="conversation-item"
            :class="{ active: activeConversation?.id === conversation.id }"
            @click="selectConversation(conversation)"
            @contextmenu.prevent="showConversationContextMenu($event, conversation)"
          >
            <div class="conversation-title">{{ conversation.title }}</div>
            <!-- <div class="conversation-preview">{{ conversation.title }}</div> -->
            <div class="conversation-time">{{ conversation.created_at }}</div>
          </div>
          
          <div v-if="conversations.length === 0" class="empty-state">
            <p>暂无对话记录</p>
            <button class="start-chat-btn" @click="createNewConversation">
              开始新对话
            </button>
          </div>
        </div>
      </aside>

      <!-- 右侧聊天主区域 -->
      <main class="chat-main">
        <div class="chat-header">
          <h2>{{ activeConversation?.title || '新对话' }}</h2>
        </div>
        
        <div class="messages-container" ref="messagesContainer">
          <div v-if="activeConversation" class="messages">
            <div v-for="(msg, index) in activeConversation.messages" :key="index" class="message-pair">
              
              <!-- 用户问题（靠右） -->
              <div 
                class="message user-message" 
                @contextmenu.prevent="showMessageContextMenu($event, msg, true)"
              >
                <div class="message-content">{{ msg.question }}</div>
              </div>
              
              <!-- AI回答（靠左） -->
              <div 
                class="message ai-message" 
                @contextmenu.prevent="showMessageContextMenu($event, msg, false)"
              >
                <div class="message-content">{{ msg.answer }}</div>
              </div>
              
            </div>
          </div>
          
          <div v-else class="welcome-message">
            <h3>欢迎使用AI对话</h3>
            <p>请开始一个新的对话或选择历史对话继续交流</p>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="input-area">
          <div class="input-container">
            <textarea
              v-model="currentMessage"
              placeholder="输入您的问题..."
              @keydown.enter.prevent="handleSendMessage"
              :disabled="isLoading"
              rows="1"
              ref="textareaRef"
              @input="adjustTextareaHeight"
            ></textarea>
            <button
              class="send-button"
              @click="handleSendMessage"
              :disabled="!currentMessage.trim() || isLoading"
            >
              <span v-if="isLoading">⏳</span>
              <span v-else>发送</span>
            </button>
          </div>
        </div>
      </main>
    </div>

    <!-- 右键菜单 -->
    <ContextMenu
      :visible="contextMenuVisible"
      :position="contextMenuPosition"
      :items="contextMenuItems"
      @close="closeContextMenu"
    />

    <!-- 确认对话框 -->
    <ConfirmDialog
      :visible="confirmDialogVisible"
      :title="confirmDialogTitle"
      :message="confirmDialogMessage"
      @confirm="handleConfirm"
      @cancel="handleCancel"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, reactive, onUnmounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useOrganizationStore } from '@/stores/organization';
import { conversationApi } from '@/services/api';
import type { ConversationTitle, ConversationDetail, Message } from '@/types/api';
import { fetchEventSource } from "@microsoft/fetch-event-source";
import ContextMenu, { type ContextMenuItem } from '@/components/ContextMenu.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";

dayjs.extend(utc);
dayjs.extend(timezone);

const authStore = useAuthStore();
const organizationStore = useOrganizationStore();

const conversations = ref<ConversationTitle[]>([]);
const activeConversation = ref<ConversationDetail | null>(null);
const currentMessage = ref('');
const isLoading = ref(false);
const textareaRef = ref<HTMLTextAreaElement | null>(null);
const messagesContainer = ref<HTMLDivElement | null>(null);

// 右键菜单相关
const contextMenuVisible = ref(false);
const contextMenuPosition = ref({ x: 0, y: 0 });
const contextMenuItems = ref<ContextMenuItem[]>([]);
const selectedConversation = ref<ConversationTitle | null>(null);
const selectedMessage = ref<Message | null>(null);

// 确认对话框相关
const confirmDialogVisible = ref(false);
const confirmDialogTitle = ref('');
const confirmDialogMessage = ref('');
const confirmDialogAction = ref<() => any>(() => {});

// 获取对话历史（标题列表）
const loadConversationTitles = async () => {
  if (!authStore.user) return;
  
  try {
    const ownerParams = organizationStore.getOwnerParams(authStore.user.id);
    const response = await conversationApi.getConversationTitles(
      ownerParams.owner_id, 
      ownerParams.is_user
    );
    if (response.success) {
      console.log("response的值为：", response);
      conversations.value = response.data || [];
      console.log("conversations.value的值为：", conversations.value);
    }
  } catch (error) {
    console.error('加载对话历史失败:', error);
  }
};

// 创建新对话
const createNewConversation = async () => {
  if (!authStore.user) return;
  
  isLoading.value = true;
  try {
    console.log("尝试创建对话")
    const ownerParams = organizationStore.getOwnerParams(authStore.user.id);
    const response = await conversationApi.createConversation(
      ownerParams.owner_id, 
      ownerParams.is_user
    );
    console.log("response是否成功：", response.success);
    if (response.success && response.data) {
      console.log("在createConversation中，response的值为", response.data);
      conversations.value.unshift(response.data);
      // 创建新对话后立即加载对话详情
      const detailResponse = await conversationApi.getConversationDetail(
        response.data.id, 
        ownerParams.owner_id, 
        ownerParams.is_user
      );
      if (detailResponse.success && detailResponse.data) {
        activeConversation.value = detailResponse.data;
      }
      currentMessage.value = '';
    }
  } catch (error) {
    console.error('创建对话失败:', error);
  } finally {
    isLoading.value = false;
  }
};

// 选择对话
const selectConversation = async (conversation: ConversationTitle) => {
  if (!authStore.user) return;
  
  isLoading.value = true;
  try {
    const response = await conversationApi.getConversationDetail(
      conversation.id, 
      conversation.owner_id, 
      conversation.is_user
    );
    if (response.success && response.data) {
      activeConversation.value = response.data;
      console.log("activeConversation.value的值为", activeConversation.value);
      console.log("activeConversation.messages的值为", activeConversation.value.messages);
      currentMessage.value = '';
    }
  } catch (error) {
    console.error('加载对话详情失败:', error);
  } finally {
    isLoading.value = false;
  }
};

const handleSendMessage = async () => {
  if (!currentMessage.value.trim() || !authStore.user || isLoading.value) return;

  const message = currentMessage.value.trim();
  currentMessage.value = '';
  adjustTextareaHeight();

  if (!activeConversation.value) {
    await createNewConversation();
  }

  const newMsg = reactive({
    id: 0,
    conversation_id: activeConversation.value?.id || 0,
    question: message,
    answer: "",
    created_at: dayjs().tz("Asia/Shanghai").format("YYYY-MM-DDTHH:mm:ssZ"),
  });
  activeConversation.value?.messages.push(newMsg);

  isLoading.value = true;

  try {
    const ownerParams = organizationStore.getOwnerParams(authStore.user.id);
    await conversationApi.askQuestionStream(
      {
        question: message,
        owner_id: activeConversation.value?.owner_id || ownerParams.owner_id,
        is_user: activeConversation.value?.is_user || ownerParams.is_user,
        conversation_id: activeConversation.value?.id,
      },
      (chunk) => {
        console.log("Before:", newMsg.answer);
        newMsg.answer = newMsg.answer + chunk; // 而不是 +=
        console.log("After:", newMsg.answer);
        console.log("Reactive check:", activeConversation.value?.messages.map(m => m.answer));
        nextTick().then(scrollToBottom);
      },
      async () => {
        if (activeConversation.value && authStore.user) {
          const detailResponse = await conversationApi.getConversationDetail(
            activeConversation.value.id,
            activeConversation.value.owner_id,
            activeConversation.value.is_user
          );
          if (detailResponse.success && detailResponse.data) {
            activeConversation.value = detailResponse.data;
          }
        }
        await loadConversationTitles();
        isLoading.value = false;
      },
      (err) => {
        newMsg.answer += `\n[错误]: ${err}`;
        isLoading.value = false;
      }
    );
  } catch (err) {
    console.error("发送消息失败:", err);
    isLoading.value = false;
  }
};

// 调整文本框高度
const adjustTextareaHeight = () => {
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto';
      textareaRef.value.style.height = Math.min(textareaRef.value.scrollHeight, 120) + 'px';
    }
  });
};

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

// 格式化时间
const formatTime = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
};

// 显示对话右键菜单
const showConversationContextMenu = (event: MouseEvent, conversation: ConversationTitle) => {
  event.preventDefault();
  event.stopPropagation(); // <- 很重要，阻止 document 上的 contextmenu 监听器干扰
  selectedConversation.value = conversation;
  selectedMessage.value = null;
  
  contextMenuPosition.value = { x: event.clientX, y: event.clientY };
  contextMenuItems.value = [
    {
      label: '删除对话',
      action: () => showConfirmDialog(
        '删除对话',
        `确定要删除对话 "${conversation.title}" 吗？此操作将删除该对话的所有消息。`,
        async () => {
          // 这里把 conversation.id 绑定进来
          await deleteConversation();
        }
      )
    }
  ];
  contextMenuVisible.value = true;
};

// 显示消息右键菜单
const showMessageContextMenu = (event: MouseEvent, message: Message, isQuestion: boolean) => {
  event.preventDefault();
  event.stopPropagation(); // <- 很重要，阻止 document 上的 contextmenu 监听器干扰
  selectedMessage.value = message;
  selectedConversation.value = null;
  
  contextMenuPosition.value = { x: event.clientX, y: event.clientY };
  
  if (isQuestion) {
    contextMenuItems.value = [
      {
        label: '删除问题',
        action: () => showConfirmDialog(
          '删除问题',
          '确定要删除这个问题吗？此操作将同时删除对应的回答。',
          () => deleteMessage(message.id, true)
        )
      }
    ];
  } else {
    contextMenuItems.value = [
      {
        label: '删除回答',
        action: () => showConfirmDialog(
          '删除回答',
          '确定要删除这个回答吗？问题将保留。',
          () => deleteMessage(message.id, false)
        )
      }
    ];
  }
  contextMenuVisible.value = true;
};

// 处理用户在对话框中点击确认
const handleConfirm = async () => {
  try {
    if (confirmDialogAction.value) {
      // 确保兼容同步/异步操作
      await Promise.resolve(confirmDialogAction.value());
    }
  } catch (err) {
    console.error('确认操作失败:', err);
    // 可以在此处添加错误提示
  } finally {
    // 无论如何都关闭对话框
    confirmDialogVisible.value = false;
  }
};

const handleCancel = () => {
  confirmDialogVisible.value = false;
};

// 显示确认对话框
const showConfirmDialog = (title: string, message: string, action: () => any) => {
  confirmDialogTitle.value = title;
  confirmDialogMessage.value = message;
  confirmDialogAction.value = action;
  confirmDialogVisible.value = true;
  contextMenuVisible.value = false;
};

// 删除对话
const deleteConversation = async () => {
  if (!selectedConversation.value || !authStore.user) return;
  
  try {
    const response = await conversationApi.deleteConversation(
      selectedConversation.value.id,
      selectedConversation.value.owner_id,
      selectedConversation.value.is_user
    );
    
    if (response.success) {
      // 从列表中移除
      conversations.value = conversations.value.filter(
        c => c.id !== selectedConversation.value!.id
      );
      
      // 如果删除的是当前选中的对话，清空当前对话
      if (activeConversation.value?.id === selectedConversation.value.id) {
        activeConversation.value = null;
      }
    }
  } catch (error) {
    console.error('删除对话失败:', error);
  }
};

// 删除消息
const deleteMessage = async (messageId: number, deleteQuestion: boolean) => {
  if (!authStore.user || !activeConversation.value) return;
  
  try {
    const response = await conversationApi.deleteMessage(
      messageId, 
      activeConversation.value.owner_id, 
      activeConversation.value.is_user,
      deleteQuestion
    );
    
    if (response.success && activeConversation.value) {
      // 重新加载对话详情
      const detailResponse = await conversationApi.getConversationDetail(
        activeConversation.value.id,
        activeConversation.value.owner_id,
        activeConversation.value.is_user
      );
      
      if (detailResponse.success && detailResponse.data) {
        activeConversation.value = detailResponse.data;
      }
    }
  } catch (error) {
    console.error('删除消息失败:', error);
  }
};

// 关闭右键菜单
const closeContextMenu = () => {
  contextMenuVisible.value = false;
};

// 重新加载对话数据
const reloadConversations = async () => {
  // 清空当前对话和消息
  activeConversation.value = null;
  conversations.value = [];
  
  // 重新加载对话列表
  await loadConversationTitles();
  
  // 如果有对话历史，默认选择第一个
  if (conversations.value.length > 0) {
    await selectConversation(conversations.value[0]);
  }
};

onMounted(async () => {
  // 初始化组织状态
  organizationStore.initOrganization();
  
  // 添加组织切换监听器
  organizationStore.addOrganizationChangeListener(reloadConversations);
  
  await loadConversationTitles();
  // 如果有对话历史，默认选择第一个
  if (conversations.value.length > 0) {
    await selectConversation(conversations.value[0]);
  }
});

// 组件卸载时移除监听器
onUnmounted(() => {
  organizationStore.removeOrganizationChangeListener(reloadConversations);
});
</script>

<style scoped>
.chat-view {
  height: 100%;
  background: white;
  width: 950px;
}

.chat-container {
  display: flex;
  height: 100%;
}

.conversation-sidebar {
  width: 300px;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  color: #2d3748;
  font-size: 1rem;
}

.new-chat-btn {
  padding: 0.5rem 0.75rem;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.new-chat-btn:hover {
  background: #3182ce;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.conversation-item {
  padding: 0.75rem;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: background-color 0.2s;
  border: 1px solid #e2e8f0;
}

.conversation-item:hover {
  background: #f7fafc;
}

.conversation-item.active {
  background: #ebf4ff;
  border-color: #4299e1;
}

.conversation-title {
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
}

.conversation-preview {
  color: #718096;
  font-size: 0.75rem;
  margin-bottom: 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-time {
  color: #a0aec0;
  font-size: 0.75rem;
}

.empty-state {
  text-align: center;
  padding: 2rem 1rem;
  color: #718096;
}

.start-chat-btn {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.chat-header h2 {
  margin: 0;
  color: #2d3748;
  font-size: 1.25rem;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.message {
  max-width: 80%;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  line-height: 1.5;
}

.message-pair {
  display: flex;
  flex-direction: column;
  gap: 0.5rem; /* 消息之间的垂直间距 */
}

.user-message {
  align-self: flex-end;
  background: #4299e1;
  color: white;
}

.ai-message {
  align-self: flex-start;
  background: #f7fafc;
  color: #2d3748;
  border: 1px solid #e2e8f0;
}

.welcome-message {
  text-align: center;
  padding: 2rem;
  color: #718096;
}

.input-area {
  padding: 1rem;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
}

.input-container {
  display: flex;
  gap: 0.5rem;
  align-items: flex-end;
  max-width: 800px;
  margin: 0 auto;
}

.input-container textarea {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  resize: none;
  font-family: inherit;
  font-size: 0.875rem;
  line-height: 1.5;
  min-height: 40px;
  max-height: 120px;
}

.input-container textarea:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 2px rgba(66, 153, 225, 0.1);
}

.send-button {
  padding: 0.75rem 1rem;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  min-width: 60px;
  height: 40px;
}

.send-button:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
}

.send-button:not(:disabled):hover {
  background: #3182ce;
}
</style>
