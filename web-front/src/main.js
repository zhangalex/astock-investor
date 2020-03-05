// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import axios from 'axios'
import VueAxios from 'vue-axios'
import ElementUI from 'element-ui'
// import 'element-ui/lib/theme-chalk/index.css'
import 'element-theme-chalk'

import jQuery from 'jquery'
global.jQuery = jQuery
const Bootstrap = require('bootstrap')

import App from './App'
import router from './router'
import store from './store'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import { getToken } from '@/core/auth'


require("font-awesome-webpack")
Vue.use(VueAxios, axios)
Vue.use(ElementUI,  {size: 'mini'})
Vue.config.productionTip = false

const whiteList = ['/login'];
router.beforeEach((to, from, next) => {
    NProgress.start()
    if (getToken()) {
        if (to.path === '/login') {
            NProgress.done()
            next({ path: '/' })
        } else {
           if (store.getters.roles.length === 0) {
              store.dispatch('GetInfo').then(res => {
                const roles = res.data.role
                next({...to })
                //store.dispatch('GenerateRoutes', { roles }).then(() => {
                  //router.addRoutes(store.getters.addRouters);
                  //next({...to });
                //})
              })
            } else {
              next()
            }
        }
    } else {
        if (whiteList.indexOf(to.path) !== -1) {
            next()
        } else {
            next('/login')
            NProgress.done()
        }
    }
});

router.afterEach(() => {
    NProgress.done();
});

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  template: '<App/>',
  components: { App }
})
