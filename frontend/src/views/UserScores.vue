<template>
    <div class="container mt-5" style="max-width: 900px;">
      <h3>My Quiz Scores</h3>
      <div v-if="scores.length === 0"><em>No quiz attempts found.</em></div>
      <table class="table table-striped" v-if="scores.length">
        <thead>
          <tr>
            <th>Date</th>
            <th>Quiz ID</th>
            <th>Score (%)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in scores" :key="s.id">
            <td>{{ s.timestamp ? s.timestamp.substring(0,10) : '-' }}</td>
            <td>{{ s.quiz_id }}</td>
            <td>{{ s.total_scored }}</td>
          </tr>
        </tbody>
      </table>
      <router-link to="/user/dashboard" class="btn btn-link mt-3">← Back to Dashboard</router-link>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  import { API_URL } from '../config'
  export default {
    name: "UserScores",
    data() {
      return {
        scores: []
      }
    },
    methods: {
      async fetchScores() {
        const token = localStorage.getItem('token')
        const res = await axios.get(`${API_URL}/api/user/scores`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        this.scores = res.data
      }
    },
    mounted() {
      this.fetchScores()
    }
  }
  </script>
  