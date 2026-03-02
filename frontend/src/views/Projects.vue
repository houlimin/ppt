<template>
  <div class="projects-page">
    <div class="page-header">
      <h1>我的作品</h1>
      <el-button type="primary" @click="router.push('/create')">
        <el-icon><Plus /></el-icon>
        创建新PPT
      </el-button>
    </div>
    
    <div class="projects-grid" v-loading="loading">
      <el-empty v-if="projects.length === 0 && !loading" description="暂无作品">
        <el-button type="primary" @click="router.push('/create')">创建第一个PPT</el-button>
      </el-empty>
      
      <div
        v-for="project in projects"
        :key="project.id"
        class="project-card"
        @click="handleProjectClick(project)"
      >
        <div class="project-thumbnail">
          <img v-if="project.thumbnail_url" :src="project.thumbnail_url" />
          <div v-else class="placeholder-thumbnail">
            <el-icon :size="48"><Document /></el-icon>
          </div>
          <div class="project-status">
            <el-tag :type="getStatusType(project.status)" size="small">
              {{ getStatusText(project.status) }}
            </el-tag>
          </div>
        </div>
        <div class="project-info">
          <h3>{{ project.title }}</h3>
          <p class="project-meta">
            <span>{{ project.page_count }} 页</span>
            <span>{{ formatDate(project.updated_at) }}</span>
          </p>
          <div class="project-actions">
            <el-button
              type="primary"
              size="small"
              text
              @click.stop="handleEdit(project)"
            >
              编辑
            </el-button>
            <el-button
              type="success"
              size="small"
              text
              @click.stop="handleExport(project)"
            >
              导出
            </el-button>
            <el-button
              type="danger"
              size="small"
              text
              @click.stop="handleDelete(project)"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>
    </div>
    
    <div class="pagination" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadProjects"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { pptApi } from '@/api/ppt'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Document } from '@element-plus/icons-vue'

const router = useRouter()

const loading = ref(false)
const projects = ref([])
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

onMounted(() => {
  loadProjects()
})

async function loadProjects() {
  loading.value = true
  try {
    const response = await pptApi.getProjects({
      page: currentPage.value,
      page_size: pageSize.value
    })
    projects.value = response.items
    total.value = response.total
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

function getStatusType(status) {
  const types = {
    draft: 'info',
    generating: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

function getStatusText(status) {
  const texts = {
    draft: '草稿',
    generating: '生成中',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || status
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

function handleProjectClick(project) {
  if (project.status === 'completed') {
    router.push(`/editor/${project.id}`)
  }
}

function handleEdit(project) {
  router.push(`/editor/${project.id}`)
}

async function handleExport(project) {
  try {
    const response = await pptApi.exportProject(project.id)
    window.open(response.file_url, '_blank')
    ElMessage.success('导出成功')
  } catch (error) {
    console.error(error)
  }
}

async function handleDelete(project) {
  try {
    await ElMessageBox.confirm('确定要删除这个项目吗？', '提示', {
      type: 'warning'
    })
    await pptApi.deleteProject(project.id)
    ElMessage.success('删除成功')
    loadProjects()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}
</script>

<style lang="scss" scoped>
.projects-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  
  h1 {
    font-size: 28px;
    color: #303133;
  }
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  min-height: 300px;
}

.project-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }
  
  .project-thumbnail {
    position: relative;
    height: 150px;
    background: #f5f7fa;
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .placeholder-thumbnail {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #c0c4cc;
    }
    
    .project-status {
      position: absolute;
      top: 8px;
      right: 8px;
    }
  }
  
  .project-info {
    padding: 16px;
    
    h3 {
      font-size: 16px;
      color: #303133;
      margin-bottom: 8px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    .project-meta {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      color: #909399;
      margin-bottom: 12px;
    }
    
    .project-actions {
      display: flex;
      gap: 8px;
    }
  }
}

.pagination {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}
</style>
