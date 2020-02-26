
import Axios from 'axios';
import variables from "@/variables.js";
const _CONFIG = variables;

const state = {
    authUser: {
        is_authenticated : false
    },
    jwt: localStorage.getItem('token'),
    appServerSettings: {},
    interceptorSettings: {
        headers: {
            // Set your Authorization to 'JWT', not Bearer!!!
            //Authorization: `JWT ${this.$store.state.jwt}`,
            "Content-Type": "application/json"
        },
        xhrFields: {
            withCredentials: true
        }
    },
    axiosInstance : false
};

const getters = {
    appServerSettings: state => state.appServerSettings,
    axiosInstance: state => state.axiosInstance,
    my: state => state.authUser,
    interceptorSettings : state => state.interceptorSettings
}

const actions = {
    getAppServerSettings({ commit }) {

        return new Promise((resolve, reject)=> {
            Axios.get(_CONFIG.API_ENDPOINTS, { crossDomain: true })
            .then(appServerSettingsponse => {
                commit('setAppServerSettings', appServerSettingsponse);
                resolve();
            })
            .catch(error => {
                reject(error);
            })
        })

    },

    updateStatus({ commit }) {

        return new Promise((resolve, reject)=> {

            if(!state.authUser.is_authenticated) {
                reject();
            }

            console.log('GETTING STATUS : ' + state.appServerSettings.endpoints.user.my_status);
            Axios.get(
                state.appServerSettings.endpoints.user.my_status,
                state.interceptorSettings
            )
            .then(result => {
                if(!result.data['success'])
                    throw result.data['error']; 
                
                commit('updateUserStatus', result.data['status']);
                resolve();
            })
            .catch(error => {
                console.log(state.appServerSettings.endpoints.user.my_status);
                reject(error);
            });
        })

    },

    /* async userLogin({ commit }, payload) {
        //const payload = { username: this.username, password: this.password };

        const loginResponse = await Axios.post(
            state.appServerSettings.endpoints.user.authentication,
            payload);

        commit('userLogin', loginResponse);

        const updateUserInformation = await state.axiosInstance({
            url: state.appServerSettings.endpoints.user.info,
            method: 'get'
        });

        commit('updateUserInformation', updateUserInformation)

        return
    }*/
    userLogin({ commit }, payload) {
        //const payload = { username: this.username, password: this.password };

        return new Promise((resolve, reject) => {

            Axios.post(
                state.appServerSettings.endpoints.user.authentication,
                payload)
            .then(loginResponse => {
                
                if(loginResponse.data['error']) {
                    reject(loginResponse.data);
                    return;
                }

                commit('userLogin', loginResponse);

                state.axiosInstance({
                    url: state.appServerSettings.endpoints.user.info,
                    method: 'get'
                })
                .then(updateUserInformation => {
                    updateUserInformation.data['password'] = payload.password;
                    commit('updateUserInformation', updateUserInformation);
                    resolve();
                })
                .catch(error => {
                    reject(error);
                });

            })
            .catch(error => {
                reject(error);
            });
        })

        /*
        return Axios.post(
            state.appServerSettings.endpoints.user.authentication,
            payload)
        .then(loginResponse => {
            commit('userLogin', loginResponse);

            state.axiosInstance({
                url: state.appServerSettings.endpoints.user.info,
                method: 'get'
            }).then(updateUserInformation => {
                commit('updateUserInformation', updateUserInformation)
            })
        });
        */
    },
    userLogout({commit}) {
        return new Promise((resolve) => {
            var username = state.authUser.username;

            commit('userLogout');

            return resolve({'success': {'username' : username }, 'message' : 'Logout Success'});
        });
    }
}

const mutations = {
    updateToken(state, newToken) {
        //console.log(newToken);
        // TODO: For security purposes, take localStorage out of the project.
        localStorage.setItem('token', newToken);
        state.jwt = newToken;

        state.interceptorSettings.headers.Authorization = `JWT ${state.jwt}`;

        //console.log(state.interceptorSettings);
    },
    updateUserStatus(state, my_status) {
        //console.log(userInfo);

        state.authUser['profile'] = my_status;

        //console.log(state.authUser)
    },
    updateUserInformation(state, userInfo) {
        //console.log(userInfo);

        state.authUser = {
            unique_id : userInfo.data['unique_id'],
            username : userInfo.data['username'],
            is_authenticated: true,
            password : userInfo.data['password'],
            status : userInfo.data['status']
        };

        //console.log(state.authUser)
    },
    removeToken(state) {
        // TODO: For security purposes, take localStorage out of the project.
        localStorage.removeItem('token');
        state.jwt = null;
    },

    userLogin: (state, loginResponse) => {
        loginResponse = loginResponse.data;
        //console.log(loginResponse.access_token);
        mutations.updateToken(state, loginResponse.access_token);

        state.axiosInstance = Axios.create(state.interceptorSettings);

        //console.log(state.interceptorSettings);

    },

    userLogout: (state) => {
        state.authUser = {
            is_authenticated : false
        };
        state.interceptorSettings = {
            headers: {
                // Set your Authorization to 'JWT', not Bearer!!!
                //Authorization: `JWT ${this.$store.state.jwt}`,
                "Content-Type": "application/json"
            },
            xhrFields: {
                withCredentials: true
            }
        };
        state.axiosInstance = false;

    },

    setAppServerSettings: (state, appServerSettings) => {

        console.log('Setting Application Settings from Server.');
        appServerSettings = appServerSettings.data;

        if(!('endpoints' in appServerSettings))
            throw 'NO_APPLICATION_SETTINGS';
        
        var app_server_settings = {};

        // Check which CDN Server is active
        var best_server = appServerSettings.cdn_servers['main']

        if (appServerSettings.cdn_servers && appServerSettings.cdn_endpoints) {

            app_server_settings = appServerSettings;

            app_server_settings['CDN_ENDPOINTS'] = {};
            for (var i in appServerSettings.cdn_endpoints) {
                app_server_settings['CDN_ENDPOINTS'][i] = best_server + appServerSettings.cdn_endpoints[i];
            }
            app_server_settings['application_ready'] = true;
        }

        state.appServerSettings = app_server_settings;
    }
}

export default {
    state,
    mutations,
    getters,
    actions
}