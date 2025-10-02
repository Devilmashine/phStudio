/**
 * Enhanced Admin Dashboard
 * Улучшенный административный дашборд с real-time обновлениями
 */

import React, { useEffect, useMemo, useState } from 'react';
import { 
  CalendarDaysIcon,
  UserGroupIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  ClockIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { useBookingStore, useEmployeeStore, useUIStore } from '../../../stores';
import { useBookingEvents } from '../../../hooks/useWebSocket';
import {
  BookingState,
  EmployeeStatus,
  CRMDashboardResponse,
  CRMPipelineStage,
  CRMEmployeePerformance,
} from '../../../stores/types';
import { StatCard } from './StatCard';
import { RecentBookings } from './RecentBookings';
import { BookingChart } from './BookingChart';
import { EmployeeActivity } from './EmployeeActivity';
import { SystemHealth } from './SystemHealth';
import { PipelineOverview } from './PipelineOverview';
import { TopEmployees } from './TopEmployees';
import LoadingSpinner from '../../common/LoadingSpinner';
import { crmAnalyticsApi } from '../../../services/api/crmAnalyticsApi';

interface DashboardStats {
  totalBookings: number;
  todayBookings: number;
  completedBookings: number;
  pendingBookings: number;
  totalRevenue: number;
  monthlyRevenue: number;
  activeEmployees: number;
  completionRate: number;
  averageBookingValue: number;
}

export const EnhancedAdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [crmMetrics, setCrmMetrics] = useState<CRMDashboardResponse | null>(null);
  const [pipeline, setPipeline] = useState<CRMPipelineStage[]>([]);
  const [topEmployees, setTopEmployees] = useState<CRMEmployeePerformance[]>([]);
  const [metricsError, setMetricsError] = useState<string | null>(null);

  const bookings = useBookingStore(state => state.bookings);
  const bookingFilters = useBookingStore(state => state.bookingFilters);
  const fetchBookings = useBookingStore(state => state.fetchBookings);
  const setBookingFilters = useBookingStore(state => state.setFilters);
  const clearBookingFilters = useBookingStore(state => state.clearFilters);
  const bookingsLoading = useBookingStore(state => state.loading);
  
  const { 
    employees, 
    fetchEmployees,
    loading: employeesLoading 
  } = useEmployeeStore();

  const { wsConnected, showSuccess } = useUIStore();

  // Setup real-time event handlers
  useBookingEvents({
    onBookingCreated: () => {
      showSuccess('Новое бронирование создано');
      refreshDashboard();
    },
    onBookingUpdated: () => {
      refreshDashboard();
    },
    onBookingStateChanged: () => {
      refreshDashboard();
    },
    onBookingCancelled: () => {
      refreshDashboard();
    },
  });

  // Load initial data
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchBookings(),
        fetchEmployees(),
        fetchCrmMetrics(),
      ]);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCrmMetrics = async () => {
    try {
      const metrics = await crmAnalyticsApi.getDashboard();
      setCrmMetrics(metrics);
      setPipeline(metrics.pipeline);
      setTopEmployees(metrics.top_employees);
      setMetricsError(null);
    } catch (error: any) {
      console.error('Error loading CRM metrics:', error);
      setMetricsError(error?.message || 'Не удалось загрузить CRM метрики');
      setCrmMetrics(null);
      setPipeline([]);
      setTopEmployees([]);
    }
  };

  const refreshDashboard = async () => {
    setRefreshing(true);
    try {
      await loadDashboardData();
    } finally {
      setRefreshing(false);
    }
  };

  const handleStageSelect = async (stage: CRMPipelineStage) => {
    const currentStateFilter = bookingFilters.state;
    if (currentStateFilter === stage.state) {
      clearBookingFilters();
    } else {
      setBookingFilters({ state: stage.state });
    }
    await fetchBookings();
  };

  // Calculate stats from loaded data
  const pendingStage = useMemo(() => {
    return pipeline.find(stage => stage.state === BookingState.PENDING);
  }, [pipeline]);

  const completedStage = useMemo(() => {
    return pipeline.find(stage => stage.state === BookingState.COMPLETED);
  }, [pipeline]);

  useEffect(() => {
    const calculateStats = () => {
      if (crmMetrics) {
        const overview = crmMetrics.overview;
        const completedCount = completedStage?.count ?? 0;
        const pendingCount = pendingStage?.count ?? 0;

        const completionRate = overview.total_bookings > 0
          ? (completedCount / overview.total_bookings) * 100
          : 0;

        setStats({
          totalBookings: overview.total_bookings,
          todayBookings: overview.completed_today,
          completedBookings: completedCount,
          pendingBookings: pendingCount,
          totalRevenue: overview.revenue_30_days,
          monthlyRevenue: overview.revenue_30_days,
          activeEmployees: employees.filter(e => e.status === EmployeeStatus.ACTIVE).length,
          completionRate,
          averageBookingValue: overview.avg_booking_value,
        });
        return;
      }

      if (bookings.length === 0 && employees.length === 0) {
        setStats(null);
        return;
      }

      const now = new Date();
      const today = now.toISOString().split('T')[0];
      const currentMonth = now.getMonth();
      const currentYear = now.getFullYear();

      const totalBookings = bookings.length;
      const todayBookings = bookings.filter(b => b.booking_date === today).length;
      const completedBookings = bookings.filter(b => b.state === BookingState.COMPLETED).length;
      const pendingBookings = bookings.filter(b => b.state === BookingState.PENDING).length;

      const totalRevenue = bookings
        .filter(b => b.state === BookingState.COMPLETED)
        .reduce((sum, b) => sum + b.total_price, 0);

      const monthlyRevenue = bookings
        .filter(b => {
          const bookingDate = new Date(b.booking_date);
          return (
            bookingDate.getMonth() === currentMonth &&
            bookingDate.getFullYear() === currentYear &&
            b.state === BookingState.COMPLETED
          );
        })
        .reduce((sum, b) => sum + b.total_price, 0);

      const activeEmployees = employees.filter(e => e.status === EmployeeStatus.ACTIVE).length;

      const completionRate = totalBookings > 0 ? (completedBookings / totalBookings) * 100 : 0;
      const averageBookingValue = completedBookings > 0 ? totalRevenue / completedBookings : 0;

      setStats({
        totalBookings,
        todayBookings,
        completedBookings,
        pendingBookings,
        totalRevenue,
        monthlyRevenue,
        activeEmployees,
        completionRate,
        averageBookingValue,
      });
    };

    calculateStats();
  }, [crmMetrics, bookings, employees, completedStage, pendingStage]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner className="w-8 h-8" />
        <span className="ml-2 text-gray-600 dark:text-gray-400">
          Загрузка дашборда...
        </span>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
        <div className="flex">
          <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
              Нет данных для отображения
            </h3>
            <div className="mt-2 text-sm text-yellow-700 dark:text-yellow-300">
              <p>Загрузите данные или проверьте подключение к серверу.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Employee CRM
          </h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Обзор деятельности команды и бронирований
          </p>
        </div>

        <div className="flex items-center gap-4">
          {/* Connection status */}
          <div className="flex items-center">
            <div 
              className={`w-2 h-2 rounded-full mr-2 ${
                wsConnected ? 'bg-green-500' : 'bg-red-500'
              }`} 
            />
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {wsConnected ? 'Подключено' : 'Отключено'}
            </span>
          </div>

          {/* Refresh button */}
          <button
            onClick={refreshDashboard}
            disabled={refreshing}
            className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {refreshing ? (
              <LoadingSpinner className="w-4 h-4 mr-2" />
            ) : (
              <ClockIcon className="w-4 h-4 mr-2" />
            )}
            Обновить
          </button>
        </div>
      </div>

      {metricsError && (
        <div className="border border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/20 text-sm text-yellow-800 dark:text-yellow-200 rounded-lg p-4">
          <p className="font-medium">CRM метрики недоступны</p>
          <p className="mt-1">{metricsError}</p>
        </div>
      )}

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Всего бронирований"
          value={stats.totalBookings.toString()}
          change={`${stats.todayBookings} сегодня`}
          changeType="neutral"
          icon={CalendarDaysIcon}
          color="blue"
        />

        <StatCard
          title="Выполнено"
          value={stats.completedBookings.toString()}
          change={`${stats.completionRate.toFixed(1)}% завершено`}
          changeType={stats.completionRate >= 80 ? "positive" : "negative"}
          icon={ChartBarIcon}
          color="green"
        />

        <StatCard
          title="Доход за месяц"
          value={`${stats.monthlyRevenue.toLocaleString('ru-RU')} ₽`}
          change={`${stats.averageBookingValue.toLocaleString('ru-RU')} ₽ средний чек`}
          changeType="positive"
          icon={CurrencyDollarIcon}
          color="indigo"
        />

        <StatCard
          title="Активные сотрудники"
          value={stats.activeEmployees.toString()}
          change={`из ${employees.length} всего`}
          changeType="neutral"
          icon={UserGroupIcon}
          color="purple"
        />
      </div>

      {/* Pipeline and top performers */}
      <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">
        <div className="xl:col-span-3 bg-white dark:bg-gray-800 shadow-sm rounded-lg border border-gray-200 dark:border-gray-700 h-full flex flex-col">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Воронка бронирований</h3>
                <p className="text-xs text-gray-500 dark:text-gray-400">Отслеживайте переходы сделок по стадиям</p>
              </div>
              <ChartBarIcon className="w-5 h-5 text-gray-400 hidden sm:block" />
            </div>
          </div>
          <div className="p-6 flex-1 overflow-auto">
            <PipelineOverview stages={pipeline} />
          </div>
        </div>

        <div className="xl:col-span-2 bg-white dark:bg-gray-800 shadow-sm rounded-lg border border-gray-200 dark:border-gray-700 h-full flex flex-col">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Лидеры команды</h3>
                <p className="text-xs text-gray-500 dark:text-gray-400">Кто приносит максимум выручки по завершённым бронированиям</p>
              </div>
              <UserGroupIcon className="w-5 h-5 text-gray-400 hidden sm:block" />
            </div>
          </div>
          <div className="p-6 flex-1 overflow-auto">
            <TopEmployees employees={topEmployees} />
          </div>
        </div>
      </div>

      {/* Charts and tables */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent bookings */}
        <div className="lg:col-span-2">
          <RecentBookings 
            bookings={bookings.slice(0, 10)}
            loading={bookingsLoading}
            onRefresh={refreshDashboard}
          />
        </div>

        {/* System health */}
        <div>
          <SystemHealth 
            wsConnected={wsConnected}
            bookingsCount={bookings.length}
            employeesCount={employees.length}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Booking chart */}
        <BookingChart 
          bookings={bookings}
          loading={bookingsLoading}
          revenueTrend={crmMetrics?.revenue_trend}
        />

        {/* Employee activity */}
        <EmployeeActivity 
          employees={employees}
          loading={employeesLoading}
        />
      </div>
    </div>
  );
};

export default EnhancedAdminDashboard;
