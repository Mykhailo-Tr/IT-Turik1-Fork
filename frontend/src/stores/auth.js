import { defineStore } from 'pinia';
import api from '@/api';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null,
        isLoggedIn: !!localStorage.getItem('access')
    }),
    actions: {
        async register(userData) {
            await api.post('auth/register/', userData);
        },
        async login(credentials) {
            const response = await api.post('auth/login/', credentials);
            localStorage.setItem('access', response.data.access);
            localStorage.setItem('refresh', response.data.refresh);
            this.isLoggedIn = true;
        },
        logout() {
            localStorage.clear();
            this.isLoggedIn = false;
            this.user = null;
        }
    }
});