<template>
  <div id="app">
    <div class="container-fluid">
      <div class="row">
        <nav class="col-md-3 d-none d-md-block sidebar">
          <h2>Risk Types</h2>
          <ul>
            <li v-for="model in riskModels">
              <router-link :to="'/object/new/' + model.uuid">{{ model.name }}</router-link>
            </li>
          </ul>
        </nav>
        <main role="main" class="col-md-9 ml-sm-auto pt-3 px-4">
          <router-view />
        </main>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'model-list',
    computed: {
      riskModels () {
        return this.$store.state.risk_models;
      }
    }
  }
</script>

<style scoped>
  .sidebar {
    background-color: #eef3f8;
    padding: 25px;
    top: 0;
    height: 100vh;
  }

  .sidebar h2 {
    font-size: 1.1rem;
    font-weight: bold;
    margin-bottom: 0.6rem;
  }

  .sidebar ul {
    list-style: none;

    margin: 0;
    padding: 0;
  }

  .sidebar ul li {
    margin-bottom: 8px;
  }
</style>
