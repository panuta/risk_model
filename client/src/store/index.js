import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    risk_models: []
  },
  mutations: {
    setRiskModels (state, models) {
      state.risk_models = models;
    }
  }
});

export default store;
