<template>
  <div class="scope-generator">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <span>实验组分设置</span>
          </div>
        </template>
        
        <!-- 动态组分输入 -->
        <div v-for="(component, index) in form.components" :key="index" class="component-item">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item :label="'组分名称 ' + (index + 1)" :prop="'components.' + index + '.name'" :rules="rules.componentName">
                <el-input v-model="component.name" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="'可选值'" :prop="'components.' + index + '.values'" :rules="rules.componentValues">
                <el-select
                  v-model="component.values"
                  multiple
                  filterable
                  allow-create
                  default-first-option
                  :reserve-keyword="true"
                  placeholder="请输入或选择可选值"
                  @change="handleValueChange(index, $event)"
                >
                  <el-option
                    v-for="item in component.options"
                    :key="item"
                    :label="item"
                    :value="item"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="4">
              <el-button type="danger" @click="removeComponent(index)">删除</el-button>
            </el-col>
          </el-row>
        </div>
        
        <el-button type="primary" @click="addComponent">添加组分</el-button>
      </el-card>

      <el-card class="box-card" style="margin-top: 20px">
        <template #header>
          <div class="card-header">
            <span>文件设置</span>
          </div>
        </template>
        
        <el-form-item label="文件名">
          <el-input v-model="form.filename" placeholder="默认为 'reaction.csv'" />
        </el-form-item>
      </el-card>

      <div class="form-buttons">
        <el-button type="primary" @click="generateScope" :loading="loading">
          生成实验范围
        </el-button>
      </div>
    </el-form>

    <!-- 结果展示 -->
    <el-dialog v-model="showResult" title="生成结果" width="70%">
      <div v-if="generatedFile">
        <el-alert
          title="实验范围已成功生成！"
          type="success"
          :closable="false"
          show-icon
        />
        <div class="download-section">
          <el-button type="primary" @click="downloadFile">
            下载CSV文件
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const formRef = ref(null)
const loading = ref(false)
const showResult = ref(false)
const generatedFile = ref(null)

const form = reactive({
  components: [{ 
    name: '', 
    values: [], 
    options: [] 
  }],
  filename: 'reaction.csv'
})

const rules = {
  componentName: [
    { required: true, message: '请输入组分名称', trigger: 'blur' },
  ],
  componentValues: [
    { required: true, message: '请至少输入一个可选值', trigger: 'change' },
  ]
}

const addComponent = () => {
  form.components.push({ 
    name: '', 
    values: [], 
    options: [] 
  })
}

const removeComponent = (index) => {
  form.components.splice(index, 1)
}

const handleValueChange = (index, values) => {
  const component = form.components[index]
  const filteredValues = values.filter(v => v.trim() !== '')
  component.values = filteredValues
  component.options = Array.from(new Set([
    ...filteredValues,
    ...component.options
  ])).filter(v => v.trim() !== '')
  
  if (filteredValues.length === 0) {
    component.values = []
  }
}

const generateScope = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    loading.value = true
    
    const componentsData = {}
    form.components.forEach(comp => {
      componentsData[comp.name] = comp.values
    })
    
    const response = await fetch('/api/v1/scope/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        components: componentsData,
        filename: form.filename,
        continuous_features: true
      })
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      if (response.status === 400 && errorData.detail.includes('需要至少3个完成的实验数据')) {
        throw new Error('需要至少3个完成的实验数据才能进行优化')
      }
      throw new Error(errorData.detail || '生成失败')
    }
    
    const blob = await response.blob()
    const filename = response.headers.get('Content-Disposition')
      ?.split('filename=')[1]
      ?.replace(/['"]/g, '')
    
    generatedFile.value = {
      filename: filename || form.filename,
      blobUrl: URL.createObjectURL(blob),
      isInitialDesign: filename === 'initial_design.csv'
    }
    showResult.value = true
    
    if (generatedFile.value.isInitialDesign) {
      ElMessage.success('初始实验设计已生成，请完成实验后重新上传数据')
    }
    
  } catch (error) {
    ElMessage.error(error.message || '生成失败，请检查输入')
  } finally {
    loading.value = false
  }
}

const downloadFile = async () => {
  if (!generatedFile.value) return
  
  try {
    const response = await fetch(generatedFile.value.blobUrl)
    if (!response.ok) {
      throw new Error('文件获取失败')
    }

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.style.display = 'none'
    a.href = url
    a.download = generatedFile.value.filename
    document.body.appendChild(a)
    a.click()
    
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error(error.message || '下载失败，请重试')
  }
}
</script>

<style scoped>
.scope-generator {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.box-card {
  margin-bottom: 20px;
  background: var(--el-bg-color);
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.box-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.card-header {
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.component-item {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.form-buttons {
  margin-top: 30px;
  text-align: center;
}

.download-section {
  margin-top: 20px;
  text-align: center;
}

@media (max-width: 768px) {
  .scope-generator {
    padding: 10px;
  }
  
  .box-card {
    margin-bottom: 16px;
  }
  
  .card-header {
    font-size: 16px;
  }
  
  :deep(.el-form-item__label) {
    width: 100px !important;
  }
  
  .component-item {
    margin-bottom: 16px;
    padding-bottom: 16px;
  }
}

@media (max-width: 480px) {
  .card-header {
    font-size: 14px;
  }
  
  :deep(.el-form-item__label) {
    width: 80px !important;
  }
  
  .form-buttons {
    margin-top: 20px;
  }
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

:deep(.el-tabs__active-bar) {
  height: 3px;
  border-radius: 2px;
}

:deep(.el-tabs__nav) {
  margin-bottom: 20px;
}

@media (prefers-color-scheme: dark) {
  .box-card {
    background: rgba(28, 28, 30, 0.7);
    border-color: rgba(255, 255, 255, 0.1);
  }
  
  .card-header {
    color: #ffffff;
  }
  
  .input-field {
    background: rgba(28, 28, 30, 0.8);
    border-color: rgba(255, 255, 255, 0.1);
    color: #ffffff;
  }
  
  .input-field:hover {
    border-color: rgba(255, 255, 255, 0.3);
  }
}
</style>
