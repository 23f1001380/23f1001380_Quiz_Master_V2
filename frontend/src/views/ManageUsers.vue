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
            <li class="nav-item"><router-link class="nav-link active" to="/admin/users">Manage Users</router-link></li>
          </ul>
          <button class="btn btn-outline-light btn-sm" @click="logout">Logout</button>
        </div>
      </nav>
  
      <div class="container mt-5" style="max-width: 900px;">
        <h2 class="mb-4">Manage Users</h2>
        
        <div class="mb-3 d-flex">
          <input v-model="userSearch" @input="fetchUsers" class="form-control w-25" placeholder="Search users by name or email" />
        </div>
       
        <div class="table-responsive">
          <table class="table table-bordered table-hover align-middle">
            <thead class="table-secondary">
              <tr>
                <th>ID</th>
                <th>Email</th>
                <th>Full Name</th>
                <th>Role</th>
                <th>Active</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id">
                <td>{{ u.id }}</td>
                <td>{{ u.email }}</td>
                <td>{{ u.full_name }}</td>
                <td>{{ u.role }}</td>
                <td>
                  <span v-if="u.active" class="badge bg-success">Active</span>
                  <span v-else class="badge bg-danger">Blocked</span>
                </td>
                <td>
                  <button
                    class="btn btn-sm"
                    :class="u.active ? 'btn-warning' : 'btn-success'"
                    @click="toggleUserActive(u)"
                  >
                    {{ u.active ? 'Block' : 'Unblock' }}
                  </button>
                  <button class="btn btn-info btn-sm ms-2" @click="showUserStats(u)">
                    View Stats
                  </button>
                  <button class="btn btn-danger btn-sm ms-2" @click="deleteUser(u.id)">
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="users.length === 0" class="p-2">No users found.</div>
        </div>
       
        <div v-if="selectedUser" class="modal fade show d-block" tabindex="-1" style="background:rgba(0,0,0,0.3)">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">Stats for {{ selectedUser.full_name || selectedUser.email }}</h5>
                <button type="button" class="btn-close" @click="selectedUser=null"></button>
              </div>
              <div class="modal-body">
                <canvas ref="userStatsChart"></canvas>
              </div>
              <div class="modal-footer">
                <button class="btn btn-secondary" @click="selectedUser=null">Close</button>
              </div>
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
    name: "ManageUsers",
    data() {
      return {
        userSearch: "",
        users: [],
        selectedUser: null,
        userStats: [],
        userStatsChart: null
      }
    },
    methods: {
      getToken() {
        return localStorage.getItem("token")
      },
      fetchUsers() {
        axios.get(`${API_URL}/api/admin/users`, {
          params: { search: this.userSearch },
          headers: { Authorization: `Bearer ${this.getToken()}` }
        })
        .then(res => { this.users = res.data })
        .catch(() => { this.users = [] })
      },
      toggleUserActive(user) {
        axios.put(`${API_URL}/api/admin/users/${user.id}`, {
          active: !user.active
        }, {
          headers: { Authorization: `Bearer ${this.getToken()}` }
        }).then(() => this.fetchUsers())
      },
      deleteUser(id) {
        if (!confirm("Delete this user?")) return
        axios.delete(`${API_URL}/api/admin/users/${id}`, {
          headers: { Authorization: `Bearer ${this.getToken()}` }
        }).then(() => this.fetchUsers())
      },
      showUserStats(user) {
        this.selectedUser = user
        axios.get(`${API_URL}/api/admin/user_stats/${user.id}`, {
          headers: { Authorization: `Bearer ${this.getToken()}` }
        }).then(res => {
          this.userStats = res.data
          this.renderUserStatsChart()
        })
      },
      renderUserStatsChart() {
        if (this.userStatsChart) this.userStatsChart.destroy()
        this.userStatsChart = new Chart(this.$refs.userStatsChart, {
          type: "bar",
          data: {
            labels: this.userStats.map(x => x.quiz_name || `Quiz #${x.quiz_id}`),
            datasets: [{
              label: "Score (%)",
              data: this.userStats.map(x => x.score)
            }]
          }
        })
      },
      logout() {
        localStorage.removeItem("token")
        this.$router.push("/login")
      }
    },
    mounted() {
      this.fetchUsers()
    }
  }
  </script>
  