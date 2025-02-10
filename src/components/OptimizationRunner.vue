<template>
  <div class="optimization-runner">
    <div class="header">
      <h1>实验优化配置</h1>
    </div>
    
    <el-tabs v-model="activeTab" class="tabs-container">
      <el-tab-pane label="优化目标" name="objectives">
        <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
          <el-card class="box-card">
            <div v-for="(objective, index) in form.objectives" :key="index" class="objective-item">
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-form-item :label="'目标 ' + (index + 1)" :prop="'objectives.' + index + '.name'" :rules="rules.objectiveName">
                    <el-input v-model="objective.name" placeholder="如：yield" class="input-field" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item :label="'优化模式'" :prop="'objectives.' + index + '.mode'" :rules="rules.objectiveMode">
                    <el-select v-model="objective.mode" class="select-field">
                      <el-option label="最大化" value="max" />
                      <el-option label="最小化" value="min" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="阈值">
                    <el-input v-model.number="objective.threshold" type="number" class="input-field" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-button type="danger" @click="removeObjective(index)" class="delete-btn">删除目标</el-button>
            </div>
            <el-button type="primary" @click="addObjective" class="add-btn">添加优化目标</el-button>
          </el-card>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="优化参数" name="parameters">
        <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
          <el-card class="box-card">
            <el-form-item label="实验批次大小">
              <el-input-number v-model="form.batch" :min="1" :max="20" class="input-field" />
            </el-form-item>

            <el-form-item label="采样方法">
              <el-select v-model="form.samplingMethod" class="select-field">
                <el-option label="随机种子" value="seed" />
                <el-option label="拉丁超立方" value="lhs" />
                <el-option label="CVT采样" value="cvtsampling" />
              </el-select>
            </el-form-item>

            <el-form-item label="随机种子">
              <el-input-number v-model="form.seed" :min="0" class="input-field" />
            </el-form-item>

            <el-form-item label="获取预测">
              <el-switch v-model="form.getPredictions" class="switch-field" />
            </el-form-item>

            <el-form-item label="采集函数">
              <el-select v-model="form.acquisitionFunction" class="select-field">
                <el-option label="EHVI" value="EHVI" />
                <el-option label="MOUCB" value="MOUCB" />
                <el-option label="MOGreedy" value="MOGreedy" />
              </el-select>
            </el-form-item>

            <el-form-item label="不确定性系数">
              <el-input-number v-model="form.sigmaUncertainty" :min="0" :step="0.1" class="input-field" />
            </el-form-item>

            <el-form-item label="CSV文件">
              <el-upload
                class="upload-demo"
                action="/api/v1/data/upload"
                :on-success="handleUploadSuccess"
                :on-error="handleUploadError"
                :before-upload="beforeUpload"
              >
                <el-button type="primary" class="upload-btn">选择文件</el-button>
                <template #tip>
                  <div class="el-upload__tip">
                    请上传reaction.csv文件
                  </div>
                </template>
              </el-upload>
            </el-form-item>
          </el-card>
        </el-form>
      </el-tab-pane>
    </el-tabs>

    <div class="form-buttons">
      <el-button type="primary" @click="startOptimization" :loading="loading" class="optimize-btn">
        开始优化
      </el-button>
    </div>

    <!-- 优化结果展示 -->
    <el-dialog v-model="showResult" title="优化结果" width="80%" class="result-dialog">
      <div v-if="optimizationResult">
        <el-alert
          title="优化完成！"
          type="success"
          :closable="false"
          show-icon
        />
        <div class="result-section">
          <el-button type="primary" @click="downloadResults" class="download-btn">
            下载结果
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
const optimizationResult = ref(null)
const activeTab = ref('objectives')

const form = reactive({
  objectives: [{ name: '', mode: 'max', threshold: null }],
  batch: 5,
  samplingMethod: 'seed',
  seed: 0,
  getPredictions: true,
  uploadedFile: null,
  acquisitionFunction: 'EHVI',
  sigmaUncertainty: 1.0
})

const rules = {
  objectiveName: [
    { required: true, message: '请输入优化目标名称', trigger: 'blur' }
  ],
  objectiveMode: [
    { required: true, message: '请选择优化模式', trigger: 'change' }
  ]
}

const addObjective = () => {
  form.objectives.push({ name: '', mode: 'max', threshold: null })
}

const removeObjective = (index) => {
  form.objectives.splice(index, 1)
}

const handleUploadSuccess = (response, uploadFile) => {
  form.uploadedFile = uploadFile.raw
  ElMessage.success('文件上传成功')
}

const handleUploadError = () => {
  ElMessage.error('文件上传失败')
}

const beforeUpload = (file) => {
  const isCsv = file.type === 'text/csv' || file.name.endsWith('.csv')
  if (!isCsv) {
    ElMessage.error('请上传CSV文件')
    return false
  }
  return true
}

const startOptimization = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    if (!form.uploadedFile) {
      ElMessage.error('请先上传reaction.csv文件')
      return
    }
    
    loading.value = true
    
    const formData = new FormData()
    formData.append('file', form.uploadedFile)
    formData.append('objectives', JSON.stringify(form.objectives.map(obj => obj.name)))
    formData.append('objective_mode', JSON.stringify(form.objectives.map(obj => obj.mode)))
    formData.append('objective_thresholds', JSON.stringify(form.objectives.map(obj => obj.threshold)))
    formData.append('batch', form.batch)
    formData.append('init_sampling_method', form.samplingMethod)
    formData.append('seed', form.seed)
    formData.append('get_predictions', form.getPredictions)
    formData.append('acquisition_function', form.acquisitionFunction)
    formData.append('sigma_uncertainty', form.sigmaUncertainty)
    formData.append('continuous_features', true)
    formData.append('add_random_samples', true)
    
    const response = await fetch('/api/v1/optimization/run', {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      if (response.status === 400 && errorData.detail.includes('需要至少3个完成的实验数据')) {
        throw new Error('需要至少3个完成的实验数据才能进行优化')
      }
      throw new Error(errorData.detail || '优化失败')
    }
    
    const filename = response.headers.get('Content-Disposition')
      ?.split('filename=')[1]
      ?.replace(/['"]/g, '')
    
    const blob = await response.blob()
    optimizationResult.value = {
      filename: filename || 'optimization_results.csv',
      blobUrl: URL.createObjectURL(blob),
      isInitialDesign: filename === 'initial_design.csv'
    }
    showResult.value = true
    
    if (optimizationResult.value.isInitialDesign) {
      ElMessage.success('初始实验设计已生成，请完成实验后重新上传数据')
    }
    
  } catch (error) {
    ElMessage.error(error.message || '优化失败，请检查输入')
  } finally {
    loading.value = false
  }
}

const downloadResults = () => {
  if (!optimizationResult.value) return
  
  try {
    const a = document.createElement('a')
    a.href = optimizationResult.value.blobUrl
    a.download = optimizationResult.value.filename
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(optimizationResult.value.blobUrl)
    a.remove()
  } catch (error) {
    ElMessage.error('下载失败，请重试')
  }
}
</script>

<style scoped>
.optimization-runner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.tabs-container {
  background: transparent;
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

.objective-item {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.input-field {
  width: 100%;
}

.select-field {
  width: 100%;
}

.add-btn,
.optimize-btn,
.upload-btn,
.download-btn {
  border-radius: 8px;
  padding: 10px 20px;
  font-weight: 500;
}

.delete-btn {
  border-radius: 8px;
  padding: 8px 16px;
  font-weight: 500;
}

.form-buttons {
  margin-top: 30px;
  text-align: center;
}

.result-section {
  margin-top: 20px;
  text-align: center;
}

.upload-demo {
  margin-top: 10px;
}

.result-dialog {
  border-radius: 12px;
}

/* 响应式处理 */
@media (max-width: 768px) {
  .optimization-runner {
    padding: 10px;
  }
  
  .header h1 {
    font-size: 20px;
  }
  
  :deep(.el-tabs__item) {
    font-size: 14px;
    padding: 0 16px;
  }
  
  .box-card {
    margin-bottom: 16px;
  }
  
  .objective-item {
    margin-bottom: 16px;
    padding-bottom: 16px;
  }
  
  .form-buttons {
    margin-top: 20px;
  }
}

@media (max-width: 480px) {
  .header h1 {
    font-size: 18px;
  }
  
  :deep(.el-tabs__item) {
    font-size: 12px;
    padding: 0 12px;
  }
  
  .form-buttons {
    margin-top: 16px;
  }
}

@media (prefers-color-scheme: dark) {
  .box-card {
    background: rgba(28, 28, 30, 0.7);
    border-color: rgba(255, 255, 255, 0.1);
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
