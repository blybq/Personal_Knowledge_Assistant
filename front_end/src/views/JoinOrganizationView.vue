<template>
  <div class="join-org-view">
    <div class="join-org-container">
      <div class="header">
        <h1>加入组织</h1>
        <button class="back-btn" @click="goBack">
          ← 返回
        </button>
      </div>

      <div class="search-section">
        <div class="search-input">
          <label for="invite-code">输入邀请码</label>
          <input
            id="invite-code"
            v-model="inviteCode"
            type="text"
            placeholder="请输入组织邀请码"
            @keydown.enter="searchOrganization"
          />
          <button
            class="search-btn"
            @click="searchOrganization"
            :disabled="!inviteCode.trim() || isSearching"
          >
            {{ isSearching ? '搜索中...' : '搜索' }}
          </button>
        </div>

        <div v-if="searchError" class="error-message">
          {{ searchError }}
        </div>
      </div>

      <div v-if="searchedOrganization" class="organization-result">
        <div class="org-card">
          <h3>找到的组织</h3>
          <div class="org-details">
            <div class="org-field">
              <span class="field-label">组织名称:</span>
              <span class="field-value">{{ searchedOrganization.name }}</span>
            </div>
            <div class="org-field" v-if="searchedOrganization.description">
              <span class="field-label">描述:</span>
              <span class="field-value">{{ searchedOrganization.description }}</span>
            </div>
            <div class="org-field">
              <span class="field-label">成员数量:</span>
              <span class="field-value">{{ searchedOrganization.member_count || 0 }} 名成员</span>
            </div>
            <div class="org-field">
              <span class="field-label">创建时间:</span>
              <span class="field-value">{{ formatTime(searchedOrganization.created_at) }}</span>
            </div>
          </div>
          
          <button
            class="join-btn"
            @click="joinOrganization"
            :disabled="isJoining"
          >
            {{ isJoining ? '加入中...' : '加入组织' }}
          </button>
        </div>
      </div>

      <div v-else-if="hasSearched && !searchedOrganization" class="no-result">
        <p>未找到对应的组织，请检查邀请码是否正确</p>
      </div>

      <div v-if="joinSuccess" class="success-message">
        <p>成功加入组织！</p>
        <button class="continue-btn" @click="goToOrganizations">
          查看我的组织
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { organizationApi } from '@/services/api';
import type { Organization } from '@/types/api';

const router = useRouter();
const authStore = useAuthStore();

const inviteCode = ref('');
const searchedOrganization = ref<Organization | null>(null);
const isSearching = ref(false);
const isJoining = ref(false);
const hasSearched = ref(false);
const searchError = ref('');
const joinSuccess = ref(false);

// 搜索组织
const searchOrganization = async () => {
  if (!inviteCode.value.trim() || !authStore.user) return;

  isSearching.value = true;
  searchError.value = '';
  hasSearched.value = true;

  try {
    const response = await organizationApi.searchOrganization(inviteCode.value.trim());
    if (response.success && response.data) {
      searchedOrganization.value = response.data;
    } else {
      searchedOrganization.value = null;
      searchError.value = response.message || '未找到组织';
    }
  } catch (error: any) {
    searchedOrganization.value = null;
    searchError.value = error.response?.data?.message || '搜索失败';
    console.error('搜索组织失败:', error);
  } finally {
    isSearching.value = false;
  }
};

// 加入组织
const joinOrganization = async () => {
  if (!searchedOrganization.value || !authStore.user) return;

  isJoining.value = true;
  try {
    const response = await organizationApi.joinOrganization({
      invite_code: searchedOrganization.value.invite_code,
      user_id: authStore.user.id
    });

    if (response.success) {
      joinSuccess.value = true;
      // 可以在这里添加一些成功加入后的处理，比如显示成功消息
    } else {
      searchError.value = response.message || '加入组织失败';
    }
  } catch (error: any) {
    searchError.value = error.response?.data?.message || '加入组织失败';
    console.error('加入组织失败:', error);
  } finally {
    isJoining.value = false;
  }
};

// 返回上一页
const goBack = () => {
  router.push('/account-management');
};

// 跳转到组织列表
const goToOrganizations = () => {
  router.push('/account-management');
};

// 格式化时间
const formatTime = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN');
};
</script>

<style scoped>
.join-org-view {
  min-height: 100vh;
  background: #f8fafc;
  padding: 2rem;
}

.join-org-container {
  max-width: 600px;
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

.back-btn {
  padding: 0.5rem 1rem;
  background: #e2e8f0;
  color: #4a5568;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.back-btn:hover {
  background: #cbd5e0;
}

.search-section {
  margin-bottom: 2rem;
}

.search-input {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.search-input label {
  font-weight: 500;
  color: #2d3748;
}

.search-input input {
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.search-input input:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 2px rgba(66, 153, 225, 0.1);
}

.search-btn {
  padding: 0.75rem;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.search-btn:hover:not(:disabled) {
  background: #3182ce;
}

.search-btn:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
}

.error-message {
  color: #e53e3e;
  text-align: center;
  padding: 0.5rem;
  background: #fed7d7;
  border: 1px solid #feb2b2;
  border-radius: 6px;
}

.organization-result {
  margin-bottom: 2rem;
}

.org-card {
  padding: 1.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
}

.org-card h3 {
  margin: 0 0 1rem 0;
  color: #2d3748;
  font-size: 1.125rem;
}

.org-details {
  margin-bottom: 1.5rem;
}

.org-field {
  display: flex;
  margin-bottom: 0.75rem;
}

.field-label {
  font-weight: 600;
  color: #4a5568;
  min-width: 80px;
}

.field-value {
  color: #2d3748;
  flex: 1;
}

.join-btn {
  width: 100%;
  padding: 0.75rem;
  background: #48bb78;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.join-btn:hover:not(:disabled) {
  background: #38a169;
}

.join-btn:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
}

.no-result {
  text-align: center;
  padding: 2rem;
  color: #718096;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.success-message {
  text-align: center;
  padding: 2rem;
  background: #f0fff4;
  border: 1px solid #9ae6b4;
  border-radius: 8px;
  color: #2f855a;
}

.success-message p {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
}

.continue-btn {
  padding: 0.75rem 1.5rem;
  background: #48bb78;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.continue-btn:hover {
  background: #38a169;
}
</style>
