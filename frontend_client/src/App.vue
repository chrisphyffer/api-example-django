<template>
  <div id="app" class="container-fluid">
    <br />
  <ul class="nav nav-pills nav-justified">
    <li class="nav-item">
      <router-link to="/doctor-dashboard"><button class="btn btn-info">Doctor Dashboard</button></router-link>
    </li>
    <li class="nav-item">
      <router-link to="/patient-kiosk"><button class="btn btn-info">Patient Kiosk</button></router-link>
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