import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Organization } from '@/types/api';

export const useOrganizationStore = defineStore('organization', () => {
  // 当前选中的组织（null表示个人账号）
  const currentOrganization = ref<Organization | null>(null);
  
  // 是否为组织账号模式
  const isOrganizationMode = computed(() => !!currentOrganization.value);
  
  // 当前所有者ID（用户ID或组织ID）
  const currentOwnerId = computed(() => 
    isOrganizationMode.value ? currentOrganization.value!.id : null
  );
  
  // 组织切换事件监听器
  const organizationChangeListeners = ref<Set<() => void>>(new Set());
  
  // 添加组织切换监听器
  const addOrganizationChangeListener = (listener: () => void) => {
    organizationChangeListeners.value.add(listener);
  };
  
  // 移除组织切换监听器
  const removeOrganizationChangeListener = (listener: () => void) => {
    organizationChangeListeners.value.delete(listener);
  };
  
  // 触发组织切换事件
  const triggerOrganizationChange = () => {
    organizationChangeListeners.value.forEach(listener => listener());
  };
  
  // 设置当前组织
  const setCurrentOrganization = (organization: Organization | null) => {
    currentOrganization.value = organization;
    // 保存到localStorage以便页面刷新后保持状态
    if (organization) {
      localStorage.setItem('current_organization', JSON.stringify(organization));
    } else {
      localStorage.removeItem('current_organization');
    }
    // 触发组织切换事件
    triggerOrganizationChange();
  };
  
  // 从localStorage初始化组织状态
  const initOrganization = () => {
    const savedOrganization = localStorage.getItem('current_organization');
    if (savedOrganization) {
      currentOrganization.value = JSON.parse(savedOrganization);
    }
  };
  
  // 切换到个人账号
  const switchToPersonalAccount = () => {
    setCurrentOrganization(null);
  };
  
  // 获取当前所有者的参数（用于API调用）
  const getOwnerParams = (userId: number) => {
    if (isOrganizationMode.value && currentOrganization.value) {
      return {
        owner_id: currentOrganization.value.id,
        is_user: false
      };
    } else {
      return {
        owner_id: userId,
        is_user: true
      };
    }
  };
  
  return {
    currentOrganization,
    isOrganizationMode,
    currentOwnerId,
    setCurrentOrganization,
    initOrganization,
    switchToPersonalAccount,
    getOwnerParams,
    addOrganizationChangeListener,
    removeOrganizationChangeListener
  };
});
