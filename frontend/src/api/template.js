import api from './index'

export const templateApi = {
  async getTemplates(params) {
    return api.get('/templates', { params })
  },

  async getCategories() {
    return api.get('/templates/categories')
  },

  async getTemplate(id) {
    return api.get(`/templates/${id}`)
  },
  
  async createTemplate(data) {
    return api.post('/templates', data)
  },
  
  async uploadThumbnail(formData) {
    return api.post('/templates/upload-thumbnail', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  async getMyTemplates(params) {
    return api.get('/templates/user/my', { params })
  },
  
  async updateTemplate(id, data) {
    return api.put(`/templates/${id}`, data)
  },
  
  async deleteTemplate(id) {
    return api.delete(`/templates/${id}`)
  }
}
