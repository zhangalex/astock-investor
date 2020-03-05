<template>
<div class="usermg">
  <div style="margin-bottom: 20px">
    <el-breadcrumb separator-class="el-icon-arrow-right">
      <el-breadcrumb-item>超级管理</el-breadcrumb-item>
      <el-breadcrumb-item>用户管理</el-breadcrumb-item>
    </el-breadcrumb>
  </div>
  <normal-frame title=""  width="100%" :hasBordered="false">
    <vue-table :url="userListUrl"  className="table is-striped amdintable" :showPager="true" @onRowSelected="userSelected" :operations="operations"></vue-table>
  </normal-frame>
  <div style="text-align: left; margin-top:15px;">
    <el-button type="primary" @click="addUser" size="small" >添加用户</el-button>
  </div>
  <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="35%">
      <div class="box">
        <el-form :model="userForm" status-icon ref="userForm" label-width="100px">
          <el-form-item label="手机号" v-if="!isEdit">
            <el-input v-model="userForm.mobile" autoComplete="on"></el-input>
          </el-form-item>
          <el-form-item label="用户名">
            <el-input v-model="userForm.username" autoComplete="on"></el-input>
          </el-form-item>
          <el-form-item label="角色">
            <el-select v-model="userForm.roles" placeholder="请选择角色" style="width: 100%;">
              <el-option label="普通" value="normal"></el-option>
              <el-option label="VIP" value="vip"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="到期时间">
            <el-date-picker type="date" placeholder="选择日期" v-model="userForm.expirationTime" value-format="yyyy-MM-dd" style="width: 100%;"></el-date-picker>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="submitUser()" size="small">{{dialogBtnText}}</el-button>
          </el-form-item>
        </el-form>
      </div>
  </el-dialog>
</div>
</template>

<script>
import { MessageBox, Message } from 'element-ui'
import VueTable    from '@/components/common/vue-table'
import NormalFrame from '@/components/common/normal-frame'
import HTTP from "@/core/fetch"
export default {
  name: 'user-management',
  data () {
    return {
      dialogVisible: false,
      isEdit: false,
      userListUrl: '/admin/users',
      userForm: {
        id: '',
        username: '',
        mobile: '',
        roles: '',
        expirationTime: ''
      },
      operations: [
        {
          title: '删除',
          callback: (item) => {
            const self = this
            MessageBox.confirm('您确实要删除该行记录吗？', '删除确认', {confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning'}).then(() => {
              HTTP.delete(`/admin/users?user_id=${item.id}`).then(dt => {
                this.userListUrl = `${this.userListUrl}?${Math.random()}`
              })
            }, ()=> {})
          },
          isShow: (item) => {
            return true
          }
        },
        {
          title: '冻结',
          callback: (item) => {
            const self = this
            MessageBox.confirm('您确实要冻结该用户吗？', '冻结确认', {confirmButtonText: '冻结', cancelButtonText: '取消', type: 'warning'}).then(() => {
              HTTP.put(`/admin/user_frozen?user_id=${item.id}`).then(dt => {
                this.userListUrl = `${this.userListUrl}?${Math.random()}`
              })
            }, ()=> {})
          },
          isShow: (item) => {
            return item.isFrozen == '否'
          }
        },
        {
          title: '解冻',
          callback: (item) => {
            const self = this
            MessageBox.confirm('您确实要解冻该用户吗？', '解冻确认', {confirmButtonText: '解冻', cancelButtonText: '取消', type: 'warning'}).then(() => {
              HTTP.put(`/admin/user_frozen?user_id=${item.id}`).then(dt => {
                this.userListUrl = `${this.userListUrl}?${Math.random()}`
              })
            }, ()=> {})
          },
          isShow: (item) => {
            return item.isFrozen == '是'
          }
        },
        {
          title: '编辑',
          callback: (item) => {
            this.isEdit = true
            this.userForm.roles = item.roles.toLocaleLowerCase() 
            this.userForm.expirationTime = item.expirationTime
            this.userForm.id = item.id
            this.userForm.username = item.username
            this.dialogVisible = true
            
          },
          isShow: (item) => {
            return true
          }
        }
      ]
    }
  },
  mounted () {
  },
  methods: {
    addUser () {
      this.isEdit = false 
      this.userForm = {id: '', mobile: '', roles: '', expirationTime: ''}
      this.dialogVisible = true
    },
    submitUser () {
      console.log(this.userForm)
      HTTP.post('/admin/user', this.userForm).then(dt => {
        this.dialogVisible = false 
        this.loadData(1)
      })
    },
    userSelected () {
      console.log('ok....')
    }
  },
  computed: {
    dialogTitle () {
      return this.isEdit ? "编辑用户" : "手动添加用户"
    },
    dialogBtnText () {
      return this.isEdit ? "提交修改" : "提交添加"
    } 
  },
  components: {
    VueTable, NormalFrame
  }
}
</script>

<style lang='scss' scoped>
.usermg {
  padding: 10px;
}
.box {
  padding: 5px 0px 5px 0px;
}

</style>
