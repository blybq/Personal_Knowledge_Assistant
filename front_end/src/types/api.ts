export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
  is_admin?: boolean;
  is_banned?: boolean;
}

export interface Message {
  id: number;
  conversation_id: number;
  question: string;
  answer: string;
  created_at: string;
}

export interface ConversationTitle {
  id: number;
  owner_id: number;
  is_user: boolean;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationDetail {
  id: number;
  title: string;
  messages: Message[];
  created_at: string;
  owner_id: number;
  is_user: boolean;
}

export interface NoteTitle {
  id: number;
  title: string;
  folder_id?: number;
  created_at: string;
  updated_at: string;
  user_id?: number;
}

export interface NoteAttachment {
  id: number;
  note_id: number;
  file_name: string;
  file_url: string;
  mime_type: string;
  size: number;
  created_at: string;
}

export interface NoteDetail {
  id: number;
  title: string;
  content: string;
  user_id?: number;
  folder_id?: number;
  created_at: string;
  updated_at: string;
  attachments?: NoteAttachment[];
}

export interface NoteFolder {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
  notes_count?: number;
}

export interface Organization {
  id: number;
  name: string;
  description?: string;
  invite_code: string;
  creator_id: number;
  created_at: string;
  updated_at: string;
  is_creator: boolean;
  member_count: number;
}

export interface OrganizationMember {
  user_id: number;
  username: string;
  email: string;
  is_creator: boolean;
  joined_at: string;
}

export interface OrganizationCreateRequest {
  name: string;
  description?: string;
  user_id: number;  // 新增：用户ID
}

export interface OrganizationUpdateRequest {
  name: string;
  description?: string;
  user_id: number;  // 新增：用户ID
}

export interface JoinOrganizationRequest {
  invite_code: string;
  user_id: number;  // 新增：用户ID
}

export interface DeleteOrganizationRequest {
  user_id: number;  // 新增：删除组织请求
}

export interface LeaveOrganizationRequest {
  user_id: number;  // 新增：离开组织请求
}

export interface GetMembersRequest {
  user_id: number;  // 新增：获取成员请求
}

export interface RemoveMemberRequest {
  user_id: number;  // 新增：移除成员请求
}

export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface AskRequest {
  question: string;
  owner_id: number;
  is_user: boolean;
  conversation_id?: number;
}

export interface CreateNoteRequest {
  title: string;
  content: string;
  owner_id: number;
  is_user: boolean;
  folder_id?: number;
}

export interface UpdateNoteRequest {
  title?: string;
  content?: string;
  folder_id?: number;
}

export interface CreateFolderRequest {
  name: string;
  owner_id: number;
  is_user: boolean;
}

export interface SendResetCodeRequest {
  email: string;
}

export interface VerifyResetCodeRequest {
  email: string;
  verification_code: string;
}

export interface ResetPasswordRequest {
  email: string;
  verification_code: string;
  new_password: string;
}
