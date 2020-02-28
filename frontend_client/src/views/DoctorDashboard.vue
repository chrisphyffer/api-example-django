<template>
  <div>
    <br />
    <br />
    <div class="row">
      <div class="col-6">
        <h1>Welcome Dr. Chrono</h1><br />
      </div>

      <div class="col-6 text-right">
        Statistics:
        <br />
        Appointments Scheduled for Today : {{ appointments.length }}
        <br />
        Combined Patient Wait Time Since Start : {{ total_patient_wait_time }}
        <button v-on:click="retrieve_appointments_status()">Refresh Status</button>
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
          <th scope="col">Check In</th>
          <th scope="col">Begin Session</th>
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
          
          <td >
            <div v-if="typeof(appointment.patient) == 'object' && 
                      DRCHRONO_VALID_SEEABLE_PATIENTS.indexOf(appointment.status) == -1 &&
                        DRCHRONO_CLOSED_APPOINTMENTS.indexOf(appointment.status) == -1 &&
                        DRCHRONO_VALID_APPOINTMENTS.indexOf(appointment.status) != -1">
              <button class="btn btn-success"
                v-on:click="check_in_patient(appointment.patient, appointment.id)"
              >Check In Patient</button>
            </div>
          </td>
          <td>
            <div  v-if="DRCHRONO_VALID_SEEABLE_PATIENTS.indexOf(appointment.status) != -1 &&
                        DRCHRONO_CLOSED_APPOINTMENTS.indexOf(appointment.status) == -1 ">
              <button class="btn btn-success"
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
      DRCHRONO_VALID_SEEABLE_PATIENTS: ['Arrived', 'Checked In', 'Checked In Online'],
      DRCHRONO_CLOSED_APPOINTMENTS: ['Complete', 'In Session', 'In Room'],
      DRCHRONO_VALID_APPOINTMENTS: ['Confirmed'],

      appointments: [],

      //// In the event the same patient is visiting the office,
      //// there will be no need to reconnect to the api and fetch patient information again.
      patient_list: {},
      total_patient_wait_time: null,
      APP_CONFIG: variables,

      wait_times : {}, // {'appt_id' : x_seconds }
      application_settings_loaded : false
    };
  },
  watch : {
    application_settings_loaded : function() {
      if(this.application_settings_loaded) {
        this.get_total_patient_wait_time();

        setInterval(() => {
          this.retrieve_appointments_status();
        }, 1000000000)
      }
    }
  },
  methods: {
    fetch_application_settings : function() {
      Axios.get(this.APP_CONFIG.API_URL + `/frontend-client-settings/`)
        .then(result => {
          if(result.data['success']) {
            this.DRCHRONO_VALID_SEEABLE_PATIENTS = result.data['DRCHRONO_VALID_SEEABLE_PATIENTS'];
            this.DRCHRONO_CLOSED_APPOINTMENTS = result.data['DRCHRONO_CLOSED_APPOINTMENTS'];
            this.DRCHRONO_VALID_APPOINTMENTS = result.data['DRCHRONO_VALID_APPOINTMENTS'];
            this.application_settings_loaded = true;
          } else {
            throw "Unable to fetch Application Settings from Django Server.";
          }

        }).catch(error => {
            this.$swal({
              title : 'Error fetching Client Settings',
              html : error
            })
        })
    },

    get_total_patient_wait_time : function() {
      Axios.get(this.APP_CONFIG.API_URL + `/total-patient-wait-time/`)
        .then(result => {
          if(result.data['success']) {
            this.total_patient_wait_time = result.data['total_wait_time'];
          }
        })
    },
    
    begin_timer: function() {
      var appointment_updated_date = false;
      var current_date = false;
      var wait_time = false;
      setInterval(() => {
        for(var appt in this.appointments) {
          if(this.DRCHRONO_VALID_SEEABLE_PATIENTS.indexOf(this.appointments[appt].status) == -1)
            continue;
          
          if(!this.appointments[appt].date_checked_in)
            continue;

          appointment_updated_date = Math.floor(new Date(this.appointments[appt].date_checked_in).getTime());
          current_date = new Date().getTime();

          appointment_updated_date /= 1000
          current_date /= 1000
          wait_time = Math.floor(current_date - appointment_updated_date)
          
          if(!this.wait_times[this.appointments[appt].id]) {
            this.$set(this.wait_times, this.appointments[appt].id, 0);
          }

          this.$set(this.wait_times, this.appointments[appt].id, wait_time);
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
            throw result.data["error"]
          }

          this.$swal({
            type: "success",
            title: "Patient Session Started.",
            html: `${appointment.patient.first_name} ${appointment.patient.last_name}`
          });

          this.fetch_appointment(appointment.id);
          this.get_total_patient_wait_time();
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
      });
    },

    retrieve_appointments_status: function(param) {
      Axios.post(
        this.APP_CONFIG.API_URL + '/appointments-status/'
      )
        .then(result => {

          if (!result.data["success"]) {
            error_handler.run(this.$swal, {
              title: "",
              description: (result.data['error']) ? result.data['error'] : "Something wrong happened."})
            return;
          }

          // Match Corresponding Statuses
          for(var appt in this.appointments) {
            for(var appt_id in result.data['appointments']) {
              if(this.appointments[appt]['id'] == appt_id) {
                this.appointments[appt]['status'] = result.data['appointments'][appt_id]
              }
            }
          }

        });
    },

    retrieve_appointments_list: function(param) {

      Axios.post(
        this.APP_CONFIG.API_URL + '/appointments/'
      )
        .then(result => {

          if (!result.data["success"]) {
            error_handler.run(this.$swal, {
              title: "",
              description: (result.data['error']) ? result.data['error'] : "Something wrong happened."})
            return;
          }

          this.appointments = result.data['appointments'];

          // Match corresponding patients:
          for(var appt in this.appointments) {
            if (this.patient_list[this.appointments.patient]) {
              this.appointments[result.appt].patient = this.patient_list[this.appointments.patient];
              continue;
            }
            
            this.look_up_patient(appt).then(result => {
              this.appointments[result.appt].patient = result.patient;
              this.patient_list[result.patient.id] = result.patient;
            }).catch(error => {
                error_handler.run(this.$swal, {
                  title: "Error Retrieving Patient",
                  description: (result.data['error']) ? result.data['error'] : "Something wrong happened."})
            })
          }

          this.begin_timer();
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
    },

    check_in_patient: function(patient, appt_id) {
      Axios.post(
        this.APP_CONFIG.API_URL + "/check-in-patient/",
        {
          id : patient.id
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
            title: "Patient has been succesfully checked in.",
            html: `<strong>${patient.first_name} ${patient.last_name}</strong> has been succesfully checked in.`
            // AUTO CLOSE
          });

          this.fetch_appointment(appt_id);

        })

        .catch(error => {
          error_handler.run(this.$swal, `PATIENT_SIGN_IN_ERROR: {error}`);
        });
    }
  },
  mounted() {
    this.retrieve_appointments_list();
    this.fetch_application_settings();
    
  }
};
</script>