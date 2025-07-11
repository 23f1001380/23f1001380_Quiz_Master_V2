<template>
  <div class="container mt-5" style="max-width: 700px;">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Admin – Subjects</h2>
      
      <button class="btn btn-outline-secondary" @click="goToDashboard">
        Return to Dashboard
      </button>
    </div>
    
    <form @submit.prevent="addSubject" class="mb-4">
      <div class="input-group mb-2">
        <input v-model="newSubject.name" placeholder="Subject Name" class="form-control" required />
        <input v-model="newSubject.description" placeholder="Description" class="form-control" />
        <button class="btn btn-success" type="submit" :disabled="!newSubject.name.trim()">Add</button>
      </div>
    </form>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>
    
    <table class="table table-bordered">
      <thead>
        <tr>
          <th>Name</th>
          <th>Description</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="subject in subjects" :key="subject.id">
          <td>
            <input v-model="subject.name" class="form-control" />
          </td>
          <td>
            <input v-model="subject.description" class="form-control" />
          </td>
          <td>
            <button class="btn btn-primary btn-sm me-2" @click="updateSubject(subject)">Update</button>
            <button class="btn btn-danger btn-sm" @click="deleteSubject(subject.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="subjects.length === 0 && !error">
      <em>No subjects found.</em>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { API_URL } from '../config'

export default {
  name: "AdminSubjects",
  data() {
    return {
      subjects: [],
      newSubject: { name: '', description: '' },
      error: '',
      success: ''
    }
  },
  methods: {
    goToDashboard() {
      this.$router.push('/admin')
    },
    async fetchSubjects() {
      this.error = ''
      try {
        const token = localStorage.getItem('token')
        const res = await axios.get(`${API_URL}/api/admin/subjects`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        this.subjects = res.data
      } catch (err) {
        this.error = err.response?.data?.msg || 'Could not fetch subjects'
      }
    },
    async addSubject() {
      this.error = ''
      this.success = ''
      try {
        const token = localStorage.getItem('token')
        await axios.post(`${API_URL}/api/admin/subjects`, this.newSubject, {
          headers: { Authorization: `Bearer ${token}` }
        })
        this.success = 'Subject added!'
        this.newSubject = { name: '', description: '' }
        this.fetchSubjects()
        setTimeout(() => { this.success = '' }, 2000)
      } catch (err) {
        this.error = err.response?.data?.msg || 'Could not add subject'
      }
    },
    async updateSubject(subject) {
      this.error = ''
      this.success = ''
      try {
        const token = localStorage.getItem('token')
        await axios.put(`${API_URL}/api/admin/subjects/${subject.id}`, subject, {
          headers: { Authorization: `Bearer ${token}` }
        })
        this.success = 'Subject updated!'
        this.fetchSubjects()
        setTimeout(() => { this.success = '' }, 2000)
      } catch (err) {
        this.error = err.response?.data?.msg || 'Could not update subject'
      }
    },
    async deleteSubject(id) {
      if (!confirm('Delete this subject?')) return
      this.error = ''
      this.success = ''
      try {
        const token = localStorage.getItem('token')
        await axios.delete(`${API_URL}/api/admin/subjects/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        this.success = 'Subject deleted!'
        this.fetchSubjects()
        setTimeout(() => { this.success = '' }, 2000)
      } catch (err) {
        this.error = err.response?.data?.msg || 'Could not delete subject'
      }
    }
  },
  mounted() {
    this.fetchSubjects()
  }
}
</script>
