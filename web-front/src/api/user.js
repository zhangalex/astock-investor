import http from "@/core/fetch"

const UserAPI = {
    login(mobile, password, validCode) {
        return http.post(`/user/login`, { mobile, password, validCode })
    },
    modify_password(oldpassword, newpassword) {
        return http.post(`/user/modifypwd`, { oldpassword, newpassword })
    },
    getUserInfo() {
        return http.get('/user/user_info')
    },
    send_mobile_validCode(mobile, validCode) {
        return http.post(`/user/send_mobile_code`, { mobile, validCode })
    },
    register(registerInfo) {
        return http.post(`/user/register`, registerInfo)
    },
    submitOrder(orderInfo) {
        return http.post(`/user/order_product`, orderInfo)
    }
    

}

export default UserAPI;
