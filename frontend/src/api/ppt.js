import api from './index'

export const pptApi = {
  async generateByText(data) {
    return api.post('/ppt/generate/text', data)
  },

  async generateByOutline(data) {
    return api.post('/ppt/generate/outline', data)
  },

  async generateByDocument(formData) {
    return api.post('/ppt/generate/document', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 300000 // 文件上传可能较慢，增加超时
    })
  },

  async getGenerationStatus(taskId) {
    return api.get(`/ppt/generate/status/${taskId}`)
  },

  async getProjects(params) {
    return api.get('/ppt/projects', { params })
  },

  async getProject(id) {
    return api.get(`/ppt/projects/${id}`)
  },

  async updateProject(id, data) {
    return api.put(`/ppt/projects/${id}`, data)
  },

  async deleteProject(id) {
    return api.delete(`/ppt/projects/${id}`)
  },

  async exportProject(id) {
    return api.get(`/ppt/projects/${id}/export`, {
      responseType: 'blob',
      timeout: 120000 // 导出可能需要时间生成
    })
  }
}
