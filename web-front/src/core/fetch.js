import axios from 'axios';
import { Message, MessageBox } from 'element-ui';
import store from '../store';
import { getToken } from '@/core/auth';

// 创建axios实例
const service = axios.create({
    baseURL: process.env.BASE_API, // api的base_url
    timeout: 8000 // 请求超时时间
});

// request拦截器
service.interceptors.request.use(config => {
    // console.log('token...', store, store.getters.token)
    // if (store.getters.token) {
    //     config.headers['Authorization'] = `AiBearer ${store.getters.token}`; // 让每个请求携带自定义token 请根据实际情况自行修改
    // }
    let token = getToken()
    if (token && token !== 'undefined') {
        config.headers['Authorization'] = `AiBearer ${token}`; // 让每个请求携带自定义token 请根据实际情况自行修改
    }
    return config;
}, error => {
    // Do something with request error
    console.log(error); // for debug
    Promise.reject(error);
})
// respone拦截器
service.interceptors.response.use(
    response => {
        /**
         * code为非1是抛错 可结合自己业务进行修改
         */
        const res = response.data;
        // console.log('res.....',res)
        if (res.code !== undefined && res.code != 1) {
            Message({
                message: res.message,
                type: 'error',
                duration: 5 * 1000
            });
            return Promise.reject(error);
        } else {
            // return response.data;
            return response;
        }
    },
    error => {
        // console.log(error.response); // for debug
        const resp = error.response
        if (resp && resp.data) {
            switch(resp.status) {
                case 403:
                    Message({
                        message:  resp.data.message || '登陆失败，用户名或者密码错误。',
                        type: 'error',
                        duration: 5 * 1000
                    });
                    break 

                case 404:
                    Message({
                        message:  resp.data.message || '找不到该资源',
                        type: 'error',
                        duration: 5 * 1000
                    });
                    location.href = "/"
                    break 

                case 401:
                    MessageBox.confirm('你已被登出, 可以取消继续留在该页面, 或者重新登录', '确定登出', {
                        confirmButtonText: '重新登录',
                        cancelButtonText: '取消',
                        type: 'warning'
                    }).then(() => {
                        store.dispatch('FedLogOut').then(() => {
                            location.reload(); // 为了重新实例化vue-router对象 避免bug
                        });
                    })
                    break

                case 500:
                    Message({
                        message: resp.data.message,
                        type: 'error',
                        duration: 5 * 1000
                    });
                    break
                default:
                    Message({
                        message: resp.data.message,
                        type: 'error',
                        duration: 5 * 1000
                    });
                    break
            }

        } else {
            Message({
                message: error.message,
                type: 'error',
                duration: 5 * 1000
            });
        }

        return Promise.reject(error);
    }
)

export default service;
