import { defineRouter } from '#q-app/wrappers'
import {
  createRouter,
  createMemoryHistory,
  createWebHistory,
  createWebHashHistory,
} from 'vue-router'
import routes from './routes'

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default defineRouter(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === 'history'
      ? createWebHistory
      : createWebHashHistory

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(process.env.VUE_ROUTER_BASE),
  })

  // Router guard for authentication
  Router.beforeEach(async (to, from, next) => {
    // Import the useAuth composable dynamically to avoid circular imports
    const { useAuth } = await import('../composables/useAuth')
    const { fetchMe, isAuthenticated } = useAuth()

    // Define public routes (no authentication required)
    const publicRoutes = ['/', '/login', '/register']

    // Check if the route requires authentication
    // Exact match for public routes, or starts with /verify-email or /listing/
    const isPublicRoute = publicRoutes.includes(to.path) ||
                          to.path.startsWith('/verify-email') ||
                          to.path.startsWith('/listing/')

    if (!isPublicRoute) {
      // Check if user is already authenticated
      if (!isAuthenticated.value) {
        // Try to fetch user from HTTP-only cookie
        const isValid = await fetchMe()

        if (!isValid) {
          // Redirect to login with return URL
          next({
            path: '/login',
            query: { redirect: to.fullPath }
          })
          return
        }
      }
    }

    // If we get here, either route is public or user is authenticated
    next()
  })

  return Router
})
