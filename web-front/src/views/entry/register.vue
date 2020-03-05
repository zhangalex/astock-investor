<template>
  <div class="row">
    <div class="col-md-12"> 
      <div class="register-container">
        <el-form autoComplete="on" :model="registerForm" :rules="rules"  ref="registerForm" label-position="left" label-width="100px">
          <el-form-item prop="mobile" label="手机号码">
            <el-input name="mobile" type="text" v-model="registerForm.mobile" autoComplete="on" placeholder="手机号码(请填写真实的手机号，以用于登陆和重置密码)" required="true"></el-input>
          </el-form-item>
          <el-form-item prop="validCode" label="">
            <el-col :span="8"> 
            <img :src="validCodeUrl" @click.stop="changeCode" style="margin-left:10px"/>
            </el-col>
            <el-col :span="16">
            <el-input name="validCode" type="text" v-model="registerForm.validCode" autoComplete="on" placeholder="请输入图片中的验证码（点击图片可更改）" required="true"></el-input>
            </el-col> 
          </el-form-item>
          <el-form-item>
            <el-col :span="8">
              <el-input type="text" v-model="registerForm.mobileValidCode" placeholder="填写手机收到的数字" />
            </el-col>
            <el-col :span="16">
              <el-button type="success" style="margin-left: 10px;" :disabled="isDisableMobileBtn" @click.stop="sendValidToMobile">{{sendMobileTxt}}</el-button>
            </el-col>
          </el-form-item>
          <el-form-item prop="username" label="用户名">
            <el-input name="username" type="text" v-model="registerForm.username" autoComplete="on" placeholder="用户名(可以是你的姓名或者花名，会显示到你的主页)" required="true"></el-input>
          </el-form-item>
          <el-form-item prop="password" label="登陆密码">
            <el-input name="password" type="password" v-model="registerForm.password" autoComplete="on" placeholder="密码"></el-input>
          </el-form-item>
          <el-form-item prop="repeatPassword" label="密码确认">
            <el-input name="repeatPassword" type="password" v-model="registerForm.repeatPassword" autoComplete="on" placeholder="密码确认"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" style="width:100%; margin-top:15px;" :loading="loading" @click.native.prevent="submitRegister('registerForm')">
              提交
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script>
import { MessageBox, Message } from 'element-ui'
import API from '@/api/user'
import $ from 'jQuery'
export default {
  name: 'register',
  data() {
    return {
      registerForm: {
        username: '',
        mobile: '',
        validCode: '',
        password: '',
        repeatPassword: '',
        mobileValidCode: ''
      },
      loading: false,
      isDisableMobileBtn: false,
      sendMobileTxt: '发送手机验证码',
      validCodeUrl: '/api/v1.0/user/verify_code?num=zc',
      rules: {
          mobile: [
            { required: true, message: '请输入手机号', trigger: 'blur' },
            { min: 11, max: 15, message: '长度在 11 到 15 个字符', trigger: 'blur' }
          ],
          username: [
            { required: true, message: '请输入用户名', trigger: 'blur' },
            { min: 2, max: 15, message: '长度在 3 到 15 个字符', trigger: 'blur' }
          ],
          password: [
            { required: true, message: '请输入密码', trigger: 'blur' },
            { min: 6, max: 10, message: '长度在 6 到 10 个字符', trigger: 'blur' }
          ],
          repeatPassword: [
            { required: true, message: '请输入密码确认，保持两次相同', trigger: 'blur' },
            { min: 6, max: 10, message: '长度在 6 到 10 个字符', trigger: 'blur' }
          ]
      }
    }
  },
  mounted () {
  },
  methods: {
    submitRegister (formName) {
      this.$refs[formName].validate((valid) => {
          if (valid) {
            if(this.registerForm.password !== this.registerForm.repeatPassword) {
              Message({message: '两次密码不一致，请重新输入密码', type: 'error', duration: 5 * 1000});
              return false
            }
            API.register(this.registerForm).then(dt => {
              Message({message: '注册成功，可以马上登陆！您将可以免费试用该工具5天，谢谢您的惠顾。', type: 'success', duration: 10 * 1000});
              this.$emit('registerSuccessed')
            })

          } else {
            return false;
          }
      });
    },
    changeCode () {
      this.validCodeUrl = `/api/v1.0/user/verify_code?num=${Math.random().toString().replace('0.','')}`
    },
    sendValidToMobile () {
      if(this.registerForm.mobile != '' && this.registerForm.validCode != '') {
        API.send_mobile_validCode(this.registerForm.mobile, this.registerForm.validCode).then(dt => {
          console.log(dt.data)
          this.processSendMobileBtn()
          Message({message: '手机验证码发送成功，请注意查收。', type: 'success', duration: 2 * 1000});
        })
      }
    },
    processSendMobileBtn () {
      this.isDisableMobileBtn = true 
      let self = this
      let waitTime = 60 //senconds
      self.sendMobileTxt = `(${waitTime}) 重新发送`
      let timer = setInterval(() => {
        waitTime --
        self.sendMobileTxt = `(${waitTime}) 重新发送`
        if(waitTime <= 0) {
          clearInterval(timer)
          // self.changeCode()
          self.isDisableMobileBtn = false
          self.sendMobileTxt = '发送手机验证码'
        } 
      }, 1000)
    }
  }
}
</script>
<style lang="scss" scoped>
@import "src/styles/mixin.scss";
.el-form-item {
  margin-bottom: 20px;
}
.register-container {
 
}  


</style>

