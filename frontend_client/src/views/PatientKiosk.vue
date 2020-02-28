<template>
  <div>
    <div v-if="!patient_has_appointment">
      <div class="error" v-if="error_message">{{ error_message }}</div>
      <h1>Patient Sign Up Sheet</h1>First Name :
      <input v-model="first_name" type="text" :class="{ 'error' : missing.first_name }" />
      <Br />Last Name :
      <input v-model="last_name" type="text" :class="{ 'error' : missing.last_name }" />
      <br />SSN # :
      <input v-model="ssn" type="text" :class="{ 'error' : missing.ssn }" />
      <br />
      <button v-on:click="verify_patient_schedule()">Sign In</button>
    </div>

    <div v-if="patient_has_appointment">
      <h1>Welcome {{ first_name }} {{ last_name }}</h1>
      <h2>Enter your demographic information</h2>
      <label>Gender:
        <select v-model="gender">
          <option>Male</option>
          <option>Female</option>
          <option>Unknown - Decline to state</option>
        </select>
      </label><br />
      <label>
        Preferred Language:
        <select v-model="preferred_language">
          <option value="eng">English</option>
          <option value="zho">Chinese</option>
          <option value="other">Other</option>
          <option value="unknown">Unknown</option>
        </select>
      </label><br />
      <button class="btn btn-success" v-on:click="check_in_patient()">Submit</button>
    </div>
  </div>
</template>

<script>
import Axios from "axios";
import faker from "faker";
import { mapGetters, mapActions } from "vuex";
import variables from "@/variables.js";
import error_handler from "@/error_handler.js";

export default {
  data() {
    return {
      APP_CONFIG : variables,
      missing: {
        first_name: false,
        last_name: false,
        ssn: false
      },
      error_message: "",
      first_name: "",
      last_name: "",
      ssn: "",
      gender: 'Unknown',
      preferred_language: 'Unknown',

      patient_has_appointment: false
    };
  },
  methods: {
    check_in_patient: function() {
      Axios.post(
        this.APP_CONFIG.API_URL + "/check-in-patient/",
        {
          first_name : this.first_name,
          last_name : this.last_name,
          ssn : this.ssn,
          gender : this.gender,
          preferred_language : this.preferred_language
        },
        {
            headers : { 'Content-Type': 'application/json' }
        }
      )
        .then(result => {
          if (!result.data["success"]) {
            error_handler.run(this.$swal, {
              title: 'Error Checking In',
              description: result.data['error'] ? result.data['error'] : 'There is an error with checking in patient.'
            });
            return;
          }

          this.$swal({
            type: "success",
            title: "Thank you for Signing in!",
            html: "Please have a seat, our Doctor shall be with you shortly."
            // AUTO CLOSE
          }).then(result => {
            //console.log(result);
            this.clear_user_information();
          });

        })

        .catch(error => {
          error_handler.run(this.$swal, `PATIENT_SIGN_IN_ERROR: {error}`);
        });
    },

    verify_patient_schedule: function() {
      if (!this.first_name || !this.last_name || !this.ssn) {
        this.error_message = "Please enter all of your information.";

        this.missing = {
          first_name: this.first_name,
          last_name: this.last_name,
          ssn: this.ssn
        };
        return;
      }

      Axios.post('http://localhost:8000/verify-patient-has-appointment/',
        {
          first_name : this.first_name,
          last_name : this.last_name,
          ssn : this.ssn
        },
        { headers : { 'Content-Type': 'application/json' } })
        .then(result => {
          if(result.data['success']) {
            this.patient_has_appointment = true;
          }
          else {
            this.$swal({'title' : 'Could not verify if patient has an existing appointment...'})
          }
        })


    },

    clear_user_information: function() {
      this.error_message = "";
      this.first_name = "";
      this.last_name = "";
      this.ssn = "";
      this.gender = '';
      this.preferred_language = '';
      this.patient_has_appointment = false;
    }
  },
  mounted() {}
};
</script>