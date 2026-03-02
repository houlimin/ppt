import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'

import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: '<div />' } },
    { path: '/login', component: Login },
    { path: '/register', component: Register }
  ]
})

describe('Login', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders login form', () => {
    const wrapper = mount(Login, {
      global: {
        plugins: [router, ElementPlus]
      }
    })
    
    expect(wrapper.find('h1').text()).toBe('登录')
    expect(wrapper.find('input[placeholder="请输入用户名或邮箱"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
  })

  it('has login button', () => {
    const wrapper = mount(Login, {
      global: {
        plugins: [router, ElementPlus]
      }
    })
    
    const button = wrapper.find('.login-btn')
    expect(button.exists()).toBe(true)
    expect(button.text()).toContain('登录')
  })

  it('shows register link', () => {
    const wrapper = mount(Login, {
      global: {
        plugins: [router, ElementPlus]
      }
    })
    
    expect(wrapper.text()).toContain('还没有账号')
    expect(wrapper.text()).toContain('立即注册')
  })
})

describe('Register', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders register form', () => {
    const wrapper = mount(Register, {
      global: {
        plugins: [router, ElementPlus]
      }
    })
    
    expect(wrapper.find('h1').text()).toBe('注册')
    expect(wrapper.find('input[placeholder="请输入用户名"]').exists()).toBe(true)
    expect(wrapper.find('input[placeholder="请输入邮箱"]').exists()).toBe(true)
  })

  it('has password confirmation field', () => {
    const wrapper = mount(Register, {
      global: {
        plugins: [router, ElementPlus]
      }
    })
    
    const passwordInputs = wrapper.findAll('input[type="password"]')
    expect(passwordInputs.length).toBe(2)
  })

  it('shows login link', () => {
    const wrapper = mount(Register, {
      global: {
        plugins: [router, ElementPlus]
      }
    })
    
    expect(wrapper.text()).toContain('已有账号')
    expect(wrapper.text()).toContain('立即登录')
  })
})
