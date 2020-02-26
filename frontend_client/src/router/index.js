import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import DoctorDashboard from '../views/DoctorDashboard.vue'
import PatientKiosk from '../views/PatientKiosk.vue'

Vue.use(VueRouter)

const routes = [
  { path: '/patient-kiosk', name: 'PatientKiosk', component : PatientKiosk },
  { path: '/doctor-dashboard', name: 'DoctorDashboard', component: DoctorDashboard },
  { path: '/', name: 'Home', component: Home }
]

const router = new VueRouter({
  routes
})

export default router
