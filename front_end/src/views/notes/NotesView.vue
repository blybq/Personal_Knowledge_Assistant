<template>
  <div class="notes-view">
    <div class="notes-container">
      <!-- 左侧文件夹列表栏 -->
      <FoldersSidebar
        :folders="allFolders"
        :selected-folder="selectedFolder"
        @folder-selected="selectFolder"
        @create-folder="showFolderDialog = true"
        @folder-contextmenu="showFolderContextMenu"
      />

      <!-- 中间笔记列表栏 -->
      <NotesSidebar
        :notes="notes"
        :selected-folder="selectedFolder"
        :active-note="activeNote"
        @note-selected="selectNote"
        @create-note="createNewNote"
        @note-contextmenu="showNoteContextMenu"
      />

      <!-- 右侧笔记编辑区域 -->
      <NoteEditor
        ref="noteEditorRef"
        :note="activeNote"
        :is-saving="isSaving"
        @save-note="saveNote"
        @delete-note="deleteNote"
        @content-change="handleContentChange"
      />
    </div>

    <!-- 创建文件夹对话框 -->
    <FolderModal
      :visible="showFolderDialog"
      @close="showFolderDialog = false"
      @confirm="createFolder"
    />

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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useOrganizationStore } from '@/stores/organization';
import { noteApi } from '@/services/api';
import type { NoteTitle, NoteDetail, NoteFolder } from '@/types/api';
import FoldersSidebar from './FoldersSidebar.vue';
import NotesSidebar from './NotesSidebar.vue';
import NoteEditor from './NoteEditor.vue';
import FolderModal from './FolderModal.vue';
import ContextMenu, { type ContextMenuItem } from '@/components/ContextMenu.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';

const authStore = useAuthStore();
const organizationStore = useOrganizationStore();

const allFolders = ref<NoteFolder[]>([]);
const selectedFolder = ref<NoteFolder | null>(null);
const notes = ref<NoteTitle[]>([]);
const activeNote = ref<NoteDetail | null>(null);
const isSaving = ref(false);
const showFolderDialog = ref(false);

// 右键菜单相关
const contextMenuVisible = ref(false);
const contextMenuPosition = ref({ x: 0, y: 0 });
const contextMenuItems = ref<ContextMenuItem[]>([]);
const selectedNote = ref<NoteTitle | null>(null);
const selectedFolderForDelete = ref<NoteFolder | null>(null);

// 确认对话框相关
const confirmDialogVisible = ref(false);
const confirmDialogTitle = ref('');
const confirmDialogMessage = ref('');
const confirmDialogAction = ref<() => void>(() => {});



// 获取所有文件夹
const loadFolders = async () => {
  if (!authStore.user) return;

  try {
    const ownerParams = organizationStore.getOwnerParams(authStore.user.id);
    const response = await noteApi.getFolders(
      ownerParams.owner_id, 
      ownerParams.is_user
    );
    if (response.success && response.data) {
      allFolders.value = response.data;
    }
  } catch (error) {
    console.error('加载文件夹失败:', error);
  }
};

// 获取文件夹下的笔记标题列表
const loadNoteTitles = async (folderId?: number) => {
  if (!authStore.user) return;

  try {
    const response = await noteApi.getNoteTitles(folderId);
    if (response.success && response.data) {
      notes.value = response.data;
    }
  } catch (error) {
    console.error('加载笔记标题失败:', error);
  }
};

// 选择文件夹
const selectFolder = async (folder: NoteFolder) => {
  selectedFolder.value = folder;
  await loadNoteTitles(folder.id);
  activeNote.value = null;
};

// 创建新笔记
const createNewNote = async () => {
  if (!authStore.user) return;

  // 检查是否选择了文件夹
  if (!selectedFolder.value) {
    showConfirmDialog(
      '提示',
      '请先选择一个文件夹',
      () => {
        // 点击确定后关闭对话框，不做其他操作
        confirmDialogVisible.value = false;
      }
    );
    return;
  }

  try {
    const ownerParams = organizationStore.getOwnerParams(authStore.user.id);
    const response = await noteApi.createNote({
      title: '新笔记',
      content: '',
      owner_id: ownerParams.owner_id,
      is_user: ownerParams.is_user,
      folder_id: selectedFolder.value?.id
    });

    if (response.success && response.data) {
      const noteTitle: NoteTitle = {
        id: response.data.id,
        title: response.data.title,
        folder_id: response.data.folder_id || undefined,
        created_at: response.data.created_at,
        updated_at: response.data.updated_at
      };
      notes.value.unshift(noteTitle);
      activeNote.value = response.data;
    }
  } catch (error) {
    console.error('创建笔记失败:', error);
  }
};

const noteEditorRef = ref<InstanceType<typeof NoteEditor> | null>(null);

// 选择笔记
const selectNote = async (note: NoteTitle) => {
  try {
    console.log("开始执行selectNote");
    const response = await noteApi.getNoteDetail(note.id);
    console.log("接收到response", response.data);
    if (response.success && response.data) {
      activeNote.value = response.data;
    }
    if (response.success) {
      await nextTick();
      console.log('noteEditorRef', noteEditorRef.value)
      // 调用子组件暴露的方法
      noteEditorRef.value?.initQuill(activeNote.value);
    }
    console.log("activeNote的值为：", activeNote);
  } catch (error) {
    console.error('获取笔记详情失败:', error);
  }
};

// 保存笔记
const saveNote = async () => {
  if (!activeNote.value || !authStore.user) return;
  console.log("进入saveNote函数");

  isSaving.value = true;
  try {
    console.log("activeNote的值为，", activeNote.value);
    const response = await noteApi.updateNote(activeNote.value.id, {
      title: activeNote.value.title,
      content: activeNote.value.content
    });

    if (response.success && response.data) {
      const index = notes.value.findIndex(n => n.id === activeNote.value!.id);
      if (index !== -1) {
        notes.value[index] = {
          id: response.data.id,
          title: response.data.title,
          folder_id: response.data.folder_id || undefined,
          created_at: response.data.created_at,
          updated_at: response.data.updated_at
        };
      }
    }
  } catch (error) {
    console.error('保存笔记失败:', error);
  } finally {
    isSaving.value = false;
  }
};

// 删除笔记
const deleteNote = async () => {
  if (!activeNote.value || !authStore.user) return;

  if (!confirm('确定要删除这个笔记吗？')) return;

  try {
    const response = await noteApi.deleteNote(activeNote.value.id);
    if (response.success) {
      notes.value = notes.value.filter(n => n.id !== activeNote.value!.id);
      activeNote.value = null;
    }
  } catch (error) {
    console.error('删除笔记失败:', error);
  }
};

// 创建文件夹
const createFolder = async (name: string) => {
  if (!name.trim() || !authStore.user) return;

  try {
    const ownerParams = organizationStore.getOwnerParams(authStore.user.id);
    const response = await noteApi.createFolder({
      name: name.trim(),
      owner_id: ownerParams.owner_id,
      is_user: ownerParams.is_user
    });

    if (response.success && response.data) {
      allFolders.value.push(response.data);
      showFolderDialog.value = false;
    }
  } catch (error) {
    console.error('创建文件夹失败:', error);
  }
};

// 内容变化时自动保存（防抖，10秒间隔）
let saveTimeout: number | null = null;
const handleContentChange = (newContent: string) => {
  console.log('[Debug] handleContentChange: newContent =', newContent);
  if (activeNote.value) {
    activeNote.value.content = newContent; // 更新 activeNote
    console.log('[Debug] activeNote.value 更新为', activeNote.value);
  }
  if (saveTimeout) {
    clearTimeout(saveTimeout);
  }
  saveTimeout = setTimeout(() => {
    if (activeNote.value) {
      saveNote();
    }
  }, 10000);
};

// 监听选中的文件夹变化
watch(selectedFolder, () => {
  activeNote.value = null;
});

watch(activeNote, (val) => {
  console.log("activeNote变化：", val);
}, { deep: true });

// 显示文件夹右键菜单
const showFolderContextMenu = (event: MouseEvent, folder: NoteFolder) => {
  console.log('文件夹右键菜单被触发', folder.name);
  event.preventDefault();
  event.stopPropagation(); // <- 很重要，阻止 document 上的 contextmenu 监听器干扰
  selectedFolderForDelete.value = folder;
  selectedNote.value = null;
  
  contextMenuPosition.value = { x: event.clientX, y: event.clientY };
  contextMenuItems.value = [
    {
      label: '删除文件夹',
      action: () => showConfirmDialog(
        '删除文件夹',
        `确定要删除文件夹 "${folder.name}" 吗？此操作将删除该文件夹下的所有笔记和附件。`,
        deleteFolder
      )
    }
  ];
  contextMenuVisible.value = true;
  console.log('右键菜单状态:', contextMenuVisible.value);
};

// 显示笔记右键菜单
const showNoteContextMenu = (event: MouseEvent, note: NoteTitle) => {
  console.log('笔记右键菜单被触发', note.title);
  event.preventDefault();
  event.stopPropagation(); // <- 很重要，阻止 document 上的 contextmenu 监听器干扰
  selectedNote.value = note;
  selectedFolderForDelete.value = null;
  
  contextMenuPosition.value = { x: event.clientX, y: event.clientY };
  contextMenuItems.value = [
    {
      label: '删除笔记',
      action: () => showConfirmDialog(
        '删除笔记',
        `确定要删除笔记 "${note.title}" 吗？此操作将删除该笔记的所有附件。`,
        deleteSelectedNote
      )
    }
  ];
  contextMenuVisible.value = true;
  console.log('右键菜单状态:', contextMenuVisible.value);
};

// 显示确认对话框
const showConfirmDialog = (title: string, message: string, action: () => void) => {
  confirmDialogTitle.value = title;
  confirmDialogMessage.value = message;
  confirmDialogAction.value = action;
  confirmDialogVisible.value = true;
  contextMenuVisible.value = false;
};

// 删除文件夹
const deleteFolder = async () => {
  if (!selectedFolderForDelete.value) return;
  
  try {
    const response = await noteApi.deleteFolder(selectedFolderForDelete.value.id);
    
    if (response.success) {
      // 从列表中移除
      allFolders.value = allFolders.value.filter(
        f => f.id !== selectedFolderForDelete.value!.id
      );
      
      // 如果删除的是当前选中的文件夹，清空当前文件夹
      if (selectedFolder.value?.id === selectedFolderForDelete.value.id) {
        selectedFolder.value = null;
        await loadNoteTitles();
      }
    }
  } catch (error) {
    console.error('删除文件夹失败:', error);
  }
};

// 删除选中的笔记
const deleteSelectedNote = async () => {
  if (!selectedNote.value) return;
  
  try {
    const response = await noteApi.deleteNote(selectedNote.value.id);
    
    if (response.success) {
      // 从列表中移除
      notes.value = notes.value.filter(n => n.id !== selectedNote.value!.id);
      
      // 如果删除的是当前选中的笔记，清空当前笔记
      if (activeNote.value?.id === selectedNote.value.id) {
        activeNote.value = null;
      }
    }
  } catch (error) {
    console.error('删除笔记失败:', error);
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

// 重新加载笔记数据
const reloadNotes = async () => {
  // 清空当前选中的文件夹、笔记和活动笔记
  selectedFolder.value = null;
  activeNote.value = null;
  notes.value = [];
  allFolders.value = [];
  
  // 重新加载文件夹和笔记列表
  await loadFolders();
  await loadNoteTitles();
};

onMounted(async () => {
  // 初始化组织状态
  organizationStore.initOrganization();
  
  // 添加组织切换监听器
  organizationStore.addOrganizationChangeListener(reloadNotes);
  
  await loadFolders();
  await loadNoteTitles();
});

// 组件卸载时移除监听器
onUnmounted(() => {
  organizationStore.removeOrganizationChangeListener(reloadNotes);
});
</script>

<style scoped>
.notes-view {
  height: 100%;
  background: white;
}

.notes-container {
  display: flex;
  height: 100%;
}

</style>
