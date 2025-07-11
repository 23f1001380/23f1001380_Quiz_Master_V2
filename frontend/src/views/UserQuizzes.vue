<template>
  <div class="container mt-5" style="max-width: 700px;">
    <h3>Quizzes for: <span class="text-primary">{{ chapterName }}</span></h3>
    <div v-if="quizzes.length === 0"><em>No quizzes available.</em></div>
    <div class="list-group">
      <div v-for="quiz in quizzes" :key="quiz.id"
        class="list-group-item d-flex justify-content-between align-items-center">
        <div>
          <strong>{{ quiz.remarks }}</strong>
          <span class="text-muted ms-2">({{ quiz.date_of_quiz ? quiz.date_of_quiz.substring(0, 10) : 'TBA' }})</span>
        </div>
        <button class="btn btn-outline-primary btn-sm" @click="startQuiz(quiz.id)">Attempt Quiz</button>
      </div>
    </div>
    <router-link :to="`/user/chapters/${chapterId}`" class="btn btn-link mt-3">← Back to Chapters</router-link>
  </div>
</template>

<script>
import axios from 'axios'
import { API_URL } from '../config'
export default {
  name: "UserQuizzes",
  data() {
    return {
      quizzes: [],
      chapterId: null,
      chapterName: ''
    }
  },
  methods: {
    async fetchQuizzes() {
      const token = localStorage.getItem('token')
      const res = await axios.get(`${API_URL}/api/user/quizzes/${this.chapterId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      this.quizzes = res.data
    },
    startQuiz(quiz_id) {
      
      this.$router.push({ path: `/user/attempt/${quiz_id}`, query: { chapter_id: this.chapterId } })
    }
  },
  mounted() {
    this.chapterId = this.$route.params.chapter_id
    this.chapterName = this.$route.query.chapter || ''
    this.fetchQuizzes()
  }
}
</script>
