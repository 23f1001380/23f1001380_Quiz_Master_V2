<template>
  <div class="container mt-5" style="max-width: 900px;">
    <h3>Attempt Quiz</h3>
    <div v-if="quizDuration !== null && !submitted" class="mb-3">
      <span class="badge bg-primary fs-5">
        Time Left: {{ minutes }}:{{ seconds < 10 ? '0' : '' }}{{ seconds }}
      </span>
    </div>
    <form @submit.prevent="submitQuiz" v-if="questions.length > 0 && !submitted">
      <div v-for="(q, idx) in questions" :key="q.id" class="mb-4">
        <div class="mb-2"><strong>Q{{ idx + 1 }}:</strong> {{ q.question_statement }}</div>
        <div class="list-group">
          <label v-for="opt in q.options" :key="opt.id" class="list-group-item">
            <input
              type="radio"
              :name="`question_${q.id}`"
              :value="opt.id"
              v-model="userAnswers[q.id]"
              required
            />
            {{ opt.text }}
          </label>
        </div>
      </div>
      <button class="btn btn-success" type="submit">Submit Quiz</button>
    </form>

    <div v-if="submitted">
      <h4 class="mt-4">Quiz Submitted!</h4>
      <div class="alert alert-info">
        <div><strong>Score:</strong> {{ score }}%</div>
        <div><strong>Correct Answers:</strong> {{ correct_answers }} / {{ total_questions }}</div>
      </div>
      <router-link to="/user/scores" class="btn btn-outline-secondary">View My Scores</router-link>
      <router-link to="/user/dashboard" class="btn btn-link">Back to Dashboard</router-link>
    </div>

    <div v-if="questions.length === 0 && !submitted"><em>No questions found for this quiz.</em></div>
    <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
  </div>
</template>

<script>
import axios from 'axios'
import { API_URL } from '../config'
export default {
  name: "UserAttemptQuiz",
  data() {
    return {
      quizId: null,
      chapterId: null,
      questions: [],
      userAnswers: {},
      submitted: false,
      score: null,
      correct_answers: null,
      total_questions: null,
      error: '',
      quizDuration: null, 
      timeLeft: 0,
      timer: null,
    }
  },
  computed: {
    minutes() {
      return Math.floor(this.timeLeft / 60)
    },
    seconds() {
      return this.timeLeft % 60
    }
  },
  methods: {
    async fetchQuizDetails() {
      
      const token = localStorage.getItem('token')
      
      const quizRes = await axios.get(`${API_URL}/api/user/quizzes/${this.chapterId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      const quiz = quizRes.data.find(q => q.id == this.quizId)
      this.quizDuration = quiz ? quiz.time_duration : 10 
      this.timeLeft = this.quizDuration * 60
      
      await this.fetchQuestions()
      
      this.startTimer()
    },
    async fetchQuestions() {
      const token = localStorage.getItem('token')
      const res = await axios.get(`${API_URL}/api/user/questions/${this.quizId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      this.questions = res.data
    },
    async submitQuiz(auto = false) {
      
      if (this.submitted) return
      
      const answers = Object.keys(this.userAnswers).map(qid => ({
        question_id: Number(qid),
        selected_option_id: this.userAnswers[qid]
      }))
      const token = localStorage.getItem('token')
      try {
        const res = await axios.post(`${API_URL}/api/user/submit_quiz`, {
          quiz_id: this.quizId, answers
        }, { headers: { Authorization: `Bearer ${token}` } })
        this.score = res.data.score
        this.correct_answers = res.data.correct_answers
        this.total_questions = res.data.total_questions
        this.submitted = true
        clearInterval(this.timer)
        if (auto) {
          this.error = "Time's up! Your quiz was automatically submitted."
        }
      } catch (e) {
        this.error = e.response?.data?.msg || "Failed to submit quiz"
      }
    },
    startTimer() {
      this.timer = setInterval(() => {
        if (this.timeLeft > 0) {
          this.timeLeft--
        } else {
          clearInterval(this.timer)
          this.submitQuiz(true)
        }
      }, 1000)
    }
  },
  mounted() {
    this.quizId = this.$route.params.quiz_id
    this.chapterId = this.$route.query.chapter_id || null
    this.fetchQuizDetails()
  },
  beforeUnmount() {
    if (this.timer) clearInterval(this.timer)
  }
}
</script>
