/**
 * Enhanced Auth API Client
 * Интеграция с новым enhanced auth backend API
 */

import api from '../api';
import {
  EnhancedEmployee,
  ApiResponse
} from '../../stores/types';

interface LoginRequest {
  username: string;
  password: string;
  mfa_code?: string;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  employee: EnhancedEmployee;
  mfa_required: boolean;
  expires_in: number;
}

interface RefreshTokenResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

interface MFASetupResponse {
  secret: string;
  qr_code: string;
  backup_codes: string[];
}

class EnhancedAuthApi {
  private readonly basePath = '/api/v1/auth';

  /**
   * Login with credentials
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await api.post<ApiResponse<LoginResponse>>(
      `${this.basePath}/login`,
      credentials
    );
    return response.data.data;
  }

  /**
   * Logout current session
   */
  async logout(token: string): Promise<void> {
    await api.post(`${this.basePath}/logout`, {}, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  /**
   * Refresh access token
   */
  async refreshToken(refreshToken: string): Promise<RefreshTokenResponse> {
    const response = await api.post<ApiResponse<RefreshTokenResponse>>(
      `${this.basePath}/refresh`,
      { refresh_token: refreshToken }
    );
    return response.data.data;
  }

  /**
   * Get current user profile
   */
  async getProfile(): Promise<EnhancedEmployee> {
    const response = await api.get<ApiResponse<EnhancedEmployee>>(`${this.basePath}/profile`);
    return response.data.data;
  }

  /**
   * Update user profile
   */
  async updateProfile(data: Partial<EnhancedEmployee>): Promise<EnhancedEmployee> {
    const response = await api.put<ApiResponse<EnhancedEmployee>>(
      `${this.basePath}/profile`,
      data
    );
    return response.data.data;
  }

  /**
   * Change password
   */
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await api.post(`${this.basePath}/change-password`, {
      current_password: currentPassword,
      new_password: newPassword,
    });
  }

  /**
   * Setup MFA (Multi-Factor Authentication)
   */
  async setupMFA(): Promise<MFASetupResponse> {
    const response = await api.post<ApiResponse<MFASetupResponse>>(`${this.basePath}/mfa/setup`);
    return response.data.data;
  }

  /**
   * Verify MFA code
   */
  async verifyMFA(code: string): Promise<boolean> {
    const response = await api.post<ApiResponse<{ verified: boolean }>>(
      `${this.basePath}/mfa/verify`,
      { code }
    );
    return response.data.data.verified;
  }

  /**
   * Disable MFA
   */
  async disableMFA(password: string): Promise<void> {
    await api.post(`${this.basePath}/mfa/disable`, {
      password,
    });
  }

  /**
   * Generate new backup codes for MFA
   */
  async generateBackupCodes(): Promise<string[]> {
    const response = await api.post<ApiResponse<{ backup_codes: string[] }>>(
      `${this.basePath}/mfa/backup-codes`
    );
    return response.data.data.backup_codes;
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(email: string): Promise<void> {
    await api.post(`${this.basePath}/password-reset/request`, {
      email,
    });
  }

  /**
   * Reset password with token
   */
  async resetPassword(token: string, newPassword: string): Promise<void> {
    await api.post(`${this.basePath}/password-reset/confirm`, {
      token,
      new_password: newPassword,
    });
  }

  /**
   * Verify email address
   */
  async verifyEmail(token: string): Promise<void> {
    await api.post(`${this.basePath}/verify-email`, {
      token,
    });
  }

  /**
   * Resend email verification
   */
  async resendEmailVerification(): Promise<void> {
    await api.post(`${this.basePath}/resend-verification`);
  }

  /**
   * Get active sessions
   */
  async getActiveSessions(): Promise<Array<{
    id: string;
    device: string;
    ip_address: string;
    location: string;
    created_at: string;
    last_activity: string;
    is_current: boolean;
  }>> {
    const response = await api.get<ApiResponse<any>>(`${this.basePath}/sessions`);
    return response.data.data;
  }

  /**
   * Revoke session
   */
  async revokeSession(sessionId: string): Promise<void> {
    await api.delete(`${this.basePath}/sessions/${sessionId}`);
  }

  /**
   * Revoke all other sessions
   */
  async revokeAllOtherSessions(): Promise<void> {
    await api.post(`${this.basePath}/sessions/revoke-all`);
  }

  /**
   * Check if username is available
   */
  async checkUsernameAvailability(username: string): Promise<{ available: boolean }> {
    const response = await api.get<ApiResponse<{ available: boolean }>>(
      `${this.basePath}/check-username`,
      { params: { username } }
    );
    return response.data.data;
  }

  /**
   * Check if email is available
   */
  async checkEmailAvailability(email: string): Promise<{ available: boolean }> {
    const response = await api.get<ApiResponse<{ available: boolean }>>(
      `${this.basePath}/check-email`,
      { params: { email } }
    );
    return response.data.data;
  }

  /**
   * Get security events log
   */
  async getSecurityEvents(params?: {
    page?: number;
    per_page?: number;
    event_type?: string;
  }): Promise<Array<{
    id: string;
    event_type: string;
    description: string;
    ip_address: string;
    user_agent: string;
    timestamp: string;
    metadata: Record<string, any>;
  }>> {
    const response = await api.get<ApiResponse<any>>(`${this.basePath}/security-events`, {
      params,
    });
    return response.data.data;
  }
}

// Export singleton instance
export const enhancedAuthApi = new EnhancedAuthApi();
export default enhancedAuthApi;
