import { createRouter, createWebHistory } from 'vue-router'


import Login from '../views/Login.vue'
import SignUp from '../views/SignUp.vue'


import AdminDashboard from '../views/AdminDashboard.vue'
import AdminSubjects from '../views/AdminSubjects.vue'
import AdminChapters from '../views/AdminChapters.vue'
import AdminQuizzes from '../views/AdminQuizzes.vue'
import AdminQuestions from '../views/AdminQuestions.vue'
import ManageUsers from '../views/ManageUsers.vue'



import Dashboard from '../views/Dashboard.vue'
import UserSubjects from '../views/UserSubjects.vue'
import UserChapters from '../views/UserChapters.vue'
import UserQuizzes from '../views/UserQuizzes.vue'
import UserAttemptQuiz from '../views/UserAttemptQuiz.vue'
import UserScores from '../views/UserScores.vue'

const routes = [
  
  { path: '/login', component: Login },
  { path: '/signup', component: SignUp },

  
  { path: '/admin', component: AdminDashboard },
  { path: '/admin/subjects', component: AdminSubjects },
  { path: '/admin/chapters', component: AdminChapters },
  { path: '/admin/quizzes', component: AdminQuizzes },
  { path: '/admin/questions', component: AdminQuestions },
  { path: '/admin/users', component: ManageUsers },

  
  { path: '/user/dashboard', component: Dashboard },
  { path: '/user/subjects', component: UserSubjects },
  { path: '/user/chapters/:subject_id', component: UserChapters, props: true },
  { path: '/user/quizzes/:chapter_id', component: UserQuizzes, props: true },
  { path: '/user/attempt/:quiz_id', component: UserAttemptQuiz, props: true },
  { path: '/user/scores', component: UserScores },

  
  { path: '/', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
