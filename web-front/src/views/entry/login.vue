<template>
  <div class="row">
    <div class="col-md-12"> 
      <div class="login-container">
        <!-- <img class="rsjsh" src="~assets/images/rsjsh.png" /> -->
        <el-form autoComplete="on" :model="loginForm"  ref="loginForm" label-position="left" label-width="0px"
          class="card-box login-form">
          <div class="title">Investor Assistant - Login</div>
          <el-form-item prop="mobile">
            <el-input name="mobile" type="text" v-model="loginForm.mobile" autoComplete="on" placeholder="手机号码" required="true" ></el-input>
          </el-form-item>
          <el-form-item prop="password">
            <el-input name="password" type="password" v-model="loginForm.password" autoComplete="on" placeholder="密码"></el-input>
          </el-form-item>
          <el-form-item prop="validCode">
            <el-col :span="8"> 
            <img :src="validCodeUrl" @click.stop="changeCode" style="margin-left:10px"/>
            </el-col>
            <el-col :span="16">
            <el-input name="validCode" type="text" @keyup.enter.native="handleLogin" v-model="loginForm.validCode" autoComplete="on" placeholder="请输入图片中的验证码（点击图片可更改）" required="true"></el-input>
            </el-col> 
            
          </el-form-item>
          <el-form-item>
            <el-button type="primary" style="width:100%;" :loading="loading" @click.native.prevent="handleLogin">
              登录
            </el-button>
          </el-form-item>
        </el-form>
        <!-- <div class="toRegister"><a @click.stop="showContact">有疑问？点击查看联系方式</a></div> -->
        <!-- <div class="toRegister"><a @click.stop="showRegister">还没有账号？去注册 <i class="fa fa-arrow-right" aria-hidden="true" /></a></div> -->
        <!-- <div class="findPassword"><a @click.stop="showReset"><i class="fa fa-arrow-left" aria-hidden="true" /> 忘记密码？去重置</a></div> -->
        <!-- <div class="findPassword"><a @click.stop="showContact"><i class="fa fa-arrow-left" aria-hidden="true" /> 有疑问？点击查看联系方式</a></div> -->
      </div>
    </div>
    <el-dialog title="用户注册" :visible.sync="zcdialogVisible" @close="closeDialog">
      <register @registerSuccessed="closeRegister"></register>
    </el-dialog>
    <el-dialog
      title="试用期结束，购买服务继续使用 (当前交易接口尚未开发完毕，暂时使用直接付款的方式)"
      :visible.sync="orderDialogVisible" @open="openOrder">
      <div style="margin-top: -10px">
        <el-radio-group v-model="order.buyMonthes" @change="changeMonth">
          <el-radio-button label="1">1个月</el-radio-button>
          <el-radio-button label="3">3个月(9.5折)</el-radio-button>
          <el-radio-button label="6">6个月(8.8折)</el-radio-button>
          <el-radio-button label="12">1年(8.3折)</el-radio-button>
        </el-radio-group>
      </div>
      <div class="amount"><label>{{amountText}}</label> <label>{{realAmountText}}</label></div>
      <div class="qrcode">
        <div class="row">
          <div class="col-md-6" style="padding:15px">
            <div class="title">微信支付</div>
            <img src="~assets/images/weixin_pay.jpg" style="width: 100%;height: 260px;"/>
          </div>
          <div class="col-md-6" style="padding:15px">
            <div class="title">支付宝支付</div>
            <img src="~assets/images/ali_pay.jpg" style="width: 100%;height: 260px;"/>
          </div>
        </div>
      </div>
      <el-input type="textarea" :rows="2" placeholder="如果您用微信支付，就填写您的微信账号；如果您使用支付宝支付，请填写您的支付宝账号。)" v-model="order.leaveWords"></el-input>
      <el-button type="primary" style="width:100%; margin-top:15px; margin-bottom: 10px" :loading="orderLoading" @click.native.prevent="submitOrder">我已经支付完毕，请为我解禁账号</el-button>
    </el-dialog>
    <el-dialog title="联系我们" :visible.sync="contactdialogVisible" @close="closeCtDialog">
      <p>电子邮件：hellolaojiang@qq.com</p>
      <p>QQ号码： 492515284</p>
      <p>微信二维码(扫码关注)：</p>
      <p><img src="../../assets/wxewm.png" style="border:solid 1px silver; width:300px;height:375px;"></p>
    </el-dialog>
  </div>
</template>

<script>
import { MessageBox, Message } from 'element-ui'
import $ from 'jQuery'
import Order from '@/core/order'
import UserApi from '@/api/user'
export default {
  name: 'login',
  data() {
    return {
      loginForm: {
        mobile: '',
        password: '',
        validCode: ''
      },
      loading: false,
      orderLoading: false,
      zcdialogVisible: false,
      orderDialogVisible: false,
      contactdialogVisible: false,
      validCodeUrl: '/api/v1.0/user/verify_code?num=lg',
      amountText: '',
      realAmountText: '',
      order: {
        buyMonthes: '1',
        leaveWords: '',
        mobile: ''
      }
    }
  },
  mounted () {
    $('body').addClass('loginBg')
    this.changeMonth()
  },
  methods: {
    handleLogin() {
      this.loading = true;
      this.$store.dispatch('Login', this.loginForm).then((dt) => {
          const data = dt.data 
          if(data.needPay !== 'true') {
            this.loading = false
            $('.qqgroup').hide()
            $('body').removeClass('loginBg')
            this.$router.push({ path: '/' })
          } else {
            // this.order.mobile = data.mobile
            // this.orderDialogVisible = true
            this.$message({message: '账户到期或者被冻结，请与管理员联系。', type: 'error'})
          }
          this.loading = false
          
        }).catch((e) => {
          this.loading = false
      });
    },
    showRegister () {
      this.zcdialogVisible = true
    },
    showReset () {

    },
    showContact () {
      this.contactdialogVisible = true
    },
    closeDialog () {
      this.changeCode()
    },
    closeRegister () {
      this.zcdialogVisible = false
    },
    closeCtDialog () {
      this.contactdialogVisible = false
    },
    changeCode () {
      this.validCodeUrl = `/api/v1.0/user/verify_code?num=${Math.random().toString().replace('0.','')}`
    },
    openOrder () {
      this.changeMonth()
    },
    changeMonth () {
      let fee, realFee
      [fee, realFee] = Order.calculateFee(this.order.buyMonthes)
      this.amountText = `总价：￥${fee}`
      if(fee !== realFee) {
        this.realAmountText = `原价：￥${realFee}`
      } else {
        this.realAmountText = ''
      }
      console.log(fee, realFee)
    },
    submitOrder () {
      if(this.order.leaveWords !== '' && this.order.mobile !== '') {
        this.orderLoading = true
        UserApi.submitOrder(this.order).then(dt => {
          this.order.leaveWords = ''
          this.order.mobile = ''
          this.order.buyMonthes = '1'
          this.orderDialogVisible = false
          this.loginForm.mobile = ''
          this.loginForm.password = ''
          this.loginForm.validCode = ''
          Message({message: '我们已经收到您提交的订单，在我们确认订单的时间里面，你可以免费使用该产品1天。立刻登陆吧！', type: 'success', duration: 10 * 1000});
          this.orderLoading = false 
          this.changeCode()
        }).catch((e) => {
          this.orderLoading = false
        });
      } else {
        console.log(this.order)
        // console.log($('input[type="textarea"]', this.$el))
        $('textarea', this.$el).focus()
      }
    }
  },
  components: {'register': require('@/views/entry/register')}
}
</script>
<style lang="scss">
@import "src/styles/entry_auto_adapt";
.el-dialog__wrapper {
  top: -40px;
}
.el-form-item {
  margin-top: 20px;
  margin-bottom: 20px;
}
</style>
<style lang="scss" scoped>
@import "src/styles/mixin.scss";
.login-container {
  margin: 20px auto;
  border: 1px solid #ebebeb;
  border-radius: 3px;
  transition: .2s;
  padding: 30px 20px 50px 20px;
  background-color: #fff;
  position: relative;
  a {
    color: grey;
    &:hover {
      color: red;
    }
  }
}

.toRegister {
  position: absolute;
  bottom: 15px;
  right: 15px;
}
.findPassword {
  position: absolute;
  bottom: 15px;
  left: 15px;
}
.rsjsh {
  position: absolute;
  width: 200px;
  height: 75px;
  top: 20px; 
  right: -10px;
}
.login-container .title {
  font-size: 28px;
  font-weight: 300;
  margin: 10px 0px;
  font-family: 'EnglishTowne';
  color: grey;
}
.qrcode .row .title {
  text-align: center;
  padding: 5px 0px;
  font-weight: 500;
}
.qrcode img{
  border: dashed 1px silver;
}
.amount {
  margin-top: 10px;
  font-size: 18px;
}
.amount label {
  margin-right: 15px;
}
.amount label:first-child {
  color: black;
  font-weight: 400;
}
.amount label:last-child {
  font-weight: 300;
  text-decoration: line-through;
}

</style>

