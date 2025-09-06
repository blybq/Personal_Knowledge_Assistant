<template>
  <div class="organizations-view">
    <div class="organizations-container">
      <div class="header">
        <h1>我加入的组织</h1>
        <button class="join-org-btn" @click="goToJoinOrganization">
          + 加入新组织
        </button>
      </div>

      <div class="organizations-list">
        <div
          v-for="organization in organizations"
          :key="organization.id"
          class="organization-card"
        >
          <div class="org-info">
            <h3 class="org-name">{{ organization.name }}</h3>
            <p class="org-description" v-if="organization.description">
              {{ organization.description }}
            </p>
            <div class="org-meta">
              <span class="org-members">
                {{ organization.member_count || 0 }} 名成员
              </span>
              <span class="org-created">
                创建于 {{ formatTime(organization.created_at) }}
              </span>
            </div>
          </div>
          <div class="org-actions">
            <span class="invite-code">邀请码: {{ organization.invite_code }}</span>
          </div>
        </div>

        <div v-if="organizations.length === 0" class="empty-state">
          <p>您还没有加入任何组织</p>
          <button class="join-first-btn" @click="goToJoinOrganization">
            立即加入组织
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { organizationApi } from '@/services/api';
import type { Organization } from '@/types/api';

const router = useRouter();
const authStore = useAuthStore();

const organizations = ref<Organization[]>([]);
const isLoading = ref(false);

// 获取用户加入的组织
const loadOrganizations = async () => {
  if (!authStore.user) return;

  isLoading.value = true;
  try {
    const response = await organizationApi.getUserOrganizations(authStore.user.id);
    if (response.success && response.data) {
      organizations.value = response.data;
    }
  } catch (error) {
    console.error('加载组织列表失败:', error);
  } finally {
    isLoading.value = false;
  }
};

// 跳转到加入组织页面
const goToJoinOrganization = () => {
  router.push('/organizations/join');
};

// 格式化时间
const formatTime = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN');
};

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login');
    return;
  }
  await loadOrganizations();
});
</script>

<style scoped>
.organizations-view {
  min-height: 100vh;
  background: #f8fafc;
  padding: 2rem;
}

.organizations-container {
  width: 90%;
  max-width: 1000px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.header h1 {
  margin: 0;
  color: #2d3748;
  font-size: 1.5rem;
}

.join-org-btn {
  padding: 0.75rem 1.5rem;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.join-org-btn:hover {
  background: #3182ce;
}

.organizations-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.organization-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: box-shadow 0.2s;
}

.organization-card:hover {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.org-info {
  flex: 1;
}

.org-name {
  margin: 0 0 0.5rem 0;
  color: #2d3748;
  font-size: 1.125rem;
  font-weight: 600;
}

.org-description {
  margin: 0 0 0.75rem 0;
  color: #718096;
  line-height: 1.5;
}

.org-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #a0aec0;
}

.org-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.invite-code {
  padding: 0.5rem 0.75rem;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #4a5568;
  font-family: monospace;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #718096;
}

.empty-state p {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
}

.join-first-btn {
  padding: 0.75rem 1.5rem;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.join-first-btn:hover {
  background: #3182ce;
}
</style>
