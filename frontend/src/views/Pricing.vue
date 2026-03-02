<template>
  <div class="pricing-page">
    <div class="page-header">
      <h1>会员订阅</h1>
      <p>解锁更多功能，享受无限创作</p>
    </div>
    
    <div class="pricing-cards">
      <div
        v-for="product in products"
        :key="product.type"
        :class="['pricing-card', { featured: product.type === 'yearly' }]"
      >
        <div class="badge" v-if="product.type === 'yearly'">推荐</div>
        <h2>{{ product.name }}</h2>
        <div class="price">
          <span class="currency">¥</span>
          <span class="amount">{{ product.price }}</span>
          <span class="period">/{{ getPeriod(product.type) }}</span>
        </div>
        <div class="original-price" v-if="product.original_price">
          原价 ¥{{ product.original_price }}
          <span class="discount">省{{ product.discount }}</span>
        </div>
        <ul class="features-list">
          <li v-for="(feature, index) in getFeatures(product.type)" :key="index">
            <el-icon><Check /></el-icon>
            {{ feature }}
          </li>
        </ul>
        <el-button
          :type="product.type === 'yearly' ? 'primary' : 'default'"
          size="large"
          @click="handleSubscribe(product)"
          :loading="subscribing === product.type"
        >
          {{ product.type === 'monthly' ? '立即订阅' : '选择此方案' }}
        </el-button>
      </div>
    </div>
    
    <div class="comparison-table">
      <h2>功能对比</h2>
      <el-table :data="comparisonData" border>
        <el-table-column prop="feature" label="功能" width="200" />
        <el-table-column prop="free" label="免费版" align="center" />
        <el-table-column prop="member" label="会员版" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.member === true" color="#67c23a"><Check /></el-icon>
            <el-icon v-else-if="row.member === false" color="#f56c6c"><Close /></el-icon>
            <span v-else>{{ row.member }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <div class="faq-section">
      <h2>常见问题</h2>
      <el-collapse>
        <el-collapse-item
          v-for="(faq, index) in faqs"
          :key="index"
          :title="faq.question"
          :name="index"
        >
          <p>{{ faq.answer }}</p>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { paymentApi } from '@/api/payment'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { Check, Close } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const products = ref([])
const subscribing = ref('')

onMounted(async () => {
  await loadProducts()
})

async function loadProducts() {
  try {
    products.value = await paymentApi.getProducts()
  } catch (error) {
    console.error(error)
  }
}

function getPeriod(type) {
  const periods = {
    monthly: '月',
    quarterly: '季',
    yearly: '年'
  }
  return periods[type] || ''
}

function getFeatures(type) {
  const features = {
    monthly: [
      '无限次数生成',
      '200+高级模板',
      '高清导出',
      'PDF/图片多格式导出',
      '10GB云端存储',
      '无水印导出'
    ],
    quarterly: [
      '无限次数生成',
      '200+高级模板',
      '高清导出',
      'PDF/图片多格式导出',
      '10GB云端存储',
      '无水印导出',
      '优先客服支持'
    ],
    yearly: [
      '无限次数生成',
      '200+高级模板',
      '高清/超清导出',
      'PDF/图片多格式导出',
      '10GB云端存储',
      '无水印导出',
      '优先客服支持',
      '专属会员活动'
    ]
  }
  return features[type] || []
}

async function handleSubscribe(product) {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  subscribing.value = product.type
  try {
    const order = await paymentApi.createOrder({
      product_type: product.type,
      payment_method: 'alipay'
    })
    
    ElMessage.success('订单创建成功，正在跳转支付...')
    
    setTimeout(() => {
      ElMessage.info('支付功能演示：支付成功')
    }, 2000)
  } catch (error) {
    console.error(error)
  } finally {
    subscribing.value = ''
  }
}

const comparisonData = [
  { feature: '每日生成次数', free: '3次', member: '无限' },
  { feature: '模板数量', free: '50+', member: '200+' },
  { feature: '导出分辨率', free: '标准', member: true },
  { feature: 'PDF导出', free: false, member: true },
  { feature: '图片导出', free: false, member: true },
  { feature: '云端存储', free: '5个项目', member: '10GB' },
  { feature: '无水印导出', free: false, member: true },
  { feature: '高级AI模型', free: false, member: true },
  { feature: '优先客服', free: false, member: true }
]

const faqs = [
  {
    question: '会员可以随时取消吗？',
    answer: '是的，您可以随时取消会员订阅，取消后会员权益将持续到当前订阅周期结束。'
  },
  {
    question: '支持哪些支付方式？',
    answer: '目前支持支付宝、微信支付两种主流支付方式。'
  },
  {
    question: '会员到期后我的作品会丢失吗？',
    answer: '不会，您的所有作品都会保留。但超出免费存储限制的作品将无法编辑。'
  },
  {
    question: '可以开具发票吗？',
    answer: '可以，请在支付成功后联系客服申请开具增值税发票。'
  }
]
</script>

<style lang="scss" scoped>
.pricing-page {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
  
  h1 {
    font-size: 32px;
    color: #303133;
    margin-bottom: 8px;
  }
  
  p {
    color: #909399;
    font-size: 16px;
  }
}

.pricing-cards {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 60px;
  
  .pricing-card {
    background: #fff;
    padding: 32px;
    border-radius: 12px;
    width: 300px;
    text-align: center;
    position: relative;
    border: 1px solid #ebeef5;
    
    &.featured {
      border: 2px solid #409eff;
      transform: scale(1.05);
      
      .badge {
        position: absolute;
        top: -12px;
        left: 50%;
        transform: translateX(-50%);
        background: #409eff;
        color: #fff;
        padding: 4px 16px;
        border-radius: 12px;
        font-size: 12px;
      }
    }
    
    h2 {
      font-size: 20px;
      color: #303133;
      margin-bottom: 16px;
    }
    
    .price {
      margin-bottom: 8px;
      
      .currency {
        font-size: 20px;
        color: #409eff;
      }
      
      .amount {
        font-size: 48px;
        font-weight: 600;
        color: #409eff;
      }
      
      .period {
        font-size: 14px;
        color: #909399;
      }
    }
    
    .original-price {
      font-size: 14px;
      color: #909399;
      text-decoration: line-through;
      margin-bottom: 16px;
      
      .discount {
        color: #f56c6c;
        text-decoration: none;
        margin-left: 8px;
      }
    }
    
    .features-list {
      list-style: none;
      padding: 0;
      margin: 24px 0;
      text-align: left;
      
      li {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 0;
        color: #606266;
        font-size: 14px;
        
        .el-icon {
          color: #67c23a;
        }
      }
    }
    
    .el-button {
      width: 100%;
    }
  }
}

.comparison-table {
  margin-bottom: 60px;
  
  h2 {
    text-align: center;
    font-size: 24px;
    color: #303133;
    margin-bottom: 24px;
  }
}

.faq-section {
  h2 {
    text-align: center;
    font-size: 24px;
    color: #303133;
    margin-bottom: 24px;
  }
  
  .el-collapse {
    background: #fff;
    border-radius: 8px;
  }
}
</style>
