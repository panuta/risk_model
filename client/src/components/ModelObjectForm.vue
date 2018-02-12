<template>
  <div class="container">
    <h3>New {{ riskModel.name }} Form</h3>

    <form>
      <div class="form-group">
        <label for="exampleInputEmail1">Email address</label>
        <input type="email" class="form-control" id="exampleInputEmail1" aria-describedby="emailHelp" placeholder="Enter email">
        <small id="emailHelp" class="form-text text-muted">We'll never share your email with anyone else.</small>
      </div>
      <div class="form-group">
        <label for="exampleInputPassword1">Password</label>
        <input type="password" class="form-control" id="exampleInputPassword1" placeholder="Password">
      </div>
      <div class="form-check">
        <input type="checkbox" class="form-check-input" id="exampleCheck1">
        <label class="form-check-label" for="exampleCheck1">Check me out</label>
      </div>

      <div class="form-buttons">
        <button type="submit" class="btn btn-primary">Submit</button>
      </div>
    </form>
  </div>
</template>

<script>
  export default {
    name: 'model-object-form',
    computed: {
      riskModel () {
        const model_uuid = this.$route.params.uuid;
        return this.$store.state.risk_models.filter(model => model.uuid === model_uuid)[0];
      }
    }
  }
</script>

<style scoped>
  .container {
    padding: 5px 10px;
  }

  h3 {
    font-size: 1.6rem;
    font-weight: bold;
    margin-bottom: 1rem;
  }
</style>
