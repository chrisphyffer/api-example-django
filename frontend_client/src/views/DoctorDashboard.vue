<template>
  <div>
    <br />
    <br />
    <div class="row">
      <div class="col-6">
        <h1>Welcome Dr. Chrono</h1>
      </div>

      <div class="col-6 text-right">
        Statistics:
        <br />
        Appointments Scheduled for Today : {{ appointments.length }}
        <br />
        Average Patient Wait Time Overall : {{ average_patient_wait_time }}
      </div>
    </div>

    <br />
    <br />
    <h2>List of Appointments</h2>
    <table class="table table-striped">
      <thead>
        <tr>
          <th scope="col"></th>
          <th scope="col">Scheduled For</th>
          <th scope="col">Photo</th>
          <th scope="col">First Name</th>
          <th scope="col">Last Name</th>
          <th scope="col">Phone Number</th>
          <th scope="col">Status</th>
          <th scope="col">Time Waiting</th>
          <th scope="col"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="appointment in appointments" v-bind:key="appointment.id">
          <td></td>
          <td>{{ appointment.scheduled_time }}</td>
          <td>PHOTO</td>
          <td>{{ appointment.patient.firstName }}</td>
          <td>{{ appointment.patient.lastName }}</td>
          <td>{{ appointment.patient.phone }}</td>
          <td>{{ appointment.status }}</td>
          <td>{{ appointment.wait_time }}</td>
          <td>
            <div v-if="appointment.status == 'checked_in'">
              <button
                class="btn btn-success"
                v-on:click="begin_appointment(appointment)"
              >Begin Patient Session</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <div class="row"></div>
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
      appointments: [],
      average_patient_wait_time: 2999, // In seconds
      APP_CONFIG: variables
    };
  },
  methods: {
    begin_appointment: function(appointment, confirmed) {
      //// Confirm with the Doctor if this patient is to be seen.
      if (!confirmed) {
        this.$swal({
          title: "Begin Patient Session Confirmation",
          html:
            `PHOTO <br />` +
            `Do you want to start a session with` +
            ` <strong>${appointment.patient.firstName} ` +
            `${appointment.patient.lastName}</strong>?`,
          confirmButtonText: "Yes Proceed",
          showCancelButton: true,
          showCloseButton: true
        }).then(result => {
          if (result.value) {
            this.begin_appointment(appointment, true);
          }
        });

        return;
      }

      //// Let us now begin our Patient's Appointment.

      Axios.post(
        this.APP_CONFIG.API_URL + "/frontend-api-test/",
        {} // Parameters
        //this.interceptorSettings
      )
        .then(result => {
          if (!result.data["success"]) {
            var error_message = "Something wrong happened.";
            var title = "";
            error_handler.run(this.$swal, {
              title: title,
              description: error_message
            });
            return;
          }

          this.$swal({
            type: "success",
            title: "Patient Session Started.",
            html: `${appointment.patient.firstName} ${appointment.patient.lastName}`
          });
        })
        .catch(error => {
          error_handler.run(this.$swal, "APPOINTMENT_BEGIN_ERROR");
        });
    },

    //// Generate some Fake Data until the Dr. Chrono API is accessible.
    fake_data: function() {
      var status_enum = ["arrived", "checked_in", "complete"];
      for (var i = 0; i < 18; i++) {
        this.appointments.push({
          doctor: 0,
          patient: {
            uid: faker.random.uuid(),
            firstName: faker.name.firstName(),
            lastName: faker.name.lastName(),
            phone: faker.phone.phoneNumber(),
            photo: faker.random.image()
          },

          //// Dr.Chrono handles all the internal time/date calculations for us.
          scheduled_time: "November 3rd 2020 @ 5:50PM",

          status: status_enum[Math.floor(Math.random() * status_enum.length)],

          is_walk_in: false,
          wait_time: 333 //// Chrono api will handle this, otherwise -
          //// Just start when the scheduled_time
          //// and now are overlapped.
        });
      }
    },

    retrieve_patient_list: function() {
      Axios.post(
        this.APP_CONFIG.API_URL + "/frontend-api-test/",
        {} // Parameters
        //this.interceptorSettings
      )
        .then(result => {
          if (!result.data["success"]) {
            var error_message = "Something wrong happened.";
            var title = "";
            error_handler.run(this.$swal, {
              title: title,
              description: error_message
            });
            return;
          }
        })
        .catch(error => {
          error_handler.run(this.$swal, "APPOINTMENT_LIST_RETRIEVAL_ERROR");
        });
    }
  },
  mounted() {
    //// We retrieve the list of appointments
    //// from the API endpoint:appointments_list
    //// https://app.drchrono.com/api-docs/#operation/appointments_list

    this.fake_data();
    this.retrieve_patient_list();
  }
};
</script>