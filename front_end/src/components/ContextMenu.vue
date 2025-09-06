<template>
  <div 
    v-if="visible" 
    ref="menuRef"
    class="context-menu" 
    :style="{ top: `${position.y}px`, left: `${position.x}px` }"
    @click.stop
    @contextmenu.stop
  >
    <div 
      v-for="item in items" 
      :key="item.label" 
      class="context-menu-item" 
      @click="handleItemClick(item)"
    >
      {{ item.label }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

export interface ContextMenuItem {
  label: string;
  action: () => void;
  disabled?: boolean;
}

const props = defineProps<{
  visible: boolean;
  position: { x: number; y: number };
  items: ContextMenuItem[];
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const menuRef = ref<HTMLElement | null>(null);

const handleItemClick = (item: ContextMenuItem) => {
  if (!item.disabled) {
    item.action();
    emit('close');
  }
};

// 只有当事件发生在菜单外部时才关闭
const handleOutsideEvent = (e: Event) => {
  if (!props.visible) return;
  const target = e.target as Node | null;
  if (!menuRef.value) return;
  if (!target || !menuRef.value.contains(target)) {
    emit('close');
  }

};

onMounted(() => {
  document.addEventListener('click', handleOutsideEvent);
  document.addEventListener('contextmenu', handleOutsideEvent);
});

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideEvent);
  document.removeEventListener('contextmenu', handleOutsideEvent);
});
</script>

<style scoped>
.context-menu {
  position: fixed;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  min-width: 120px;
}

.context-menu-item {
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #4a5568;
  transition: background-color 0.2s;
}

.context-menu-item:hover {
  background: #f7fafc;
}

.context-menu-item:first-child {
  border-top-left-radius: 6px;
  border-top-right-radius: 6px;
}

.context-menu-item:last-child {
  border-bottom-left-radius: 6px;
  border-bottom-right-radius: 6px;
}
</style>
