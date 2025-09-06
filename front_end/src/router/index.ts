import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/components/MainLayout.vue'
import LoginView from '@/views/LoginView.vue'
import AccountManagementView from '@/views/AccountManagementView.vue'
import JoinOrganizationView from '@/views/JoinOrganizationView.vue'
import OrganizationManagementView from '@/views/OrganizationManagementView.vue'
import ResetPasswordView from '@/views/ResetPasswordView.vue'
import AdminView from '@/views/AdminView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/home'
    },
    {
      path: '/home',
      name: 'home',
      component: MainLayout,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresAuth: false }
    },
    {
      path: '/account-management',
      name: 'account-management',
      component: AccountManagementView,
      meta: { requiresAuth: true }
    },
    {
      path: '/organizations/join',
      name: 'join-organization',
      component: JoinOrganizationView,
      meta: { requiresAuth: true }
    },
    {
      path: '/organization-management',
      name: 'organization-management',
      component: OrganizationManagementView,
      meta: { requiresAuth: true }
    },
    {
      path: '/reset-password',
      name: 'reset-password',
      component: ResetPasswordView,
      meta: { requiresAuth: false }
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/home'
    }
  ],
})

// 路由守卫 - 检查认证状态和管理员权限
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('user')
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const isAdmin = user.is_admin === true
  
  // 检查认证状态
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } 
  // 检查管理员权限
  else if (to.meta.requiresAdmin && !isAdmin) {
    // 如果不是管理员，重定向到首页并显示提示
    alert('需要管理员权限才能访问此页面')
    next('/')
  }
  // 如果已登录但访问登录页，重定向到首页
  else if (to.path === '/login' && isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
