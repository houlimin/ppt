import api from './index'

export const authApi = {
  async register(data) {
    return api.post('/auth/register', data)
  },

  async login(data) {
    return api.post('/auth/login', data)
  },

  async logout() {
    return api.post('/auth/logout')
  },

  async getProfile() {
    return api.get('/user/profile')
  },

  async updateProfile(data) {
    return api.put('/user/profile', data)
  },

  async getMembership() {
    return api.get('/user/membership')
  }
}
