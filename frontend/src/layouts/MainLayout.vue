<template>
  <div class="main-layout">
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <div class="logo" @click="router.push('/')">
            <el-icon :size="28"><Document /></el-icon>
            <span class="logo-text">AI PPT生成</span>
          </div>
          
          <el-menu
            :default-active="activeMenu"
            mode="horizontal"
            :ellipsis="false"
            class="nav-menu"
            @select="handleMenuSelect"
          >
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/create">创建PPT</el-menu-item>
            <el-menu-item index="/templates">模板中心</el-menu-item>
            <el-menu-item index="/pricing">会员订阅</el-menu-item>
          </el-menu>
          
          <div class="user-area">
            <template v-if="userStore.isLoggedIn">
              <el-dropdown @command="handleCommand">
                <span class="user-info">
                  <el-avatar :size="32" :src="userStore.user?.avatar_url">
                    {{ userStore.user?.nickname?.charAt(0) || 'U' }}
                  </el-avatar>
                  <span class="username">{{ userStore.user?.nickname }}</span>
                  <el-tag v-if="userStore.isMember" type="warning" size="small">会员</el-tag>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="projects">我的作品</el-dropdown-item>
                    <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                    <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
            <template v-else>
              <el-button type="primary" @click="router.push('/login')">登录</el-button>
              <el-button @click="router.push('/register')">注册</el-button>
            </template>
          </div>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
      
      <el-footer class="footer">
        <div class="footer-content">
          <p>&copy; 2024 AI智能PPT生成平台. All rights reserved.</p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Document } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

function handleMenuSelect(index) {
  router.push(index)
}

function handleCommand(command) {
  switch (command) {
    case 'projects':
      router.push('/projects')
      break
    case 'profile':
      router.push('/profile')
      break
    case 'logout':
      userStore.logout()
      break
  }
}
</script>

<style lang="scss" scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 0 40px;
  height: 64px;
  display: flex;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  
  .header-content {
    width: 100%;
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  
  .logo-text {
    font-size: 20px;
    font-weight: 600;
    color: #409eff;
    margin-left: 8px;
  }
}

.nav-menu {
  flex: 1;
  justify-content: center;
  border-bottom: none;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  
  .username {
    font-size: 14px;
    color: #606266;
  }
}

.main-content {
  margin-top: 64px;
  min-height: calc(100vh - 64px - 60px);
  padding: 20px 40px;
  background: #f5f7fa;
}

.footer {
  background: #fff;
  border-top: 1px solid #ebeef5;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  .footer-content {
    text-align: center;
    color: #909399;
    font-size: 14px;
  }
}
</style>
