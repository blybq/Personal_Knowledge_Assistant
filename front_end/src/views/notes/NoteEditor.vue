<template>
  <main class="notes-main">
    <div v-show="note" class="note-editor">
      <!-- 标题区 -->
      <div class="editor-header">
        <input
          v-model="noteTitle"
          placeholder="笔记标题"
          class="title-input"
          @blur="$emit('save-note')"
        />
        <!-- <div class="editor-actions">
          <button class="save-btn" @click="$emit('save-note')" :disabled="isSaving">
            {{ isSaving ? '保存中...' : '保存' }}
          </button>
          <button class="delete-btn" @click="$emit('delete-note')">
            删除
          </button>
          <label class="upload-btn">
            上传文件
            <input type="file" class="hidden" @change="handleUpload" />
          </label>
        </div> -->
      </div>

      <!-- 按钮区：标题下面 -->
      <div class="editor-actions">
        <button class="save-btn" @click="$emit('save-note')" :disabled="isSaving">
          <span class="icon">💾</span>
          {{ isSaving ? '保存中...' : '保存' }}
        </button>

        <label class="upload-btn">
          <span class="icon">📤</span> 上传文件
          <input type="file" class="hidden" @change="handleUpload" />
        </label>
      </div>

      <!-- 富文本编辑器 -->
        <!-- <div id="quill-toolbar"></div> -->
      <div ref="editorContainer" class="editor" :class="{ 'editor-disabled': !note }"></div>

      <!-- 附件区 -->
      <div class="attachments" v-if="attachments.length > 0">
        <div 
          v-for="file in attachments" 
          :key="file.id" 
          class="attachment-item"
          @contextmenu.prevent="showAttachmentContextMenu($event, file)"
        >
          <!-- 图片缩略图 -->
          <template v-if="file.mime_type.startsWith('image/')">
            <img
              :src="file.file_url"
              class="thumb"
              @click="openPreview(file.file_url)"
            />
          </template>

          <!-- 普通文件 -->
          <template v-else>
            <div class="file-card">
              📎
              <a :href="file.file_url" target="_blank">
                {{ file.file_name }}
              </a>
              <span class="file-size">({{ formatSize(file.size) }})</span>
            </div>
          </template>
        </div>
      </div>

      <!-- Lightbox 预览 -->
      <div v-if="previewUrl" class="lightbox" @click="closePreview">
        <img :src="previewUrl" class="lightbox-img" />
      </div>
    </div>

    <!-- <div v-else class="welcome-message">
      <h3>欢迎使用云笔记</h3>
      <p>请选择一个笔记或创建新笔记开始记录</p>
    </div> -->

    <!-- 右键菜单 -->
    <ContextMenu
      :visible="contextMenuVisible"
      :position="contextMenuPosition"
      :items="contextMenuItems"
      @close="closeContextMenu"
    />

    <!-- 确认对话框 -->
    <ConfirmDialog
      :visible="confirmDialogVisible"
      :title="confirmDialogTitle"
      :message="confirmDialogMessage"
      @confirm="handleConfirm"
      @cancel="handleCancel"
    />
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import Quill from 'quill';
import { nextTick } from 'vue';
import 'quill/dist/quill.snow.css';
import type { NoteDetail, NoteAttachment } from '@/types/api';
import Container from 'quill/blots/container';
import { noteApi } from '@/services/api';
import ContextMenu, { type ContextMenuItem } from '@/components/ContextMenu.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';

const noteTitle = computed({
  get: () => props.note?.title ?? '',
  set: (val: string) => {
    if (props.note) {
      props.note.title = val;
    }
  }
});

// ✅ 修复 TS 报错：解构 props 后用 ref 包裹
const props = defineProps<{
  note: NoteDetail | null;
  isSaving: boolean;
}>();

const emit = defineEmits<{
  (e: 'save-note'): void;
  (e: 'delete-note'): void;
  (e: 'content-change', content: string): void;
}>();

// 附件列表
const attachments = ref<NoteAttachment[]>([]);

// Lightbox 预览
const previewUrl = ref<string | null>(null);
const openPreview = (url: string) => (previewUrl.value = url);
const closePreview = () => (previewUrl.value = null);

// 右键菜单相关
const contextMenuVisible = ref(false);
const contextMenuPosition = ref({ x: 0, y: 0 });
const contextMenuItems = ref<ContextMenuItem[]>([]);
const selectedAttachment = ref<NoteAttachment | null>(null);

// 确认对话框相关
const confirmDialogVisible = ref(false);
const confirmDialogTitle = ref('');
const confirmDialogMessage = ref('');
const confirmDialogAction = ref<() => void>(() => {});

// Quill 编辑器
const editorContainer = ref<HTMLDivElement | null>(null);
let quill: Quill | null = null;

// 提取一个初始化或刷新 Quill 的函数
const initQuill = (note: NoteDetail | null) => {
  console.log("editorContainer.value的值为，", editorContainer.value);
  if (!editorContainer.value) return;

  console.log("quill的值为，", quill);

  console.log('editorContainer offsetHeight:', editorContainer.value?.offsetHeight);
  console.log('editorContainer offsetWidth:', editorContainer.value?.offsetWidth);
  console.log('editorContainer computedStyle:', getComputedStyle(editorContainer.value));

  console.log('editorContainer', editorContainer.value);
  console.log('quill.container', quill?.container);
  console.log('quill.root', quill?.root);
  console.log('quill.container offsetHeight', quill?.container.offsetHeight);
  console.log('quill.root offsetHeight', quill?.root.offsetHeight);
  // console.log('computed style', getComputedStyle(quill?.container!));

  // 如果 Quill 没有初始化，先初始化
  if (!quill) {
    quill = new Quill(editorContainer.value, {
      theme: 'snow',
      modules: {
        toolbar: [
          ['bold', 'italic', 'underline', 'strike'],
          [{ size: ['small', false, 'large', 'huge'] }],
          [{ font: [] }],
          [{ list: 'ordered' }, { list: 'bullet' }],
        ],
      },
    });

    // 监听编辑变化
    quill.on('text-change', () => {
      if (props.note) {
        props.note.content = quill!.root.innerHTML;
        emit('content-change', props.note.content);
      }
    });
  }

  quill.enable(true);
  quill.focus();

  // 每次传入新的 note，都刷新内容
  if (note) {
    quill.root.innerHTML = note.content || '';
  } else {
    quill.root.innerHTML = ''; // note为空，显示空编辑器
  }
};

onMounted(async () => {
  await nextTick();
  initQuill(props.note); // 组件挂载时初始化编辑器
});

// ✅ watch props.note，当笔记存在时初始化 Quill
watch(
  () => props.note,
  async (newNote) => {
    console.log('[Debug] watch note:', newNote);
    await nextTick(); // 等 DOM 渲染完成
    initQuill(newNote);
    
    // 加载笔记附件
    if (newNote) {
      try {
        const response = await noteApi.getNoteAttachments(newNote.id);
        if (response.success && response.data) {
          attachments.value = response.data;
        }
      } catch (error) {
        console.error('获取附件列表失败:', error);
      }
    } else {
      attachments.value = [];
    }
  },
  { immediate: true } // 立即执行一次
);


// 上传文件逻辑
const handleUpload = async (e: Event) => {
  const input = e.target as HTMLInputElement;
  if (!input.files?.length || !props.note) return;

  const file = input.files[0];
  
  try {
    // 调用后端API上传文件
    const response = await noteApi.uploadAttachment(props.note.id, file);
    
    if (response.success && response.data) {
      // 将新附件添加到列表
      attachments.value.push(response.data);
    } else {
      console.error('上传失败:', response.message);
    }
  } catch (error) {
    console.error('上传文件出错:', error);
  }
};

// 格式化文件大小
const formatSize = (bytes: number) => {
  if (bytes < 1024) return bytes + 'B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + 'KB';
  return (bytes / 1024 / 1024).toFixed(1) + 'MB';
};

// 显示附件右键菜单
const showAttachmentContextMenu = (event: MouseEvent, attachment: NoteAttachment) => {
  console.log('附件右键菜单被触发', attachment.file_name);
  event.preventDefault();
  event.stopPropagation(); // <- 很重要，阻止 document 上的 contextmenu 监听器干扰
  selectedAttachment.value = attachment;
  
  contextMenuPosition.value = { x: event.clientX, y: event.clientY };
  contextMenuItems.value = [
    {
      label: '删除附件',
      action: () => showConfirmDialog(
        '删除附件',
        `确定要删除附件 "${attachment.file_name}" 吗？此操作将从数据库和存储中永久删除该文件。`,
        deleteAttachment
      )
    }
  ];
  contextMenuVisible.value = true;
  console.log('附件右键菜单状态:', contextMenuVisible.value);
};

// 显示确认对话框
const showConfirmDialog = (title: string, message: string, action: () => void) => {
  confirmDialogTitle.value = title;
  confirmDialogMessage.value = message;
  confirmDialogAction.value = action;
  confirmDialogVisible.value = true;
  contextMenuVisible.value = false;
};

// 删除附件
const deleteAttachment = async () => {
  if (!selectedAttachment.value) return;
  
  try {
    const response = await noteApi.deleteAttachment(selectedAttachment.value.id);
    
    if (response.success) {
      // 从列表中移除
      attachments.value = attachments.value.filter(
        a => a.id !== selectedAttachment.value!.id
      );
    }
  } catch (error) {
    console.error('删除附件失败:', error);
  }
};

// 处理用户在对话框中点击确认
const handleConfirm = async () => {
  try {
    if (confirmDialogAction.value) {
      // 确保兼容同步/异步操作
      await Promise.resolve(confirmDialogAction.value());
    }
  } catch (err) {
    console.error('确认操作失败:', err);
    // 可以在此处添加错误提示
  } finally {
    // 无论如何都关闭对话框
    confirmDialogVisible.value = false;
  }
};

const handleCancel = () => {
  confirmDialogVisible.value = false;
};

// 关闭右键菜单
const closeContextMenu = () => {
  contextMenuVisible.value = false;
};

// 暴露方法给父组件
defineExpose({ initQuill });
</script>

<style scoped>
.notes-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.note-editor {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.editor-header {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.title-input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 1.25rem;
  font-weight: 600;
}

.title-input:focus {
  outline: none;
  border-color: #4299e1;
}

.editor-actions {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.save-btn,
.upload-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
}

.save-btn {
  background: #48bb78;
  color: white;
}

.save-btn:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
}

.delete-btn {
  background: #f56565;
  color: white;
}

.editor {
  flex: 1;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  margin: 1rem;
  padding: 0.5rem;
  min-height: 300px;
}

::v-deep(.ql-editor) {
  font-family: 'Arial, sans-serif'; /* 默认字体 */
  font-size: 14px;                  /* 默认字号 */
  color: #000000;                       /* 默认字体颜色 */
  line-height: 1.5;                  /* 行高 */
}

.editor-disabled {
  background-color: #f5f5f5;
  pointer-events: none; /* 禁止点击和输入 */
}

.attachments {
  margin: 1rem;
}

.attachment-item {
  margin-bottom: 0.75rem;
}

.thumb {
  max-width: 200px;
  border-radius: 4px;
  cursor: pointer;
  transition: transform 0.2s;
}
.thumb:hover {
  transform: scale(1.05);
}

.file-card {
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: #f9fafb;
  font-size: 0.9rem;
  display: inline-block;
}

.file-card a {
  margin-left: 0.25rem;
  color: #2563eb;
  text-decoration: none;
}

.file-card a:hover {
  text-decoration: underline;
}

.file-size {
  color: #6b7280;
  font-size: 0.8rem;
  margin-left: 0.25rem;
}

/* Lightbox 样式 */
.lightbox {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
}

.lightbox-img {
  max-width: 90%;
  max-height: 90%;
  border-radius: 6px;
}

.welcome-message {
  text-align: center;
  padding: 2rem;
  color: #718096;
}
/* 保留你原有的样式，新增上传按钮 */
.upload-btn {
  background: #3182ce;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
}
.upload-btn input {
  display: none;
}
.upload-btn:hover {
  background: #2b6cb0;
}

.icon {
  font-size: 1rem;
  display: inline-block;
}
</style>
