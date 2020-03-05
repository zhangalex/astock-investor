<template>
<div class="usercenter_main">
  <div>
  <el-breadcrumb separator-class="el-icon-arrow-right">
  <el-breadcrumb-item>用户中心</el-breadcrumb-item>
  <el-breadcrumb-item>用户资料</el-breadcrumb-item>
  </el-breadcrumb>
  </div>
  <div class="info" v-if="user.username != ''">
    <ul>
      <li>用户名：</li><li>{{user.username}}</li>
    </ul>
    <ul>
      <li>角色：</li><li>{{user.rolename}}</li>
    </ul>
    <ul>
      <li>到期日期：</li><li>{{user.expireTime}}</li>
    </ul>
  </div>
 </div>
</template>

<script>
import API from '@/api/user'
export default {
  name: 'usercenter-main',
  data () {
    return {
      user: {
        username: '',
        rolename: '',
        expireTime: ''
      }
    }
  },
  mounted () {
    this.loadData()
  },
  methods: {
    loadData () {
      API.getUserInfo().then(dt => {
        const data = dt.data
        console.log(data)
        this.user.username = data.name 
        this.user.rolename = {'root': '超级管理员', 'vip': 'VIP', 'normal': '普通用户'}[data.role[0]]
        this.user.expireTime = data.expireTime
      })
    }
  }
}
</script>

<style lang='scss' scoped>
.usercenter_main {
  padding: 10px;
}
.info {
  margin-top: 20px;
  padding: 10px;
  background-color: lightyellow;
  border: solid 1px rgb(238, 232, 232);
  border-radius: 3px;
  width: 300px;
}
.info ul {
  list-style-type: none;
  width: 220px;
  display: table;
  table-layout: fixed;
  padding: 0px;
  margin: 0px;
  font-weight: 400;

  > li {
    padding: 5px;
    display: table-cell;
    font-size: 15px;
  }
  > li:last-child {
    text-align: left;
  }
}

</style>
