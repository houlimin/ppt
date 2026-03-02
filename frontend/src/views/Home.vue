<template>
  <div class="home-page">
    <section class="hero">
      <div class="hero-content">
        <h1>AI智能PPT生成平台</h1>
        <p>输入您的想法，AI为您自动生成专业PPT演示文稿</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="handleStart">
            立即开始
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
          <el-button size="large" @click="router.push('/templates')">
            浏览模板
          </el-button>
        </div>
        <div class="hero-stats">
          <div class="stat-item">
            <span class="stat-number">10万+</span>
            <span class="stat-label">用户选择</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">200+</span>
            <span class="stat-label">精美模板</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">30秒</span>
            <span class="stat-label">快速生成</span>
          </div>
        </div>
      </div>
      <div class="hero-image">
        <div class="demo-ppt">
          <div class="ppt-slide">
            <div class="slide-title">AI智能演示</div>
            <div class="slide-content">
              <div class="slide-item"></div>
              <div class="slide-item"></div>
              <div class="slide-item"></div>
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <section class="features">
      <h2>核心功能</h2>
      <div class="feature-grid">
        <div class="feature-card" v-for="feature in features" :key="feature.title">
          <el-icon :size="48" :color="feature.color">
            <component :is="feature.icon" />
          </el-icon>
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.description }}</p>
        </div>
      </div>
    </section>
    
    <section class="how-it-works">
      <h2>如何使用</h2>
      <div class="steps">
        <div class="step" v-for="(step, index) in steps" :key="index">
          <div class="step-number">{{ index + 1 }}</div>
          <h3>{{ step.title }}</h3>
          <p>{{ step.description }}</p>
        </div>
      </div>
    </section>
    
    <section class="pricing-preview">
      <h2>会员方案</h2>
      <div class="pricing-cards">
        <div class="pricing-card">
          <h3>免费版</h3>
          <div class="price">¥0<span>/永久</span></div>
          <ul class="features-list">
            <li><el-icon><Check /></el-icon> 每日3次生成</li>
            <li><el-icon><Check /></el-icon> 50+基础模板</li>
            <li><el-icon><Check /></el-icon> 标准分辨率导出</li>
          </ul>
          <el-button type="default" @click="router.push('/register')">免费注册</el-button>
        </div>
        <div class="pricing-card featured">
          <div class="badge">推荐</div>
          <h3>年度会员</h3>
          <div class="price">¥299<span>/年</span></div>
          <ul class="features-list">
            <li><el-icon><Check /></el-icon> 无限次数生成</li>
            <li><el-icon><Check /></el-icon> 200+高级模板</li>
            <li><el-icon><Check /></el-icon> 高清导出</li>
            <li><el-icon><Check /></el-icon> 无水印</li>
          </ul>
          <el-button type="primary" @click="router.push('/pricing')">立即订阅</el-button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { 
  ArrowRight, 
  Check, 
  Edit, 
  Document, 
  Picture,
  Timer,
  MagicStick
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const features = [
  {
    icon: Edit,
    title: '文本生成',
    description: '输入自然语言描述，AI自动理解并生成完整PPT',
    color: '#409eff'
  },
  {
    icon: Document,
    title: '文档导入',
    description: '支持Word、PDF、Markdown等多种格式文档导入',
    color: '#67c23a'
  },
  {
    icon: Picture,
    title: '精美模板',
    description: '200+专业设计模板，覆盖商务、教育、创意等场景',
    color: '#e6a23c'
  },
  {
    icon: Timer,
    title: '快速生成',
    description: '30秒内完成PPT生成，大幅提升工作效率',
    color: '#f56c6c'
  }
]

const steps = [
  {
    title: '输入需求',
    description: '描述您的PPT主题和内容要求'
  },
  {
    title: 'AI生成',
    description: 'AI智能分析并生成PPT大纲和内容'
  },
  {
    title: '编辑优化',
    description: '在线编辑调整，完善细节'
  },
  {
    title: '导出分享',
    description: '一键导出PPTX文件或分享链接'
  }
]

function handleStart() {
  if (userStore.isLoggedIn) {
    router.push('/create')
  } else {
    router.push('/register')
  }
}
</script>

<style lang="scss" scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 60px 0;
  min-height: 500px;
  
  .hero-content {
    flex: 1;
    
    h1 {
      font-size: 48px;
      color: #303133;
      margin-bottom: 20px;
      background: linear-gradient(135deg, #409eff, #67c23a);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    p {
      font-size: 20px;
      color: #606266;
      margin-bottom: 30px;
    }
  }
  
  .hero-actions {
    display: flex;
    gap: 16px;
    margin-bottom: 40px;
  }
  
  .hero-stats {
    display: flex;
    gap: 40px;
    
    .stat-item {
      text-align: center;
      
      .stat-number {
        display: block;
        font-size: 32px;
        font-weight: 600;
        color: #409eff;
      }
      
      .stat-label {
        font-size: 14px;
        color: #909399;
      }
    }
  }
  
  .hero-image {
    flex: 1;
    display: flex;
    justify-content: center;
    
    .demo-ppt {
      width: 400px;
      height: 280px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
      animation: float 3s ease-in-out infinite;
      
      .ppt-slide {
        background: #fff;
        height: 100%;
        border-radius: 8px;
        padding: 30px;
        
        .slide-title {
          height: 30px;
          background: linear-gradient(90deg, #409eff, #67c23a);
          border-radius: 4px;
          margin-bottom: 20px;
          width: 60%;
        }
        
        .slide-content {
          .slide-item {
            height: 16px;
            background: #e4e7ed;
            border-radius: 4px;
            margin-bottom: 12px;
            
            &:nth-child(1) { width: 100%; }
            &:nth-child(2) { width: 80%; }
            &:nth-child(3) { width: 60%; }
          }
        }
      }
    }
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.features, .how-it-works, .pricing-preview {
  padding: 60px 0;
  
  h2 {
    text-align: center;
    font-size: 32px;
    color: #303133;
    margin-bottom: 40px;
  }
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  
  .feature-card {
    background: #fff;
    padding: 30px;
    border-radius: 12px;
    text-align: center;
    transition: all 0.3s;
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    h3 {
      font-size: 18px;
      color: #303133;
      margin: 16px 0 8px;
    }
    
    p {
      font-size: 14px;
      color: #909399;
      line-height: 1.6;
    }
  }
}

.steps {
  display: flex;
  justify-content: space-between;
  
  .step {
    flex: 1;
    text-align: center;
    padding: 0 20px;
    
    .step-number {
      width: 60px;
      height: 60px;
      background: linear-gradient(135deg, #409eff, #337ecc);
      color: #fff;
      font-size: 24px;
      font-weight: 600;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 20px;
    }
    
    h3 {
      font-size: 18px;
      color: #303133;
      margin-bottom: 8px;
    }
    
    p {
      font-size: 14px;
      color: #909399;
    }
  }
}

.pricing-cards {
  display: flex;
  justify-content: center;
  gap: 40px;
  
  .pricing-card {
    background: #fff;
    padding: 40px;
    border-radius: 12px;
    width: 320px;
    text-align: center;
    position: relative;
    
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
    
    h3 {
      font-size: 24px;
      color: #303133;
      margin-bottom: 16px;
    }
    
    .price {
      font-size: 48px;
      font-weight: 600;
      color: #409eff;
      margin-bottom: 24px;
      
      span {
        font-size: 16px;
        color: #909399;
        font-weight: normal;
      }
    }
    
    .features-list {
      list-style: none;
      padding: 0;
      margin-bottom: 24px;
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
  }
}
</style>
