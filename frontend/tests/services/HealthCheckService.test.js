import { describe, it, expect, beforeEach, vi } from 'vitest';
import { HealthCheckService } from '../../scripts/services/HealthCheckService.js';

describe('HealthCheckService', () => {
  let service;
  let mockApiClient;
  let mockUIFeedbackManager;

  beforeEach(() => {
    // Mock console methods
    vi.spyOn(console, 'log').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});

    // Create mocks
    mockApiClient = {
      healthCheck: vi.fn()
    };

    mockUIFeedbackManager = {
      showError: vi.fn()
    };

    // Create service instance
    service = new HealthCheckService(mockApiClient, mockUIFeedbackManager);
  });

  describe('Constructor', () => {
    it('should initialize with API client and UI feedback manager', () => {
      expect(service.apiClient).toBe(mockApiClient);
      expect(service.uiFeedbackManager).toBe(mockUIFeedbackManager);
    });
  });

  describe('checkBackendHealth()', () => {
    it('should call API client healthCheck', async () => {
      mockApiClient.healthCheck.mockResolvedValue({
        status: 'healthy',
        openai_api_configured: true
      });

      await service.checkBackendHealth();

      expect(mockApiClient.healthCheck).toHaveBeenCalled();
    });

    it('should log health status to console', async () => {
      const healthStatus = {
        status: 'healthy',
        openai_api_configured: true
      };
      mockApiClient.healthCheck.mockResolvedValue(healthStatus);

      await service.checkBackendHealth();

      expect(console.log).toHaveBeenCalledWith('Backend API Status:', healthStatus);
    });

    it('should not show error when OpenAI API is configured', async () => {
      mockApiClient.healthCheck.mockResolvedValue({
        status: 'healthy',
        openai_api_configured: true
      });

      await service.checkBackendHealth();

      expect(mockUIFeedbackManager.showError).not.toHaveBeenCalled();
    });

    it('should show error when OpenAI API is not configured', async () => {
      mockApiClient.healthCheck.mockResolvedValue({
        status: 'healthy',
        openai_api_configured: false
      });

      await service.checkBackendHealth();

      expect(mockUIFeedbackManager.showError).toHaveBeenCalledWith(
        'OpenAI API key not configured. Please check your .env file.'
      );
    });

    it('should handle backend connection errors', async () => {
      const error = new Error('Connection refused');
      mockApiClient.healthCheck.mockRejectedValue(error);

      await service.checkBackendHealth();

      expect(console.error).toHaveBeenCalledWith('Backend health check failed:', error);
      expect(mockUIFeedbackManager.showError).toHaveBeenCalledWith(
        'Cannot connect to backend server. Please ensure it is running at http://localhost:8000'
      );
    });

    it('should handle network timeout errors', async () => {
      const error = new Error('Timeout');
      mockApiClient.healthCheck.mockRejectedValue(error);

      await service.checkBackendHealth();

      expect(mockUIFeedbackManager.showError).toHaveBeenCalledWith(
        'Cannot connect to backend server. Please ensure it is running at http://localhost:8000'
      );
    });

    it('should handle API errors gracefully', async () => {
      const error = new Error('500 Internal Server Error');
      mockApiClient.healthCheck.mockRejectedValue(error);

      await service.checkBackendHealth();

      expect(mockUIFeedbackManager.showError).toHaveBeenCalled();
      expect(console.error).toHaveBeenCalled();
    });

    it('should handle missing openai_api_configured field', async () => {
      mockApiClient.healthCheck.mockResolvedValue({
        status: 'healthy'
        // openai_api_configured is undefined
      });

      await service.checkBackendHealth();

      // Should show error when field is missing (falsy)
      expect(mockUIFeedbackManager.showError).toHaveBeenCalledWith(
        'OpenAI API key not configured. Please check your .env file.'
      );
    });

    it('should handle explicit false for openai_api_configured', async () => {
      mockApiClient.healthCheck.mockResolvedValue({
        status: 'healthy',
        openai_api_configured: false
      });

      await service.checkBackendHealth();

      expect(mockUIFeedbackManager.showError).toHaveBeenCalledWith(
        'OpenAI API key not configured. Please check your .env file.'
      );
    });
  });

  describe('Integration: Health check workflow', () => {
    it('should complete successful health check without errors', async () => {
      mockApiClient.healthCheck.mockResolvedValue({
        status: 'healthy',
        openai_api_configured: true,
        version: '1.0.0'
      });

      await service.checkBackendHealth();

      expect(mockApiClient.healthCheck).toHaveBeenCalled();
      expect(console.log).toHaveBeenCalled();
      expect(mockUIFeedbackManager.showError).not.toHaveBeenCalled();
    });

    it('should detect and report configuration issues', async () => {
      mockApiClient.healthCheck.mockResolvedValue({
        status: 'degraded',
        openai_api_configured: false
      });

      await service.checkBackendHealth();

      expect(mockUIFeedbackManager.showError).toHaveBeenCalledWith(
        'OpenAI API key not configured. Please check your .env file.'
      );
    });

    it('should detect and report connection failures', async () => {
      mockApiClient.healthCheck.mockRejectedValue(new Error('ECONNREFUSED'));

      await service.checkBackendHealth();

      expect(console.error).toHaveBeenCalledWith(
        'Backend health check failed:',
        expect.any(Error)
      );
      expect(mockUIFeedbackManager.showError).toHaveBeenCalledWith(
        'Cannot connect to backend server. Please ensure it is running at http://localhost:8000'
      );
    });
  });
});
