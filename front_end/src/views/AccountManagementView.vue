<template>
  <div class="account-management-view">
    <div class="account-management-container">
      <!-- 用户信息部分 -->
      <div class="user-info-section">
        <div class="section-header">
          <h2>账号信息</h2>
        </div>
        <div class="user-info-card">
          <div class="user-details">
            <div class="user-field">
              <span class="field-label">用户名:</span>
              <span class="field-value">{{ authStore.user?.username }}</span>
              <button class="edit-btn" @click="showEditUsernameModal">修改</button>
            </div>
            <div class="user-field">
              <span class="field-label">邮箱:</span>
              <span class="field-value">{{ authStore.user?.email }}</span>
              <span class="field-note">（邮箱不可修改）</span>
            </div>
            <div class="user-field">
              <span class="field-label">密码:</span>
              <span class="field-value">********</span>
              <button class="edit-btn" @click="showChangePasswordModal">修改密码</button>
            </div>
            <div class="user-field">
              <span class="field-label">账号操作:</span>
              <button class="delete-btn" @click="showDeleteAccountModal">注销账号</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 组织管理部分 -->
      <div class="organizations-section">
        <div class="section-header">
          <h2>组织管理</h2>
          <div class="section-actions">
            <button class="create-org-btn" @click="showCreateOrganizationModal">
              + 创建新组织
            </button>
            <button class="join-org-btn" @click="goToJoinOrganization">
              + 加入新组织
            </button>
          </div>
        </div>

        <!-- 我创建的组织 -->
        <div class="organizations-subsection">
          <h3>我创建的组织</h3>
          <div class="organizations-list">
            <div
              v-for="organization in createdOrganizations"
              :key="organization.id"
              class="organization-card"
              @click="goToOrganization(organization)"
            >
              <div class="org-info">
                <h4 class="org-name">{{ organization.name }}</h4>
                <p class="org-description" v-if="organization.description">
                  {{ organization.description }}
                </p>
                <div class="org-meta">
                  <span class="org-members">
                    {{ organization.member_count }} 名成员
                  </span>
                  <span class="org-created">
                    创建于 {{ formatTime(organization.created_at) }}
                  </span>
                </div>
              </div>
              <div class="org-actions">
                <span class="invite-code">邀请码: {{ organization.invite_code }}</span>
                <div class="action-buttons">
                  <button
                    class="rename-btn"
                    @click.stop="showRenameOrganizationModal(organization)"
                    title="重命名组织"
                  >
                    ✏️
                  </button>
                  <button
                    class="delete-btn"
                    @click.stop="showDeleteOrganizationModal(organization)"
                    title="解散组织"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </div>

            <div v-if="createdOrganizations.length === 0" class="empty-state">
              <p>您还没有创建任何组织</p>
              <button class="create-first-btn" @click="showCreateOrganizationModal">
                创建第一个组织
              </button>
            </div>
          </div>
        </div>

        <!-- 我加入的组织 -->
        <div class="organizations-subsection">
          <h3>我加入的组织</h3>
          <div class="organizations-list">
            <div
              v-for="organization in joinedOrganizations"
              :key="organization.id"
              class="organization-card"
              @click="goToOrganization(organization)"
            >
              <div class="org-info">
                <h4 class="org-name">{{ organization.name }}</h4>
                <p class="org-description" v-if="organization.description">
                  {{ organization.description }}
                </p>
                <div class="org-meta">
                  <span class="org-members">
                    {{ organization.member_count }} 名成员
                  </span>
                  <span class="org-created">
                    创建于 {{ formatTime(organization.created_at) }}
                  </span>
                </div>
              </div>
              <div class="org-actions">
                <span class="invite-code">邀请码: {{ organization.invite_code }}</span>
                <button
                  class="leave-btn"
                  @click.stop="showLeaveOrganizationModal(organization)"
                  title="离开组织"
                >
                  离开
                </button>
              </div>
            </div>

            <div v-if="joinedOrganizations.length === 0" class="empty-state">
              <p>您还没有加入任何组织</p>
              <button class="join-first-btn" @click="goToJoinOrganization">
                立即加入组织
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 模态框 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <!-- 创建组织模态框 -->
        <div v-if="modalType === 'createOrganization'" class="modal">
          <h3>创建新组织</h3>
          <form @submit.prevent="createOrganization">
            <div class="form-group">
              <label for="org-name">组织名称</label>
              <input
                id="org-name"
                v-model="newOrganization.name"
                type="text"
                required
                placeholder="请输入组织名称"
              />
            </div>
            <div class="form-group">
              <label for="org-description">组织描述（可选）</label>
              <textarea
                id="org-description"
                v-model="newOrganization.description"
                placeholder="请输入组织描述"
                rows="3"
              ></textarea>
            </div>
            <div class="modal-actions">
              <button type="button" @click="closeModal">取消</button>
              <button type="submit" :disabled="isLoading">
                {{ isLoading ? '创建中...' : '创建' }}
              </button>
            </div>
          </form>
        </div>

        <!-- 重命名组织模态框 -->
        <div v-if="modalType === 'renameOrganization'" class="modal">
          <h3>重命名组织</h3>
          <form @submit.prevent="renameOrganization">
            <div class="form-group">
              <label for="rename-org-name">组织名称</label>
              <input
                id="rename-org-name"
                v-model="editingOrganization.name"
                type="text"
                required
                placeholder="请输入新的组织名称"
              />
            </div>
            <div class="form-group">
              <label for="rename-org-description">组织描述（可选）</label>
              <textarea
                id="rename-org-description"
                v-model="editingOrganization.description"
                placeholder="请输入新的组织描述"
                rows="3"
              ></textarea>
            </div>
            <div class="modal-actions">
              <button type="button" @click="closeModal">取消</button>
              <button type="submit" :disabled="isLoading">
                {{ isLoading ? '更新中...' : '更新' }}
              </button>
            </div>
          </form>
        </div>

        <!-- 修改用户名模态框 -->
        <div v-if="modalType === 'editUsername'" class="modal">
          <h3>修改用户名</h3>
          <form @submit.prevent="updateUsername">
            <div class="form-group">
              <label for="new-username">新用户名</label>
              <input
                id="new-username"
                v-model="newUsername"
                type="text"
                required
                placeholder="请输入新的用户名"
              />
            </div>
            <div class="modal-actions">
              <button type="button" @click="closeModal">取消</button>
              <button type="submit" :disabled="isLoading">
                {{ isLoading ? '更新中...' : '更新' }}
              </button>
            </div>
          </form>
        </div>

        <!-- 修改密码模态框 -->
        <div v-if="modalType === 'changePassword'" class="modal">
          <h3>修改密码</h3>
          <form @submit.prevent="changePassword">
            <div class="form-group">
              <label for="current-password">当前密码</label>
              <input
                id="current-password"
                v-model="passwordData.currentPassword"
                type="password"
                required
                placeholder="请输入当前密码"
              />
            </div>
            <div class="form-group">
              <label for="new-password">新密码</label>
              <input
                id="new-password"
                v-model="passwordData.newPassword"
                type="password"
                required
                placeholder="请输入新密码"
                minlength="6"
              />
            </div>
            <div class="form-group">
              <label for="confirm-password">确认新密码</label>
              <input
                id="confirm-password"
                v-model="passwordData.confirmPassword"
                type="password"
                required
                placeholder="请再次输入新密码"
                minlength="6"
              />
            </div>
            
            <!-- 错误消息显示 -->
            <div v-if="errorMessage" class="error-message">
              {{ errorMessage }}
            </div>
            
            <div class="modal-actions">
              <button type="button" @click="closeModal">取消</button>
              <button type="submit" :disabled="isLoading">
                {{ isLoading ? '更新中...' : '更新' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 确认对话框 -->
    <div v-if="showConfirmDialog" class="modal-overlay" @click="closeConfirmDialog">
      <div class="modal-content confirm-dialog" @click.stop>
        <h3>{{ confirmDialogTitle }}</h3>
        <p>{{ confirmDialogMessage }}</p>
        <div class="dialog-actions">
          <button @click="closeConfirmDialog">取消</button>
          <button @click="handleConfirm" class="danger">
            {{ confirmDialogAction === 'deleteOrganization' ? '解散' : '离开' }}
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
import { organizationApi, authApi } from '@/services/api';
import type { Organization, OrganizationCreateRequest, OrganizationUpdateRequest } from '@/types/api';

const router = useRouter();
const authStore = useAuthStore();

const organizations = ref<Organization[]>([]);
const isLoading = ref(false);
const showModal = ref(false);
const showConfirmDialog = ref(false);
const modalType = ref('');
const confirmDialogTitle = ref('');
const confirmDialogMessage = ref('');
const confirmDialogAction = ref('');
const selectedOrganization = ref<Organization | null>(null);

// 表单数据
const newOrganization = ref<OrganizationCreateRequest>({
  name: '',
  description: '',
  user_id: authStore.user?.id || 0
});

const editingOrganization = ref<OrganizationUpdateRequest>({
  name: '',
  description: '',
  user_id: authStore.user?.id || 0
});

const newUsername = ref('');
const passwordData = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});
const errorMessage = ref('');

// 计算属性：我创建的组织和我加入的组织
const createdOrganizations = computed(() => 
  organizations.value.filter(org => org.is_creator)
);

const joinedOrganizations = computed(() => 
  organizations.value.filter(org => !org.is_creator)
);

// 加载用户组织
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

// 创建组织
const createOrganization = async () => {
  if (!authStore.user) return;

  isLoading.value = true;
  try {
    const createData = {
      ...newOrganization.value,
      user_id: authStore.user.id
    };
    const response = await organizationApi.createOrganization(createData);
    console.log("在createOrganization中，response的值为", response.data);
    if (response.success) {
      await loadOrganizations();
      closeModal();
      newOrganization.value = { name: '', description: '', user_id: authStore.user.id };
    }
  } catch (error) {
    console.error('创建组织失败:', error);
  } finally {
    isLoading.value = false;
  }
};

// 重命名组织
const renameOrganization = async () => {
  if (!selectedOrganization.value || !authStore.user) return;

  isLoading.value = true;
  try {
    const updateData = {
      ...editingOrganization.value,
      user_id: authStore.user.id
    };
    const response = await organizationApi.updateOrganization(
      selectedOrganization.value.id,
      updateData
    );
    if (response.success && response.data) {
      await loadOrganizations();
      closeModal();
    }
  } catch (error) {
    console.error('重命名组织失败:', error);
  } finally {
    isLoading.value = false;
  }
};

// 解散组织
const deleteOrganization = async () => {
  if (!selectedOrganization.value || !authStore.user) return;

  isLoading.value = true;
  try {
    const response = await organizationApi.deleteOrganization(
      selectedOrganization.value.id,
      authStore.user.id
    );
    if (response.success) {
      await loadOrganizations();
      closeConfirmDialog();
    }
  } catch (error) {
    console.error('解散组织失败:', error);
  } finally {
    isLoading.value = false;
  }
};

// 离开组织
const leaveOrganization = async () => {
  if (!selectedOrganization.value || !authStore.user) return;

  isLoading.value = true;
  try {
    const response = await organizationApi.leaveOrganization(
      selectedOrganization.value.id,
      authStore.user.id
    );
    if (response.success) {
      await loadOrganizations();
      closeConfirmDialog();
    }
  } catch (error) {
    console.error('离开组织失败:', error);
  } finally {
    isLoading.value = false;
  }
};

// 注销账号
const deleteAccount = async () => {
  if (!authStore.user) return;

  isLoading.value = true;
  try {
    const response = await authApi.deleteAccount(authStore.user.id);
    if (response.success) {
      // 注销成功后退出登录并跳转到登录页面
      await authStore.logout();
      closeConfirmDialog();
      router.push('/login');
    }
  } catch (error) {
    console.error('注销账号失败:', error);
  } finally {
    isLoading.value = false;
  }
};

// 模态框操作
const showCreateOrganizationModal = () => {
  modalType.value = 'createOrganization';
  showModal.value = true;
};

const showRenameOrganizationModal = (organization: Organization) => {
  selectedOrganization.value = organization;
  editingOrganization.value = {
    name: organization.name,
    description: organization.description || '',
    user_id: authStore.user?.id || 0
  };
  modalType.value = 'renameOrganization';
  showModal.value = true;
};

const showEditUsernameModal = () => {
  newUsername.value = authStore.user?.username || '';
  modalType.value = 'editUsername';
  showModal.value = true;
};

const showChangePasswordModal = () => {
  passwordData.value = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  };
  errorMessage.value = ''; // 清空错误消息
  modalType.value = 'changePassword';
  showModal.value = true;
};

const showDeleteOrganizationModal = (organization: Organization) => {
  selectedOrganization.value = organization;
  confirmDialogTitle.value = '解散组织';
  confirmDialogMessage.value = `确定要解散组织 "${organization.name}" 吗？此操作将删除该组织的所有数据，且不可恢复。`;
  confirmDialogAction.value = 'deleteOrganization';
  showConfirmDialog.value = true;
};

const showLeaveOrganizationModal = (organization: Organization) => {
  selectedOrganization.value = organization;
  confirmDialogTitle.value = '离开组织';
  confirmDialogMessage.value = `确定要离开组织 "${organization.name}" 吗？`;
  confirmDialogAction.value = 'leaveOrganization';
  showConfirmDialog.value = true;
};

const showDeleteAccountModal = () => {
  confirmDialogTitle.value = '注销账号';
  confirmDialogMessage.value = '确定要注销您的账号吗？此操作将删除您的所有数据，且不可恢复。';
  confirmDialogAction.value = 'deleteAccount';
  showConfirmDialog.value = true;
};

const closeModal = () => {
  showModal.value = false;
  modalType.value = '';
  selectedOrganization.value = null;
};

const closeConfirmDialog = () => {
  showConfirmDialog.value = false;
  confirmDialogTitle.value = '';
  confirmDialogMessage.value = '';
  confirmDialogAction.value = '';
  selectedOrganization.value = null;
};

const handleConfirm = () => {
  if (confirmDialogAction.value === 'deleteOrganization') {
    deleteOrganization();
  } else if (confirmDialogAction.value === 'leaveOrganization') {
    leaveOrganization();
  } else if (confirmDialogAction.value === 'deleteAccount') {
    deleteAccount();
  }
};

// 跳转到组织页面
const goToOrganization = (organization: Organization) => {
  // 设置当前组织并跳转到主界面
  const organizationStore = useOrganizationStore();
  organizationStore.setCurrentOrganization(organization);
  router.push('/');
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

// 修改用户名
const updateUsername = async () => {
  if (!authStore.user) return;

  isLoading.value = true;
  try {
    const response = await authApi.updateUsername(
      authStore.user.id,
      passwordData.value.currentPassword,
      newUsername.value
    );
    
    if (response.success) {
      // 更新本地存储的用户信息
      if (response.data) {
        authStore.setUser(response.data);
      }
      closeModal();
      // 清空表单数据
      newUsername.value = '';
      passwordData.value.currentPassword = '';
    } else {
      console.error('修改用户名失败:', response.message);
    }
  } catch (error) {
    console.error('修改用户名失败:', error);
  } finally {
    isLoading.value = false;
  }
};

// 修改密码
const changePassword = async () => {
  if (!authStore.user) return;

  // 清空之前的错误信息
  errorMessage.value = '';

  // 验证新密码和确认密码是否一致
  if (passwordData.value.newPassword !== passwordData.value.confirmPassword) {
    errorMessage.value = '新密码和确认密码不一致';
    return;
  }

  // 验证密码长度
  if (passwordData.value.newPassword.length < 6) {
    errorMessage.value = '新密码长度不能少于6位';
    return;
  }

  isLoading.value = true;
  try {
    const response = await authApi.updatePassword(
      authStore.user.id,
      passwordData.value.currentPassword,
      passwordData.value.newPassword
    );
    
    if (response.success) {
      closeModal();
      // 清空表单数据
      passwordData.value = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      };
      // 显示成功消息
      alert('密码修改成功！');
    } else {
      // 根据后端返回的错误信息显示相应的提示
      if (response.message?.includes('原密码不正确')) {
        errorMessage.value = '当前密码不正确';
      } else {
        errorMessage.value = response.message || '修改密码失败，请重试';
      }
    }
  } catch (error) {
    console.error('修改密码失败:', error);
    errorMessage.value = '修改密码失败，请检查网络连接后重试';
  } finally {
    isLoading.value = false;
  }
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
.account-management-view {
  width: 800px;
  min-height: 100vh;
  background: #f8fafc;
  padding: 2rem;
}

.account-management-container {
  max-width: 1200px;
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

.section-actions {
  display: flex;
  gap: 0.5rem;
}

.user-info-card {
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.user-field {
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

.field-note {
  color: #718096;
  font-size: 0.875rem;
}

.edit-btn {
  padding: 0.25rem 0.5rem;
  background: #e2e8f0;
  color: #4a5568;
  border: none;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
}

.edit-btn:hover {
  background: #cbd5e0;
}

.organizations-subsection {
  margin-bottom: 2rem;
}

.organizations-subsection h3 {
  margin: 0 0 1rem 0;
  color: #2d3748;
  font-size: 1.125rem;
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
  cursor: pointer;
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

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.rename-btn,
.delete-btn,
.leave-btn {
  padding: 0.5rem 0.75rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
}

.rename-btn {
  background: #e6fffa;
  color: #234e52;
}

.rename-btn:hover {
  background: #b2f5ea;
}

.delete-btn {
  background: #fed7d7;
  color: #742a2a;
}

.delete-btn:hover {
  background: #feb2b2;
}

.leave-btn {
  background: #e2e8f0;
  color: #4a5568;
}

.leave-btn:hover {
  background: #cbd5e0;
}

.create-org-btn,
.join-org-btn {
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
}

.create-org-btn {
  background: #48bb78;
  color: white;
}

.create-org-btn:hover {
  background: #38a169;
}

.join-org-btn {
  background: #4299e1;
  color: white;
}

.join-org-btn:hover {
  background: #3182ce;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #718096;
  border: 2px dashed #e2e8f0;
  border-radius: 8px;
}

.empty-state p {
  margin: 0 0 1rem 0;
}

.create-first-btn,
.join-first-btn {
  padding: 0.75rem 1.5rem;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
}

.create-first-btn:hover,
.join-first-btn:hover {
  background: #3182ce;
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
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal h3 {
  margin: 0 0 1.5rem 0;
  color: #2d3748;
  font-size: 1.25rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #2d3748;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.875rem;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 2px rgba(66, 153, 225, 0.1);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.modal-actions button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
}

.modal-actions button[type="button"] {
  background: #e2e8f0;
  color: #4a5568;
}

.modal-actions button[type="button"]:hover {
  background: #cbd5e0;
}

.modal-actions button[type="submit"] {
  background: #4299e1;
  color: white;
}

.modal-actions button[type="submit"]:hover:not(:disabled) {
  background: #3182ce;
}

.modal-actions button:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
}

/* 确认对话框样式 */
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

/* 错误消息样式 */
.error-message {
  color: #e53e3e;
  background-color: #fed7d7;
  border: 1px solid #feb2b2;
  border-radius: 6px;
  padding: 0.75rem;
  margin: 1rem 0;
  font-size: 0.875rem;
  text-align: center;
}
</style>
