<template>
  <el-container>
    <el-header>
      <h1>EDBO+ 优化系统</h1>
    </el-header>
    
    <el-main>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="实验设计" name="scope">
          <ScopeGenerator />
        </el-tab-pane>
        <el-tab-pane label="优化运行" name="optimization">
          <OptimizationRunner />
        </el-tab-pane>
      </el-tabs>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import ScopeGenerator from './components/ScopeGenerator.vue'
import OptimizationRunner from './components/OptimizationRunner.vue'

const activeTab = ref('scope')
</script>

<style>
.el-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-header {
  background: linear-gradient(135deg, var(--el-color-primary) 0%, var(--el-color-primary-light-3) 100%);
  color: white;
  text-align: center;
  line-height: 60px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 1;
  position: sticky;
  top: 0;
}

.el-header h1 {
  font-size: 24px;
  font-weight: 600;
  letter-spacing: 1px;
  margin: 0;
}

.el-main {
  padding: 20px;
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  background: var(--el-bg-color);
}

:deep(.el-tabs) {
  background: var(--el-bg-color);
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:deep(.el-tabs__header) {
  margin: 0;
}

:deep(.el-tabs__nav-wrap) {
  padding: 0 20px;
}

:deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 500;
  padding: 0 24px;
  height: 48px;
  line-height: 48px;
}

/* 响应式处理 */
@media (max-width: 768px) {
  .el-header h1 {
    font-size: 1.2rem;
    line-height: 50px;
  }
  
  .el-main {
    padding: 8px;
  }

  :deep(.el-tabs) {
    padding: 12px;
    border-radius: 8px;
  }

  :deep(.el-tabs__item) {
    font-size: 14px;
    padding: 0 16px;
    height: 40px;
    line-height: 40px;
  }

  :deep(.el-tabs__nav-wrap) {
    padding: 0 12px;
  }
}

@media (max-width: 480px) {
  .el-header h1 {
    font-size: 1rem;
    line-height: 40px;
  }

  :deep(.el-tabs__item) {
    font-size: 12px;
    padding: 0 12px;
  }
}
</style>
