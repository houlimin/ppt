import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '@/stores/user'

vi.mock('@/api/auth', () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    getProfile: vi.fn()
  }
}))

import { authApi } from '@/api/auth'

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('initializes with empty state', () => {
    const store = useUserStore()
    
    expect(store.user).toBeNull()
    expect(store.token).toBe('')
    expect(store.isLoggedIn).toBe(false)
    expect(store.isMember).toBe(false)
  })

  it('sets token on login', async () => {
    const mockResponse = {
      access_token: 'test-token',
      user: {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        nickname: 'Test User',
        membership_type: 'free',
        is_member: false,
        created_at: '2024-01-01T00:00:00'
      }
    }
    
    authApi.login.mockResolvedValue(mockResponse)
    
    const store = useUserStore()
    await store.login({ username: 'testuser', password: 'password' })
    
    expect(store.token).toBe('test-token')
    expect(store.user.username).toBe('testuser')
    expect(store.isLoggedIn).toBe(true)
    expect(localStorage.getItem('token')).toBe('test-token')
  })

  it('clears state on logout', async () => {
    localStorage.setItem('token', 'test-token')
    
    const store = useUserStore()
    store.user = { id: 1, username: 'testuser' }
    store.token = 'test-token'
    
    store.logout()
    
    expect(store.token).toBe('')
    expect(store.user).toBeNull()
    expect(localStorage.getItem('token')).toBeNull()
  })

  it('detects member status correctly', () => {
    const store = useUserStore()
    
    store.user = {
      membership_type: 'yearly',
      membership_expire_at: new Date(Date.now() + 86400000).toISOString(),
      is_member: true
    }
    
    expect(store.isMember).toBe(true)
  })
})
