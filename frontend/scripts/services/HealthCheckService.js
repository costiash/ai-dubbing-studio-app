/**
 * Health Check Service
 *
 * Verifies backend API health and configuration status.
 * Single responsibility: Backend connectivity verification.
 */
export class HealthCheckService {
  constructor(apiClient, uiFeedbackManager) {
    this.apiClient = apiClient;
    this.uiFeedbackManager = uiFeedbackManager;
  }

  /**
   * Check backend API health and configuration
   */
  async checkBackendHealth() {
    try {
      const health = await this.apiClient.healthCheck();
      console.log('Backend API Status:', health);

      if (!health.openai_api_configured) {
        this.uiFeedbackManager.showError(
          'OpenAI API key not configured. Please check your .env file.'
        );
      }
    } catch (error) {
      console.error('Backend health check failed:', error);
      this.uiFeedbackManager.showError(
        'Cannot connect to backend server. Please ensure it is running at http://localhost:8000'
      );
    }
  }
}
