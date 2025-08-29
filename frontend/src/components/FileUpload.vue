<template>
  <div class="upload-container">
    <!-- Header -->
    <div class="header">
      <div class="header-content">
        <h1 class="title">文件上传</h1>
        <Button 
          variant="outline" 
          color="primary" 
          size="sm"
          @click="goToChat"
        >
          返回聊天
        </Button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Left Panel: Upload Section -->
      <div class="left-panel">
        <div class="upload-section">
          <div class="upload-area" @click="openFileDialog" @dragover.prevent @drop.prevent="handleDrop">
            <input 
              ref="fileInput" 
              type="file" 
              multiple 
              accept=".pdf,.doc,.docx,.txt"
              @change="handleFileSelect"
              style="display: none"
            />
            <div class="upload-icon">
              <i class="icon icon-upload" style="font-size: 48px; color: #6366f1;"></i>
            </div>
            <h3 class="upload-title">选择文件上传</h3>
            <p class="upload-description">点击选择文件或拖拽文件到此处</p>
            <p class="upload-formats">支持 PDF、Word、TXT 格式</p>
          </div>
        </div>

        <!-- Upload Progress -->
        <div v-if="uploadingFiles.length > 0" class="progress-section">
          <h3 class="section-title">正在上传</h3>
          <div class="file-list">
            <div 
              v-for="file in uploadingFiles" 
              :key="file.id"
              class="file-item uploading"
            >
              <div class="file-info">
                <div class="file-name">{{ file.name }}</div>
                <div class="file-size">{{ formatFileSize(file.size) }}</div>
              </div>
              <div class="file-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: file.progress + '%' }"></div>
                </div>
                <span class="progress-text">{{ file.progress }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Panel: Files List -->
      <div class="right-panel">
        <!-- Uploaded Files List -->
        <div v-if="uploadedFiles.length > 0" class="files-section">
          <div class="section-header">
            <h3 class="section-title">已上传文件 ({{ uploadedFiles.length }})</h3>
            <Button 
              variant="text" 
              color="danger" 
              size="sm"
              @click="clearAllFiles"
            >
              清空全部
            </Button>
          </div>
          <div class="file-list">
            <div 
              v-for="file in uploadedFiles" 
              :key="file.id"
              class="file-item completed"
            >
              <div class="file-info">
                <div class="file-name">{{ file.name }}</div>
                <div class="file-meta">
                  <span class="file-size">{{ formatFileSize(file.size) }}</span>
                  <span class="file-date">{{ formatDate(file.uploadTime) }}</span>
                </div>
              </div>
              <div class="file-actions">
                <Button 
                  variant="text" 
                  color="danger" 
                  size="sm"
                  @click="deleteFile(file.id)"
                >
                  删除
                </Button>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="empty-state">
          <i class="icon icon-file" style="font-size: 64px; color: #d1d5db; margin-bottom: 16px;"></i>
          <p class="empty-text">还没有上传任何文件</p>
          <p class="empty-subtext">上传文件后可以在AI聊天中使用文档内容</p>
        </div>
      </div>
    </div>

    <!-- Error Toast -->
    <div v-if="errorMessage" class="error-toast">
      <i class="icon icon-close"></i>
      {{ errorMessage }}
      <Button 
        variant="text" 
        size="sm"
        @click="errorMessage = ''"
        style="margin-left: auto; color: inherit;"
      >
        ✕
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from 'vue-devui/button'
import 'vue-devui/button/style.css'
import { FileUploadService } from '../services/fileUploadService'

// Router
const router = useRouter()

// Types
interface UploadingFile {
  id: string
  name: string
  size: number
  progress: number
  file: File
}

interface UploadedFile {
  id: number
  name: string
  size: number
  uploadTime: Date
}

// Reactive state
const fileInput = ref<HTMLInputElement>()
const uploadingFiles = ref<UploadingFile[]>([])
const uploadedFiles = ref<UploadedFile[]>([])
const errorMessage = ref('')

// Navigation
const goToChat = () => {
  router.push('/')
}

// File handling
const openFileDialog = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    handleFiles(Array.from(target.files))
  }
}

const handleDrop = (event: DragEvent) => {
  const files = event.dataTransfer?.files
  if (files) {
    handleFiles(Array.from(files))
  }
}

const handleFiles = async (files: File[]) => {
  // Validate file types
  const allowedTypes = ['.pdf', '.doc', '.docx', '.txt']
  const validFiles = files.filter(file => {
    const extension = '.' + file.name.split('.').pop()?.toLowerCase()
    return allowedTypes.includes(extension)
  })

  if (validFiles.length !== files.length) {
    errorMessage.value = '只支持 PDF、Word、TXT 格式的文件'
    setTimeout(() => errorMessage.value = '', 3000)
  }

  // Process valid files
  for (const file of validFiles) {
    await uploadFile(file)
  }
}

const uploadFile = async (file: File) => {
  const uploadingFile: UploadingFile = {
    id: Date.now() + Math.random().toString(),
    name: file.name,
    size: file.size,
    progress: 0,
    file: file
  }

  uploadingFiles.value.push(uploadingFile)

  try {
    // Simulate progress
    const progressInterval = setInterval(() => {
      if (uploadingFile.progress < 90) {
        uploadingFile.progress += Math.random() * 20
      }
    }, 200)

    // Upload file
    const response = await FileUploadService.uploadFile(file)
    
    clearInterval(progressInterval)
    uploadingFile.progress = 100

    // Move to uploaded files
    setTimeout(() => {
      uploadingFiles.value = uploadingFiles.value.filter(f => f.id !== uploadingFile.id)
      uploadedFiles.value.unshift({
        id: response.file_id,
        name: response.filename,
        size: response.size,
        uploadTime: new Date()
      })
    }, 500)

  } catch (error) {
    // Remove from uploading list and show error
    uploadingFiles.value = uploadingFiles.value.filter(f => f.id !== uploadingFile.id)
    errorMessage.value = `上传失败: ${file.name} - ${error instanceof Error ? error.message : '未知错误'}`
    setTimeout(() => errorMessage.value = '', 5000)
  }
}

const deleteFile = async (fileId: number) => {
  try {
    await FileUploadService.deleteFile(fileId)
    uploadedFiles.value = uploadedFiles.value.filter(f => f.id !== fileId)
  } catch (error) {
    errorMessage.value = `删除失败: ${error instanceof Error ? error.message : '未知错误'}`
    setTimeout(() => errorMessage.value = '', 3000)
  }
}

const clearAllFiles = async () => {
  if (confirm('确定要删除所有已上传的文件吗？')) {
    try {
      for (const file of uploadedFiles.value) {
        await FileUploadService.deleteFile(file.id)
      }
      uploadedFiles.value = []
    } catch (error) {
      errorMessage.value = `清空失败: ${error instanceof Error ? error.message : '未知错误'}`
      setTimeout(() => errorMessage.value = '', 3000)
    }
  }
}

// Utility functions
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (date: Date): string => {
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Load existing files
const loadUploadedFiles = async () => {
  try {
    const files = await FileUploadService.getUploadedFiles()
    uploadedFiles.value = files
  } catch (error) {
    console.error('Failed to load uploaded files:', error)
  }
}

// Lifecycle
onMounted(() => {
  loadUploadedFiles()
})
</script>

<style scoped>
.upload-container {
  min-height: 100vh;
  background: white;
  display: flex;
  flex-direction: column;
}

.header {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 16px 24px;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
}

.main-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 8px;
  display: flex;
  gap: 12px;
  min-height: calc(100vh - 80px);
}

.left-panel {
  flex: 1;
  min-width: 0;
  max-width: 50%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.right-panel {
  flex: 1;
  min-width: 0;
  max-width: 50%;
}

.upload-section {
  display: flex;
  justify-content: center;
}

.upload-area {
  background: white;
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 24px 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
}

.upload-area:hover {
  border-color: #6366f1;
  background: #f8fafc;
}

.upload-icon {
  margin-bottom: 12px;
}

.upload-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.upload-description {
  margin: 0 0 6px 0;
  color: #64748b;
  font-size: 14px;
}

.upload-formats {
  margin: 0;
  font-size: 12px;
  color: #9ca3af;
}

.progress-section,
.files-section {
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  height: fit-content;
}

.section-header {
  background: #f8fafc;
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  padding: 12px 16px 0;
}

.progress-section .section-title {
  padding: 0;
}

.file-list {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  background: #fafafa;
  font-size: 14px;
}

.file-item.uploading {
  background: #f5f3ff;
  border-color: #c7d2fe;
}

.file-item.completed {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 13px;
  font-weight: 500;
  color: #1e293b;
  word-break: break-all;
  margin-bottom: 4px;
}

.file-size {
  font-size: 11px;
  color: #64748b;
}

.file-meta {
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: #64748b;
}

.file-date {
  color: #9ca3af;
}

.file-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 100px;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #6366f1;
  transition: width 0.3s ease;
  border-radius: 2px;
}

.progress-text {
  font-size: 11px;
  color: #64748b;
  font-weight: 500;
  min-width: 30px;
}

.file-actions {
  display: flex;
  align-items: center;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #9ca3af;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  height: fit-content;
}

.empty-text {
  margin: 0 0 6px 0;
  font-size: 16px;
  font-weight: 500;
  color: #6b7280;
}

.empty-subtext {
  margin: 0;
  font-size: 13px;
  color: #9ca3af;
}

.error-toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: 12px 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-width: 400px;
}

@media (max-width: 750px) {
  .main-content {
    flex-direction: column;
    padding: 12px 8px;
    gap: 12px;
  }
  
  .header {
    padding: 12px 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .upload-area {
    padding: 20px 12px;
  }
  
  .file-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .file-progress {
    width: 100%;
    min-width: 0;
  }
  
  .left-panel,
  .right-panel {
    flex: none;
    min-width: 0;
    max-width: none;
  }
}
</style>
