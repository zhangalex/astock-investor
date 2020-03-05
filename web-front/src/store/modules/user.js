import API from "@/api/user"
import { getToken, setToken, removeToken } from '@/core/auth';
import DefaultAvatar from '@/assets/images/man1.png'

const userModule = {
    state: {
        token: '',
        name: '',
        avatar: '',
        roles: []
    },

    mutations: {
        SET_TOKEN: (state, token) => {
            state.token = token;
        },
        SET_NAME: (state, name) => {
            state.name = name;
        },
        SET_AVATAR: (state, avatar) => {
            state.avatar = avatar;
        },
        SET_ROLES: (state, roles) => {
            state.roles = roles;
        }
    },

    actions: {
        // 登录
        Login({ commit }, userInfo) {
            const mobile = userInfo.mobile.trim();
            return new Promise((resolve, reject) => {
                API.login(mobile, userInfo.password, userInfo.validCode).then(response => {
                    const data = response.data 
                    if(data.token) {
                        setToken(data.token);
                    }
                    resolve(response);
                }).catch(error => {
                    reject(error);
                });
            });
        },
        // 获取用户信息
        GetInfo({ commit, state }) {
            return new Promise((resolve, reject) => {
                API.getUserInfo().then(response => {
                    const data = response.data;
                    commit('SET_ROLES', data.role);
                    commit('SET_NAME', data.name);
                    commit('SET_AVATAR', data.avatar == null || data.avatar == '' ? DefaultAvatar : data.avatar);
                    commit('SET_TOKEN', getToken()); //不管是登陆还是登陆后的刷新，都会调用获取用户信息的方法
                    resolve(response);
                }).catch(error => {
                    reject(error);
                });
            });
        },

        // 登出
        LogOut({ commit, state }) {
            return new Promise((resolve, reject) => {
                commit('SET_TOKEN', '');
                commit('SET_ROLES', []);
                removeToken();
                resolve();
            });
        },

        // 前端 登出
        FedLogOut({ commit }) {
            return new Promise(resolve => {
                commit('SET_TOKEN', '');
                removeToken();
                resolve();
            });
        }
    }
}

export default userModule;
