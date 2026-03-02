<template>
  <div class="profile-page">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <div class="user-info">
            <el-avatar :size="80" :src="userStore.user?.avatar_url">
              {{ userStore.user?.nickname?.charAt(0) || 'U' }}
            </el-avatar>
            <h2>{{ userStore.user?.nickname }}</h2>
            <p class="username">@{{ userStore.user?.username }}</p>
            <el-tag v-if="userStore.isMember" type="warning">
              {{ userStore.user?.membership_type }} 会员
            </el-tag>
            <el-tag v-else type="info">免费用户</el-tag>
          </div>
          
          <div class="stats">
            <div class="stat-item">
              <span class="stat-value">{{ stats.projects }}</span>
              <span class="stat-label">作品</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ stats.generations }}</span>
              <span class="stat-label">生成次数</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card>
          <el-tabs v-model="activeTab">
            <el-tab-pane label="个人资料" name="profile">
              <el-form
                ref="profileFormRef"
                :model="profileForm"
                :rules="profileRules"
                label-width="80px"
              >
                <el-form-item label="昵称" prop="nickname">
                  <el-input v-model="profileForm.nickname" />
                </el-form-item>
                
                <el-form-item label="职业" prop="profession">
                  <el-input v-model="profileForm.profession" />
                </el-form-item>
                
                <el-form-item label="行业" prop="industry">
                  <el-select v-model="profileForm.industry" style="width: 100%">
                    <el-option
                      v-for="industry in industries"
                      :key="industry"
                      :label="industry"
                      :value="industry"
                    />
                  </el-select>
                </el-form-item>
                
                <el-form-item>
                  <el-button type="primary" @click="updateProfile" :loading="updating">
                    保存修改
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
            
            <el-tab-pane label="会员信息" name="membership">
              <div class="membership-info" v-if="userStore.isMember">
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="会员类型">
                    {{ userStore.user?.membership_type }}
                  </el-descriptions-item>
                  <el-descriptions-item label="到期时间">
                    {{ formatDate(userStore.user?.membership_expire_at) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="存储空间">
                    {{ formatStorage(userStore.user?.storage_used) }} / 10GB
                  </el-descriptions-item>
                </el-descriptions>
              </div>
              <div class="membership-upgrade" v-else>
                <el-empty description="您还不是会员">
                  <el-button type="primary" @click="router.push('/pricing')">
                    升级会员
                  </el-button>
                </el-empty>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="订单记录" name="orders">
              <el-table :data="orders" v-loading="loadingOrders">
                <el-table-column prop="order_no" label="订单号" width="200" />
                <el-table-column prop="product_type" label="产品">
                  <template #default="{ row }">
                    {{ getProductLabel(row.product_type) }}
                  </template>
                </el-table-column>
                <el-table-column prop="amount" label="金额">
                  <template #default="{ row }">
                    ¥{{ row.amount }}
                  </template>
                </el-table-column>
                <el-table-column prop="payment_status" label="状态">
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.payment_status)">
                      {{ getStatusLabel(row.payment_status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="创建时间">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
            
            <el-tab-pane label="账号安全" name="security">
              <el-form label-width="100px">
                <el-form-item label="登录邮箱">
                  <span>{{ userStore.user?.email }}</span>
                </el-form-item>
                <el-form-item label="修改密码">
                  <el-button @click="showPasswordDialog = true">修改密码</el-button>
                </el-form-item>
                <el-form-item label="注销账号">
                  <el-button type="danger" @click="handleDeleteAccount">
                    注销账号
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
    
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="400px">
      <el-form :model="passwordForm" label-width="80px">
        <el-form-item label="当前密码">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="changePassword">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { authApi } from '@/api/auth'
import { paymentApi } from '@/api/payment'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('profile')
const updating = ref(false)
const loadingOrders = ref(false)
const orders = ref([])
const showPasswordDialog = ref(false)
const stats = ref({
  projects: 0,
  generations: 0
})

const profileForm = reactive({
  nickname: '',
  profession: '',
  industry: ''
})

const profileRules = {
  nickname: [
    { max: 50, message: '昵称不能超过50个字符', trigger: 'blur' }
  ]
}

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const industries = [
  '互联网/IT',
  '金融',
  '教育',
  '医疗',
  '制造业',
  '零售',
  '房地产',
  '媒体/广告',
  '政府/公共事业',
  '其他'
]

onMounted(async () => {
  await loadProfile()
  await loadOrders()
})

async function loadProfile() {
  try {
    const user = await authApi.getProfile()
    profileForm.nickname = user.nickname || ''
    profileForm.profession = user.profession || ''
    profileForm.industry = user.industry || ''
  } catch (error) {
    console.error(error)
  }
}

async function loadOrders() {
  loadingOrders.value = true
  try {
    orders.value = await paymentApi.getOrders()
  } catch (error) {
    console.error(error)
  } finally {
    loadingOrders.value = false
  }
}

async function updateProfile() {
  updating.value = true
  try {
    await authApi.updateProfile(profileForm)
    await userStore.fetchProfile()
    ElMessage.success('保存成功')
  } catch (error) {
    console.error(error)
  } finally {
    updating.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

function formatStorage(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  while (bytes >= 1024 && i < units.length - 1) {
    bytes /= 1024
    i++
  }
  return `${bytes.toFixed(2)} ${units[i]}`
}

function getProductLabel(type) {
  const labels = {
    monthly: '月度会员',
    quarterly: '季度会员',
    yearly: '年度会员'
  }
  return labels[type] || type
}

function getStatusType(status) {
  const types = {
    pending: 'info',
    paid: 'success',
    failed: 'danger',
    refunded: 'warning'
  }
  return types[status] || 'info'
}

function getStatusLabel(status) {
  const labels = {
    pending: '待支付',
    paid: '已支付',
    failed: '支付失败',
    refunded: '已退款'
  }
  return labels[status] || status
}

async function changePassword() {
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  
  ElMessage.info('密码修改功能演示')
  showPasswordDialog.value = false
}

async function handleDeleteAccount() {
  try {
    await ElMessageBox.confirm(
      '确定要注销账号吗？此操作不可恢复。',
      '警告',
      {
        type: 'warning',
        confirmButtonText: '确定注销',
        cancelButtonText: '取消'
      }
    )
    
    ElMessage.info('账号注销功能演示')
  } catch (error) {
    // 用户取消
  }
}
</script>

<style lang="scss" scoped>
.profile-page {
  max-width: 1000px;
  margin: 0 auto;
}

.user-info {
  text-align: center;
  padding: 20px 0;
  
  h2 {
    font-size: 20px;
    color: #303133;
    margin: 16px 0 4px;
  }
  
  .username {
    color: #909399;
    font-size: 14px;
    margin-bottom: 12px;
  }
}

.stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  padding: 20px 0;
  border-top: 1px solid #ebeef5;
  margin-top: 20px;
  
  .stat-item {
    text-align: center;
    
    .stat-value {
      display: block;
      font-size: 24px;
      font-weight: 600;
      color: #409eff;
    }
    
    .stat-label {
      font-size: 12px;
      color: #909399;
    }
  }
}

.membership-info {
  padding: 20px 0;
}

.membership-upgrade {
  padding: 40px 0;
}
</style>
