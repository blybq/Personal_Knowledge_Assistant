<template>
  <div class="main-layout">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-left">
        <h1 class="logo">个人知识助手</h1>
      </div>
      <div class="header-right">
        <span class="username" v-if="!organizationStore.isOrganizationMode">
          欢迎，{{ authStore.user?.username }}
        </span>
        <span class="username" v-else>
          欢迎进入组织 {{ organizationStore.currentOrganization?.name }}
        </span>
        <button 
          class="account-management-btn" 
          @click="goToManagement"
          v-if="!organizationStore.isOrganizationMode"
        >
          账号管理
        </button>
        <button 
          class="account-management-btn" 
          @click="goToOrganizationManagement"
          v-else
        >
          组织管理
        </button>
        <button 
          class="admin-btn" 
          @click="goToAdmin"
          v-if="authStore.user?.is_admin && !organizationStore.isOrganizationMode"
        >
          管理员
        </button>
        <button class="logout-btn" @click="handleLogout">
          {{ organizationStore.isOrganizationMode ? '退出组织' : '退出' }}
        </button>
      </div>
    </header>

    <div class="content-wrapper">
      <!-- 左侧导航栏 -->
      <aside class="sidebar">
        <nav class="nav">
          <button
            class="nav-item"
            :class="{ active: activeTab === 'chat' }"
            @click="activeTab = 'chat'"
          >
            <span class="nav-icon">💬</span>
            <span class="nav-text">AI对话</span>
          </button>
          <button
            class="nav-item"
            :class="{ active: activeTab === 'notes' }"
            @click="activeTab = 'notes'"
          >
            <span class="nav-icon">📝</span>
            <span class="nav-text">云笔记</span>
          </button>
        </nav>
      </aside>

      <!-- 主内容区域 -->
      <main class="main-content">
        <ChatView v-if="activeTab === 'chat'" />
        <NotesView v-else-if="activeTab === 'notes'" />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useOrganizationStore } from '@/stores/organization';
import ChatView from '@/views/ChatView.vue';
import NotesView from '@/views/notes/NotesView.vue';

const router = useRouter();
const authStore = useAuthStore();
const organizationStore = useOrganizationStore();

const activeTab = ref<'chat' | 'notes'>('chat');

onMounted(() => {
  authStore.initAuth();
  organizationStore.initOrganization();
  if (!authStore.isAuthenticated) {
    router.push('/login');
  }
});

const handleLogout = async () => {
  if (organizationStore.isOrganizationMode) {
    // 退出组织模式，回到个人账号
    organizationStore.switchToPersonalAccount();
  } else {
    // 完全退出登录
    await authStore.logout();
    router.push('/login');
  }
};

const goToManagement = () => {
  if (organizationStore.isOrganizationMode) {
    router.push('/organization-management');
  } else {
    router.push('/account-management');
  }
};

const goToOrganizationManagement = () => {
  router.push('/organization-management');
};

const goToAdmin = () => {
  router.push('/admin');
};
</script>

<style scoped>
.main-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
  width: 1230px;
}

.header {
  height: 60px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header-left .logo {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.username {
  color: #4a5568;
  font-weight: 500;
}

.account-management-btn {
  padding: 0.5rem 1rem;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.account-management-btn:hover {
  background: #3182ce;
}

.admin-btn {
  padding: 0.5rem 1rem;
  background: #805ad5;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.admin-btn:hover {
  background: #6b46c1;
}

.logout-btn {
  padding: 0.5rem 1rem;
  background: #e53e3e;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.logout-btn:hover {
  background: #c53030;
}

.content-wrapper {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  width: 250px;
  background: white;
  border-right: 1px solid #e2e8f0;
  padding: 1rem 0;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border: none;
  background: none;
  cursor: pointer;
  transition: background-color 0.2s;
  border-radius: 0;
  text-align: left;
}

.nav-item:hover {
  background: #f7fafc;
}

.nav-item.active {
  background: #ebf4ff;
  border-right: 3px solid #4299e1;
}

.nav-item.active .nav-text {
  color: #4299e1;
  font-weight: 600;
}

.nav-icon {
  margin-right: 0.75rem;
  font-size: 1.125rem;
}

.nav-text {
  color: #4a5568;
  font-weight: 500;
}

.main-content {
  flex: 1;
  overflow: hidden;
  background: white;
}
</style>
