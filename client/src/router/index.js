import Vue from 'vue';
import Router from 'vue-router';
import ModelList from '../components/ModelList';
import ModelObjectForm from '../components/ModelObjectForm';
import ModelUnselected from '../components/ModelUnselected';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Home',
      component: ModelList,
      children: [
        {
          path: '/object/new/:uuid',
          name: 'RiskObjectForm',
          component: ModelObjectForm,
        },
        {
          path: '',
          component: ModelUnselected,
        }
      ]
    },
  ],
});
