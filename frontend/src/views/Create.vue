<template>
  <div class="create-page">
    <el-row :gutter="20">
      <el-col :span="16">
        <div class="create-main">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>创建PPT</span>
                <el-radio-group v-model="inputType" size="small">
                  <el-radio-button label="text">文本描述</el-radio-button>
                  <el-radio-button label="outline">大纲结构</el-radio-button>
                  <el-radio-button label="document">文档上传</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            
            <div class="input-area">
              <template v-if="inputType === 'text'">
                <el-input
                  v-model="textDescription"
                  type="textarea"
                  :rows="8"
                  placeholder="请描述您的PPT主题和内容要求...&#10;&#10;例如：制作一份关于人工智能发展史的演讲PPT，包含5-8页，需要时间轴展示"
                />
                <div class="input-options">
                  <el-input-number
                    v-model="pageCount"
                    :min="1"
                    :max="50"
                    label="页数"
                  />
                </div>
              </template>
              
              <template v-else-if="inputType === 'outline'">
                <el-input
                  v-model="outlineTitle"
                  placeholder="PPT标题"
                  class="outline-title"
                />
                <div class="outline-editor">
                  <div
                    v-for="(page, index) in outlinePages"
                    :key="index"
                    class="outline-page"
                  >
                    <div class="page-header">
                      <span>第 {{ index + 1 }} 页</span>
                      <el-button
                        type="text"
                        @click="removeOutlinePage(index)"
                        :icon="Delete"
                      />
                    </div>
                    <el-input
                      v-model="page.title"
                      placeholder="页面标题"
                    />
                    <el-input
                      v-model="page.content"
                      type="textarea"
                      :rows="3"
                      placeholder="页面内容要点（每行一个要点）"
                    />
                  </div>
                  <el-button
                    type="primary"
                    text
                    @click="addOutlinePage"
                    :icon="Plus"
                  >
                    添加页面
                  </el-button>
                </div>
              </template>
              
              <template v-else>
                <el-upload
                  ref="uploadRef"
                  drag
                  :auto-upload="false"
                  :limit="1"
                  :on-change="handleFileChange"
                  accept=".doc,.docx,.pdf,.md,.txt"
                >
                  <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                  <div class="el-upload__text">
                    拖拽文件到此处，或 <em>点击上传</em>
                  </div>
                  <template #tip>
                    <div class="el-upload__tip">
                      支持 Word、PDF、Markdown、TXT 格式，文件大小不超过 10MB
                    </div>
                  </template>
                </el-upload>
              </template>
            </div>
          </el-card>
        </div>
      </el-col>
      
      <el-col :span="8">
        <div class="create-sidebar">
          <el-card>
            <template #header>
              <span>生成设置</span>
            </template>
            
            <el-form label-position="top">
              <el-form-item label="选择模板">
                <div style="display: flex; gap: 8px;">
                  <el-select
                    v-model="selectedTemplateId"
                    :label="selectedTemplateName"
                    placeholder="选择模板"
                    style="width: 100%"
                    @change="onTemplateChange"
                    filterable
                  >
                    <el-option
                      v-for="item in templateOptions"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                    />
                  </el-select>
                  <el-button :icon="Refresh" circle @click="loadTemplates" title="刷新模板" />
                </div>
              </el-form-item>
              
              <el-form-item label="AI模型">
                <el-radio-group v-model="selectedModel">
                  <el-radio label="qwen">
                    千问
                    <el-tag v-if="!userStore.isMember" size="small" type="info">免费</el-tag>
                  </el-radio>
                  <el-radio label="kimi" :disabled="!userStore.isMember">
                    Kimi
                    <el-tag size="small" type="warning">会员</el-tag>
                  </el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item>
                <el-button
                  type="primary"
                  size="large"
                  :loading="generating"
                  @click="handleGenerate"
                  style="width: 100%"
                >
                  {{ generating ? '生成中...' : '开始生成' }}
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
          
          <el-card v-if="generating" class="progress-card">
            <template #header>
              <span>生成进度</span>
            </template>
            <el-progress
              :percentage="progress"
              :status="progressStatus"
            />
            <p class="progress-message">{{ progressMessage }}</p>
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch, toRaw, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { pptApi } from '@/api/ppt'
import { templateApi } from '@/api/template'
import { ElMessage } from 'element-plus'
import { Delete, Plus, UploadFilled, Refresh } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const inputType = ref('text')
const textDescription = ref('')
const pageCount = ref(8)
const outlineTitle = ref('')
const outlinePages = ref([
  { title: '', content: '' }
])
const selectedTemplateId = ref(null)
const selectedTemplate = ref(null)
const selectedModel = ref('qwen')
const templates = ref([])
const generating = ref(false)
const progress = ref(0)
const progressMessage = ref('')
const progressStatus = ref('')
const uploadRef = ref()
const uploadedFile = ref(null)

const templateOptions = computed(() => {
  return templates.value.map(t => ({
    value: t.id,
    label: t.name
  }))
})

const selectedTemplateName = computed(() => {
  const template = templates.value.find(t => t.id === selectedTemplateId.value)
  return template?.name || ''
})

function onTemplateChange(val) {
  console.log('Template changed to:', val)
  selectedTemplate.value = templates.value.find(t => t.id === val) || null
}

let pollInterval = null

onMounted(async () => {
  await loadTemplates()
})

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})

async function loadTemplates() {
  try {
    const response = await templateApi.getTemplates({ page: 1, page_size: 50 })
    console.log('Loaded templates:', response)
    templates.value = response.items
    if (templates.value.length > 0) {
      await nextTick()
      
      const templateIdFromQuery = route.query.template_id
      const targetId = templateIdFromQuery ? parseInt(templateIdFromQuery) : templates.value[0].id
      
      const targetTemplate = templates.value.find(t => t.id === targetId)
      if (targetTemplate) {
        selectedTemplateId.value = targetTemplate.id
        selectedTemplate.value = targetTemplate
        console.log('Selected template from query:', targetId, targetTemplate.name)
      } else {
        selectedTemplateId.value = templates.value[0].id
        selectedTemplate.value = templates.value[0]
      }
    }
  } catch (error) {
    console.error('Failed to load templates:', error)
    ElMessage.error('加载模板失败')
  }
}

function addOutlinePage() {
  outlinePages.value.push({ title: '', content: '' })
}

function removeOutlinePage(index) {
  outlinePages.value.splice(index, 1)
}

function handleFileChange(file) {
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过10MB')
    return
  }
  uploadedFile.value = file.raw
}

async function handleGenerate() {
  if (!validateInput()) return
  
  generating.value = true
  progress.value = 0
  progressMessage.value = '正在提交任务...'
  progressStatus.value = ''
  
  const templateId = selectedTemplateId.value
  console.log('Generating PPT with templateId:', templateId)
  
  try {
    let response
    
    if (inputType.value === 'text') {
      response = await pptApi.generateByText({
        description: textDescription.value,
        template_id: templateId,
        ai_model: selectedModel.value,
        page_count: pageCount.value
      })
    } else if (inputType.value === 'outline') {
      const outline = outlinePages.value.map((page, index) => ({
        page_index: index + 1,
        title: page.title,
        content: page.content.split('\n').filter(c => c.trim()),
        layout_type: 'single_column'
      }))
      
      response = await pptApi.generateByOutline({
        title: outlineTitle.value,
        outline,
        template_id: templateId,
        ai_model: selectedModel.value
      })
    } else {
      if (!uploadedFile.value) {
        ElMessage.error('请上传文件')
        generating.value = false
        return
      }
      
      const formData = new FormData()
      formData.append('file', uploadedFile.value)
      formData.append('ai_model', selectedModel.value)
      if (templateId) {
        formData.append('template_id', templateId)
      }
      
      response = await pptApi.generateByDocument(formData)
    }
    
    pollGenerationStatus(response.task_id, response.project_id)
  } catch (error) {
    console.error('Generation error:', error)
    generating.value = false
    progressStatus.value = 'exception'
    // 显示具体的错误信息
    if (error.response && error.response.data && error.response.data.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('请求失败，请检查网络或重试')
    }
  }
}

function validateInput() {
  if (inputType.value === 'text') {
    if (!textDescription.value.trim()) {
      ElMessage.error('请输入PPT描述')
      return false
    }
    if (textDescription.value.length < 10) {
      ElMessage.error('描述内容太短，请详细描述您的需求')
      return false
    }
  } else if (inputType.value === 'outline') {
    if (!outlineTitle.value.trim()) {
      ElMessage.error('请输入PPT标题')
      return false
    }
    if (outlinePages.value.length === 0) {
      ElMessage.error('请添加至少一页内容')
      return false
    }
  }
  return true
}

async function pollGenerationStatus(taskId, projectId) {
  progressMessage.value = '正在生成PPT...'
  progress.value = 10
  
  pollInterval = setInterval(async () => {
    try {
      const status = await pptApi.getGenerationStatus(taskId)
      progress.value = status.progress
      progressMessage.value = status.message
      
      if (status.status === 'completed') {
        clearInterval(pollInterval)
        generating.value = false
        progressStatus.value = 'success'
        ElMessage.success('PPT生成成功')
        router.push(`/editor/${projectId}`) // 这里跳转到编辑器页面
      } else if (status.status === 'failed') {
        clearInterval(pollInterval)
        generating.value = false
        progressStatus.value = 'exception'
        ElMessage.error(status.message || '生成失败')
      }
    } catch (error) {
      console.error(error)
      // 如果连续多次失败，可以考虑停止轮询
      // 这里暂时只记录错误，不中断，因为网络波动可能是暂时的
    }
  }, 2000)
}
</script>

<style lang="scss" scoped>
.create-page {
  max-width: 1400px;
  margin: 0 auto;
}

.create-main {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .input-area {
    min-height: 400px;
  }
  
  .input-options {
    margin-top: 16px;
  }
}

.outline-title {
  margin-bottom: 16px;
}

.outline-editor {
  .outline-page {
    background: #f5f7fa;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    
    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      font-weight: 500;
      color: #606266;
    }
    
    .el-input {
      margin-bottom: 12px;
    }
  }
}

.create-sidebar {
  .progress-card {
    margin-top: 20px;
    
    .progress-message {
      margin-top: 12px;
      color: #909399;
      font-size: 14px;
    }
  }
}
</style>

<style lang="scss">
.el-select {
  .el-input__wrapper {
    .el-input__inner {
      color: #606266 !important;
    }
  }
}
</style>
