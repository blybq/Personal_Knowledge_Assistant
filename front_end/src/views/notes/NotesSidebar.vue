<template>
  <aside class="notes-sidebar">
    <div class="sidebar-header">
      <h3 v-if="selectedFolder">{{ selectedFolder.name }}</h3>
      <h3 v-else>全部笔记</h3>
      <button class="new-note-btn" @click="$emit('create-note')">
        + 新笔记
      </button>
    </div>

    <div class="notes-list">
      <div
        v-for="note in notes"
        :key="note.id"
        class="note-item"
        :class="{ active: activeNote?.id === note.id }"
        @click="$emit('note-selected', note)"
        @contextmenu.prevent="$emit('note-contextmenu', $event, note)"
      >
        <div class="note-title">{{ note.title }}</div>
        <div class="note-time">{{ formatTime(note.updated_at) }}</div>
      </div>
      
      <div v-if="notes.length === 0" class="empty-state">
        <p>暂无笔记</p>
        <button class="create-note-btn" @click="$emit('create-note')">
          创建第一个笔记
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import type { NoteTitle, NoteFolder } from '@/types/api';

defineProps<{
  notes: NoteTitle[];
  selectedFolder: NoteFolder | null;
  activeNote: NoteTitle | null;
}>();

defineEmits<{
  (e: 'note-selected', note: NoteTitle): void;
  (e: 'create-note'): void;
  (e: 'note-contextmenu', event: MouseEvent, note: NoteTitle): void;
}>();

// 格式化时间
const formatTime = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN');
};
</script>

<style scoped>
.notes-sidebar {
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

.new-note-btn {
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s;
}

.new-note-btn:hover {
  background: #f7fafc;
}

.notes-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.note-item {
  padding: 0.75rem;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: background-color 0.2s;
  border: 1px solid #e2e8f0;
}

.note-item:hover {
  background: #f7fafc;
}

.note-item.active {
  background: #ebf4ff;
  border-color: #4299e1;
}

.note-title {
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
}

.note-time {
  color: #a0aec0;
  font-size: 0.75rem;
}

.empty-state {
  text-align: center;
  padding: 2rem 1rem;
  color: #718096;
}

.create-note-btn {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
</style>
