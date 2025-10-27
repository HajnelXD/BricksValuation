/**
 * Environment Configuration
 * Centralizes all environment variables used in the application
 * Variables must be prefixed with VITE_ to be accessible in browser
 */

export const env = {
  /**
   * API Configuration
   */
  api: {
    baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
    version: import.meta.env.VITE_API_VERSION || '1',
    timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000', 10),
  },

  /**
   * App Configuration
   */
  app: {
    title: import.meta.env.VITE_APP_TITLE || 'BricksValuation',
    env: import.meta.env.VITE_APP_ENV || 'development',
    isDev: import.meta.env.DEV,
    isProd: import.meta.env.PROD,
  },

  /**
   * Feature Flags
   */
  features: {
    enableMockData: import.meta.env.VITE_ENABLE_MOCK_DATA === 'true',
  },

  /**
   * Logging Configuration
   */
  logging: {
    level: import.meta.env.VITE_LOG_LEVEL || 'info',
  },
};

export default env;
