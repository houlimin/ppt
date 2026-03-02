import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')

  const isLoggedIn = computed(() => !!token.value)
  const isMember = computed(() => user.value?.is_member || false)

  async function login(credentials) {
    try {
      const response = await authApi.login(credentials)
      token.value = response.access_token
      user.value = response.user
      localStorage.setItem('token', response.access_token)
      return response
    } catch (error) {
      throw error
    }
  }

  async function register(userData) {
    try {
      const response = await authApi.register(userData)
      token.value = response.access_token
      user.value = response.user
      localStorage.setItem('token', response.access_token)
      return response
    } catch (error) {
      throw error
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  async function fetchProfile() {
    try {
      const response = await authApi.getProfile()
      user.value = response
      return response
    } catch (error) {
      logout()
      throw error
    }
  }

  return {
    user,
    token,
    isLoggedIn,
    isMember,
    login,
    register,
    logout,
    fetchProfile
  }
})
