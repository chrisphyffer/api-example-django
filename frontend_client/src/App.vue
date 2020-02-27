<template>
  <div id="app" class="container-fluid">
    <br />
  <ul class="nav nav-pills nav-justified">
    <li class="nav-item">
      <button class="btn btn-info"><router-link to="/doctor-dashboard">Doctor Dashboard</router-link></button>
    </li>
    <li class="nav-item">
      <button class="btn btn-info"><router-link to="/patient-kiosk">Patient Kiosk</router-link></button>
    </li>
  </ul>
    <router-view />

  </div>
</template>

<style lang="scss">
@import "~bootstrap/scss/bootstrap";
.btn a {
  color: #FFF !important;
}
</style>