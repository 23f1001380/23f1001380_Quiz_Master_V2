<template>
    <div class="container mt-5" style="max-width: 900px;">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h2>Admin – Questions</h2>
        <button class="btn btn-outline-secondary" @click="goToDashboard">
          Return to Dashboard
        </button>
      </div>
     
      <form @submit.prevent="addQuestion" class="mb-4">
        <div class="row mb-2">
          <div class="col">
            <select v-model="selectedSubjectId" class="form-control" required @change="filterChapters">
              <option disabled value="">Select Subject</option>
              <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                {{ subject.name }}
              </option>
            </select>
          </div>
          <div class="col">
            <select v-model="selectedChapterId" class="form-control" required @change="filterQuizzes" :disabled="!selectedSubjectId">
              <option disabled value="">Select Chapter</option>
              <option v-for="chapter in filteredChapters" :key="chapter.id" :value="chapter.id">
                {{ chapter.name }}
              </option>
            </select>
          </div>
          <div class="col">
            <select v-model="newQuestion.quiz_id" class="form-control" required :disabled="!selectedChapterId">
              <option disabled value="">Select Quiz</option>
              <option v-for="quiz in filteredQuizzes" :key="quiz.id" :value="quiz.id">
                {{ quiz.remarks }}
              </option>
            </select>
          </div>
        </div>
        
        <div class="input-group mb-2">
          <input v-model="newQuestion.question_statement" placeholder="Question" class="form-control" required />
        </div>
        <div class="row mb-2">
          <div class="col-12 col-md-6 mb-2 mb-md-0" v-for="(opt, idx) in newOptions" :key="idx">
            <div class="input-group">
              <span class="input-group-text">
                <input type="radio" :value="idx" v-model="correctOptionIdx" required :aria-label="'Mark option ' + (idx+1) + ' as correct'" />
              </span>
              <input v-model="opt.text" class="form-control" :placeholder="`Option ${idx+1}`" required />
            </div>
          </div>
        </div>
        <div class="mb-2 text-muted" style="font-size:0.92em;">
          <span>Select the radio button for the correct option.</span>
        </div>
        <button class="btn btn-success" type="submit" :disabled="!formReady">Add Question</button>
      </form>
      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-if="success" class="alert alert-success">{{ success }}</div>
      <table class="table table-bordered">
        <thead>
          <tr>
            <th>Quiz</th>
            <th>Question</th>
            <th>Options</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="question in questions" :key="question.id">
            <td>{{ getQuizRemarks(question.quiz_id) }}</td>
            <td><input v-model="question.question_statement" class="form-control" /></td>
            <td>
              <ul style="padding-left: 16px;">
                <li v-for="opt in question.options || []" :key="opt.id" class="mb-1 d-flex align-items-center">
                 
                  <template v-if="editedOption && editedOption.id === opt.id">
                    <input v-model="editedOption.text" class="form-control form-control-sm me-1" style="max-width: 220px; display: inline;" />
                    <input type="checkbox" v-model="editedOption.is_correct" class="form-check-input me-1" :id="'chk'+opt.id" />
                    <label :for="'chk'+opt.id" class="me-2" style="font-size:0.95em;">Correct</label>
                    <button class="btn btn-success btn-sm me-1" @click="saveOptionEdit(opt.id)">Save</button>
                    <button class="btn btn-secondary btn-sm me-1" @click="cancelOptionEdit">Cancel</button>
                  </template>
                  <template v-else>
                    {{ opt.text }}
                    <span v-if="opt.is_correct" class="badge bg-success ms-1">Correct</span>
                    <button class="btn btn-link btn-sm p-0 ms-2" title="Edit" @click="editOption(opt)">
                      <span class="bi bi-pencil-square"></span>✏️
                    </button>
                  </template>
                </li>
                <div v-if="(question.options || []).length === 0" class="text-muted" style="font-size:0.95em;">
                  No options added.
                </div>
              </ul>
            </td>
            <td>
              <button class="btn btn-primary btn-sm me-2" @click="updateQuestion(question)">Update</button>
              <button class="btn btn-danger btn-sm" @click="deleteQuestion(question.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="questions.length === 0 && !error"><em>No questions found.</em></div>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  import { API_URL } from '../config'
  
  export default {
    name: "AdminQuestions",
    data() {
      return {
        questions: [],
        quizzes: [],
        chapters: [],
        subjects: [],
        filteredChapters: [],
        filteredQuizzes: [],
        selectedSubjectId: '',
        selectedChapterId: '',
        newQuestion: { quiz_id: '', question_statement: '' },
        newOptions: [
          { text: '' },
          { text: '' },
          { text: '' },
          { text: '' }
        ],
        correctOptionIdx: null,
        error: '',
        success: '',
        editedOption: null 
      }
    },
    computed: {
      formReady() {
        return (
          this.newQuestion.quiz_id &&
          this.newQuestion.question_statement.trim() &&
          this.newOptions.every(opt => opt.text.trim()) &&
          this.correctOptionIdx !== null
        )
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
      async fetchQuizzes() {
        const token = localStorage.getItem('token')
        const res = await axios.get(`${API_URL}/api/admin/quizzes`, { headers: { Authorization: `Bearer ${token}` } })
        this.quizzes = res.data
        this.filterQuizzes()
      },
      filterChapters() {
        if (!this.selectedSubjectId) {
          this.filteredChapters = []
          this.selectedChapterId = ''
          this.filteredQuizzes = []
          this.newQuestion.quiz_id = ''
        } else {
          this.filteredChapters = this.chapters.filter(ch => ch.subject_id == this.selectedSubjectId)
          if (!this.filteredChapters.some(c => c.id === this.selectedChapterId)) {
            this.selectedChapterId = ''
          }
          this.filterQuizzes()
        }
      },
      filterQuizzes() {
        if (!this.selectedChapterId) {
          this.filteredQuizzes = []
          this.newQuestion.quiz_id = ''
        } else {
          this.filteredQuizzes = this.quizzes.filter(q => q.chapter_id == this.selectedChapterId)
          if (!this.filteredQuizzes.some(q => q.id === this.newQuestion.quiz_id)) {
            this.newQuestion.quiz_id = ''
          }
        }
      },
      async fetchQuestions() {
        this.error = ''
        try {
          const token = localStorage.getItem('token')
          const res = await axios.get(`${API_URL}/api/admin/questions`, {
            headers: { Authorization: `Bearer ${token}` }
          })
         
          this.questions = await Promise.all(res.data.map(async (q) => {
            try {
              const optRes = await axios.get(`${API_URL}/api/admin/options?question_id=${q.id}`, {
                headers: { Authorization: `Bearer ${token}` }
              })
              return { ...q, options: optRes.data }
            } catch {
              return { ...q, options: [] }
            }
          }))
        } catch (err) {
          this.error = err.response?.data?.msg || 'Could not fetch questions'
        }
      },
      async addQuestion() {
        this.error = ''
        this.success = ''
        if (!this.formReady) return
  
        try {
          const token = localStorage.getItem('token')
          
          const res = await axios.post(`${API_URL}/api/admin/questions`, this.newQuestion, {
            headers: { Authorization: `Bearer ${token}` }
          })
          const questionId = res.data.id
          
          for (let i = 0; i < 4; i++) {
            await axios.post(`${API_URL}/api/admin/options`, {
              question_id: questionId,
              text: this.newOptions[i].text,
              is_correct: i === this.correctOptionIdx
            }, {
              headers: { Authorization: `Bearer ${token}` }
            })
          }
          this.success = 'Question and options added!'
          
          this.newQuestion.question_statement = ''
          this.newOptions = [{ text: '' }, { text: '' }, { text: '' }, { text: '' }]
          this.correctOptionIdx = null
          this.fetchQuestions()
          setTimeout(() => { this.success = '' }, 2000)
        } catch (err) {
          this.error = err.response?.data?.msg || 'Could not add question and options'
        }
      },
      async updateQuestion(question) {
        this.error = ''
        this.success = ''
        try {
          const token = localStorage.getItem('token')
          await axios.put(`${API_URL}/api/admin/questions/${question.id}`, question, {
            headers: { Authorization: `Bearer ${token}` }
          })
          this.success = 'Question updated!'
          this.fetchQuestions()
          setTimeout(() => { this.success = '' }, 2000)
        } catch (err) {
          this.error = err.response?.data?.msg || 'Could not update question'
        }
      },
      async deleteQuestion(id) {
        if (!confirm('Delete this question?')) return
        this.error = ''
        this.success = ''
        try {
          const token = localStorage.getItem('token')
          await axios.delete(`${API_URL}/api/admin/questions/${id}`, {
            headers: { Authorization: `Bearer ${token}` }
          })
          this.success = 'Question deleted!'
          this.fetchQuestions()
          setTimeout(() => { this.success = '' }, 2000)
        } catch (err) {
          this.error = err.response?.data?.msg || 'Could not delete question'
        }
      },
      getQuizRemarks(quiz_id) {
        const quiz = this.quizzes.find(q => q.id === quiz_id)
        return quiz ? quiz.remarks : '-'
      },
      
      editOption(opt) {
        
        this.editedOption = { ...opt }
      },
      async saveOptionEdit(optionId) {
        try {
          const token = localStorage.getItem('token')
          await axios.put(`${API_URL}/api/admin/options/${optionId}`, this.editedOption, {
            headers: { Authorization: `Bearer ${token}` }
          })
          this.editedOption = null
          this.fetchQuestions()
        } catch (err) {
          this.error = err.response?.data?.msg || 'Could not update option'
        }
      },
      cancelOptionEdit() {
        this.editedOption = null
      }
    },
    async mounted() {
      await this.fetchSubjects()
      await this.fetchChapters()
      await this.fetchQuizzes()
      await this.fetchQuestions()
    }
  }
  </script>
  