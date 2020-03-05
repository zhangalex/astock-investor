import Vue from 'vue'
import Router from 'vue-router'
// import Welcome from '@/components/welcome'

Vue.use(Router)

export default new Router({
  linkActiveClass: 'active',
  routes: [
    {
      path: '/',
      name: 'Welcome',
      component: () => import(/* webpackChunkName: 'welcome' */'@/components/welcome')
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import(/* webpackChunkName: 'entry' */'@/views/entry/login')
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import(/* webpackChunkName: 'entry' */'@/views/entry/register')
    },
    {
      path: '/hk_to_mainland',
      name: 'HkMainland',
      component: () => import(/* webpackChunkName: 'hsgt' */'@/views/channel/hk-mainland')
    },
    {
      path: '/hsgt_buyandsold',
      name: 'HsgtBuyAndSold',
      component: () => import(/* webpackChunkName: 'hsgt' */'@/views/channel/hsgt-buyandsold')
    },
    {
      path: '/ggt_buyandsold',
      name: 'GgtBuyAndSold',
      component: () => import(/* webpackChunkName: 'hsgt' */'@/views/channel/ggt-buyandsold')
    },
    {
      path: '/holders_analysis',
      name: 'HsgtHoldersAnalysis',
      component: () => import(/* webpackChunkName: 'hsgt' */'@/views/channel/holders-analysis')

    },
    {
      path: '/astock_baseinfo',
      name: 'astockBaseInfo',
      component: () => import(/* webpackChunkName: 'todayAStock' */'@/views/astock/astock-baseinfo')

    },
    {
      path: '/finance_analysis',
      name: 'financeAnalysis',
      component: () => import(/* webpackChunkName: 'stockAnalysis' */'@/components/finance-analysis')

    },
    {
      path: '/shareholder_analysis',
      name: 'shareholderAnalysis',
      component: () => import(/* webpackChunkName: 'stockAnalysis' */'@/components/shareholder-analysis')

    },
    {
      path: '/company_analysis',
      name: 'companyAnalysis',
      component: () => import(/* webpackChunkName: 'stockAnalysis' */'@/components/company-analysis')

    },
    
    // {
    //   path: '/msci',
    //   name: 'Msci',
    //   component: () => import('../components/msci')
    // },
    // {
    //   path: '/calculator',
    //   name: 'Calculator',
    //   component: () => import('../components/calculator')
    // },
    {
      path: '/about',
      name: 'About',
      component: () => import(/* webpackChunkName: 'contact' */'@/components/about')
    },
    {
      path: '/contact',
      name: 'Contact',
      component: () => import(/* webpackChunkName: 'contact' */'@/components/contact-us')
    },
    {
      path: '/usercenter',
      name: 'UserCenterIndex',
      component: () => import(/* webpackChunkName: 'usercenter' */'@/views/usercenter/index')
    },
    {
      path: '/usercenter_modifypassword',
      name: 'UserCenterModifyPwd',
      component: () => import(/* webpackChunkName: 'usercenter' */'@/views/usercenter/modifypwd')
    },
    {
      path: '/user_management',
      name: 'UserManage',
      component: () => import(/* webpackChunkName: 'usercenter' */'@/views/admin/user-management')
    }


  ]
})
