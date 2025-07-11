<template>
  <div class="container mt-5" style="max-width: 400px;">
    <h2>Sign Up</h2>
    <form @submit.prevent="handleSignup">
      <div class="mb-3">
        <input v-model="email" type="email" id="signup-email" name="email" class="form-control" placeholder="Email" required>
      </div>
      <div class="mb-3">
        <input v-model="password" type="password" id="signup-password" name="password" class="form-control" placeholder="Password" required>
      </div>
      <div class="mb-3">
        <input v-model="full_name" type="text" id="signup-fullname" name="full_name" class="form-control" placeholder="Full Name">
      </div>
      <div class="mb-3">
        <input v-model="qualification" type="text" id="signup-qualification" name="qualification" class="form-control" placeholder="Qualification">
      </div>
      <button class="btn btn-success w-100" type="submit">Sign Up</button>
    </form>
    <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
    <div v-if="success" class="alert alert-success mt-3">{{ success }}</div>
    <!-- Back to Login Button -->
    <div class="text-center mt-4">
      <button class="btn btn-link p-0" @click="goToLogin">Back to Login</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { API_URL } from '../config'

export default {
  name: "SignUp",
  data() {
    return {
      email: '',
      password: '',
      full_name: '',
      qualification: '',
      success: '',
      error: ''
    }
  },
  methods: {
    async handleSignup() {
      this.error = ''
      this.success = ''
      try {
        const response = await axios.post(`${API_URL}/api/auth/signup`, {
          email: this.email,
          password: this.password,
          full_name: this.full_name,
          qualification: this.qualification
        })
        this.success = response.data.msg
      } catch (err) {
        this.error = err.response?.data?.msg || 'Signup failed'
      }
    },
    goToLogin() {
      this.$router.push('/login')
    }
  }
}
</script>
