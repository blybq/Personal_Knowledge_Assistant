<template>
  <div class="login-container">
    <div class="login-layout">
      <!-- 左侧登录表单 -->
      <div class="login-card">
        <h1 class="login-title">个人知识助手</h1>
        
        <div class="tab-container">
          <button 
            class="tab-button" 
            :class="{ active: activeTab === 'login' }"
            @click="activeTab = 'login'"
          >
            登录
          </button>
          <button 
            class="tab-button" 
            :class="{ active: activeTab === 'register' }"
            @click="activeTab = 'register'"
          >
            注册
          </button>
        </div>

      <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="form">
        <div class="form-group">
          <label for="email">邮箱</label>
          <input
            id="email"
            v-model="loginForm.email"
            type="email"
            required
            placeholder="请输入邮箱"
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="loginForm.password"
            type="password"
            required
            placeholder="请输入密码"
          />
        </div>

        <button type="submit" class="submit-button" :disabled="authStore.isLoading">
          {{ authStore.isLoading ? '登录中...' : '登录' }}
        </button>

        <div v-if="loginError" class="error-message">
          {{ loginError }}
        </div>

        <div class="forgot-password">
          <router-link to="/reset-password">忘记密码？</router-link>
        </div>
      </form>

      <form v-else @submit.prevent="handleRegister" class="form">
        <div class="form-group">
          <label for="reg-username">用户名</label>
          <input
            id="reg-username"
            v-model="registerForm.username"
            type="text"
            required
            placeholder="请输入用户名"
          />
        </div>

        <div class="form-group">
          <label for="reg-email">邮箱</label>
          <input
            id="reg-email"
            v-model="registerForm.email"
            type="email"
            required
            placeholder="请输入邮箱"
          />
        </div>

        <div class="form-group">
          <label for="reg-password">密码</label>
          <input
            id="reg-password"
            v-model="registerForm.password"
            type="password"
            required
            placeholder="请输入密码"
          />
        </div>

        <button type="submit" class="submit-button" :disabled="authStore.isLoading">
          {{ authStore.isLoading ? '注册中...' : '注册' }}
        </button>

        <div v-if="registerError" class="error-message">
          {{ registerError }}
        </div>
        <div v-if="registerSuccess" class="success-message">
          注册成功！请登录
        </div>
      </form>
      </div>

      <!-- 右侧装饰区域 -->
      <div class="decorative-side">
        <div class="feature-icons">
          <div class="feature-item">
            <div class="icon">💬</div>
            <h3>智能对话</h3>
            <p>与AI进行自然流畅的问答交流</p>
          </div>
          <div class="feature-item">
            <div class="icon">📝</div>
            <h3>云笔记</h3>
            <p>随时随地记录和整理您的想法</p>
          </div>
          <div class="feature-item">
            <div class="icon">👥</div>
            <h3>团队协作</h3>
            <p>与团队成员共享知识和资源</p>
          </div>
          <div class="feature-item">
            <div class="icon">🔒</div>
            <h3>安全可靠</h3>
            <p>您的数据受到全面保护</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const activeTab = ref<'login' | 'register'>('login');
const loginError = ref('');
const registerError = ref('');
const registerSuccess = ref(false);

const loginForm = reactive({
  email: '',
  password: ''
});

const registerForm = reactive({
  username: '',
  email: '',
  password: ''
});

const handleLogin = async () => {
  loginError.value = '';
  
  if (!loginForm.email || !loginForm.password) {
    loginError.value = '请填写完整信息';
    return;
  }

  const result = await authStore.login(loginForm.email, loginForm.password);
  
  console.log("登录的结果result为", result);
  if (result.success) {
    if (result.data?.user.is_admin){
      router.push('/admin');
    } else {
      router.push('/home');
    }
  } else {
    loginError.value = result.message;
  }
};

const handleRegister = async () => {
  registerError.value = '';
  registerSuccess.value = false;

  if (!registerForm.username || !registerForm.email || !registerForm.password) {
    registerError.value = '请填写完整信息';
    return;
  }

  const result = await authStore.register(
    registerForm.username,
    registerForm.email,
    registerForm.password
  );

  if (result.success) {
    registerSuccess.value = true;
    registerForm.username = '';
    registerForm.email = '';
    registerForm.password = '';
    setTimeout(() => {
      activeTab.value = 'login';
      registerSuccess.value = false;
    }, 2000);
  } else {
    registerError.value = result.message;
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  width: 1200px;
}

.login-layout {
  display: flex;
  width: 100%;
  max-width: 1200px;
  gap: 2rem;
  align-items: center;
}

.login-card {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  flex: 1;
  max-width: 450px;
}

.decorative-side {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
}

.feature-icons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  max-width: 500px;
}

.feature-item {
  text-align: center;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  transition: transform 0.3s ease, background 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.15);
}

.icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.feature-item h3 {
  margin: 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.feature-item p {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.9;
}

.login-title {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
  font-size: 1.8rem;
  font-weight: 600;
}

.tab-container {
  display: flex;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #e1e5e9;
}

.tab-button {
  flex: 1;
  padding: 0.75rem;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 1rem;
  color: #666;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

.tab-button.active {
  color: #667eea;
  border-bottom-color: #667eea;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 500;
}

.form-group input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.submit-button {
  padding: 0.75rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.submit-button:hover:not(:disabled) {
  background: #5a67d8;
}

.submit-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error-message {
  color: #e53e3e;
  text-align: center;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.success-message {
  color: #38a169;
  text-align: center;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.forgot-password {
  text-align: center;
  margin-top: 1rem;
}

.forgot-password a {
  color: #667eea;
  text-decoration: none;
  font-size: 0.9rem;
}

.forgot-password a:hover {
  text-decoration: underline;
}
</style>
