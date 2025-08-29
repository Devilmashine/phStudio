/**
 * Consent Service for Frontend
 * Handles communication with backend consent APIs
 */

import { apiClient } from './api';

export interface CookieConsentRequest {
  accepted_categories: string[];
}

export interface CookieConsentResponse {
  categories_accepted: string[];
  consent_recorded: boolean;
  consents_count: number;
}

export interface BookingConsentRequest {
  booking_data: Record<string, any>;
  consent_versions?: Record<string, string>;
}

export interface ConsentSummary {
  user_identifier: string;
  consent_status: Record<string, any>;
  total_consents: number;
}

export interface ConsentWithdrawalRequest {
  user_identifier: string;
  consent_type: string;
}

class ConsentService {
  private baseUrl = '/api/consent';

  /**
   * Record cookie consent preferences
   */
  async recordCookieConsent(acceptedCategories: string[]): Promise<CookieConsentResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/cookie-consent/record`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          accepted_categories: acceptedCategories
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to record cookie consent:', error);
      throw error;
    }
  }

  /**
   * Get available cookie categories
   */
  async getCookieCategories(): Promise<Record<string, any>> {
    try {
      const response = await fetch(`${this.baseUrl}/cookie-consent/categories`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to get cookie categories:', error);
      throw error;
    }
  }

  /**
   * Get user's current cookie preferences
   */
  async getCookiePreferences(userIdentifier: string): Promise<{ preferences: Record<string, boolean> }> {
    try {
      const response = await fetch(`${this.baseUrl}/cookie-consent/preferences/${encodeURIComponent(userIdentifier)}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to get cookie preferences:', error);
      throw error;
    }
  }

  /**
   * Record consent for booking operations
   */
  async recordBookingConsent(bookingData: Record<string, any>, consentVersions?: Record<string, string>): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/booking-consent/record`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          booking_data: bookingData,
          consent_versions: consentVersions || {}
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to record booking consent:', error);
      throw error;
    }
  }

  /**
   * Get consent summary for a user
   */
  async getConsentSummary(userIdentifier: string): Promise<ConsentSummary> {
    try {
      const response = await fetch(`${this.baseUrl}/consent/summary/${encodeURIComponent(userIdentifier)}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to get consent summary:', error);
      throw error;
    }
  }

  /**
   * Withdraw a specific type of consent
   */
  async withdrawConsent(userIdentifier: string, consentType: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/consent/withdraw`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          user_identifier: userIdentifier,
          consent_type: consentType
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to withdraw consent:', error);
      throw error;
    }
  }

  /**
   * Get all consents for a user
   */
  async getUserConsents(userIdentifier: string, consentType?: string): Promise<any> {
    try {
      const url = new URL(`${this.baseUrl}/consent/user/${encodeURIComponent(userIdentifier)}`, window.location.origin);
      if (consentType) {
        url.searchParams.set('consent_type', consentType);
      }

      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to get user consents:', error);
      throw error;
    }
  }

  /**
   * Check health of consent service
   */
  async checkHealth(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/consent/health`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Consent service health check failed:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const consentService = new ConsentService();
export default consentService;