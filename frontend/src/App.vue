<template>
  <div id="app">
    <el-container>
      <el-header>
        <h1>数据开发平台</h1>
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

.el-header h1 {
  margin: 0;
  font-size: 24px;
}

.el-main {
  padding: 20px;
}
</style>
