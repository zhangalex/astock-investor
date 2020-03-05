const getters = {
  sidebar: state => state.app.sidebar,
  token: state => state.user.token,
  avatar: state => state.user.avatar,
  name: state => state.user.name,
  roles: state => state.user.roles,
  islogon: state => state.user.token != null && state.user.token !== ''
  // permission_routers: state => state.permission.routers,
  // addRouters: state => state.permission.addRouters
};
export default getters
