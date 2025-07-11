<template>
    <div class="container mt-5" style="max-width: 700px;">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h2>Admin – Chapters</h2>
        
        <button class="btn btn-outline-secondary" @click="goToDashboard">
          Return to Dashboard
        </button>
      </div>
      
      <form @submit.prevent="addChapter" class="mb-4">
        <div class="input-group mb-2">
          <select v-model="newChapter.subject_id" class="form-control" required>
            <option disabled value="">Select Subject</option>
            <option v-for="subject in subjects" :key="subject.id" :value="subject.id">{{ subject.name }}</option>
          </select>
          <input v-model="newChapter.name" placeholder="Chapter Name" class="form-control" required />
          <input v-model="newChapter.description" placeholder="Description" class="form-control" />
          <button class="btn btn-success" type="submit" :disabled="!newChapter.name.trim()">Add</button>
        </div>
      </form>
      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-if="success" class="alert alert-success">{{ success }}</div>
     
      <table class="table table-bordered">
        <thead>
          <tr>
            <th>Subject</th>
            <th>Name</th>
            <th>Description</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="chapter in chapters" :key="chapter.id">
            <td>{{ getSubjectName(chapter.subject_id) }}</td>
            <td><input v-model="chapter.name" class="form-control" /></td>
            <td><input v-model="chapter.description" class="form-control" /></td>
            <td>
              <button class="btn btn-primary btn-sm me-2" @click="updateChapter(chapter)">Update</button>
              <button class="btn btn-danger btn-sm" @click="deleteChapter(chapter.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="chapters.length === 0 && !error"><em>No chapters found.</em></div>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  import { API_URL } from '../config'
  
  export default {
    name: "AdminChapters",
    data() {
      return {
        chapters: [],
        subjects: [],
        newChapter: { subject_id: '', name: '', description: '' },
        error: '',
        success: ''
      }
    },
    methods: {
      goToDashboard() {
        this.$router.push('/admin')
      },
      async fetchSubjects() {
        const token = localStorage.getItem('token')
        const res = await axios.get(`${API_URL}/api/admin/subjects`, { headers: { Authorization: `Bearer ${token}` } })
        this.subjects = res.data
      },
      async fetchChapters() {
        this.error = ''
        try {
          const token = localStorage.getItem('token')
          const res = await axios.get(`${API_URL}/api/admin/chapters`, {
            headers: { Authorization: `Bearer ${token}` }
          })
          this.chapters = res.data
        } catch (err) {
          this.error = err.response?.data?.msg || 'Could not fetch chapters'
        }
      },
      async addChapter() {
        this.error = ''
        this.success = ''
        try {
          const token = localStorage.getItem('token')
          await axios.post(`${API_URL}/api/admin/chapters`, this.newChapter, {
            headers: { Authorization: `Bearer ${token}` }
          })
          this.success = 'Chapter added!'
          this.newChapter = { subject_id: '', name: '', description: '' }
          this.fetchChapters()
          setTimeout(() => { this.success = '' }, 2000)
        } catch (err) {
          this.error = err.response?.data?.msg || 'Could not add chapter'
        }
      },
      async updateChapter(chapter) {
        this.error = ''
        this.success = ''
        try {
          const token = localStorage.getItem('token')
          await axios.put(`${API_URL}/api/admin/chapters/${chapter.id}`, chapter, {
            headers: { Authorization: `Bearer ${token}` }
          })
          this.success = 'Chapter updated!'
          this.fetchChapters()
          setTimeout(() => { this.success = '' }, 2000)
        } catch (err) {
          this.error = err.response?.data?.msg || 'Could not update chapter'
        }
      },
      async deleteChapter(id) {
        if (!confirm('Delete this chapter?')) return
        this.error = ''
        this.success = ''
        try {
          const token = localStorage.getItem('token')
          await axios.delete(`${API_URL}/api/admin/chapters/${id}`, {
            headers: { Authorization: `Bearer ${token}` }
          })
          this.success = 'Chapter deleted!'
          this.fetchChapters()
          setTimeout(() => { this.success = '' }, 2000)
        } catch (err) {
          this.error = err.response?.data?.msg || 'Could not delete chapter'
        }
      },
      getSubjectName(subject_id) {
        const subj = this.subjects.find(s => s.id === subject_id)
        return subj ? subj.name : '-'
      }
    },
    async mounted() {
      await this.fetchSubjects()
      this.fetchChapters()
    }
  }
  </script>
  