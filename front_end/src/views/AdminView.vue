<template>
  <div class="admin-view">
    <div class="admin-container">
      <!-- 管理员导航 -->
      <div class="admin-nav">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          :class="['nav-btn', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- 用户管理 -->
      <div v-if="activeTab === 'users'" class="admin-section">
        <div class="section-header">
          <h2>用户管理</h2>
          <div class="search-box">
            <input 
              v-model="userSearch" 
              type="text" 
              placeholder="搜索用户名或邮箱..."
              @input="searchUsers"
            />
          </div>
        </div>

        <div class="table-container">
          <table class="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>用户名</th>
                <th>邮箱</th>
                <th>注册时间</th>
                <th>管理员</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.email }}</td>
                <td>{{ formatTime(user.created_at) }}</td>
                <td>
                  <span :class="['badge', user.is_admin ? 'admin' : 'user']">
                    {{ user.is_admin ? '是' : '否' }}
                  </span>
                </td>
                <td>
                  <span :class="['badge', user.is_banned ? 'banned' : 'active']">
                    {{ user.is_banned ? '封禁' : '正常' }}
                  </span>
                </td>
                <td class="actions">
                  <button 
                    class="btn-view" 
                    @click="viewUserDetails(user.id)"
                    title="查看详情"
                  >
                    👁️
                  </button>
                  <button 
                    v-if="!user.is_banned" 
                    class="btn-ban" 
                    @click="showBanModal(user)"
                    title="封禁用户"
                  >
                    🚫
                  </button>
                  <button 
                    v-if="user.is_banned" 
                    class="btn-unban" 
                    @click="showUnbanModal(user)"
                    title="解封用户"
                  >
                    ✅
                  </button>
                  <button 
                    class="btn-delete" 
                    @click="showDeleteUserModal(user)"
                    title="删除用户"
                  >
                    🗑️
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- 分页控件 -->
          <div v-if="usersPagination.total_pages > 1" class="pagination">
            <button 
              :disabled="usersPagination.page === 1"
              @click="loadUsers(usersPagination.page - 1)"
            >
              上一页
            </button>
            <span>第 {{ usersPagination.page }} 页 / 共 {{ usersPagination.total_pages }} 页</span>
            <button 
              :disabled="usersPagination.page === usersPagination.total_pages"
              @click="loadUsers(usersPagination.page + 1)"
            >
              下一页
            </button>
          </div>
        </div>
      </div>

      <!-- 组织管理 -->
      <div v-if="activeTab === 'organizations'" class="admin-section">
        <div class="section-header">
          <h2>组织管理</h2>
          <div class="search-box">
            <input 
              v-model="orgSearch" 
              type="text" 
              placeholder="搜索组织名称..."
              @input="searchOrganizations"
            />
          </div>
        </div>

        <div class="table-container">
          <table class="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>组织名称</th>
                <th>描述</th>
                <th>创建者</th>
                <th>成员数</th>
                <th>创建时间</th>
                <th>邀请码</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="org in filteredOrganizations" :key="org.id">
                <td>{{ org.id }}</td>
                <td>{{ org.name }}</td>
                <td>{{ org.description || '无描述' }}</td>
                <td>{{ org.creator_name }}</td>
                <td>{{ org.member_count }}</td>
                <td>{{ formatTime(org.created_at) }}</td>
                <td class="invite-code">{{ org.invite_code }}</td>
                <td class="actions">
                  <button 
                    class="btn-view" 
                    @click="viewOrganizationDetails(org.id)"
                    title="查看详情"
                  >
                    👁️
                  </button>
                  <button 
                    class="btn-delete" 
                    @click="showDeleteOrgModal(org)"
                    title="解散组织"
                  >
                    🗑️
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- 分页控件 -->
          <div v-if="orgsPagination.total_pages > 1" class="pagination">
            <button 
              :disabled="orgsPagination.page === 1"
              @click="loadOrganizations(orgsPagination.page - 1)"
            >
              上一页
            </button>
            <span>第 {{ orgsPagination.page }} 页 / 共 {{ orgsPagination.total_pages }} 页</span>
            <button 
              :disabled="orgsPagination.page === orgsPagination.total_pages"
              @click="loadOrganizations(orgsPagination.page + 1)"
            >
              下一页
            </button>
          </div>
        </div>
      </div>

      <!-- 操作日志 -->
      <div v-if="activeTab === 'operations'" class="admin-section">
        <div class="section-header">
          <h2>操作日志</h2>
        </div>

        <div class="table-container">
          <table class="admin-table">
            <thead>
              <tr>
                <th>操作ID</th>
                <th>管理员</th>
                <th>目标类型</th>
                <th>目标ID</th>
                <th>操作类型</th>
                <th>操作详情</th>
                <th>操作时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="op in operations" :key="op.id">
                <td>{{ op.id }}</td>
                <td>{{ op.admin_username }}</td>
                <td>{{ op.target_type }}</td>
                <td>{{ op.target_id }}</td>
                <td>{{ op.operation_type }}</td>
                <td>{{ op.operation_details }}</td>
                <td>{{ formatTime(op.created_at) }}</td>
              </tr>
            </tbody>
          </table>

          <!-- 分页控件 -->
          <div v-if="opsPagination.total_pages > 1" class="pagination">
            <button 
              :disabled="opsPagination.page === 1"
              @click="loadOperations(opsPagination.page - 1)"
            >
              上一页
            </button>
            <span>第 {{ opsPagination.page }} 页 / 共 {{ opsPagination.total_pages }} 页</span>
            <button 
              :disabled="opsPagination.page === opsPagination.total_pages"
              @click="loadOperations(opsPagination.page + 1)"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 模态框 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <!-- 封禁用户模态框 -->
        <div v-if="modalType === 'banUser'" class="modal">
          <h3>封禁用户</h3>
          <p>确定要封禁用户 "{{ selectedUser?.username }}" 吗？</p>
          <div class="form-group">
            <label for="ban-reason">封禁原因（可选）</label>
            <textarea
              id="ban-reason"
              v-model="banReason"
              placeholder="请输入封禁原因"
              rows="3"
            ></textarea>
          </div>
          <div class="modal-actions">
            <button @click="closeModal">取消</button>
            <button @click="banUser" class="danger">确认封禁</button>
          </div>
        </div>

        <!-- 解封用户模态框 -->
        <div v-if="modalType === 'unbanUser'" class="modal">
          <h3>解封用户</h3>
          <p>确定要解封用户 "{{ selectedUser?.username }}" 吗？</p>
          <div class="form-group">
            <label for="unban-reason">解封原因（可选）</label>
            <textarea
              id="unban-reason"
              v-model="unbanReason"
              placeholder="请输入解封原因"
              rows="3"
            ></textarea>
          </div>
          <div class="modal-actions">
            <button @click="closeModal">取消</button>
            <button @click="unbanUser" class="success">确认解封</button>
          </div>
        </div>

        <!-- 删除用户模态框 -->
        <div v-if="modalType === 'deleteUser'" class="modal">
          <h3>删除用户</h3>
          <p>确定要删除用户 "{{ selectedUser?.username }}" 吗？此操作将永久删除该用户的所有数据！</p>
          <div class="form-group">
            <label for="delete-reason">删除原因（可选）</label>
            <textarea
              id="delete-reason"
              v-model="deleteReason"
              placeholder="请输入删除原因"
              rows="3"
            ></textarea>
          </div>
          <div class="modal-actions">
            <button @click="closeModal">取消</button>
            <button @click="deleteUser" class="danger">确认删除</button>
          </div>
        </div>

        <!-- 解散组织模态框 -->
        <div v-if="modalType === 'deleteOrg'" class="modal">
          <h3>解散组织</h3>
          <p>确定要解散组织 "{{ selectedOrg?.name }}" 吗？此操作将永久删除该组织的所有数据！</p>
          <div class="form-group">
            <label for="delete-org-reason">解散原因（可选）</label>
            <textarea
              id="delete-org-reason"
              v-model="deleteOrgReason"
              placeholder="请输入解散原因"
              rows="3"
            ></textarea>
          </div>
          <div class="modal-actions">
            <button @click="closeModal">取消</button>
            <button @click="deleteOrganization" class="danger">确认解散</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 详情模态框 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content detail-modal" @click.stop>
        <!-- 用户详情模态框 -->
        <div v-if="detailType === 'user'" class="modal">
          <h3>用户详情 - {{ userDetails?.user?.username }}</h3>
          <div class="detail-content">
            <div class="detail-section">
              <h4>基本信息</h4>
              <p><strong>ID:</strong> {{ userDetails?.user?.id }}</p>
              <p><strong>邮箱:</strong> {{ userDetails?.user?.email }}</p>
              <p><strong>注册时间:</strong> {{ formatTime(userDetails?.user?.created_at) }}</p>
              <p><strong>状态:</strong> {{ userDetails?.user?.is_banned ? '封禁' : '正常' }}</p>
              <p><strong>管理员:</strong> {{ userDetails?.user?.is_admin ? '是' : '否' }}</p>
            </div>

            <div class="detail-section">
              <h4>对话记录</h4>
              <p>共 {{ userDetails?.conversations?.length || 0 }} 个对话</p>
              <ul v-if="userDetails?.conversations?.length">
                <li v-for="conv in userDetails.conversations" :key="conv.id">
                  {{ conv.title }} (创建于: {{ formatTime(conv.created_at) }})
                </li>
              </ul>
            </div>

            <div class="detail-section">
              <h4>笔记文件夹</h4>
              <p>共 {{ userDetails?.folders?.length || 0 }} 个文件夹</p>
              <ul v-if="userDetails?.folders?.length">
                <li v-for="folder in userDetails.folders" :key="folder.id">
                  {{ folder.name }} ({{ userDetails.folder_notes[folder.id] || 0 }} 个笔记)
                </li>
              </ul>
            </div>

            <div class="detail-section">
              <h4>加入的组织</h4>
              <p>共 {{ userDetails?.organizations?.length || 0 }} 个组织</p>
              <ul v-if="userDetails?.organizations?.length">
                <li v-for="(org, isCreator) in userDetails.organizations" :key="org.id">
                  {{ org.name }} ({{ isCreator ? '创建者' : '成员' }})
                </li>
              </ul>
            </div>
          </div>
          <div class="modal-actions">
            <button @click="closeDetailModal">关闭</button>
          </div>
        </div>

        <!-- 组织详情模态框 -->
        <div v-if="detailType === 'organization'" class="modal">
          <h3>组织详情 - {{ orgDetails?.organization?.name }}</h3>
          <div class="detail-content">
            <div class="detail-section">
              <h4>基本信息</h4>
              <p><strong>ID:</strong> {{ orgDetails?.organization?.id }}</p>
              <p><strong>描述:</strong> {{ orgDetails?.organization?.description || '无描述' }}</p>
              <p><strong>邀请码:</strong> {{ orgDetails?.organization?.invite_code }}</p>
              <p><strong>创建时间:</strong> {{ formatTime(orgDetails?.organization?.created_at) }}</p>
            </div>

            <div class="detail-section">
              <h4>成员列表 ({{ orgDetails?.members?.length || 0 }} 人)</h4>
              <ul v-if="orgDetails?.members?.length">
                <li v-for="(member, isCreator) in orgDetails.members" :key="member.id">
                  {{ member.username }} ({{ isCreator ? '创建者' : '成员' }})
                </li>
              </ul>
            </div>

            <div class="detail-section">
              <h4>对话记录</h4>
              <p>共 {{ orgDetails?.conversations?.length || 0 }} 个对话</p>
              <ul v-if="orgDetails?.conversations?.length">
                <li v-for="conv in orgDetails.conversations" :key="conv.id">
                  {{ conv.title }} (创建于: {{ formatTime(conv.created_at) }})
                </li>
              </ul>
            </div>

            <div class="detail-section">
              <h4>笔记文件夹</h4>
              <p>共 {{ orgDetails?.folders?.length || 0 }} 个文件夹</p>
              <ul v-if="orgDetails?.folders?.length">
                <li v-for="folder in orgDetails.folders" :key="folder.id">
                  {{ folder.name }} ({{ orgDetails.folder_notes[folder.id] || 0 }} 个笔记)
                </li>
              </ul>
            </div>
          </div>
          <div class="modal-actions">
            <button @click="closeDetailModal">关闭</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { adminApi } from '@/services/api';
import type { User, Organization } from '@/types/api';

const router = useRouter();
const authStore = useAuthStore();

// 导航标签
const tabs = ref([
  { id: 'users', label: '用户管理' },
  { id: 'organizations', label: '组织管理' },
  { id: 'operations', label: '操作日志' }
]);
const activeTab = ref('users');

// 用户管理相关
const users = ref<User[]>([]);
const userSearch = ref('');
const usersPagination = ref({
  page: 1,
  page_size: 20,
  total_count: 0,
  total_pages: 0
});

// 组织管理相关
const organizations = ref<any[]>([]);
const orgSearch = ref('');
const orgsPagination = ref({
  page: 1,
  page_size: 20,
  total_count: 0,
  total_pages: 0
});

// 操作日志相关
const operations = ref<any[]>([]);
const opsPagination = ref({
  page: 1,
  page_size: 20,
  total_count: 0,
  total_pages: 0
});

// 模态框相关
const showModal = ref(false);
const showDetailModal = ref(false);
const modalType = ref('');
const detailType = ref('');
const selectedUser = ref<User | null>(null);
const selectedOrg = ref<any>(null);
const userDetails = ref<any>(null);
const orgDetails = ref<any>(null);

// 表单数据
const banReason = ref('');
const unbanReason = ref('');
const deleteReason = ref('');
const deleteOrgReason = ref('');

// 计算属性：过滤后的用户和组织
const filteredUsers = computed(() => {
  if (!userSearch.value) return users.value;
  const search = userSearch.value.toLowerCase();
  return users.value.filter(user => 
    user.username.toLowerCase().includes(search) ||
    user.email.toLowerCase().includes(search)
  );
});

const filteredOrganizations = computed(() => {
  if (!orgSearch.value) return organizations.value;
  const search = orgSearch.value.toLowerCase();
  return organizations.value.filter(org => 
    org.name.toLowerCase().includes(search) ||
    (org.description && org.description.toLowerCase().includes(search))
  );
});

// 加载用户列表
const loadUsers = async (page: number = 1) => {
  try {
    const response = await adminApi.getUsers(page, usersPagination.value.page_size, authStore.user?.id);
    if (response.success && response.data) {
      users.value = response.data.users;
      usersPagination.value = {
        page: response.data.page,
        page_size: response.data.page_size,
        total_count: response.data.total_count,
        total_pages: response.data.total_pages
      };
    }
  } catch (error) {
    console.error('加载用户列表失败:', error);
  }
};

// 加载组织列表
const loadOrganizations = async (page: number = 1) => {
  try {
    const response = await adminApi.getOrganizations(page, orgsPagination.value.page_size, authStore.user?.id);
    if (response.success && response.data) {
      organizations.value = response.data.organizations;
      orgsPagination.value = {
        page: response.data.page,
        page_size: response.data.page_size,
        total_count: response.data.total_count,
        total_pages: response.data.total_pages
      };
    }
  } catch (error) {
    console.error('加载组织列表失败:', error);
  }
};

// 加载操作日志
const loadOperations = async (page: number = 1) => {
  try {
    const response = await adminApi.getOperations(page, opsPagination.value.page_size, authStore.user?.id);
    if (response.success && response.data) {
      operations.value = response.data.operations;
      opsPagination.value = {
        page: response.data.page,
        page_size: response.data.page_size,
        total_count: response.data.total_count,
        total_pages: response.data.total_pages
      };
    }
  } catch (error) {
    console.error('加载操作日志失败:', error);
  }
};

// 搜索功能
const searchUsers = () => {
  // 搜索逻辑已经在计算属性中实现
};

const searchOrganizations = () => {
  // 搜索逻辑已经在计算属性中实现
};

// 模态框操作
const showBanModal = (user: User) => {
  selectedUser.value = user;
  banReason.value = '';
  modalType.value = 'banUser';
  showModal.value = true;
};

const showUnbanModal = (user: User) => {
  selectedUser.value = user;
  unbanReason.value = '';
  modalType.value = 'unbanUser';
  showModal.value = true;
};

const showDeleteUserModal = (user: User) => {
  selectedUser.value = user;
  deleteReason.value = '';
  modalType.value = 'deleteUser';
  showModal.value = true;
};

const showDeleteOrgModal = (org: any) => {
  selectedOrg.value = org;
  deleteOrgReason.value = '';
  modalType.value = 'deleteOrg';
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  modalType.value = '';
  selectedUser.value = null;
  selectedOrg.value = null;
  banReason.value = '';
  unbanReason.value = '';
  deleteReason.value = '';
  deleteOrgReason.value = '';
};

// 详情模态框操作
const viewUserDetails = async (userId: number) => {
  try {
    const response = await adminApi.getUserDetails(userId, authStore.user?.id);
    if (response.success && response.data) {
      userDetails.value = response.data;
      detailType.value = 'user';
      showDetailModal.value = true;
    }
  } catch (error) {
    console.error('获取用户详情失败:', error);
  }
};

const viewOrganizationDetails = async (orgId: number) => {
  try {
    const response = await adminApi.getOrganizationDetails(orgId, authStore.user?.id);
    if (response.success && response.data) {
      orgDetails.value = response.data;
      detailType.value = 'organization';
      showDetailModal.value = true;
    }
  } catch (error) {
    console.error('获取组织详情失败:', error);
  }
};

const closeDetailModal = () => {
  showDetailModal.value = false;
  detailType.value = '';
  userDetails.value = null;
  orgDetails.value = null;
};

// 管理员操作
const banUser = async () => {
  if (!selectedUser.value) return;
  
  try {
    const response = await adminApi.banUser(authStore.user?.id, 
      { operated_user_id: selectedUser.value.id, reason: banReason.value });
    if (response.success) {
      await loadUsers(usersPagination.value.page);
      closeModal();
    }
  } catch (error) {
    console.error('封禁用户失败:', error);
  }
};

const unbanUser = async () => {
  if (!selectedUser.value) return;
  
  try {
    const response = await adminApi.unbanUser(authStore.user?.id, { operated_user_id: selectedUser.value.id, reason: unbanReason.value });
    if (response.success) {
      await loadUsers(usersPagination.value.page);
      closeModal();
    }
  } catch (error) {
    console.error('解封用户失败:', error);
  }
};

const deleteUser = async () => {
  if (!selectedUser.value) return;
  
  try {
    const response = await adminApi.deleteUser(authStore.user?.id, 
      { operated_user_id: selectedUser.value.id, reason: deleteReason.value });
    if (response.success) {
      await loadUsers(usersPagination.value.page);
      closeModal();
    }
  } catch (error) {
    console.error('删除用户失败:', error);
  }
};

const deleteOrganization = async () => {
  if (!selectedOrg.value) return;
  
  try {
    const response = await adminApi.deleteOrganization(authStore.user?.id, 
      { org_id: selectedOrg.value.id, reason: deleteOrgReason.value });
    if (response.success) {
      await loadOrganizations(orgsPagination.value.page);
      closeModal();
    }
  } catch (error) {
    console.error('解散组织失败:', error);
  }
};

// 格式化时间
const formatTime = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN');
};

// 组件挂载
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login');
    return;
  }
  
  // 检查是否为管理员
  // 这里需要实现管理员权限检查
  // 暂时先加载数据
  await loadUsers();
  await loadOrganizations();
  await loadOperations();
});
</script>

<style scoped>
.admin-view {
  min-height: 100vh;
  background: #f8fafc;
  padding: 2rem;
  margin: 0 auto;
}

.admin-container {
  max-width: 1400px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.admin-nav {
  display: flex;
  background: #f1f5f9;
  border-bottom: 1px solid #e2e8f0;
}

.nav-btn {
  padding: 1rem 2rem;
  border: none;
  background: none;
  cursor: pointer;
  font-weight: 500;
  color: #64748b;
  transition: all 0.2s;
}

.nav-btn:hover {
  background: #e2e8f0;
  color: #334155;
}

.nav-btn.active {
  background: white;
  color: #3b82f6;
  border-bottom: 2px solid #3b82f6;
}

.admin-section {
  padding: 2rem;
  width: 1000px;
  color: black;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  margin: 0;
  color: #1e293b;
  font-size: 1.5rem;
}

.search-box input {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  width: 300px;
}

.table-container {
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.admin-table th,
.admin-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.admin-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.admin-table tbody tr:hover {
  background: #f8fafc;
}

.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge.admin {
  background: #dbeafe;
  color: #1e40af;
}

.badge.user {
  background: #e5e7eb;
  color: #374151;
}

.badge.active {
  background: #dcfce7;
  color: #166534;
}

.badge.banned {
  background: #fee2e2;
  color: #991b1b;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn-view, .btn-ban, .btn-unban, .btn-delete {
  padding: 0.25rem 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-view {
  background: #e0f2fe;
  color: #0369a1;
}

.btn-ban {
  background: #fef3c7;
  color: #92400e;
}

.btn-unban {
  background: #dcfce7;
  color: #166534;
}

.btn-delete {
  background: #fee2e2;
  color: #991b1b;
}

.invite-code {
  font-family: monospace;
  background: #f1f5f9;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding: 1rem;
}

.pagination button {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination button:not(:disabled):hover {
  background: #f3f4f6;
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

.detail-modal {
  max-width: 800px;
}

.modal h3 {
  margin: 0 0 1.5rem 0;
  color: #1e293b;
  font-size: 1.25rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  resize: vertical;
}

.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
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

.modal-actions button:first-child {
  background: #e5e7eb;
  color: #374151;
}

.modal-actions button.danger {
  background: #ef4444;
  color: white;
}

.modal-actions button.success {
  background: #10b981;
  color: white;
}

.modal-actions button:hover:not(:disabled) {
  opacity: 0.9;
}

/* 详情模态框样式 */
.detail-content {
  max-height: 60vh;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.detail-section:last-child {
  border-bottom: none;
}

.detail-section h4 {
  margin: 0 0 0.75rem 0;
  color: #374151;
  font-size: 1.125rem;
}

.detail-section p {
  margin: 0.5rem 0;
  color: #6b7280;
}

.detail-section ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.detail-section li {
  margin: 0.25rem 0;
  color: #6b7280;
}
</style>
