<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 初始化认证状态
authStore.initAuth()
</script>

<template>
  <RouterView />
</template>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f8fafc;
}

#app {
  height: 100vh;
  width: 100%;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 通用按钮样式 */
button {
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

/* 输入框样式 */
input, textarea {
  font-family: inherit;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

input:focus, textarea:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 2px rgba(66, 153, 225, 0.1);
}

/* 通用卡片样式 */
.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

/* 桌面端优化 - 使用百分比宽度而不是固定宽度 */
.main-layout {
  width: 100%;
}

.chat-container,
.notes-container {
  width: 100%;
  height: 100%;
}

.conversation-sidebar {
  width: 25%;
  min-width: 300px;
  max-width: 400px;
}

.notes-sidebar {
  width: 25%;
  min-width: 300px;
  max-width: 400px;
}

.chat-main,
.notes-main {
  width: 75%;
  flex: 1;
}

/* 登录页面优化 */
.login-container {
  width: 100%;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-card {
  width: 90%;
  max-width: 500px; /* 增大登录卡片宽度 */
  margin: 2rem auto;
}

/* 组织页面优化 */
.organizations-container,
.join-org-container {
  width: 90%;
  max-width: 1000px; /* 增大组织页面容器宽度 */
  margin: 2rem auto;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .conversation-sidebar,
  .notes-sidebar {
    width: 30%;
    min-width: 250px;
  }
  
  .chat-main,
  .notes-main {
    width: 70%;
  }
}

@media (max-width: 768px) {
  .main-layout .sidebar {
    width: 200px;
  }
  
  .chat-container .conversation-sidebar,
  .notes-container .notes-sidebar {
    width: 100%;
    max-width: none;
  }
  
  .chat-main,
  .notes-main {
    width: 100%;
  }
  
  .login-card {
    width: 95%;
    margin: 1rem auto;
  }
}

@media (max-width: 640px) {
  .main-layout .sidebar {
    display: none;
  }
  
  .chat-container .conversation-sidebar,
  .notes-container .notes-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .chat-container,
  .notes-container {
    flex-direction: column;
  }
  
  .organizations-container,
  .join-org-container {
    width: 95%;
    margin: 1rem auto;
    padding: 1rem;
  }
}
</style>
