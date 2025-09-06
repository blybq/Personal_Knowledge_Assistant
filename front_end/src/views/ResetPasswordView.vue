<template>
  <div class="reset-password-container">
    <div class="reset-password-card">
      <h1 class="reset-password-title">重置密码</h1>
      
      <div class="steps-container">
        <div class="step" :class="{ active: currentStep === 1, completed: currentStep > 1 }">
          <span class="step-number">1</span>
          <span class="step-text">输入邮箱</span>
        </div>
        <div class="step-connector" :class="{ completed: currentStep > 1 }"></div>
        <div class="step" :class="{ active: currentStep === 2, completed: currentStep > 2 }">
          <span class="step-number">2</span>
          <span class="step-text">验证身份</span>
        </div>
        <div class="step-connector" :class="{ completed: currentStep > 2 }"></div>
        <div class="step" :class="{ active: currentStep === 3 }">
          <span class="step-number">3</span>
          <span class="step-text">设置新密码</span>
        </div>
      </div>

      <!-- 步骤1: 输入邮箱 -->
      <form v-if="currentStep === 1" @submit.prevent="sendVerificationCode" class="form">
        <div class="form-group">
          <label for="email">邮箱地址</label>
          <input
            id="email"
            v-model="resetForm.email"
            type="email"
            required
            placeholder="请输入您的邮箱地址"
          />
        </div>

        <button type="submit" class="submit-button" :disabled="isLoading">
          {{ isLoading ? '发送中...' : '获取验证码' }}
        </button>

        <div v-if="step1Error" class="error-message">
          {{ step1Error }}
        </div>
        <div v-if="step1Success" class="success-message">
          验证码已发送到您的邮箱，请查收
        </div>

        <div class="back-to-login">
          <router-link to="/login">返回登录</router-link>
        </div>
      </form>

      <!-- 步骤2: 输入验证码 -->
      <form v-if="currentStep === 2" @submit.prevent="verifyCode" class="form">
        <div class="form-group">
          <label for="verification-code">验证码</label>
          <div class="code-input-container">
            <input
              id="verification-code"
              v-model="resetForm.verificationCode"
              type="text"
              required
              maxlength="6"
              placeholder="请输入6位验证码"
              class="code-input"
            />
            <button 
              type="button" 
              class="resend-button" 
              :disabled="countdown > 0"
              @click="sendVerificationCode"
            >
              {{ countdown > 0 ? `${countdown}s后重新发送` : '重新发送' }}
            </button>
          </div>
        </div>

        <button type="submit" class="submit-button" :disabled="isLoading">
          {{ isLoading ? '验证中...' : '验证' }}
        </button>

        <div v-if="step2Error" class="error-message">
          {{ step2Error }}
        </div>

        <div class="back-to-login">
          <router-link to="/login">返回登录</router-link>
        </div>
      </form>

      <!-- 步骤3: 设置新密码 -->
      <form v-if="currentStep === 3" @submit.prevent="resetPassword" class="form">
        <div class="form-group">
          <label for="new-password">新密码</label>
          <input
            id="new-password"
            v-model="resetForm.newPassword"
            type="password"
            required
            minlength="6"
            placeholder="请输入新密码（至少6位）"
          />
        </div>

        <div class="form-group">
          <label for="confirm-password">确认新密码</label>
          <input
            id="confirm-password"
            v-model="resetForm.confirmPassword"
            type="password"
            required
            minlength="6"
            placeholder="请再次输入新密码"
          />
        </div>

        <div v-if="passwordMismatch" class="error-message">
          两次输入的密码不一致
        </div>
        <div v-if="sameAsOldPassword" class="error-message">
          新密码不能与旧密码相同
        </div>

        <button type="submit" class="submit-button" :disabled="isLoading || passwordMismatch || sameAsOldPassword">
          {{ isLoading ? '重置中...' : '重置密码' }}
        </button>

        <div v-if="step3Error" class="error-message">
          {{ step3Error }}
        </div>
        <div v-if="step3Success" class="success-message">
          密码重置成功！请使用新密码登录
        </div>

        <div class="back-to-login">
          <router-link to="/login">返回登录</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { authApi } from '@/services/api';

const router = useRouter();

const currentStep = ref(1);
const isLoading = ref(false);
const countdown = ref(0);
const countdownInterval = ref<number | null>(null);

const step1Error = ref('');
const step1Success = ref(false);
const step2Error = ref('');
const step3Error = ref('');
const step3Success = ref(false);

const resetForm = reactive({
  email: '',
  verificationCode: '',
  newPassword: '',
  confirmPassword: ''
});

// 计算属性
const passwordMismatch = computed(() => 
  resetForm.newPassword && resetForm.confirmPassword && 
  resetForm.newPassword !== resetForm.confirmPassword
);

const sameAsOldPassword = computed(() => {
  // 这里需要后端支持检查是否与旧密码相同
  // 暂时返回false，实际实现需要调用API
  return false;
});

// 发送验证码
const sendVerificationCode = async () => {
  if (!resetForm.email) {
    step1Error.value = '请输入邮箱地址';
    return;
  }

  isLoading.value = true;
  step1Error.value = '';
  
  try {
    // 调用发送验证码的API
    const response = await authApi.sendResetCode(resetForm.email);
    if (response.success) {
      step1Success.value = true;
      startCountdown();
      setTimeout(() => {
        currentStep.value = 2;
        step1Success.value = false;
      }, 2000);
    } else {
      step1Error.value = response.message || '发送验证码失败';
    }
  } catch (error: any) {
    step1Error.value = error.response?.data?.message || '发送验证码失败';
  } finally {
    isLoading.value = false;
  }
};

// 验证验证码
const verifyCode = async () => {
  if (!resetForm.verificationCode) {
    step2Error.value = '请输入验证码';
    return;
  }

  isLoading.value = true;
  step2Error.value = '';
  
  try {
    // 调用验证验证码的API
    const response = await authApi.verifyResetCode(resetForm.email, resetForm.verificationCode);
    if (response.success) {
      currentStep.value = 3;
    } else {
      step2Error.value = response.message || '验证码错误';
    }
  } catch (error: any) {
    step2Error.value = error.response?.data?.message || '验证失败';
  } finally {
    isLoading.value = false;
  }
};

// 重置密码
const resetPassword = async () => {
  if (passwordMismatch.value) {
    return;
  }

  isLoading.value = true;
  step3Error.value = '';
  
  try {
    // 调用重置密码的API
    const response = await authApi.resetPassword(
      resetForm.email,
      resetForm.verificationCode,
      resetForm.newPassword
    );
    if (response.success) {
      step3Success.value = true;
      setTimeout(() => {
        router.push('/login');
      }, 2000);
    } else {
      step3Error.value = response.message || '密码重置失败';
    }
  } catch (error: any) {
    step3Error.value = error.response?.data?.message || '密码重置失败';
  } finally {
    isLoading.value = false;
  }
};

// 倒计时功能
const startCountdown = () => {
  countdown.value = 60;
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value);
  }
  countdownInterval.value = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--;
    } else {
      if (countdownInterval.value) {
        clearInterval(countdownInterval.value);
        countdownInterval.value = null;
      }
    }
  }, 1000);
};

// 清理定时器
onUnmounted(() => {
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value);
  }
});
</script>

<style scoped>
.reset-password-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.reset-password-card {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
}

.reset-password-title {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
  font-size: 1.8rem;
  font-weight: 600;
}

.steps-container {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 2rem;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.step-number {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #e2e8f0;
  color: #718096;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.step.active .step-number {
  background: #667eea;
  color: white;
}

.step.completed .step-number {
  background: #48bb78;
  color: white;
}

.step-text {
  font-size: 0.875rem;
  color: #718096;
  font-weight: 500;
}

.step.active .step-text {
  color: #667eea;
}

.step.completed .step-text {
  color: #48bb78;
}

.step-connector {
  width: 50px;
  height: 2px;
  background: #e2e8f0;
  margin: 0 0.5rem;
}

.step-connector.completed {
  background: #48bb78;
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

.code-input-container {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.code-input {
  flex: 1;
}

.resend-button {
  padding: 0.75rem 1rem;
  background: #e2e8f0;
  color: #4a5568;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  white-space: nowrap;
}

.resend-button:hover:not(:disabled) {
  background: #cbd5e0;
}

.resend-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.back-to-login {
  text-align: center;
  margin-top: 1rem;
}

.back-to-login a {
  color: #667eea;
  text-decoration: none;
}

.back-to-login a:hover {
  text-decoration: underline;
}
</style>
