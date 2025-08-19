import AddListing from "pages/AddListing.vue"

const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/HomePage.vue') },
      { path: "add", component: AddListing }
    ],
  },
  {
    path: '/login',
    component: () => import('pages/LoginPage.vue'),
  },
  {
    path: '/verify-email/:email?',
    component: () => import('pages/VerifyEmailPage.vue'),
  },
  {
    path: '/account',
    component: () => import('pages/AccountPage.vue'),
  },
  {
    path: '/my-listings',
    component: () => import('pages/MyListings.vue')
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

export default routes
