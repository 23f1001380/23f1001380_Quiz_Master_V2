<template>
  <div class="container mt-5" style="max-width: 400px;">
    <h2>Login</h2>
    <form @submit.prevent="handleLogin">
      <div class="mb-3">
        <input v-model="email" type="email" id="login-email" name="email" class="form-control" placeholder="Email" required>
      </div>
      <div class="mb-3">
        <input v-model="password" type="password" id="login-password" name="password" class="form-control" placeholder="Password" required>
      </div>
      <button class="btn btn-primary w-100" type="submit">Login</button>
    </form>
    <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
    
    <div class="text-center mt-4">
      <span>New user? </span>
      <button class="btn btn-link p-0" @click="goToSignup">Register here</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { API_URL } from '../config'

export default {
  name: "Login",
  data() {
    return {
      email: '',
      password: '',
      token: '',
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      this.error = ''
      this.token = ''
      try {
        const response = await axios.post(`${API_URL}/api/auth/login`, {
          email: this.email,
          password: this.password
        })
        this.token = response.data.token
        localStorage.setItem('token', this.token)
        localStorage.setItem('role', response.data.role)
        // Redirect by role
        if (response.data.role === 'admin') {
          this.$router.push('/admin')
        } else {
          this.$router.push('/user/dashboard')
        }
      } catch (err) {
        this.error = err.response?.data?.msg || 'Login failed'
      }
    },
    goToSignup() {
      this.$router.push('/signup')
    }
  }
}
</script>
