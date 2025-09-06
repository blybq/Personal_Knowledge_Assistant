<template>
  <div v-if="visible" class="confirm-dialog-overlay" @click.self="cancel">
    <div class="confirm-dialog">
      <div class="confirm-dialog-header">
        <h3>{{ title }}</h3>
      </div>
      <div class="confirm-dialog-body">
        <p>{{ message }}</p>
      </div>
      <div class="confirm-dialog-actions">
        <button class="cancel-btn" @click="cancel">取消</button>
        <button class="confirm-btn" @click="confirm">确认</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  visible: boolean;
  title: string;
  message: string;
}>();

const emit = defineEmits<{
  (e: 'confirm'): void;
  (e: 'cancel'): void;
}>();

const confirm = () => {
  emit('confirm');
};

const cancel = () => {
  emit('cancel');
};
</script>

<style scoped>
.confirm-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.confirm-dialog {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  min-width: 300px;
  max-width: 400px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.confirm-dialog-header {
  margin-bottom: 1rem;
}

.confirm-dialog-header h3 {
  margin: 0;
  color: #2d3748;
  font-size: 1.125rem;
}

.confirm-dialog-body {
  margin-bottom: 1.5rem;
}

.confirm-dialog-body p {
  margin: 0;
  color: #4a5568;
  line-height: 1.5;
}

.confirm-dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.cancel-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  color: #4a5568;
  cursor: pointer;
  transition: background-color 0.2s;
}

.cancel-btn:hover {
  background: #f7fafc;
}

.confirm-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  background: #f56565;
  color: white;
  cursor: pointer;
  transition: background-color 0.2s;
}

.confirm-btn:hover {
  background: #e53e3e;
}
</style>
