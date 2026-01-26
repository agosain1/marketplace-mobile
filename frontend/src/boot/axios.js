import { defineBoot } from '#q-app/wrappers'
import axios from 'axios'

// Be careful when using SSR for cross-request state pollution
// due to creating a Singleton instance here;
// If any client changes this (global) instance, it might be a
// good idea to move this instance creation inside of the
// "export default () => {}" function below (which runs individually
// for each client)
// Ensure baseURL always has a trailing slash
const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const baseURL = apiUrl.endsWith('/') ? apiUrl : `${apiUrl}/`

const api = axios.create({
    baseURL: baseURL,
    headers: {
        'Content-Type': 'application/json'
    },
    timeout: 10000,
    withCredentials: true
});

// Flag to prevent multiple refresh attempts
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error = null) => {
    failedQueue.forEach(promise => {
        if (error) {
            promise.reject(error);
        } else {
            promise.resolve();
        }
    });
    failedQueue = [];
};

// automatic token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Handle 403 Forbidden - refresh token expired/invalid
        if (error.response?.status === 403) {
            // Clear session and redirect to login
            if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
                await api.get('/auth/clear-session').catch(() => {});
                window.location.href = '/login';
            }
            return Promise.reject(error);
        }

        // Handle 401 Unauthorized - access token expired
        if (error.response?.status === 401 && !originalRequest._retry) {
            // Don't try to refresh for auth endpoints (login, register, etc.)
            // These endpoints don't require authentication, so 401 means bad credentials
            if (originalRequest.url?.includes('auth/login') ||
                originalRequest.url?.includes('auth/logout') ||
                originalRequest.url?.includes('auth/register') ||
                originalRequest.url?.includes('auth/verify-email') ||
                originalRequest.url?.includes('auth/forgot-password') ||
                originalRequest.url?.includes('auth/resend-verification')) {
                return Promise.reject(error);
            }

            if (isRefreshing) {
                // If already refreshing, queue this request
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject });
                }).then(() => {
                    return api(originalRequest);
                }).catch((err) => {
                    return Promise.reject(err);
                });
            }

            originalRequest._retry = true;
            isRefreshing = true;

            try {
                // Attempt to refresh the access token
                await api.post('/auth/refresh');

                processQueue();
                isRefreshing = false;

                // Retry the original request with new access token
                return api(originalRequest);
            } catch (refreshError) {
                processQueue(refreshError);
                isRefreshing = false;

                // If refresh fails with 403, it will be handled by the 403 handler above
                // Otherwise, just reject the error
                return Promise.reject(refreshError);
            }
        }
        return Promise.reject(error);
    }
);

export default defineBoot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API
})

export { api }
