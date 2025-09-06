import axios from 'axios';
import type { 
  User, 
  ConversationTitle, 
  ConversationDetail,
  NoteTitle,
  NoteDetail,
  NoteAttachment,
  NoteFolder, 
  Organization,
  OrganizationMember,
  OrganizationCreateRequest,
  OrganizationUpdateRequest,
  DeleteOrganizationRequest,
  LeaveOrganizationRequest,
  GetMembersRequest,
  RemoveMemberRequest,
  LoginRequest, 
  RegisterRequest, 
  AskRequest, 
  CreateNoteRequest, 
  UpdateNoteRequest,
  CreateFolderRequest,
  JoinOrganizationRequest,
  ApiResponse 
} from '@/types/api';
import { fetchEventSource } from '@microsoft/fetch-event-source';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器，自动添加认证token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器，处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  // 用户注册
  register: async (data: RegisterRequest): Promise<ApiResponse<User>> => {
    const response = await api.post('/api/register', data);
    return response.data;
  },

  // 用户登录
  login: async (data: LoginRequest): Promise<ApiResponse<{ user: User; conversations: ConversationTitle[] }>> => {
    const response = await api.post('/api/login', data);
    if (response.data.success) {
      // 从服务器响应中获取真实的token
      const token = response.data.token;
      if (!token) {
        // 第一次登录或token生成失败，尝试重新获取用户信息
        console.warn('登录成功但未收到token，尝试重新获取用户信息');
        // 这里可以添加重试逻辑或提示用户重新登录
        // 暂时不抛出错误，让用户继续使用
      } else {
        localStorage.setItem('auth_token', token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
    }
    return response.data;
  },

  // 获取当前用户信息
  getCurrentUser: async (): Promise<ApiResponse<User>> => {
    const response = await api.get('/api/user/me');
    return response.data;
  },

  // 退出登录
  logout: async (): Promise<void> => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  },

  // 发送密码重置验证码
  sendResetCode: async (email: string): Promise<ApiResponse> => {
    const response = await api.post('/api/auth/send-reset-code', { email });
    return response.data;
  },

  // 验证重置验证码
  verifyResetCode: async (email: string, verificationCode: string): Promise<ApiResponse> => {
    const response = await api.post('/api/auth/verify-reset-code', {
      email,
      verification_code: verificationCode
    });
    return response.data;
  },

  // 重置密码
  resetPassword: async (email: string, verificationCode: string, newPassword: string): Promise<ApiResponse> => {
    const response = await api.post('/api/auth/reset-password', {
      email,
      verification_code: verificationCode,
      new_password: newPassword
    });
    return response.data;
  },

  // 修改用户名
  updateUsername: async (userId: number, currentPassword: string, newUsername: string): Promise<ApiResponse<User>> => {
    const response = await api.put(`/api/users/${userId}/username`, {
      current_password: currentPassword,
      new_username: newUsername
    });
    return response.data;
  },

  // 修改密码
  updatePassword: async (userId: number, currentPassword: string, newPassword: string): Promise<ApiResponse> => {
    const response = await api.put(`/api/users/${userId}/password`, {
      current_password: currentPassword,
      new_password: newPassword
    });
    return response.data;
  },

  // 注销账号
  deleteAccount: async (userId: number): Promise<ApiResponse> => {
    const response = await api.delete(`/api/users/self-delete`, 
      {params: {operated_user_id: userId, current_user_id: userId}}
    );
    return response.data;
  },
};

export const conversationApi = {
  // 创建新对话
  createConversation: async (ownerId: number, isUser: boolean = true): Promise<ApiResponse<ConversationTitle>> => {
    const response = await api.post('/api/conversations/new', {
      owner_id: ownerId,
      is_user: isUser
    });
    return response.data;
  },

  // 获取对话历史（标题列表）
  getConversationTitles: async (ownerId: number, isUser: boolean = true, limit = 40, offset = 0): Promise<ApiResponse<ConversationTitle[]>> => {
    const response = await api.get('/api/conversations/history', {
      params: {
        owner_id: ownerId,
        is_user: isUser,
        limit,
        offset
      }
    });
    return response.data;
  },

  // 获取对话详情（消息列表）
  getConversationDetail: async (conversationId: number, ownerId: number, isUser: boolean = true): Promise<ApiResponse<ConversationDetail>> => {
    const response = await api.get(`/api/conversations/${conversationId}`, {
      params: {
        owner_id: ownerId,
        is_user: isUser
      }
    });
    return response.data;
  },

  // 发送问题（流式响应）
  askQuestion: async (data: AskRequest): Promise<Response> => {
    return fetch(`${API_BASE_URL}/api/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
      },
      body: JSON.stringify(data),
    });
  },

    // 新增：流式请求
  askQuestionStream: async (
    data: AskRequest,
    onChunk: (chunk: string) => void,
    onDone?: () => void,
    onError?: (err: any) => void
  ) => {
    await fetchEventSource(`${API_BASE_URL}/api/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
      },
      body: JSON.stringify(data),
      onmessage(event) {
        const transferData = event.data?.trim();
        if (!transferData) return; // ⚠️ 空字符串直接忽略

        try {
          const parsed = JSON.parse(transferData);

          if (parsed.chunk) {
            onChunk(parsed.chunk);
          }

          if (parsed.done && onDone) {
            onDone();
          }

          if (parsed.error && onError) {
            onError(parsed.error);
          }
          // if (event.data) {
          //   onChunk(event.data);
          // }

          // console.log("SSE event:", event);
          // console.log("SSE data:", JSON.stringify(event.data));
        } catch (err) {
          // ⚠️ JSON 不完整或异常时，先忽略，不阻断流
          console.warn("解析 SSE 数据失败，可能是 JSON 不完整:", err, "data:", transferData);
        }
      },
      onerror(err) {
        console.error("SSE 出错:", err);
        onError?.(err);
      },
      openWhenHidden: true,
    });
  },


  // 删除对话
  deleteConversation: async (conversationId: number, ownerId: number, isUser: boolean = true): Promise<ApiResponse> => {
    const response = await api.delete(`/api/conversations/${conversationId}`, {
      params: {
        owner_id: ownerId,
        is_user: isUser
      }
    });
    return response.data;
  },

  // 删除消息
  deleteMessage: async (messageId: number, ownerId: number, isUser: boolean = true, isQuestion: boolean = false): Promise<ApiResponse> => {
    const response = await api.delete(`/api/messages/${messageId}`, {
      params: {
        owner_id: ownerId,
        is_user: isUser,
        is_question: isQuestion
      }
    });
    return response.data;
  },
};

export const noteApi = {
  // 获取所有笔记文件夹（支持用户和组织）
  getFolders: async (ownerId: number, isUser: boolean = true): Promise<ApiResponse<NoteFolder[]>> => {
    const response = await api.get(`/api/notes/folders?owner_id=${ownerId}&is_user=${isUser}`);
    return response.data;
  },

  // 创建笔记文件夹
  createFolder: async (data: CreateFolderRequest): Promise<ApiResponse<NoteFolder>> => {
    const response = await api.post('/api/notes/folders', data);
    return response.data;
  },

  // 获取文件夹下的笔记标题列表
  getNoteTitles: async (folderId?: number): Promise<ApiResponse<NoteTitle[]>> => {
    const url = folderId ? `/api/notes/titles?folder_id=${folderId}` : '/api/notes/titles';
    const response = await api.get(url);
    return response.data;
  },

  // 获取单个笔记详情
  getNoteDetail: async (noteId: number): Promise<ApiResponse<NoteDetail>> => {
    const response = await api.get(`/api/notes/${noteId}/detail`);
    return response.data;
  },

  // 创建笔记
  createNote: async (data: CreateNoteRequest): Promise<ApiResponse<NoteDetail>> => {
    const response = await api.post('/api/notes', data);
    return response.data;
  },

  // 更新笔记
  updateNote: async (noteId: number, data: UpdateNoteRequest): Promise<ApiResponse<NoteDetail>> => {
    const response = await api.put(`/api/notes/${noteId}`, data);
    return response.data;
  },

  // 删除笔记
  deleteNote: async (noteId: number): Promise<ApiResponse> => {
    const response = await api.delete(`/api/notes/${noteId}`);
    return response.data;
  },

  // 删除文件夹
  deleteFolder: async (folderId: number): Promise<ApiResponse> => {
    const response = await api.delete(`/api/notes/folders/${folderId}`);
    return response.data;
  },

  // 上传附件
  uploadAttachment: async (noteId: number, file: File): Promise<ApiResponse<NoteAttachment>> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/api/notes/${noteId}/attachments`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // 获取笔记附件列表
  getNoteAttachments: async (noteId: number): Promise<ApiResponse<NoteAttachment[]>> => {
    const response = await api.get(`/api/notes/${noteId}/attachments`);
    return response.data;
  },

  // 删除附件
  deleteAttachment: async (attachmentId: number): Promise<ApiResponse> => {
    const response = await api.delete(`/api/notes/attachments/${attachmentId}`);
    return response.data;
  },

  // 获取附件上传预签名URL（如果需要直接上传到MinIO）
  getPresignedUrl: async (noteId: number, fileName: string, mimeType: string): Promise<ApiResponse<{ upload_url: string; download_url: string }>> => {
    const response = await api.post(`/api/notes/${noteId}/presigned-url`, {
      file_name: fileName,
      mime_type: mimeType,
    });
    return response.data;
  },
};

export const organizationApi = {
  // 获取用户的所有组织（创建的和加入的）
  getUserOrganizations: async (userId: number): Promise<ApiResponse<Organization[]>> => {
    const response = await api.get(`/api/organizations/user/${userId}`);
    return response.data;
  },

  // 通过邀请码搜索组织
  searchOrganization: async (inviteCode: string): Promise<ApiResponse<Organization>> => {
    const response = await api.get(`/api/organizations/search?invite_code=${inviteCode}`);
    return response.data;
  },

  // 加入组织
  joinOrganization: async (data: JoinOrganizationRequest): Promise<ApiResponse> => {
    const response = await api.post('/api/organizations/join', data);
    return response.data;
  },

  // 创建组织
  createOrganization: async (data: OrganizationCreateRequest): Promise<ApiResponse<Organization>> => {
    const response = await api.post('/api/organizations', data);
    return response.data;
  },

  // 更新组织信息
  updateOrganization: async (organizationId: number, data: OrganizationUpdateRequest): Promise<ApiResponse<Organization>> => {
    const response = await api.put(`/api/organizations/${organizationId}`, data);
    return response.data;
  },

  // 删除组织
  deleteOrganization: async (organizationId: number, userId: number): Promise<ApiResponse> => {
    const requestData: DeleteOrganizationRequest = { user_id: userId };
    const response = await api.delete(`/api/organizations/${organizationId}`, { data: requestData });
    return response.data;
  },

  // 离开组织
  leaveOrganization: async (organizationId: number, userId: number): Promise<ApiResponse> => {
    const requestData: LeaveOrganizationRequest = { user_id: userId };
    const response = await api.post(`/api/organizations/${organizationId}/leave`, requestData);
    return response.data;
  },

  // 获取组织成员列表
  getOrganizationMembers: async (organizationId: number, userId: number): Promise<ApiResponse<OrganizationMember[]>> => {
    const requestData: GetMembersRequest = { user_id: userId };
    const response = await api.post(`/api/organizations/${organizationId}/members`, requestData);
    return response.data;
  },

  // 移除组织成员
  removeOrganizationMember: async (organizationId: number, userId: number, operatorId: number): Promise<ApiResponse> => {
    const requestData: RemoveMemberRequest = { user_id: operatorId };
    const response = await api.post(`/api/organizations/${organizationId}/members/${userId}/remove`, requestData);
    return response.data;
  },
};

// 管理员API接口
export const adminApi = {
  // 获取所有用户列表
  getUsers: async (page: number = 1, pageSize: number = 20, user_id?: number): Promise<ApiResponse<{
    users: User[];
    total_count: number;
    page: number;
    page_size: number;
    total_pages: number;
  }>> => {
    const response = await api.get('/api/admin/users', {
      params: { page, page_size: pageSize, user_id: user_id }
    });
    return response.data;
  },

  // 获取所有组织列表
  getOrganizations: async (page: number = 1, pageSize: number = 20, user_id?: number): Promise<ApiResponse<{
    organizations: any[];
    total_count: number;
    page: number;
    page_size: number;
    total_pages: number;
  }>> => {
    const response = await api.get('/api/admin/organizations', {
      params: { page, page_size: pageSize, user_id: user_id }
    });
    return response.data;
  },

  // 获取操作日志
  getOperations: async (page: number = 1, pageSize: number = 20, user_id?: number): Promise<ApiResponse<{
    operations: any[];
    total_count: number;
    page: number;
    page_size: number;
    total_pages: number;
  }>> => {
    const response = await api.get('/api/admin/operations', {
      params: { page, page_size: pageSize, user_id: user_id }
    });
    return response.data;
  },

  // 封禁用户
  banUser: async (user_id?: number, data?: { operated_user_id?: number, reason?: string }): Promise<ApiResponse> => {
    const response = await api.post(`/api/admin/users/${user_id}/ban`, data);
    return response.data;
  },

  // 解封用户
  unbanUser: async (user_id?: number, data?: { operated_user_id?: number, reason?: string }): Promise<ApiResponse> => {
    const response = await api.post(`/api/admin/users/${user_id}/unban`, data);
    return response.data;
  },

  // 删除用户
  deleteUser: async (user_id?: number, data?: { operated_user_id?: number, reason?: string }): Promise<ApiResponse> => {
    const response = await api.delete(`/api/admin/users/${user_id}`, { data });
    return response.data;
  },

  // 解散组织
  deleteOrganization: async (user_id?: number, data?: { org_id?: number, reason?: string }): Promise<ApiResponse> => {
    const response = await api.delete(`/api/admin/organizations/${user_id}`, { data });
    return response.data;
  },

  // 获取用户详情
  getUserDetails: async (operatedUserId: number, userId?: number): Promise<ApiResponse<any>> => {
    const response = await api.get(`/api/admin/users/${operatedUserId}/details`, {
      params: {user_id: userId}
    });
    return response.data;
  },

  // 获取组织详情
  getOrganizationDetails: async (orgId: number, userId?: number): Promise<ApiResponse<any>> => {
    const response = await api.get(`/api/admin/organizations/${orgId}/details`, {
      params: {user_id: userId}
    });
    return response.data;
  },
};

export default api;
