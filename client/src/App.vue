<template>
  <div id="app">
    <div v-if="loading" class="app-loading">Loading data...</div>
    <div v-if="!loading">
      <router-view />
    </div>
  </div>
</template>

<script>
  import axios from 'axios';
  import ModelList from "./components/ModelList";

  export default {
    name: 'app',
    components: {ModelList},
    data () {
      return {
        loading: true
      }
    },
    created () {
      axios.get(window.location.protocol + '//' + window.location.hostname + window.location.pathname + '/api/models/')
      .then(response => {
        this.$store.commit('setRiskModels', response.data.results);
        this.loading = false;
      })
      .catch(e => {
        this.errors.push(e)
      })
    }
  }
</script>

<style lang="scss">
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #222;
}

.app-loading {
  margin: 60px 0;
  text-align: center;
}

a {
  color: #3a6593;
}
</style>
