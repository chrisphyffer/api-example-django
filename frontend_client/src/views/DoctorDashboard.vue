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
          <th scope="col">Scheduled For<br /><span style="font-size:12px;">(Record Updated At)</span></th>
          <th scope="col">First Name</th>
          <th scope="col">Last Name</th>
          <th scope="col">Phone Number</th>
          <th scope="col">Status</th>
          <th scope="col">Time Waiting</th>
          <th scope="col">Is Walk-In</th>
          <th scope="col"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="appointment in appointments" v-bind:key="appointment.id">
          <td>{{ appointment.scheduled_time }}<br /><span style="font-size:12px;">{{ Date.parse(appointment.updated_at) }}</span></td>
          <td v-if="typeof(appointment.patient) != 'object'" colspan="3">
            Loading Patient Information...
          </td>
          <td v-if="typeof(appointment.patient) == 'object'">{{ appointment.patient.first_name }}</td>
          <td v-if="typeof(appointment.patient) == 'object'">{{ appointment.patient.last_name }}</td>
          <td v-if="typeof(appointment.patient) == 'object'">{{ appointment.patient.phone }}</td>
          <td>{{ appointment.status }}</td>
          <td>{{ wait_times[appointment.id] }}</td>
          <td>{{ appointment.is_walk_in }}</td>
          
          <td>
            <div v-if="VALID_SEEABLE_PATIENTS.indexOf(appointment.status) != -1 ">
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
      VALID_SEEABLE_PATIENTS: ['Arrived', 'Checked In'],

      appointments: [],

      //// In the event the same patient is visiting the office,
      //// there will be no need to reconnect to the api and fetch again.
      patient_list: {},
      average_patient_wait_time: 2999, // In seconds
      APP_CONFIG: variables,

      wait_times : {}, //// {'appt_id' : x_seconds }
    };
  },
  methods: {
    begin_timer: function() {
      setInterval(() => {
        //new Date() / 1000
        //Date.parse(appointments[appt].updated_at)

        //Status_transitions...
        for(var appt in this.appointments) {
          if(this.VALID_SEEABLE_PATIENTS.indexOf(this.appointments[appt].status))
            continue

          if(!this.wait_times[this.appointments[appt].id])
            this.$set(this.wait_times, this.appointments[appt].id, 0);
          this.$set(this.wait_times, this.appointments[appt].id, 
                    Math.floor(new Date() / 1000) - Math.floor(new Date(this.appointments[appt].updated_at).getTime() / 1000) );
          console.log(this.appointments[appt].id, ' ', this.wait_times[this.appointments[appt].id])
        }
      }, 1000)
    },
    begin_appointment: function(appointment, confirmed) {
      //// Confirm with the Doctor if this patient is to be seen.
      if (!confirmed) {
        this.$swal({
          title: "Begin Patient Session Confirmation",
          html:
            `Do you want to start a session with` +
            ` <strong>${appointment.patient.first_name} ` +
            `${appointment.patient.last_name}</strong>?`,
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
        this.APP_CONFIG.API_URL + `/begin-appointment/${appointment.id}/`,
        {} // Parameters
        //this.interceptorSettings
      )
        .then(result => {

          if (!result.data["success"]) {
            var title = "";
            error_handler.run(this.$swal, {
              title: "An Error Occured..",
              description: "Something wrong happened."
            });
            return;
          }

          this.$swal({
            type: "success",
            title: "Patient Session Started.",
            html: `${appointment.patient.first_name} ${appointment.patient.last_name}`
          });

          this.fetch_appointment(appointment.id);
        })
        .catch(error => {
          console.log(error);
        });
    },

    fetch_appointment : function(appointment_id) {
      Axios.get(this.APP_CONFIG.API_URL + `/appointment/${appointment_id}`)
      .then(result => {
        for(var appt in this.appointments) {
          if(this.appointments[appt].id == appointment_id) {

            var patient = this.appointments[appt].patient;
            result.data['appointment']['patient'] = patient;
            this.$set(this.appointments, appt, result.data['appointment'])

            break;
          }
        }
      })
      .catch(error => {
        console.log(error);
      })
    },

    retrieve_appointments_list: function() {
      Axios.post(
        this.APP_CONFIG.API_URL + "/appointments/"
      )
        .then(result => {

          if (!result.data["success"]) {
            error_handler.run(this.$swal, {
              title: "",
              description: (result.data['error']) ? result.data['error'] : "Something wrong happened."})
            return;
          }

          this.appointments = result.data['appointments'];
          for(var appt in this.appointments) {

            this.look_up_patient(appt).then(result => {
              this.appointments[result.appt].patient = result.patient;
              this.patient_list[this.appointments.patient] = result.patient;
            }).catch(error => {
                error_handler.run(this.$swal, {
                  title: "Error Retrieving Patient",
                  description: (result.data['error']) ? result.data['error'] : "Something wrong happened."})
            })
          }

          this.begin_timer();
        })
        .catch(error => {
          console.log(error);
        });
    },

    look_up_patient: function(appt) {
      return new Promise((resolve, reject) => {
          Axios.post(
            this.APP_CONFIG.API_URL + `/patient/${this.appointments[appt].patient}/`
          )
            .then(result => {
              if(!result.data['success']) {
                reject(result.data['error']);
                return;
              }
              resolve({appt : appt, patient : result.data['patient']} )
            })
            .catch(error => {
              reject("PATIENT_INFORMATION_RETRIEVAL_ERROR")
              return
            });
      });
    }
  },
  mounted() {
    this.retrieve_appointments_list();
    
  }
};
</script>