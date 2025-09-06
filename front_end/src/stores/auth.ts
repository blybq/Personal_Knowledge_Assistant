import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User } from '@/types/api';
import { authApi } from '@/services/api';

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null);
  const isAuthenticated = computed(() => !!user.value);
  const isLoading = ref(false);

  // 从localStorage初始化用户信息
  const initAuth = () => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      user.value = JSON.parse(savedUser);
    }
  };

  // 登录
  const login = async (email: string, password: string) => {
    isLoading.value = true;
    try {
      const response = await authApi.login({ email, password });
      if (response.success && response.data) {
        user.value = response.data.user;
        localStorage.setItem('user', JSON.stringify(response.data.user));
        return { success: true, data: response.data };
      } else {
        return { success: false, message: response.message };
      }
    } catch (error: any) {
      const message = error.response?.data?.message || '登录失败';
      return { success: false, message };
    } finally {
      isLoading.value = false;
    }
  };

  // 注册
  const register = async (username: string, email: string, password: string) => {
    isLoading.value = true;
    try {
      const response = await authApi.register({ username, email, password });
      if (response.success && response.data) {
        user.value = response.data;
        localStorage.setItem('user', JSON.stringify(response.data));
        return { success: true, data: response.data };
      } else {
        return { success: false, message: response.message };
      }
    } catch (error: any) {
      const message = error.response?.data?.message || '注册失败';
      return { success: false, message };
    } finally {
      isLoading.value = false;
    }
  };

  // 退出登录
  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      console.error('退出登录失败:', error);
    } finally {
      user.value = null;
      localStorage.removeItem('user');
      localStorage.removeItem('auth_token');
    }
  };

  // 获取当前用户信息
  const getCurrentUser = async () => {
    try {
      const response = await authApi.getCurrentUser();
      if (response.success && response.data) {
        user.value = response.data;
        localStorage.setItem('user', JSON.stringify(response.data));
      }
    } catch (error) {
      console.error('获取用户信息失败:', error);
    }
  };

  // 设置用户信息
  const setUser = (userData: User) => {
    user.value = userData;
    localStorage.setItem('user', JSON.stringify(userData));
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    initAuth,
    login,
    register,
    logout,
    getCurrentUser,
    setUser,
  };
});
