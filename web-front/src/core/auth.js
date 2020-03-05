//import Cookies from 'js-cookie'

const TokenKey = 'AIF-Token'

export function getToken() {
  //return Cookies.get(TokenKey)
  return localStorage.getItem(TokenKey)
}

export function setToken(token) {
  //return Cookies.set(TokenKey, token, { expires: 3 })
  return localStorage.setItem(TokenKey, token)
}

export function removeToken() {
  //return Cookies.remove(TokenKey)
  return localStorage.removeItem(TokenKey)
}
