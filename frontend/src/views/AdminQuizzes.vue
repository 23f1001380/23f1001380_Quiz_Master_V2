<template>
    <div class="container mt-5" style="max-width: 800px;">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h2>Admin – Quizzes</h2>
        <button class="btn btn-outline-secondary" @click="goToDashboard">
          Return to Dashboard
        </button>
      </div>
      
      <form @submit.prevent="addQuiz" class="mb-4">
        <div class="input-group mb-2">
         
          <select v-model="selectedSubjectId" class="form-control" required @change="filterChapters">
            <option disabled value="">Select Subject</option>
            <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
              {{ subject.name }}
            </option>
          </select>
          
          <select v-model="newQuiz.chapter_id" class="form-control" required :disabled="!selectedSubjectId">
            <option disabled value="">Select Chapter</option>
            <option v-for="chapter in filteredChapters" :key="chapter.id" :value="chapter.id">
              {{ chapter.name }}
            </option>
          </select>
          <input v-model="newQuiz.date_of_quiz" type="datetime-local" class="form-control" required />
          <input v-model="newQuiz.time_duration" type="number" class="form-control" placeholder="Duration (min)" required />
          
          <input v-model="newQuiz.remarks" class="form-control" placeholder="Quiz Name" />
          <button class="btn btn-success" type="submit" :disabled="!newQuiz.chapter_id">Add</button>
        </div>
      </form>
      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-if="success" class="alert alert-success">{{ success }}</div>
      <table class="table table-bordered">
        <thead>
          <tr>
            <th>Chapter</th>
            <th>Date & Time</th>
            <th>Duration</th>
            <th>Quiz Name</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="quiz in quizzes" :key="quiz.id">
            <td>{{ getChapterName(quiz.chapter_id) }}</td>
            <td>
              <input
                v-model="quiz.date_of_quiz"
                class="form-control"
                type="datetime-local"
                @change="quiz.date_of_quiz = fixToDatetimeLocal(quiz.date_of_quiz)"
              />
            </td>
            <td>
              <input v-model="quiz.time_duration" class="form-control" type="number" />
            </td>
            <td>
             
              <input v-model="quiz.remarks" class="form-control" placeholder="Quiz Name" />
            </td>
            <td>
              <button class="btn btn-primary btn-sm me-2" @click="updateQuiz(quiz)">Update</button>
              <button class="btn btn-danger btn-sm" @click="deleteQuiz(quiz.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="quizzes.length === 0 && !error"><em>No quizzes found.</em></div>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  import { API_URL } from '../config'
  
  function toDatetimeLocalString(dt) {
    if (!dt) return ''
    let d = new Date(dt)
    if (isNaN(d)) return ''
    const pad = n => n.toString().padStart(2, '0')
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
  }
  
  export default {
    name: "AdminQuizzes",
    data() {
      return {
        quizzes: [],
        subjects: [],
        chapters: [],
        filteredChapters: [],
        selectedSubjectId: '',
        newQuiz: { chapter_id: '', date_of_quiz: '', time_duration: '', remarks: '' },
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
        const token = localStorage.getItem('token')
        const res = await axios.get(`${API_URL}/api/admin/chapters`, { headers: { Authorization: `Bearer ${token}` } })
        this.chapters = res.data
        this.filterChapters()
      },
      filterChapters() {
        if (!this.selectedSubjectId) {
          this.filteredChapters = []
          this.newQuiz.chapter_id = ''
        } else {
          this.filteredChapters = this.chapters.filter(ch => ch.subject_id == this.selectedSubjectId)
          if (!this.filteredChapters.some(c => c.id === this.newQuiz.chapter_id)) {
            this.newQuiz.chapter_id = ''
          }
        }
      },
      async fetchQuizzes() {
        this.error = ''
        try {
          const token = localStorage.getItem('token')
          const res = await axios.get(`${API_URL}/api/admin/quizzes`, {
            headers: { Authorization: `Bearer ${token}` }
          })
          this.quizzes = res.data.map(q => ({
            ...q,
            date_of_quiz: toDatetimeLocalString(q.date_of_quiz)
          }))
        } catch (err) {
          this.error = err.response?.data?.msg || 'Could not fetch quizzes'
        }
      },
      async addQuiz() {
        this.error = ''
        this.success = ''
        try {
          const token = localStorage.getItem('token')
          let quizToSend = { ...this.newQuiz }
          if (quizToSend.date_of_quiz) {
            if (quizToSend.date_of_quiz.length === 16) {
              quizToSend.date_of_quiz += ':00'
            }
          }
          await axios.post(`${API_URL}/api/admin/quizzes`, quizToSend, {
            headers: { Authorization: `Bearer ${token}` }
          })
          this.success = 'Quiz added!'
          this.newQuiz = { chapter_id: '', date_of_quiz: '', time_duration: '', remarks: '' }
          this.selectedSubjectId = ''
          this.filterChapters()
          this.fetchQuizzes()
          setTimeout(() => { this.success = '' }, 2000)
        } catch (err) {
          this.error = err.response?.data?.msg || 'Could not add quiz'
        }
      },
      async updateQuiz(quiz) {
        this.error = ''
        this.success = ''
        try {
          const token = localStorage.getItem('token')
          let payload = { ...quiz }
          if (payload.date_of_quiz && payload.date_of_quiz.length === 16) {
            payload.date_of_quiz += ':00'
          }
          await axios.put(`${API_URL}/api/admin/quizzes/${quiz.id}`, payload, {
            headers: { Authorization: `Bearer ${token}` }
          })
          this.success = 'Quiz updated!'
          this.fetchQuizzes()
          setTimeout(() => { this.success = '' }, 2000)
        } catch (err) {
          this.error = err.response?.data?.msg || 'Could not update quiz'
        }
      },
      async deleteQuiz(id) {
        if (!confirm('Delete this quiz?')) return
        this.error = ''
        this.success = ''
        try {
          const token = localStorage.getItem('token')
          await axios.delete(`${API_URL}/api/admin/quizzes/${id}`, {
            headers: { Authorization: `Bearer ${token}` }
          })
          this.success = 'Quiz deleted!'
          this.fetchQuizzes()
          setTimeout(() => { this.success = '' }, 2000)
        } catch (err) {
          this.error = err.response?.data?.msg || 'Could not delete quiz'
        }
      },
      getChapterName(chapter_id) {
        const ch = this.chapters.find(c => c.id === chapter_id)
        return ch ? ch.name : '-'
      },
      fixToDatetimeLocal(str) {
        if (!str) return ''
        if (str.length === 10) return str + "T00:00"
        if (str.length === 16) return str
        if (str.length > 16) return str.substring(0, 16)
        return str
      }
    },
    async mounted() {
      await this.fetchSubjects()
      await this.fetchChapters()
      this.fetchQuizzes()
    }
  }
  </script>
  