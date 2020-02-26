import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';

import user from './user';

Vue.use(Vuex);

// Make Axios play nice with Django CSRF
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

export default new Vuex.Store({
    modules: {
        user
    },
  })