<template>
  <div id="app">
    <nav class="navbar navbar-default navbar-fixed-top" v-if="islogon">
      <div class="container" style="width:98%">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="#">The Investor Assistant</a>
        </div>
        <div id="navbar" class="collapse navbar-collapse">
          <ul class="nav navbar-nav">
            <router-link tag="li" to="/" exact><a>首页</a></router-link>
            <!-- <li class="dropdown">
              <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">沪深港通<span class="caret"></span></a>
              <ul class="dropdown-menu">
                <router-link tag="li" to="/hk_to_mainland"><a>持股记录分析</a></router-link>
                <router-link tag="li" to="/hsgt_buyandsold"><a>沪深股通-买入卖出分析</a></router-link>
                <router-link tag="li" to="/ggt_buyandsold"><a>港股通-买入卖出分析</a></router-link>
                <router-link tag="li" to="/holders_analysis"><a>沪深港通-股东分析</a></router-link>
              </ul>
            </li>  -->

            <router-link tag="li" to="/hk_to_mainland"><a>持股记录分析</a></router-link>
            <router-link tag="li" to="/hsgt_buyandsold"><a>沪深股通-买入卖出</a></router-link>
            <!-- <router-link tag="li" to="/ggt_buyandsold"><a>港股通-买入卖出</a></router-link> -->
            <router-link tag="li" to="/holders_analysis"><a>中外机构分析</a></router-link>
            <li class="dropdown">
              <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">A股统计 <span class="caret"></span></a>
              <ul class="dropdown-menu">
                <router-link tag="li" to="#"><a>今日A股</a></router-link>
                <router-link tag="li" to="/astock_baseinfo"><a>基本信息统计</a></router-link>
              </ul>
            </li>  
            <!-- <li class="dropdown">
              <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">证券分析 <span class="caret"></span></a>
              <ul class="dropdown-menu">
                <router-link tag="li" to="/finance_analysis"><a>财务分析</a></router-link>
                <router-link tag="li" to="/shareholder_analysis"><a>股东分析</a></router-link>
                <router-link tag="li" to="/company_analysis"><a>公司分析</a></router-link>
              </ul>
            </li>  -->
            <!-- <li class="dropdown">
              <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">工具 <span class="caret"></span></a>
              <ul class="dropdown-menu">
                <router-link tag="li" to="/calculator"><a>投资计算器</a></router-link>
              </ul>
            </li>  -->
            <li class="dropdown">
              <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">关于 <span class="caret"></span></a>
              <ul class="dropdown-menu">
                <router-link tag="li" to="/about"><a>简介</a></router-link>
                <router-link tag="li" to="/contact"><a>联系我们</a></router-link>
              </ul>
            </li> 
            <li class="dropdown" v-if="roles.indexOf('root') >= 0">
              <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">超级管理 <span class="caret"></span></a>
              <ul class="dropdown-menu">
                <router-link tag="li" to="/user_management"><a>用户管理</a></router-link>
              </ul>
            </li> 
          </ul>
          <ul class="nav navbar-nav navbar-right">
            <li class="dropdown">
              <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">{{name}} <span class="caret"></span></a>
              <ul class="dropdown-menu">
                <router-link tag="li" to="/usercenter"><a>用户资料</a></router-link>
                <router-link tag="li" to="/usercenter_modifypassword"><a>修改密码</a></router-link>
                <li><a @click="logout">退出</a></li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <div class="container" style="width:100%; padding: 65px 20px;">   
      <router-view></router-view>
    </div>
    <footer class="footer" v-if="islogon">
      <div class="container">
        <p class="text-muted">Copyright © 2017-2018 投资者助理</p>
      </div>
    </footer>
</div>
</template>

<script>
import 'bootstrap/dist/css/bootstrap.css'
import { mapGetters } from 'vuex'
import { MessageBox } from 'element-ui'
export default {
  name: 'app',
  data () {
    return {
    }
  },
  methods: {
    logout () {
      const self = this 
      MessageBox.confirm('确实要退出系统吗？', '确认', {
        confirmButtonText: '退出',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        self.$store.dispatch('LogOut').then(() => {
          location.reload();  // 为了重新实例化vue-router对象 避免bug
        })
      }, ()=> {console.log('You canceled')})

    }
  },
  mounted () {
  },
  computed: {
    ...mapGetters([
        'islogon',
        'name',
        'roles'
    ])
  }
}
</script>
<style lang="scss">
@font-face {
  font-family: 'EnglishTowne';
  src: url('./assets/fonts/EnglishTowne.ttf') format('truetype');
}
@font-face {
  font-family: 'HelmswaldPost';
  src: url('./assets/fonts/HelmswaldPost.otf') format('opentype');

}
body {
  margin: 0px;
  padding: 0px;
  font-size: 13px;
  background-color: #fff;
  font-family: -apple-system, '微软雅黑', BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", "Helvetica",'PingFang SC',  "Arial", sans-serif;
}
.col-md-6 {
  padding-left: 8px;
  padding-right: 8px;
}
a {
  cursor: pointer;
}
.loginBg {
  background-color: #f0ece9;
  // background: #11212b url(~assets/images/data.png) center 0px repeat-x;
  height: 100%!important;
  position: relative;
  .qqgroup {
    display: block;
    position: absolute;
    top: 10px;
    right: 30px;
    >img {
      border: solid 1px rgb(238, 243, 245);
      width: 150px;
      height: 200px;
    }
  }
}
.el-form-item__content > button {
  float: right;
}
.el-radio-button__orig-radio:checked+.el-radio-button__inner {
  color: #fff;
  background-color: rgb(247, 124, 9);
  border-color: #f77c09;
  -webkit-box-shadow: -1px 0 0 0 #f77c09;
  box-shadow: -1px 0 0 0 #f77c09;
}
</style>
<style lang="sass" scoped>
#app 
  -webkit-font-smoothing: antialiased
  -moz-osx-font-smoothing: grayscale
  // text-align: center
  position: relative

#app > .container
  padding: 65px 12px

a.navbar-brand
  font-family: 'EnglishTowne'
  font-size: 28px

.footer
  position: fxied
  left: 0px
  bottom: 0px
  margin: 20px 0px 0px 0px
  width: 100%
  height: 60px

.footer > .container
  padding-right: 15px
  padding-left: 15px

.container .text-muted 
  margin: 20px 0

.text-muted 
  color: #777
  font-size: 14px
  font-weight: 300
  text-align: center

</style>
