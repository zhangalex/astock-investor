<template>
<div class="modify_pwd">
  <div>
  <el-breadcrumb separator-class="el-icon-arrow-right">
  <!-- <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item> -->
  <el-breadcrumb-item>用户中心</el-breadcrumb-item>
  <el-breadcrumb-item>修改密码</el-breadcrumb-item>
  </el-breadcrumb>
  </div>
  <div class="box">
    <el-form :model="modifyForm" status-icon :rules="rules" ref="modifyForm" label-width="100px" >
      <el-form-item label="原密码" prop="oldPassword">
        <el-input type="password" v-model="modifyForm.oldPassword" auto-complete="off"></el-input>
      </el-form-item>
      <el-form-item label="新密码" prop="newPassword">
        <el-input type="password" v-model="modifyForm.newPassword" auto-complete="off"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="warning" @click="submitForm('modifyForm')">确认修改</el-button>
      </el-form-item>
    </el-form>
  </div>
</div>
</template>

<script>
import { MessageBox, Message } from 'element-ui'
import API from '@/api/user'
export default {
  name: 'modify-pwd',
  data () {
    return {
      modifyForm: {
        oldPassword: '',
        newPassword: ''
      },
      rules: {
          oldPassword: [
            { required: true, message: '请输入原密码', trigger: 'blur' },
            { min: 6, max: 10, message: '长度在 6 到 10 个字符', trigger: 'blur' }
          ],
          newPassword: [
            { required: true, message: '请输入新密码', trigger: 'blur' },
            { min: 6, max: 10, message: '长度在 6 到 10 个字符', trigger: 'blur' }
          ]
      }
    }
  },
  methods: {
    submitForm (formName) {
      this.$refs[formName].validate((valid) => {
          if (valid) {
            const self = this 
            MessageBox.confirm('确实要修改密码吗？', '确认', {
              confirmButtonText: '确认',
              cancelButtonText: '取消',
              type: 'warning'
            }).then(() => {
              API.modify_password(self.modifyForm.oldPassword, self.modifyForm.newPassword).then(() => {
                Message({message: '密码修改成功, 现在重新登录', type: 'success', duration: 5 * 1000});
                //修改密码成功后，重新登录
                setTimeout(() => {
                  self.$store.dispatch('LogOut').then(() => {
                    location.reload()  //为了重新实例化vue-router对象 避免bug
                  })
                }, 800)
                
            })
            }, ()=> {console.log('You canceled')})

          } else {
            return false;
          }
      });
    }
  }
}
</script>

<style lang='scss' scoped>

.modify_pwd {
  padding: 15px;
}
.box {
  margin-top: 40px;
  width: 400px;
}
</style>
