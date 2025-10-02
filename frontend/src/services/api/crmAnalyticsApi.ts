/**
 * CRM Analytics API Client
 * Provides access to aggregated metrics for the Employee CRM dashboard.
 */

import api from '../api';
import { ApiResponse, CRMDashboardResponse } from '../../stores/types';

class CRMAnalyticsApi {
  private readonly basePath = '/v2/crm';

  async getDashboard(): Promise<CRMDashboardResponse> {
    const response = await api.get<ApiResponse<CRMDashboardResponse>>(
      `${this.basePath}/dashboard`
    );
    return response.data.data;
  }
}

export const crmAnalyticsApi = new CRMAnalyticsApi();
