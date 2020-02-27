<template>
  <div id="app" class="container-fluid">
  <div>
      <button class="btn btn-info"><router-link to="/doctor-dashboard">Doctor Dashboard</router-link></button>
      <button class="btn btn-info"><router-link to="/patient-kiosk">Patient Kiosk</router-link></button>
  </div>
    <router-view />

  </div>
</template>

<style lang="scss">
@import "~bootstrap/scss/bootstrap";
</style>