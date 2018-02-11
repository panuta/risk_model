
Vue.component('risk-model-list', {
  template: '<ul><li>Model 1</li></ul>'
});


var app = new Vue({
  el: '#app',
  data: {
    message: 'Hello Vue!'
  },
  template: '<risk-model-list></risk-model-list>'
});
