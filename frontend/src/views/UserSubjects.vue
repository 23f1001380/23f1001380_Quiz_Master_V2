<template>
    <div class="container mt-5" style="max-width: 700px;">
      <h3>Select a Subject</h3>
      <div v-if="subjects.length === 0"><em>No subjects found.</em></div>
      <div class="list-group">
        <button v-for="sub in subjects" :key="sub.id"
          class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
          @click="selectSubject(sub)">
          <span>{{ sub.name }}</span>
          <span class="badge bg-info">{{ sub.description }}</span>
        </button>
      </div>
      <router-link to="/user/dashboard" class="btn btn-link mt-3">← Back to Dashboard</router-link>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  import { API_URL } from '../config'
  export default {
    name: "UserSubjects",
    data() {
      return { subjects: [] }
    },
    methods: {
      async fetchSubjects() {
        const token = localStorage.getItem('token')
        const res = await axios.get(`${API_URL}/api/user/subjects`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        this.subjects = res.data
      },
      selectSubject(sub) {
        this.$router.push({ path: `/user/chapters/${sub.id}`, query: { subject: sub.name } })
      }
    },
    mounted() {
      this.fetchSubjects()
    }
  }
  </script>
  