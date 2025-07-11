<template>
  <div class="container py-5" style="max-width: 600px;">
    
    <div class="card shadow mb-4 border-0">
      <div class="card-body d-flex align-items-center">
        <i class="bi bi-person-circle fs-1 text-primary me-3"></i>
        <div>
          <h3 class="mb-0">Welcome, {{ user.full_name || 'User' }}</h3>
          <div class="text-muted mb-1">{{ user.email }}</div>
          <span class="badge bg-info">{{ user.role ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : 'User' }}</span>
        </div>
        
        <button @click="logout" class="btn btn-outline-danger ms-auto">
          <i class="bi bi-box-arrow-right"></i> Logout
        </button>
      </div>
    </div>

    
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <router-link to="/user/subjects" class="btn btn-primary">
        <i class="bi bi-play-circle"></i> Start Quiz
      </router-link>
      <router-link to="/user/scores" class="btn btn-outline-secondary">
        <i class="bi bi-bar-chart-line"></i> My Scores
      </router-link>
      <button @click="exportCsv" class="btn btn-success">
        <i class="bi bi-download"></i> Export My Quiz Data
      </button>
    </div>

    
    <div v-if="message" class="alert alert-info mt-3 text-center">{{ message }}</div>
  </div>
</template>

<script>
import axios from 'axios'
import { API_URL } from '../config'

export default {
  name: "UserDashboard",
  data() {
    return {
      user: {},
      message: ''
    }
  },
  async mounted() {
    const token = localStorage.getItem('token')
    const res = await axios.get(`${API_URL}/api/user/dashboard`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    this.user = res.data
  },
  methods: {
    async exportCsv() {
      this.message = ''
      try {
        const token = localStorage.getItem('token')
        const res = await axios.post(`${API_URL}/api/user/export_quiz_csv`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        })
        this.message = res.data.msg || 'Export started! Check your email soon.'
      } catch (err) {
        this.message = 'Failed to start export. Please try again later.'
      }
    },
    logout() {
      localStorage.removeItem('token')
      this.$router.push('/login')
    }
  }
}
</script>


<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">

<style scoped>
.card {
  border-radius: 1rem;
}
.btn {
  min-width: 130px;
}
</style>
