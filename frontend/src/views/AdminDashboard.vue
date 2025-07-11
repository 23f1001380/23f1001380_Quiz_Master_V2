<template>
  <div>
    
    <nav class="navbar navbar-expand navbar-dark bg-dark mb-4">
      <div class="container-fluid">
        <router-link to="/admin" class="navbar-brand">Admin Home</router-link>
        <ul class="navbar-nav me-auto">
          <li class="nav-item"><router-link class="nav-link" to="/admin/subjects">Manage Subjects</router-link></li>
          <li class="nav-item"><router-link class="nav-link" to="/admin/chapters">Manage Chapters</router-link></li>
          <li class="nav-item"><router-link class="nav-link" to="/admin/quizzes">Manage Quizzes</router-link></li>
          <li class="nav-item"><router-link class="nav-link" to="/admin/questions">Manage Questions</router-link></li>
          <li class="nav-item"><router-link class="nav-link" to="/admin/users">Manage Users</router-link></li>
        </ul>
        <button class="btn btn-outline-light btn-sm" @click="logout">Logout</button>
      </div>
    </nav>
    <div class="container mt-5" style="max-width: 900px;">
      <h2 class="mb-4">Admin Dashboard</h2>

      
      <div class="mb-4">
        <form class="d-flex" @submit.prevent="searchAdmin">
          <input v-model="searchText" class="form-control me-2" type="search" placeholder="Search for user, subject, or quiz" aria-label="Search" />
          <button class="btn btn-outline-primary" type="submit">Search</button>
        </form>
      </div>

      
      <div v-if="searchResults" class="mb-4">
        <div v-if="searchResults.users && searchResults.users.length">
          <h5>Users</h5>
          <table class="table table-sm table-bordered">
            <thead>
              <tr>
                <th>ID</th>
                <th>Email</th>
                <th>Full Name</th>
                <th>Role</th>
                <th>Active</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in searchResults.users" :key="'user' + u.id">
                <td>{{ u.id }}</td>
                <td>{{ u.email }}</td>
                <td>{{ u.full_name }}</td>
                <td>{{ u.role }}</td>
                <td>
                  <span :class="u.active ? 'text-success' : 'text-danger'">
                    {{ u.active ? 'Active' : 'Blocked' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="searchResults.subjects && searchResults.subjects.length">
          <h5>Subjects</h5>
          <table class="table table-sm table-bordered">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in searchResults.subjects" :key="'subj' + s.id">
                <td>{{ s.id }}</td>
                <td>{{ s.name }}</td>
                <td>{{ s.description }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="searchResults.quizzes && searchResults.quizzes.length">
          <h5>Quizzes</h5>
          <table class="table table-sm table-bordered">
            <thead>
              <tr>
                <th>ID</th>
                <th>Remarks</th>
                <th>Chapter ID</th>
                <th>Date of Quiz</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="q in searchResults.quizzes" :key="'quiz' + q.id">
                <td>{{ q.id }}</td>
                <td>{{ q.remarks }}</td>
                <td>{{ q.chapter_id }}</td>
                <td>{{ q.date_of_quiz }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div
          v-if="(!searchResults.users || !searchResults.users.length) &&
                (!searchResults.subjects || !searchResults.subjects.length) &&
                (!searchResults.quizzes || !searchResults.quizzes.length)">
          <em>No results found.</em>
        </div>
      </div>

      
      <div class="card mb-4">
        <div class="card-header"><strong>Summary Charts</strong></div>
        <div class="row p-3">
          <div class="col-md-6 mb-3">
            <canvas ref="quizzesChart"></canvas>
          </div>
          <div class="col-md-6 mb-3">
            <canvas ref="topScorersChart"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { API_URL } from '../config'
import Chart from 'chart.js/auto'

export default {
  name: "AdminDashboard",
  data() {
    return {
      stats: {
        
        quizAttempts: [],
        topScorers: []
      },
      charts: {
        quizzesChart: null,
        topScorersChart: null
      },
      searchText: "",
      searchResults: null
    }
  },
  methods: {
    getToken() {
      return localStorage.getItem("token")
    },
    fetchStats() {
      axios.get(`${API_URL}/api/admin/summary_stats`, {
        headers: { Authorization: `Bearer ${this.getToken()}` }
      })
      .then(res => {
        
        this.stats.quizAttempts = res.data.quizAttempts || []
        this.stats.topScorers = res.data.topScorers || []
        this.renderCharts()
      })
    },
    renderCharts() {
      if (this.charts.quizzesChart) this.charts.quizzesChart.destroy()
      if (this.charts.topScorersChart) this.charts.topScorersChart.destroy()

      this.charts.quizzesChart = new Chart(this.$refs.quizzesChart, {
        type: "bar",
        data: {
          labels: this.stats.quizAttempts.map(x => x.date),
          datasets: [{
            label: "Quiz Attempts",
            data: this.stats.quizAttempts.map(x => x.count)
          }]
        }
      })
      this.charts.topScorersChart = new Chart(this.$refs.topScorersChart, {
        type: "bar",
        data: {
          labels: this.stats.topScorers.map(x => x.full_name || x.email),
          datasets: [{
            label: "Avg Score",
            data: this.stats.topScorers.map(x => x.avg_score)
          }]
        }
      })
    },
    logout() {
      localStorage.removeItem("token")
      this.$router.push("/login")
    },
    searchAdmin() {
      if (!this.searchText.trim()) return;
      axios.get(`${API_URL}/api/admin/search`, {
        params: { q: this.searchText.trim() },
        headers: { Authorization: `Bearer ${this.getToken()}` }
      })
      .then(res => {
        this.searchResults = res.data;
      })
      .catch(() => {
        this.searchResults = null;
      });
      
    }
  },
  mounted() {
    this.fetchStats()
  }
}
</script>
