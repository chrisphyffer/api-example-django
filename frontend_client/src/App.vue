<template>
  <div id="app" class="container-fluid">
    
    <div id="nav">
      <router-link to="/doctor-dashboard">Doctor Dashboard</router-link> | 
      <router-link to="/patient-kiosk">Patient Kiosk</router-link>
    </div>

    <router-view />

  </div>
</template>

<style lang="scss">
@import "~bootstrap/scss/bootstrap";
</style>