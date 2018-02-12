<template>
  <div class="container">
    <h3>New {{ riskModel.name }} Form</h3>

    <form>
      <template class="form-group" v-for="field in riskModel.fields">
        <div class="form-group">
          <label :for="'id_' + field.slug">{{ field.name }}</label>

          <template v-if="field.type === 'text'">
            <input type="text" class="form-control" :id="'id_' + field.slug" :name="field.slug">
          </template>

          <template v-if="field.type === 'number'">
            <input type="number" class="form-control" :id="'id_' + field.slug" :name="field.slug">
          </template>

          <template v-if="field.type === 'date'">
            <datepicker bootstrap-styling="true"/>
          </template>

          <template v-if="field.type === 'enum'">
            <select class="form-control" :id="'id_' + field.slug" :name="field.slug">
              <option></option>
              <option v-for="choice in field.choices.split(',')" :value="choice">{{ choice }}</option>
            </select>
          </template>

          <small v-if="!field.is_required" class="form-text text-muted">This field is optional</small>
        </div>
      </template>

      <div class="form-buttons">
        <button type="submit" class="btn btn-primary">Submit</button>
      </div>
    </form>
  </div>
</template>

<script>
  import Datepicker from 'vuejs-datepicker';

  export default {
    name: 'model-object-form',
    components: {
        Datepicker
    },
    computed: {
      riskModel () {
        const model_uuid = this.$route.params.uuid;
        return this.$store.state.risk_models.filter(model => model.uuid === model_uuid)[0];
      }
    }
  }
</script>

<style>
  .form-control[readonly] {
    background-color: #fff !important;
  }
</style>

<style scoped>
  .container {
    padding: 5px 10px;
  }

  h3 {
    font-size: 1.6rem;
    font-weight: bold;
    margin-bottom: 1rem;
  }

  .form-buttons {
    margin-top: 1.5rem;
  }

  .form-buttons .btn {
    padding: .5rem 2.3rem;
  }
</style>
