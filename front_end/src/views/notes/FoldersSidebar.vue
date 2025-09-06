<template>
  <aside class="folders-sidebar">
    <div class="sidebar-header">
      <h3>文件夹</h3>
      <button class="new-folder-btn" @click="$emit('create-folder')">
        + 新建文件夹
      </button>
    </div>
    
    <div class="folders-list">
      <div
        v-for="folder in folders"
        :key="folder.id"
        class="folder-item"
        :class="{ active: selectedFolder?.id === folder.id }"
        @click="$emit('folder-selected', folder)"
        @contextmenu.prevent="$emit('folder-contextmenu', $event, folder)"
      >
        <span class="folder-icon">📁</span>
        <span class="folder-name">{{ folder.name }}</span>
        <span class="folder-count" v-if="folder.notes_count">
          ({{ folder.notes_count }})
        </span>
      </div>
      
      <div v-if="folders.length === 0" class="empty-state">
        <p>暂无文件夹</p>
        <button class="create-folder-btn" @click="$emit('create-folder')">
          创建第一个文件夹
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import type { NoteFolder } from '@/types/api';

defineProps<{
  folders: NoteFolder[];
  selectedFolder: NoteFolder | null;
}>();

defineEmits<{
  (e: 'folder-selected', folder: NoteFolder): void;
  (e: 'create-folder'): void;
  (e: 'folder-contextmenu', event: MouseEvent, folder: NoteFolder): void;
}>();
</script>

<style scoped>
.folders-sidebar {
  width: 250px;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  color: #2d3748;
  font-size: 1rem;
}

.new-folder-btn {
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s;
}

.new-folder-btn:hover {
  background: #f7fafc;
}

.folders-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.folder-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: background-color 0.2s;
  border: 1px solid #e2e8f0;
}

.folder-item:hover {
  background: #f7fafc;
}

.folder-item.active {
  background: #ebf4ff;
  border-color: #4299e1;
}

.folder-icon {
  margin-right: 0.5rem;
}

.folder-name {
  flex: 1;
  font-size: 0.875rem;
  color: #4a5568;
}

.folder-count {
  font-size: 0.75rem;
  color: #a0aec0;
}

.empty-state {
  text-align: center;
  padding: 2rem 1rem;
  color: #718096;
}

.create-folder-btn {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
</style>
