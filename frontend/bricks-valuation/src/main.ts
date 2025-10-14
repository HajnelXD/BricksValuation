import { createApp } from 'vue';
import './style.css';
import App from './App.vue';
import { pinia } from './stores';
import { router } from './router';
import { i18n } from './i18n';

createApp(App).use(pinia).use(router).use(i18n).mount('#app');
