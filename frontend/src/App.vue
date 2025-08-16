<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-inner">
          <h1>数据开发平台</h1>
          <div class="nav">
            <router-link to="/database">
              <el-button type="primary" link>数据库</el-button>
            </router-link>
            <router-link to="/chat">
              <el-button type="primary" link>对话</el-button>
            </router-link>
          </div>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

.el-header {
  background-color: #409EFF;
  color: white;
  text-align: center;
  line-height: 60px;
}

.header-inner { display: flex; justify-content: space-between; align-items: center; }
.el-header h1 { margin: 0; font-size: 24px; }
.nav a { margin-left: 8px; }

.el-main {
  padding: 20px;
}
</style>
