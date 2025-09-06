<template>
  <div class="organization-management-view">
    <div class="organization-management-container">
      <!-- 组织信息部分 -->
      <div class="organization-info-section">
        <div class="section-header">
          <h2>组织管理 - {{ organizationStore.currentOrganization?.name }}</h2>
          <button class="back-btn" @click="goBack">
            ← 返回
          </button>
        </div>
        <div class="organization-info-card">
          <div class="organization-details">
            <div class="organization-field">
              <span class="field-label">组织名称:</span>
              <span class="field-value">{{ organizationStore.currentOrganization?.name }}</span>
            </div>
            <div class="organization-field" v-if="organizationStore.currentOrganization?.description">
              <span class="field-label">组织描述:</span>
              <span class="field-value">{{ organizationStore.currentOrganization?.description }}</span>
            </div>
            <div class="organization-field">
              <span class="field-label">邀请码:</span>
              <span class="field-value invite-code">{{ organizationStore.currentOrganization?.invite_code }}</span>
            </div>
            <div class="organization-field">
              <span class="field-label">创建时间:</span>
              <span class="field-value">{{ formatTime(organizationStore.currentOrganization?.created_at || '') }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 成员管理部分 -->
      <div class="members-section">
        <div class="section-header">
          <h2>成员管理</h2>
        </div>

        <!-- 创建者 -->
        <div class="members-subsection">
          <h3>创建者</h3>
          <div class="members-list">
            <div
              v-for="member in creatorMembers"
              :key="member.user_id"
              class="member-card"
            >
              <div class="member-info">
                <div class="member-avatar">
                  {{ member.username.charAt(0).toUpperCase() }}
                </div>
                <div class="member-details">
                  <h4 class="member-name">{{ member.username }}</h4>
                  <p class="member-email">{{ member.email }}</p>
                  <span class="member-role">创建者</span>
                </div>
              </div>
              <div class="member-meta">
                <span class="member-joined">
                  加入时间: {{ formatTime(member.joined_at) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 其他成员 -->
        <div class="members-subsection">
          <h3>其他成员</h3>
          <div class="members-list">
            <div
              v-for="member in otherMembers"
              :key="member.user_id"
              class="member-card"
            >
              <div class="member-info">
                <div class="member-avatar">
                  {{ member.username.charAt(0).toUpperCase() }}
                </div>
                <div class="member-details">
                  <h4 class="member-name">{{ member.username }}</h4>
                  <p class="member-email">{{ member.email }}</p>
                  <span class="member-role">成员</span>
                </div>
              </div>
              <div class="member-meta">
                <span class="member-joined">
                  加入时间: {{ formatTime(member.joined_at) }}
                </span>
                <button
                  v-if="isCreator"
                  class="remove-btn"
                  @click="showRemoveMemberModal(member)"
                  title="踢出成员"
                >
                  踢出
                </button>
              </div>
            </div>

            <div v-if="otherMembers.length === 0" class="empty-state">
              <p>该组织还没有其他成员</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 确认对话框 -->
    <div v-if="showConfirmDialog" class="modal-overlay" @click="closeConfirmDialog">
      <div class="modal-content confirm-dialog" @click.stop>
        <h3>踢出成员</h3>
        <p>确定要将成员 "{{ selectedMember?.username }}" 踢出组织吗？</p>
        <div class="dialog-actions">
          <button @click="closeConfirmDialog">取消</button>
          <button @click="removeMember" class="danger">
            确认踢出
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useOrganizationStore } from '@/stores/organization';
import { organizationApi } from '@/services/api';
import type { OrganizationMember } from '@/types/api';

const router = useRouter();
const authStore = useAuthStore();
const organizationStore = useOrganizationStore();

const members = ref<OrganizationMember[]>([]);
const isLoading = ref(false);
const showConfirmDialog = ref(false);
const selectedMember = ref<OrganizationMember | null>(null);

// 计算属性：是否为创建者
const isCreator = computed(() => {
  if (!organizationStore.currentOrganization) return false;
  return organizationStore.currentOrganization.is_creator;
});

// 计算属性：创建者成员和其他成员
const creatorMembers = computed(() => 
  members.value.filter(member => member.is_creator)
);

const otherMembers = computed(() => 
  members.value.filter(member => !member.is_creator)
);

// 加载组织成员
const loadOrganizationMembers = async () => {
  if (!organizationStore.currentOrganization || !authStore.user) return;

  isLoading.value = true;
  try {
    const response = await organizationApi.getOrganizationMembers(
      organizationStore.currentOrganization.id,
      authStore.user.id
    );
    if (response.success && response.data) {
      members.value = response.data;
    }
  } catch (error) {
    console.error('加载组织成员失败:', error);
  } finally {
    isLoading.value = false;
  }
};

// 踢出成员
const removeMember = async () => {
  if (!selectedMember.value || !organizationStore.currentOrganization || !authStore.user) return;

  isLoading.value = true;
  try {
    const response = await organizationApi.removeOrganizationMember(
      organizationStore.currentOrganization.id,
      selectedMember.value.user_id,
      authStore.user.id
    );
    if (response.success) {
      await loadOrganizationMembers();
      closeConfirmDialog();
    }
  } catch (error) {
    console.error('踢出成员失败:', error);
  } finally {
    isLoading.value = false;
  }
};

// 模态框操作
const showRemoveMemberModal = (member: OrganizationMember) => {
  selectedMember.value = member;
  showConfirmDialog.value = true;
};

const closeConfirmDialog = () => {
  showConfirmDialog.value = false;
  selectedMember.value = null;
};

// 返回
const goBack = () => {
  router.push('/');
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
  
  if (!organizationStore.currentOrganization) {
    router.push('/account-management');
    return;
  }

  await loadOrganizationMembers();
});
</script>

<style scoped>
.organization-management-view {
  min-height: 100vh;
  background: #f8fafc;
  padding: 2rem;
}

.organization-management-container {
  max-width: 1000px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.section-header h2 {
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
  font-size: 0.875rem;
  cursor: pointer;
}

.back-btn:hover {
  background: #cbd5e0;
}

.organization-info-card {
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.organization-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.organization-field {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.field-label {
  font-weight: 600;
  color: #2d3748;
  min-width: 80px;
}

.field-value {
  color: #4a5568;
  flex: 1;
}

.invite-code {
  font-family: monospace;
  background: #edf2f7;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}

.members-subsection {
  margin-bottom: 2rem;
}

.members-subsection h3 {
  margin: 0 0 1rem 0;
  color: #2d3748;
  font-size: 1.125rem;
}

.members-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.member-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fafafa;
}

.member-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.member-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #4299e1;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.125rem;
}

.member-details {
  flex: 1;
}

.member-name {
  margin: 0 0 0.25rem 0;
  color: #2d3748;
  font-size: 1rem;
  font-weight: 600;
}

.member-email {
  margin: 0 0 0.5rem 0;
  color: #718096;
  font-size: 0.875rem;
}

.member-role {
  padding: 0.25rem 0.5rem;
  background: #e6fffa;
  color: #234e52;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.member-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.member-joined {
  font-size: 0.875rem;
  color: #a0aec0;
}

.remove-btn {
  padding: 0.5rem 1rem;
  background: #fed7d7;
  color: #742a2a;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
}

.remove-btn:hover {
  background: #feb2b2;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #718096;
  border: 2px dashed #e2e8f0;
  border-radius: 8px;
}

.empty-state p {
  margin: 0;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  max-width: 400px;
  width: 90%;
}

.confirm-dialog {
  text-align: center;
}

.confirm-dialog h3 {
  margin: 0 0 1rem 0;
  color: #2d3748;
}

.confirm-dialog p {
  margin: 0 0 2rem 0;
  color: #718096;
  line-height: 1.5;
}

.dialog-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.dialog-actions button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
}

.dialog-actions button:first-child {
  background: #e2e8f0;
  color: #4a5568;
}

.dialog-actions button:first-child:hover {
  background: #cbd5e0;
}

.dialog-actions button.danger {
  background: #e53e3e;
  color: white;
}

.dialog-actions button.danger:hover {
  background: #c53030;
}
</style>
