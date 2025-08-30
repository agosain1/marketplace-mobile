export const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID

export const googleAuthConfig = {
  clientId: GOOGLE_CLIENT_ID,
  scope: 'openid email profile',
  prompt: 'select_account'
}
