import { createApp, ref } from 'vue'
import App from './App.vue'
// npm install element-plus --saved
// npm install @element-plus/icons-vue
// npm install vue-router@4
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createMemoryHistory, createRouter, createWebHistory, createWebHashHistory } from 'vue-router'
import QinDan from "./components/QinDan.vue";
import DeptQinDan from "./components/DeptQinDan.vue";
import { HashUrl } from './common'

const app = createApp(App);
app.use(ElementPlus);
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component);
}

const routes = [
    { path: '/', component: QinDan, name: 'Home' },
    { path: '/dept', component: DeptQinDan, name: 'Dept'},
  ]
  
const router = createRouter({
    history: createWebHashHistory(),
    routes,
});

function isAdminFunc() {
    let url = new HashUrl();
    return url.hasQueryParam('admin');
}
app.provide('is-admin', ref(isAdminFunc()));
app.use(router);
app.mount('#app')
