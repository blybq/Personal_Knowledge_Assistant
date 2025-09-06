<template>
  <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h3>新建文件夹</h3>
      <input
        v-model="folderName"
        placeholder="输入文件夹名称"
        class="folder-input"
        @keydown.enter="$emit('confirm', folderName)"
      />
      <div class="modal-actions">
        <button class="cancel-btn" @click="$emit('close')">取消</button>
        <button class="confirm-btn" @click="$emit('confirm', folderName)" :disabled="!folderName.trim()">
          创建
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

// defineProps<{
//   visible: boolean;
// }>();

defineEmits<{
  (e: 'close'): void;
  (e: 'confirm', name: string): void;
}>();

const folderName = ref('');

const props = defineProps<{
  visible: boolean;
}>();

// 当模态框显示时清空输入框
watch(() => props.visible, (newVal) => {
  if (newVal) {
    folderName.value = '';
  }
});

</script>

<style scoped>
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

.modal {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  min-width: 300px;
}

.modal h3 {
  margin: 0 0 1rem 0;
  color: #2d3748;
}

.folder-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.folder-input:focus {
  outline: none;
  border-color: #4299e1;
}

.modal-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.cancel-btn, .confirm-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.cancel-btn {
  background: #e2e8f0;
  color: #4a5568;
}

.confirm-btn {
  background: #4299e1;
  color: white;
}

.confirm-btn:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
}
</style>
