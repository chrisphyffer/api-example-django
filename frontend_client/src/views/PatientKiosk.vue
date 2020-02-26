<template>
  <div>
    <div class="error" v-if="error_message">{{ error_message }}</div>
    <h1>Patient Sign Up Sheet</h1>First Name :
    <input v-model="first_name" type="text" :class="{ 'error' : missing.first_name }" />
    <Br />Last Name :
    <input v-model="last_name" type="text" :class="{ 'error' : missing.last_name }" />
    <br />SSN # :
    <input v-model="ssn" type="text" :class="{ 'error' : missing.ssn }" />
    <br />
    <button v-on:click="sign_in()">Sign In</button>
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
      ssn: ""
    };
  },
  methods: {
    sign_in: function() {
      if (!this.first_name || !this.last_name || !this.ssn) {
        this.error_message = "Please enter all of your information.";

        this.missing = {
          first_name: this.first_name,
          last_name: this.last_name,
          ssn: this.ssn
        };
        return;
      }


      Axios.post(
        this.APP_CONFIG.API_URL + "/check-in-patient/",
        {
          first_name : this.first_name,
          last_name : this.last_name,
          ssn : this.ssn
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

    clear_user_information: function() {
      this.error_message = "";
      this.first_name = "";
      this.last_name = "";
      this.ssn = "";
    }
  },
  mounted() {}
};
</script>