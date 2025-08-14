<template>
  <div class="database-manager">
    <el-row :gutter="20">
      <!-- 左侧：连接管理 -->
      <el-col :span="6">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>数据库连接管理</span>
              <el-button type="primary" @click="showAddDialog = true">
                <el-icon><Plus /></el-icon>
                添加连接
              </el-button>
            </div>
          </template>
          
          <div class="connection-list">
            <el-empty v-if="connections.length === 0" description="暂无连接" />
            <div v-else>
              <div
                v-for="conn in connections"
                :key="conn.name"
                class="connection-item"
                :class="{ active: selectedConnection === conn.name }"
                @click="selectConnection(conn.name)"
              >
                <div class="connection-info">
                  <el-icon><Connection /></el-icon>
                  <span class="connection-name">{{ conn.name }}</span>
                  <el-tag size="small" :type="conn.db_type === 'mysql' ? 'success' : 'warning'">
                    {{ conn.db_type.toUpperCase() }}
                  </el-tag>
                </div>
                <el-button
                  type="danger"
                  size="small"
                  @click.stop="removeConnection(conn.name)"
                >
                  删除
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：表结构和数据 -->
      <el-col :span="18">
        <el-tabs v-model="activeTab" type="card">
          <!-- 表结构标签页 -->
          <el-tab-pane label="表结构" name="structure">
            <el-card>
              <template #header>
                <span>表结构信息</span>
              </template>
              
              <div v-if="!selectedConnection" class="no-selection">
                <el-empty description="请选择一个数据库连接" />
              </div>
              
              <div v-else>
                <div class="table-selection">
                  <el-select
                    v-model="selectedTable"
                    placeholder="选择表"
                    @change="loadTableStructure"
                    style="width: 200px"
                  >
                    <el-option
                      v-for="table in tables"
                      :key="table"
                      :label="table"
                      :value="table"
                    />
                  </el-select>
                </div>
                
                <div v-if="selectedTable && tableStructure" class="table-structure">
                  <h3>表: {{ tableStructure.name }}</h3>
                  <el-table :data="tableStructure.columns" border>
                    <el-table-column prop="field" label="字段名" />
                    <el-table-column prop="type" label="类型" />
                    <el-table-column prop="null" label="允许空值" />
                    <el-table-column prop="key" label="键" />
                    <el-table-column prop="default" label="默认值" />
                    <el-table-column prop="extra" label="额外信息" />
                  </el-table>
                </div>
              </div>
            </el-card>
          </el-tab-pane>

          <!-- 表数据标签页 -->
          <el-tab-pane label="表数据" name="data">
            <el-card>
              <template #header>
                <span>表数据</span>
              </template>
              
              <div v-if="!selectedConnection" class="no-selection">
                <el-empty description="请选择一个数据库连接" />
              </div>
              
              <div v-else>
                <div class="table-selection">
                  <el-select
                    v-model="selectedTableForData"
                    placeholder="选择表"
                    @change="loadTableData"
                    style="width: 200px"
                  >
                    <el-option
                      v-for="table in tables"
                      :key="table"
                      :label="table"
                      :value="table"
                    />
                  </el-select>
                </div>
                
                <div v-if="tableData && tableData.length > 0" class="table-data">
                  <div class="data-info">
                    <span>共 {{ totalCount }} 条记录</span>
                    <el-pagination
                      v-model:current-page="currentPage"
                      v-model:page-size="pageSize"
                      :page-sizes="[10, 20, 50, 100]"
                      :total="totalCount"
                      layout="total, sizes, prev, pager, next"
                      @size-change="handleSizeChange"
                      @current-change="handleCurrentChange"
                    />
                  </div>
                  
                  <el-table :data="tableData" border style="width: 100%">
                    <el-table-column
                      v-for="column in tableColumns"
                      :key="column"
                      :prop="column"
                      :label="column"
                      show-overflow-tooltip
                    />
                  </el-table>
                </div>
              </div>
            </el-card>
          </el-tab-pane>

          <!-- SQL查询标签页 -->
          <el-tab-pane label="SQL查询" name="query">
            <el-card>
              <template #header>
                <span>SQL查询</span>
              </template>
              
              <div v-if="!selectedConnection" class="no-selection">
                <el-empty description="请选择一个数据库连接" />
              </div>
              
              <div v-else>
                <div class="sql-editor">
                  <el-input
                    v-model="sqlQuery"
                    type="textarea"
                    :rows="6"
                    placeholder="输入SQL查询语句..."
                    class="sql-input"
                  />
                  <div class="sql-actions">
                    <el-button type="primary" @click="executeSQL">执行查询</el-button>
                    <el-button @click="clearSQL">清空</el-button>
                  </div>
                </div>
                
                <div v-if="queryResult && queryResult.data" class="query-result">
                  <h3>查询结果 ({{ queryResult.total }} 条记录)</h3>
                  <el-table :data="queryResult.data" border style="width: 100%">
                    <el-table-column
                      v-for="column in queryColumns"
                      :key="column"
                      :prop="column"
                      :label="column"
                      show-overflow-tooltip
                    />
                  </el-table>
                </div>
              </div>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>

    <!-- 添加连接对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="添加数据库连接"
      width="500px"
    >
      <el-form
        ref="connectionFormRef"
        :model="newConnection"
        :rules="connectionRules"
        label-width="100px"
      >
        <el-form-item label="连接名称" prop="name">
          <el-input v-model="newConnection.name" placeholder="输入连接名称" />
        </el-form-item>
        
        <el-form-item label="数据库类型" prop="db_type">
          <el-select v-model="newConnection.db_type" placeholder="选择数据库类型" style="width: 100%">
            <el-option label="MySQL" value="mysql" />
            <el-option label="Doris" value="doris" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="主机地址" prop="host">
          <el-input v-model="newConnection.host" placeholder="localhost" />
        </el-form-item>
        
        <el-form-item label="端口" prop="port">
          <el-input-number v-model="newConnection.port" :min="1" :max="65535" style="width: 100%" />
        </el-form-item>
        
        <el-form-item label="用户名" prop="username">
          <el-input v-model="newConnection.username" placeholder="输入用户名" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input v-model="newConnection.password" type="password" placeholder="输入密码" />
        </el-form-item>
        
        <el-form-item label="数据库名" prop="database">
          <el-input v-model="newConnection.database" placeholder="输入数据库名" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="addConnection">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

export default {
  name: 'DatabaseManager',
  setup() {
    const connections = ref([])
    const selectedConnection = ref('')
    const selectedTable = ref('')
    const selectedTableForData = ref('')
    const tables = ref([])
    const tableStructure = ref(null)
    const tableData = ref([])
    const totalCount = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(20)
    const showAddDialog = ref(false)
    const connectionFormRef = ref()
    const activeTab = ref('structure')
    const sqlQuery = ref('')
    const queryResult = ref(null)

    const newConnection = reactive({
      name: '',
      host: 'localhost',
      port: 3306,
      username: '',
      password: '',
      database: '',
      db_type: 'mysql'
    })

    const connectionRules = {
      name: [{ required: true, message: '请输入连接名称', trigger: 'blur' }],
      host: [{ required: true, message: '请输入主机地址', trigger: 'blur' }],
      port: [{ required: true, message: '请输入端口号', trigger: 'blur' }],
      username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
      password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
      database: [{ required: true, message: '请输入数据库名', trigger: 'blur' }],
      db_type: [{ required: true, message: '请选择数据库类型', trigger: 'change' }]
    }

    // 计算属性
    const tableColumns = computed(() => {
      if (tableData.value.length > 0) {
        return Object.keys(tableData.value[0])
      }
      return []
    })

    const queryColumns = computed(() => {
      if (queryResult.value && queryResult.value.data.length > 0) {
        return Object.keys(queryResult.value.data[0])
      }
      return []
    })

    const loadConnections = async () => {
      try {
        const response = await axios.get('/api/connections')
        connections.value = response.data
      } catch (error) {
        ElMessage.error('加载连接列表失败')
      }
    }

    const addConnection = async () => {
      try {
        await connectionFormRef.value.validate()
        await axios.post('/api/connections', newConnection)
        ElMessage.success('连接添加成功')
        showAddDialog.value = false
        resetForm()
        await loadConnections()
      } catch (error) {
        if (error.response?.data?.detail) {
          ElMessage.error(error.response.data.detail)
        } else {
          ElMessage.error('添加连接失败')
        }
      }
    }

    const removeConnection = async (name) => {
      try {
        await ElMessageBox.confirm(`确定要删除连接 "${name}" 吗？`, '确认删除', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await axios.delete(`/api/connections/${name}`)
        ElMessage.success('连接删除成功')
        
        if (selectedConnection.value === name) {
          selectedConnection.value = ''
          selectedTable.value = ''
          selectedTableForData.value = ''
          tables.value = []
          tableStructure.value = null
          tableData.value = []
          queryResult.value = null
        }
        
        await loadConnections()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除连接失败')
        }
      }
    }

    const selectConnection = async (name) => {
      selectedConnection.value = name
      selectedTable.value = ''
      selectedTableForData.value = ''
      tableStructure.value = null
      tableData.value = []
      queryResult.value = null
      await loadTables(name)
    }

    const loadTables = async (connName) => {
      try {
        const response = await axios.get(`/api/connections/${connName}/tables`)
        tables.value = response.data.tables
      } catch (error) {
        ElMessage.error('加载表列表失败')
      }
    }

    const loadTableStructure = async () => {
      if (!selectedTable.value) return
      
      try {
        const response = await axios.get(`/api/connections/${selectedConnection.value}/tables/${selectedTable.value}/structure`)
        tableStructure.value = response.data
      } catch (error) {
        ElMessage.error('加载表结构失败')
      }
    }

    const loadTableData = async () => {
      if (!selectedTableForData.value) return
      
      try {
        const response = await axios.get(`/api/connections/${selectedConnection.value}/tables/${selectedTableForData.value}/data`, {
          params: {
            limit: pageSize.value,
            offset: (currentPage.value - 1) * pageSize.value
          }
        })
        tableData.value = response.data.data
        totalCount.value = response.data.total
      } catch (error) {
        ElMessage.error('加载表数据失败')
      }
    }

    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      if (selectedTableForData.value) {
        loadTableData()
      }
    }

    const handleCurrentChange = (page) => {
      currentPage.value = page
      if (selectedTableForData.value) {
        loadTableData()
      }
    }

    const executeSQL = async () => {
      if (!sqlQuery.value.trim()) {
        ElMessage.warning('请输入SQL查询语句')
        return
      }
      
      try {
        const response = await axios.post(`/api/connections/${selectedConnection.value}/query`, {
          sql: sqlQuery.value.trim()
        })
        queryResult.value = response.data
        ElMessage.success('查询执行成功')
      } catch (error) {
        if (error.response?.data?.detail) {
          ElMessage.error(error.response.data.detail)
        } else {
          ElMessage.error('查询执行失败')
        }
      }
    }

    const clearSQL = () => {
      sqlQuery.value = ''
      queryResult.value = null
    }

    const resetForm = () => {
      Object.assign(newConnection, {
        name: '',
        host: 'localhost',
        port: 3306,
        username: '',
        password: '',
        database: '',
        db_type: 'mysql'
      })
      connectionFormRef.value?.resetFields()
    }

    onMounted(() => {
      loadConnections()
    })

    return {
      connections,
      selectedConnection,
      selectedTable,
      selectedTableForData,
      tables,
      tableStructure,
      tableData,
      totalCount,
      currentPage,
      pageSize,
      showAddDialog,
      connectionFormRef,
      activeTab,
      sqlQuery,
      queryResult,
      newConnection,
      connectionRules,
      tableColumns,
      queryColumns,
      addConnection,
      removeConnection,
      selectConnection,
      loadTableStructure,
      loadTableData,
      handleSizeChange,
      handleCurrentChange,
      executeSQL,
      clearSQL
    }
  }
}
</script>

<style scoped>
.database-manager {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.connection-list {
  max-height: 400px;
  overflow-y: auto;
}

.connection-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  margin: 5px 0;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.connection-item:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.connection-item.active {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.connection-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.connection-name {
  font-weight: 500;
}

.table-selection {
  margin-bottom: 20px;
}

.table-structure h3 {
  margin-bottom: 15px;
  color: #303133;
}

.table-data h3 {
  margin-bottom: 15px;
  color: #303133;
}

.data-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.no-selection {
  text-align: center;
  padding: 40px;
}

.sql-editor {
  margin-bottom: 20px;
}

.sql-input {
  margin-bottom: 15px;
}

.sql-actions {
  display: flex;
  gap: 10px;
}

.query-result h3 {
  margin-bottom: 15px;
  color: #303133;
}
</style>
