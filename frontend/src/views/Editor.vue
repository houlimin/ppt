<template>
  <div class="editor-page">
    <div class="editor-header">
      <div class="header-left">
        <el-button @click="router.back()" :icon="ArrowLeft">返回</el-button>
        <el-input
          v-model="projectTitle"
          class="title-input"
          placeholder="PPT标题"
          @blur="saveProject"
        />
      </div>
      <div class="header-right">
        <!-- 移除 v-if="projectTitle" 或类似的条件判断，确保按钮始终显示 -->
        <el-button type="primary" @click="handleExport" :loading="exporting">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>
    
    <div class="editor-main">
      <div class="slides-panel">
        <div class="slides-header">
          <span>幻灯片</span>
          <el-button type="text" size="small" @click="addSlide">
            <el-icon><Plus /></el-icon>
          </el-button>
        </div>
        <div class="slides-list">
          <div
            v-for="(slide, index) in slides"
            :key="index"
            :class="['slide-thumb', { active: currentSlideIndex === index }]"
            @click="currentSlideIndex = index"
          >
            <div class="slide-number">{{ index + 1 }}</div>
            <div class="slide-preview">
              <div class="preview-title">{{ slide.title }}</div>
            </div>
            <el-button
              class="delete-btn"
              type="danger"
              size="small"
              :icon="Delete"
              circle
              @click.stop="removeSlide(index)"
            />
          </div>
        </div>
      </div>
      
      <div class="editor-content">
        <div class="slide-editor" v-if="currentSlide">
          <el-form label-position="top">
            <el-form-item label="页面标题">
              <el-input
                v-model="currentSlide.title"
                placeholder="输入页面标题"
                @change="saveProject"
              />
            </el-form-item>
            
            <el-form-item label="页面内容">
              <div
                v-for="(item, index) in currentSlide.content"
                :key="index"
                class="content-item"
              >
                <el-input
                  v-model="currentSlide.content[index]"
                  placeholder="输入内容要点"
                  @change="saveProject"
                >
                  <template #append>
                    <el-button :icon="Delete" @click="removeContent(index)" />
                  </template>
                </el-input>
              </div>
              <el-button type="text" @click="addContent">
                <el-icon><Plus /></el-icon>
                添加要点
              </el-button>
            </el-form-item>
            
            <el-form-item label="布局类型">
              <el-select v-model="currentSlide.layout_type" @change="saveProject">
                <el-option label="单栏布局" value="single_column" />
                <el-option label="双栏布局" value="two_column" />
                <el-option label="三栏布局" value="three_column" />
              </el-select>
            </el-form-item>
          </el-form>
        </div>
      </div>
      
      <div class="preview-panel">
        <div class="preview-header">
          <span>预览</span>
        </div>
        <div class="preview-content">
          <div class="ppt-preview" v-if="currentSlide">
            <div class="preview-slide" :style="previewSlideStyle">
              <h2 class="slide-title" :style="{ color: themeStyle.titleColor }">{{ currentSlide.title }}</h2>
              <ul class="slide-content" :style="{ color: themeStyle.contentColor }">
                <li v-for="(item, index) in currentSlide.content" :key="index">
                  {{ item }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { pptApi } from '@/api/ppt'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Download, Plus, Delete } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const projectId = computed(() => route.params.id)
const projectTitle = ref('')
const slides = ref([])
const currentSlideIndex = ref(0)
const exporting = ref(false)
const loading = ref(false)
const themeData = ref(null)

const currentSlide = computed(() => slides.value[currentSlideIndex.value])

const themeStyle = computed(() => {
  if (!themeData.value) {
    return {
      backgroundColor: '#ffffff',
      titleColor: '#0070c0',
      contentColor: '#44546a'
    }
  }
  
  const theme = themeData.value
  const bgColor = theme.background_color 
    ? `rgb(${theme.background_color.join(',')})` 
    : '#ffffff'
  const primaryColor = theme.primary_color 
    ? `rgb(${theme.primary_color.join(',')})` 
    : '#0070c0'
  const secondaryColor = theme.secondary_color 
    ? `rgb(${theme.secondary_color.join(',')})` 
    : '#44546a'
  
  return {
    backgroundColor: bgColor,
    titleColor: primaryColor,
    contentColor: secondaryColor
  }
})

const previewSlideStyle = computed(() => {
  return {
    backgroundColor: themeStyle.value.backgroundColor
  }
})

onMounted(async () => {
  if (projectId.value) {
    await loadProject()
  }
})

async function loadProject() {
  loading.value = true
  try {
    const project = await pptApi.getProject(projectId.value)
    projectTitle.value = project.title
    slides.value = project.content_json?.pages || []
    themeData.value = project.content_json?.theme || null
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

async function saveProject() {
  if (!projectId.value) return
  
  try {
    await pptApi.updateProject(projectId.value, {
      title: projectTitle.value,
      content_json: {
        title: projectTitle.value,
        pages: slides.value,
        theme: themeData.value
      }
    })
  } catch (error) {
    console.error(error)
  }
}

function addSlide() {
  slides.value.push({
    page_index: slides.value.length + 1,
    title: '',
    content: [],
    layout_type: 'single_column'
  })
  currentSlideIndex.value = slides.value.length - 1
  saveProject()
}

function removeSlide(index) {
  slides.value.splice(index, 1)
  if (currentSlideIndex.value >= slides.value.length) {
    currentSlideIndex.value = slides.value.length - 1
  }
  saveProject()
}

function addContent() {
  if (currentSlide.value) {
    currentSlide.value.content.push('')
    saveProject()
  }
}

function removeContent(index) {
  if (currentSlide.value) {
    currentSlide.value.content.splice(index, 1)
    saveProject()
  }
}

async function handleExport() {
  if (exporting.value) return
  
  exporting.value = true
  ElMessage.info('正在生成PPT文件...')
  
  try {
    const response = await fetch(`/api/v1/ppt/projects/${projectId.value}/export`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const blob = await response.blob()
    
    if (!blob || blob.size === 0) {
      ElMessage.error('导出失败：文件为空')
      return
    }
    
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.style.display = 'none'
    link.href = url
    link.download = `${projectTitle.value || 'presentation'}.pptx`
    document.body.appendChild(link)
    link.click()
    
    setTimeout(() => {
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }, 100)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Export error:', error)
    ElMessage.error('导出失败：' + error.message)
  } finally {
    exporting.value = false
  }
}
</script>

<style lang="scss" scoped>
.editor-page {
  height: calc(100vh - 64px - 60px);
  display: flex;
  flex-direction: column;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;
    
    .title-input {
      width: 300px;
    }
  }
}

.editor-main {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.slides-panel {
  width: 200px;
  background: #fff;
  border-right: 1px solid #ebeef5;
  display: flex;
  flex-direction: column;
  
  .slides-header {
    padding: 12px 16px;
    border-bottom: 1px solid #ebeef5;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 500;
  }
  
  .slides-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
  }
  
  .slide-thumb {
    position: relative;
    padding: 8px;
    margin-bottom: 8px;
    background: #f5f7fa;
    border-radius: 4px;
    cursor: pointer;
    border: 2px solid transparent;
    
    &.active {
      border-color: #409eff;
      background: #ecf5ff;
    }
    
    &:hover .delete-btn {
      opacity: 1;
    }
    
    .slide-number {
      font-size: 12px;
      color: #909399;
      margin-bottom: 4px;
    }
    
    .slide-preview {
      height: 60px;
      background: #fff;
      border-radius: 2px;
      padding: 8px;
      
      .preview-title {
        font-size: 10px;
        color: #606266;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
    
    .delete-btn {
      position: absolute;
      top: 4px;
      right: 4px;
      opacity: 0;
      transition: opacity 0.2s;
    }
  }
}

.editor-content {
  flex: 1;
  padding: 20px;
  background: #f5f7fa;
  overflow-y: auto;
  
  .slide-editor {
    max-width: 600px;
    margin: 0 auto;
    background: #fff;
    padding: 24px;
    border-radius: 8px;
    
    .content-item {
      margin-bottom: 8px;
    }
  }
}

.preview-panel {
  width: 400px;
  background: #fff;
  border-left: 1px solid #ebeef5;
  display: flex;
  flex-direction: column;
  
  .preview-header {
    padding: 12px 16px;
    border-bottom: 1px solid #ebeef5;
    font-weight: 500;
  }
  
  .preview-content {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
  }
  
  .ppt-preview {
    .preview-slide {
      aspect-ratio: 16/9;
      border-radius: 4px;
      padding: 20px;
      
      .slide-title {
        font-size: 14px;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(0, 0, 0, 0.1);
      }
      
      .slide-content {
        font-size: 10px;
        line-height: 1.6;
        
        li {
          margin-bottom: 4px;
        }
      }
    }
  }
}
</style>
