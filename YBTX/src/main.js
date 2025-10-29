import { createApp, ref } from 'vue'
import App from './App.vue'
// npm install element-plus --saved
// npm install @element-plus/icons-vue
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'


const app = createApp(App);
app.use(ElementPlus);
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component);
}

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

app.mount('#app')
