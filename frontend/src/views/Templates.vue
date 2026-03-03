<template>
  <div class="templates-page">
    <div class="page-header">
      <h1>模板中心</h1>
      <p>选择精美模板，快速创建专业PPT</p>
    </div>
    
    <div class="filters">
      <el-radio-group v-model="selectedCategory" @change="loadTemplates">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button
          v-for="category in categories"
          :key="category.value"
          :label="category.value"
        >
          {{ category.label }}
        </el-radio-button>
      </el-radio-group>
      
      <div class="filter-actions">
        <el-checkbox v-model="showPremiumOnly" @change="loadTemplates">
          仅显示会员模板
        </el-checkbox>
        <el-button type="primary" @click="showUploadDialog = true">
          <el-icon><Plus /></el-icon>
          上传模板
        </el-button>
      </div>
    </div>
    
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="系统模板" name="system">
        <div class="templates-grid" v-loading="loading">
          <div
            v-for="template in templates"
            :key="template.id"
            class="template-card"
            @click="handleSelect(template)"
          >
            <div class="template-preview" :style="getPreviewStyle(template)">
              <img v-if="template.thumbnail_url" :src="template.thumbnail_url" />
              <div v-else class="placeholder-preview">
                <div class="color-preview" :style="getPreviewStyle(template)"></div>
              </div>
              <div class="template-badge" v-if="template.is_premium">
                <el-tag type="warning" size="small">会员</el-tag>
              </div>
            </div>
            <div class="template-info">
              <h3>{{ template.name }}</h3>
              <p class="template-desc" v-if="template.description">{{ template.description }}</p>
              <div class="template-meta">
                <span>
                  <el-icon><Download /></el-icon>
                  {{ template.download_count }}
                </span>
                <span>
                  <el-icon><Star /></el-icon>
                  {{ template.rating }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="我的模板" name="my">
        <div class="templates-grid" v-loading="loadingMyTemplates">
          <div
            v-for="template in myTemplates"
            :key="template.id"
            class="template-card my-template"
          >
            <div class="template-preview" :style="getPreviewStyle(template)">
              <img v-if="template.thumbnail_url" :src="template.thumbnail_url" />
              <div v-else class="placeholder-preview">
                <div class="color-preview" :style="getPreviewStyle(template)"></div>
              </div>
              <div class="template-actions">
                <el-button type="primary" size="small" @click.stop="handleUseTemplate(template)">
                  使用
                </el-button>
                <el-button type="danger" size="small" @click.stop="handleDeleteTemplate(template)">
                  删除
                </el-button>
              </div>
            </div>
            <div class="template-info">
              <h3>{{ template.name }}</h3>
              <p class="template-desc" v-if="template.description">{{ template.description }}</p>
              <div class="template-meta">
                <span>{{ getCategoryLabel(template.category) }}</span>
              </div>
            </div>
          </div>
          
          <div v-if="myTemplates.length === 0 && !loadingMyTemplates" class="empty-state">
            <el-empty description="暂无自定义模板">
              <el-button type="primary" @click="showUploadDialog = true">上传模板</el-button>
            </el-empty>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <div class="pagination" v-if="total > pageSize && activeTab === 'system'">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadTemplates"
      />
    </div>
    
    <el-dialog v-model="showUploadDialog" title="上传模板" width="600px">
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="模板名称" required>
          <el-input v-model="uploadForm.name" placeholder="请输入模板名称" />
        </el-form-item>
        
        <el-form-item label="模板分类" required>
          <el-select v-model="uploadForm.category" placeholder="请选择分类">
            <el-option
              v-for="category in categories"
              :key="category.value"
              :label="category.label"
              :value="category.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="模板描述">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模板描述"
          />
        </el-form-item>
        
        <el-form-item label="主题颜色">
          <div class="color-pickers">
            <div class="color-item">
              <span>主色</span>
              <el-color-picker v-model="uploadForm.primaryColor" />
            </div>
            <div class="color-item">
              <span>辅色</span>
              <el-color-picker v-model="uploadForm.secondaryColor" />
            </div>
            <div class="color-item">
              <span>强调色</span>
              <el-color-picker v-model="uploadForm.accentColor" />
            </div>
            <div class="color-item">
              <span>背景色</span>
              <el-color-picker v-model="uploadForm.backgroundColor" />
            </div>
          </div>
        </el-form-item>
        
        <el-form-item label="缩略图">
          <el-upload
            class="thumbnail-uploader"
            :show-file-list="false"
            :before-upload="beforeThumbnailUpload"
            :http-request="handleThumbnailUpload"
          >
            <img v-if="uploadForm.thumbnailUrl" :src="uploadForm.thumbnailUrl" class="thumbnail-preview" />
            <el-icon v-else class="thumbnail-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUploadTemplate" :loading="uploading">
          创建模板
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { templateApi } from '@/api/template'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Picture, Download, Star, Plus } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const loadingMyTemplates = ref(false)
const templates = ref([])
const myTemplates = ref([])
const categories = ref([])
const selectedCategory = ref('')
const showPremiumOnly = ref(false)
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)
const activeTab = ref('system')

const showUploadDialog = ref(false)
const uploading = ref(false)
const uploadForm = ref({
  name: '',
  category: '',
  description: '',
  primaryColor: '#0070C0',
  secondaryColor: '#44546A',
  accentColor: '#FFC000',
  backgroundColor: '#FFFFFF',
  thumbnailUrl: ''
})

onMounted(async () => {
  await loadCategories()
  await loadTemplates()
})

async function loadCategories() {
  try {
    categories.value = await templateApi.getCategories()
  } catch (error) {
    console.error(error)
  }
}

async function loadTemplates() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }
    
    if (showPremiumOnly.value) {
      params.is_premium = true
    }
    
    const response = await templateApi.getTemplates(params)
    templates.value = response.items
    total.value = response.total
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

async function loadMyTemplates() {
  loadingMyTemplates.value = true
  try {
    const response = await templateApi.getMyTemplates()
    myTemplates.value = response.items
  } catch (error) {
    console.error(error)
  } finally {
    loadingMyTemplates.value = false
  }
}

function handleTabChange(tab) {
  if (tab === 'my') {
    loadMyTemplates()
  }
}

function handleSelect(template) {
  if (template.is_premium && !userStore.isMember) {
    ElMessage.warning('该模板仅限会员使用')
    return
  }
  
  router.push({
    path: '/create',
    query: { template_id: template.id }
  })
}

function handleUseTemplate(template) {
  router.push({
    path: '/create',
    query: { template_id: template.id }
  })
}

async function handleDeleteTemplate(template) {
  try {
    await ElMessageBox.confirm('确定要删除该模板吗？', '提示', {
      type: 'warning'
    })
    
    await templateApi.deleteTemplate(template.id)
    ElMessage.success('删除成功')
    loadMyTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function getPreviewStyle(template) {
  const data = template.template_data || {}
  const primary = rgbToHex(data.primary_color) || '#0070C0'
  const bgColor = rgbToHex(data.background_color) || '#FFFFFF'
  return {
    background: `linear-gradient(135deg, ${bgColor} 50%, ${primary} 100%)`
  }
}

function getGradientStyle(template) {
  const data = template.template_data || {}
  const primary = rgbToHex(data.primary_color) || '#0070C0'
  const secondary = rgbToHex(data.secondary_color) || '#44546A'
  return `linear-gradient(135deg, ${primary} 0%, ${secondary} 100%)`
}

function rgbToHex(rgb) {
  if (!rgb) return null
  if (typeof rgb === 'string') return rgb
  if (Array.isArray(rgb)) {
    return '#' + rgb.map(x => {
      const hex = Math.min(255, Math.max(0, x)).toString(16)
      return hex.length === 1 ? '0' + hex : hex
    }).join('')
  }
  return null
}

function getCategoryLabel(value) {
  const category = categories.value.find(c => c.value === value)
  return category ? category.label : value
}

function beforeThumbnailUpload(file) {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  return true
}

async function handleThumbnailUpload(options) {
  try {
    const formData = new FormData()
    formData.append('file', options.file)
    
    const response = await templateApi.uploadThumbnail(formData)
    uploadForm.value.thumbnailUrl = response.thumbnail_url
    ElMessage.success('上传成功')
  } catch (error) {
    ElMessage.error('上传失败')
  }
}

async function handleUploadTemplate() {
  if (!uploadForm.value.name) {
    ElMessage.warning('请输入模板名称')
    return
  }
  
  if (!uploadForm.value.category) {
    ElMessage.warning('请选择模板分类')
    return
  }
  
  uploading.value = true
  try {
    const hexToRgb = (hex) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
      return result ? [
        parseInt(result[1], 16),
        parseInt(result[2], 16),
        parseInt(result[3], 16)
      ] : null
    }
    
    await templateApi.createTemplate({
      name: uploadForm.value.name,
      category: uploadForm.value.category,
      description: uploadForm.value.description,
      thumbnail_url: uploadForm.value.thumbnailUrl,
      template_data: {
        theme: `custom_${Date.now()}`,
        primary_color: hexToRgb(uploadForm.value.primaryColor),
        secondary_color: hexToRgb(uploadForm.value.secondaryColor),
        accent_color: hexToRgb(uploadForm.value.accentColor),
        background_color: hexToRgb(uploadForm.value.backgroundColor),
        title_font: '微软雅黑',
        body_font: '微软雅黑'
      }
    })
    
    ElMessage.success('创建成功')
    showUploadDialog.value = false
    
    uploadForm.value = {
      name: '',
      category: '',
      description: '',
      primaryColor: '#0070C0',
      secondaryColor: '#44546A',
      accentColor: '#FFC000',
      backgroundColor: '#FFFFFF',
      thumbnailUrl: ''
    }
    
    if (activeTab.value === 'my') {
      loadMyTemplates()
    }
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    uploading.value = false
  }
}
</script>

<style lang="scss" scoped>
.templates-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  
  h1 {
    font-size: 32px;
    color: #303133;
    margin-bottom: 8px;
  }
  
  p {
    color: #909399;
    font-size: 16px;
  }
}

.filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  .filter-actions {
    display: flex;
    align-items: center;
    gap: 16px;
  }
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  min-height: 300px;
}

.template-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }
  
  .template-preview {
    position: relative;
    height: 140px;
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .placeholder-preview {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      
      .color-preview {
        width: 100%;
        height: 100%;
      }
    }
    
    .template-badge {
      position: absolute;
      top: 8px;
      right: 8px;
    }
    
    .template-actions {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      opacity: 0;
      transition: opacity 0.3s;
    }
  }
  
  &:hover .template-actions {
    opacity: 1;
  }
  
  .template-info {
    padding: 16px;
    
    h3 {
      font-size: 16px;
      color: #303133;
      margin-bottom: 4px;
    }
    
    .template-desc {
      font-size: 12px;
      color: #909399;
      margin-bottom: 8px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    
    .template-meta {
      display: flex;
      gap: 16px;
      font-size: 12px;
      color: #909399;
      
      span {
        display: flex;
        align-items: center;
        gap: 4px;
      }
    }
  }
}

.empty-state {
  grid-column: 1 / -1;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.pagination {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

.color-pickers {
  display: flex;
  gap: 16px;
  
  .color-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    
    span {
      font-size: 12px;
      color: #606266;
    }
  }
}

.thumbnail-uploader {
  :deep(.el-upload) {
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    width: 178px;
    height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &:hover {
      border-color: #409eff;
    }
  }
  
  .thumbnail-preview {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .thumbnail-uploader-icon {
    font-size: 28px;
    color: #8c939d;
  }
}
</style>
