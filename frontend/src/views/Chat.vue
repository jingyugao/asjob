<template>
  <div class="chat-page">
    <el-row :gutter="20">
      <!-- 左侧：工具与会话 -->
      <el-col :span="6">
        <el-card class="sidebar-card">
          <template #header>
            <div class="card-header">
              <span>会话</span>
              <el-button type="primary" size="small" @click="onNewConversation">新建会话</el-button>
            </div>
          </template>

          <div class="conversation-info" v-if="selectedConversationId">
            <el-tag type="info" round>会话ID: {{ selectedConversationId }}</el-tag>
          </div>
          <div class="conversation-empty" v-else>
            <el-empty description="暂无会话，点击新建会话" />
          </div>
        </el-card>

        <el-card class="sidebar-card" style="margin-top: 16px;">
          <template #header>
            <span>可用工具</span>
          </template>
          <el-empty v-if="tools.length === 0" description="暂无工具" />
          <el-timeline v-else>
            <el-timeline-item v-for="t in tools" :key="t.name" type="primary">
              <div class="tool-item">
                <div class="tool-name">{{ t.name }}</div>
                <div class="tool-desc">{{ t.description }}</div>
                <pre class="tool-schema">{{ formatJson(t.schema) }}</pre>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>

      <!-- 右侧：聊天窗口 -->
      <el-col :span="18">
        <el-card class="chat-card">
          <template #header>
            <span>智能助理</span>
          </template>

          <div v-if="!selectedConversationId" class="no-selection">
            <el-empty description="请先新建会话" />
          </div>

          <div v-else class="chat-window">
            <div class="messages" ref="messagesRef">
              <div v-for="m in messages" :key="m.id" class="message" :class="m.role">
                <div class="meta">
                  <el-tag size="small" :type="roleTagType(m.role)">{{ labelOfRole(m.role) }}</el-tag>
                  <span v-if="m.name" class="name">{{ m.name }}</span>
                  <span class="time">{{ m.created_at }}</span>
                </div>
                <div class="content" v-if="!m.tool_call">{{ m.content }}</div>
                <div v-else class="content">
                  <div class="assistant-text">{{ m.content }}</div>
                  <div class="tool-call">
                    <div class="tool-call-title">Function Call</div>
                    <pre class="json">{{ formatJson(m.tool_call) }}</pre>
                  </div>
                </div>
              </div>
            </div>

            <div class="composer">
              <el-input
                v-model="input"
                type="textarea"
                :rows="3"
                placeholder="输入消息，按发送"
                @keyup.enter.exact.prevent="onSend"
              />
              <div class="composer-actions">
                <el-button type="primary" :loading="sending" @click="onSend">发送</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
  
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'

export default {
  name: 'Chat',
  setup() {
    const selectedConversationId = ref(null)
    const messages = ref([])
    const tools = ref([])
    const input = ref('')
    const sending = ref(false)
    const messagesRef = ref(null)

    const scrollToBottom = async () => {
      await nextTick()
      if (messagesRef.value) {
        messagesRef.value.scrollTop = messagesRef.value.scrollHeight
      }
    }

    const formatJson = (obj) => {
      try {
        return JSON.stringify(obj, null, 2)
      } catch (e) {
        return String(obj)
      }
    }

    const roleTagType = (role) => {
      if (role === 'assistant') return 'success'
      if (role === 'tool') return 'warning'
      if (role === 'system') return 'info'
      return ''
    }

    const labelOfRole = (role) => {
      if (role === 'assistant') return '助手'
      if (role === 'tool') return '工具'
      if (role === 'system') return '系统'
      return '用户'
    }

    const loadTools = async () => {
      try {
        const { data } = await axios.post('/api/v1/chat/tools')
        tools.value = data.tools || []
      } catch (e) {
        tools.value = []
      }
    }

    const loadMessages = async (conversationId) => {
      if (!conversationId) return
      const { data } = await axios.get(`/api/v1/chat/conversations/${conversationId}/messages`)
      messages.value = data || []
      await scrollToBottom()
    }

    const createConversation = async () => {
      const { data } = await axios.post('/api/v1/chat/conversations', { title: null })
      selectedConversationId.value = data.id
      messages.value = []
      return data.id
    }

    const onNewConversation = async () => {
      await createConversation()
    }

    const onSend = async () => {
      if (!input.value.trim()) return
      try {
        sending.value = true
        if (!selectedConversationId.value) {
          await createConversation()
        }
        const { data } = await axios.post('/api/v1/chat/ask', {
          conversation_id: selectedConversationId.value,
          content: input.value.trim()
        })
        selectedConversationId.value = data.conversation_id
        messages.value = data.messages || []
        input.value = ''
        await scrollToBottom()
      } catch (e) {
        // ignore
      } finally {
        sending.value = false
      }
    }

    onMounted(async () => {
      await loadTools()
    })

    return {
      selectedConversationId,
      messages,
      tools,
      input,
      sending,
      formatJson,
      onSend,
      onNewConversation,
      messagesRef,
      roleTagType,
      labelOfRole
    }
  }
}
</script>

<style scoped>
.chat-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-card .tool-item {
  margin-bottom: 8px;
}
.tool-name {
  font-weight: 600;
}
.tool-desc {
  color: #606266;
  margin: 4px 0;
}
.tool-schema {
  background: #f5f7fa;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
}

.chat-card {
  min-height: 600px;
}
.chat-window {
  display: flex;
  flex-direction: column;
  height: 70vh;
}
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  background: #fafafa;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}
.message {
  margin-bottom: 14px;
}
.message .meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.message .name { color: #606266; }
.message .time { color: #909399; font-size: 12px; }
.message .content { white-space: pre-wrap; }
.assistant-text { margin-bottom: 6px; }
.tool-call-title { font-weight: 600; margin: 6px 0; }
.json { background: #f5f7fa; padding: 8px; border-radius: 4px; overflow-x: auto; }

.composer {
  margin-top: 12px;
}
.composer-actions {
  margin-top: 8px;
  text-align: right;
}

.no-selection {
  text-align: center;
  padding: 40px 0;
}
</style>


