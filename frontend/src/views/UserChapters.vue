<template>
    <div class="container mt-5" style="max-width: 700px;">
      <h3>Chapters for: <span class="text-primary">{{ subjectName }}</span></h3>
      <div v-if="chapters.length === 0"><em>No chapters found.</em></div>
      <div class="list-group">
        <button v-for="chap in chapters" :key="chap.id"
          class="list-group-item list-group-item-action"
          @click="selectChapter(chap)">
          {{ chap.name }}
          <span class="badge bg-secondary ms-2">{{ chap.description }}</span>
        </button>
      </div>
      <router-link to="/user/subjects" class="btn btn-link mt-3">← Back to Subjects</router-link>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  import { API_URL } from '../config'
  export default {
    name: "UserChapters",
    data() {
      return {
        chapters: [],
        subjectId: null,
        subjectName: ''
      }
    },
    methods: {
      async fetchChapters() {
        const token = localStorage.getItem('token')
        const res = await axios.get(`${API_URL}/api/user/chapters/${this.subjectId}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        this.chapters = res.data
      },
      selectChapter(chap) {
        this.$router.push({ path: `/user/quizzes/${chap.id}`, query: { chapter: chap.name, subject: this.subjectName } })
      }
    },
    mounted() {
      this.subjectId = this.$route.params.subject_id
      this.subjectName = this.$route.query.subject || ''
      this.fetchChapters()
    }
  }
  </script>
  