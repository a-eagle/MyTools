import { createApp, ref } from 'vue'
import App from './App.vue'
// npm install element-plus --saved
// npm install @element-plus/icons-vue
// npm install vue-router@4
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createMemoryHistory, createRouter, createWebHistory } from 'vue-router'
import QinDan from "./components/QinDan.vue";
import DeptQinDan from "./components/DeptQinDan.vue";

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
    history: createWebHistory(),
    routes,
});

function isAdminFunc() {
    let url = window.location.href;
    // console.log(url);
    if (! url) {
        return false;
    }
    let hashIdx = url.indexOf('#');
    if (hashIdx < 0)
        return false;
    let hash = url.substring(hashIdx + 1);
    for (let item of hash.split(';')) {
        if (item.trim() == 'admin') {
            return true;
        }
    }
    return false;
}
app.provide('is-admin', ref(isAdminFunc()));
app.use(router);
app.mount('#app')
