 import { GOOGLE_CLIENT_ID } from '../../constants.js'

export const googleAuthConfig = {
  clientId: GOOGLE_CLIENT_ID,
  scope: 'openid email profile',
  prompt: 'select_account'
}
