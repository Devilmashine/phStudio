import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Tab } from '@headlessui/react';
import { Role, Permission, PERMISSIONS } from '../types/roles';
import { fetchRoles, createRole, updateRole, deleteRole } from '../services/rolesService';
import { fetchUsers, changeUserRole, deleteUser, User } from '../services/usersService';
import { hasPermission } from '../utils/permissions';
import { getCurrentUserRole } from '../utils/auth';
import Spinner from '../components/Spinner';
import { useToast } from '../components/Toast';
import { fetchBookings, bulkAction, deleteBooking, Booking } from '../services/bookingsService';
import { fetchReviews, bulkReviewAction, deleteReview, Review } from '../services/reviewsService';
import { exportData, ExportType, ExportFormat } from '../services/exportService';
import { fetchLogs, LogEntry } from '../services/logsService';

interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  full_name: string;
  created_at: string;
  last_login: string;
}

// Каркасные компоненты для разделов админки
const Dashboard = () => (
  <div>
    <h2 className="text-2xl font-bold mb-6">Аналитика</h2>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div className="bg-white rounded shadow p-6">
        <div className="text-gray-500">Бронирований за месяц</div>
        <div className="text-3xl font-bold">124</div>
      </div>
      <div className="bg-white rounded shadow p-6">
        <div className="text-gray-500">Средний чек</div>
        <div className="text-3xl font-bold">2 500 ₽</div>
      </div>
      <div className="bg-white rounded shadow p-6">
        <div className="text-gray-500">Средняя оценка</div>
        <div className="text-3xl font-bold">4.8</div>
      </div>
    </div>
  </div>
);

const BookingsManager = () => {
  const [bookings, setBookings] = React.useState<Booking[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [statusFilter, setStatusFilter] = React.useState('');
  const [dateFilter, setDateFilter] = React.useState('');
  const [selected, setSelected] = React.useState<number[]>([]);
  const [confirmDelete, setConfirmDelete] = React.useState<number | null>(null);
  const toast = useToast();

  const loadBookings = async () => {
    setLoading(true);
    try {
      const data = await fetchBookings({ status: statusFilter, date: dateFilter });
      setBookings(data);
    } catch {
      toast.showToast('Ошибка загрузки бронирований', 'error');
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    loadBookings();
    // eslint-disable-next-line
  }, [statusFilter, dateFilter]);

  const handleSelect = (id: number) => {
    setSelected(sel => sel.includes(id) ? sel.filter(i => i !== id) : [...sel, id]);
  };

  const handleSelectAll = () => {
    if (selected.length === bookings.length) setSelected([]);
    else setSelected(bookings.map(b => b.id));
  };

  const handleBulkAction = async (action: 'confirm' | 'cancel' | 'delete') => {
    setLoading(true);
    try {
      await bulkAction(selected, action);
      toast.showToast('Операция выполнена', 'success');
      setSelected([]);
      await loadBookings();
    } catch {
      toast.showToast('Ошибка выполнения операции', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteBooking = async (id: number) => {
    setLoading(true);
    try {
      await deleteBooking(id);
      toast.showToast('Бронирование удалено', 'success');
      await loadBookings();
    } catch {
      toast.showToast('Ошибка удаления бронирования', 'error');
    } finally {
      setLoading(false);
      setConfirmDelete(null);
    }
  };

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Бронирования</h2>
      <div className="flex gap-4 mb-4">
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} className="border rounded px-2 py-1">
          <option value="">Все статусы</option>
          <option value="confirmed">Подтверждено</option>
          <option value="pending">В ожидании</option>
          <option value="cancelled">Отменено</option>
        </select>
        <input type="date" value={dateFilter} onChange={e => setDateFilter(e.target.value)} className="border rounded px-2 py-1" />
        <button onClick={() => handleBulkAction('confirm')} disabled={!selected.length} className="bg-green-600 text-white px-3 py-1 rounded disabled:opacity-50">Подтвердить</button>
        <button onClick={() => handleBulkAction('cancel')} disabled={!selected.length} className="bg-yellow-500 text-white px-3 py-1 rounded disabled:opacity-50">Отменить</button>
        <button onClick={() => handleBulkAction('delete')} disabled={!selected.length} className="bg-red-600 text-white px-3 py-1 rounded disabled:opacity-50">Удалить</button>
      </div>
      {loading && <Spinner />}
      <table className="min-w-full bg-white rounded shadow">
        <thead>
          <tr>
            <th className="p-2"><input type="checkbox" checked={selected.length === bookings.length && bookings.length > 0} onChange={handleSelectAll} /></th>
            <th className="p-2">ID</th>
            <th className="p-2">Дата</th>
            <th className="p-2">Время</th>
            <th className="p-2">Клиент</th>
            <th className="p-2">Статус</th>
            <th className="p-2">Действия</th>
          </tr>
        </thead>
        <tbody>
          {bookings.map(b => (
            <tr key={b.id} className={selected.includes(b.id) ? 'bg-blue-50' : ''}>
              <td className="p-2"><input type="checkbox" checked={selected.includes(b.id)} onChange={() => handleSelect(b.id)} /></td>
              <td className="p-2">{b.id}</td>
              <td className="p-2">{b.date}</td>
              <td className="p-2">{b.time}</td>
              <td className="p-2">{b.client_name}</td>
              <td className="p-2">{b.status}</td>
              <td className="p-2">
                <button onClick={() => handleBulkAction('confirm')} className="text-green-600 hover:underline mr-2">Подтвердить</button>
                <button onClick={() => handleBulkAction('cancel')} className="text-yellow-600 hover:underline mr-2">Отменить</button>
                <button onClick={() => setConfirmDelete(b.id)} className="text-red-600 hover:underline">Удалить</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {confirmDelete !== null && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white rounded shadow-lg p-6 w-full max-w-sm">
            <div className="mb-4">Вы уверены, что хотите удалить это бронирование?</div>
            <div className="flex gap-2 justify-end">
              <button onClick={() => setConfirmDelete(null)} className="px-4 py-2">Отмена</button>
              <button onClick={() => handleDeleteBooking(confirmDelete)} className="bg-red-600 text-white px-4 py-2 rounded">Удалить</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const ReviewsManager = () => {
  const [reviews, setReviews] = React.useState<Review[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [statusFilter, setStatusFilter] = React.useState('');
  const [ratingFilter, setRatingFilter] = React.useState('');
  const [selected, setSelected] = React.useState<number[]>([]);
  const [confirmDelete, setConfirmDelete] = React.useState<number | null>(null);
  const toast = useToast();

  const loadReviews = async () => {
    setLoading(true);
    try {
      const data = await fetchReviews({ status: statusFilter, rating: ratingFilter });
      setReviews(data);
    } catch {
      toast.showToast('Ошибка загрузки отзывов', 'error');
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    loadReviews();
    // eslint-disable-next-line
  }, [statusFilter, ratingFilter]);

  const handleSelect = (id: number) => {
    setSelected(sel => sel.includes(id) ? sel.filter(i => i !== id) : [...sel, id]);
  };

  const handleSelectAll = () => {
    if (selected.length === reviews.length) setSelected([]);
    else setSelected(reviews.map(r => r.id));
  };

  const handleBulkAction = async (action: 'approve' | 'hide' | 'delete') => {
    setLoading(true);
    try {
      await bulkReviewAction(selected, action);
      toast.showToast('Операция выполнена', 'success');
      setSelected([]);
      await loadReviews();
    } catch {
      toast.showToast('Ошибка выполнения операции', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteReview = async (id: number) => {
    setLoading(true);
    try {
      await deleteReview(id);
      toast.showToast('Отзыв удалён', 'success');
      await loadReviews();
    } catch {
      toast.showToast('Ошибка удаления отзыва', 'error');
    } finally {
      setLoading(false);
      setConfirmDelete(null);
    }
  };

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Отзывы</h2>
      <div className="flex gap-4 mb-4">
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} className="border rounded px-2 py-1">
          <option value="">Все статусы</option>
          <option value="pending">На модерации</option>
          <option value="approved">Одобрено</option>
          <option value="hidden">Скрыто</option>
        </select>
        <select value={ratingFilter} onChange={e => setRatingFilter(e.target.value)} className="border rounded px-2 py-1">
          <option value="">Все оценки</option>
          {[5,4,3,2,1].map(r => <option key={r} value={r}>{r} ★</option>)}
        </select>
        <button onClick={() => handleBulkAction('approve')} disabled={!selected.length} className="bg-green-600 text-white px-3 py-1 rounded disabled:opacity-50">Одобрить</button>
        <button onClick={() => handleBulkAction('hide')} disabled={!selected.length} className="bg-yellow-500 text-white px-3 py-1 rounded disabled:opacity-50">Скрыть</button>
        <button onClick={() => handleBulkAction('delete')} disabled={!selected.length} className="bg-red-600 text-white px-3 py-1 rounded disabled:opacity-50">Удалить</button>
      </div>
      {loading && <Spinner />}
      <table className="min-w-full bg-white rounded shadow">
        <thead>
          <tr>
            <th className="p-2"><input type="checkbox" checked={selected.length === reviews.length && reviews.length > 0} onChange={handleSelectAll} /></th>
            <th className="p-2">ID</th>
            <th className="p-2">Клиент</th>
            <th className="p-2">Оценка</th>
            <th className="p-2">Текст</th>
            <th className="p-2">Статус</th>
            <th className="p-2">Действия</th>
          </tr>
        </thead>
        <tbody>
          {reviews.map(r => (
            <tr key={r.id} className={selected.includes(r.id) ? 'bg-blue-50' : ''}>
              <td className="p-2"><input type="checkbox" checked={selected.includes(r.id)} onChange={() => handleSelect(r.id)} /></td>
              <td className="p-2">{r.id}</td>
              <td className="p-2">{r.client_name}</td>
              <td className="p-2">{r.rating} ★</td>
              <td className="p-2 max-w-xs truncate" title={r.text}>{r.text}</td>
              <td className="p-2">{r.status}</td>
              <td className="p-2">
                <button onClick={() => handleBulkAction('approve')} className="text-green-600 hover:underline mr-2">Одобрить</button>
                <button onClick={() => handleBulkAction('hide')} className="text-yellow-600 hover:underline mr-2">Скрыть</button>
                <button onClick={() => setConfirmDelete(r.id)} className="text-red-600 hover:underline">Удалить</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {confirmDelete !== null && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white rounded shadow-lg p-6 w-full max-w-sm">
            <div className="mb-4">Вы уверены, что хотите удалить этот отзыв?</div>
            <div className="flex gap-2 justify-end">
              <button onClick={() => setConfirmDelete(null)} className="px-4 py-2">Отмена</button>
              <button onClick={() => handleDeleteReview(confirmDelete)} className="bg-red-600 text-white px-4 py-2 rounded">Удалить</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const ExportPanel = () => {
  const [loading, setLoading] = React.useState(false);
  const toast = useToast();

  const handleExport = async (type: ExportType, format: ExportFormat) => {
    setLoading(true);
    try {
      const blob = await exportData(type, format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${type}_${new Date().toISOString().slice(0, 10)}.${format === 'pdf' ? 'pdf' : 'xlsx'}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      toast.showToast('Файл успешно сформирован', 'success');
    } catch {
      toast.showToast('Ошибка экспорта данных', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Экспорт данных</h2>
      <div className="flex gap-4 mb-4">
        <button
          onClick={() => handleExport('bookings', 'pdf')}
          className="bg-indigo-600 text-white px-4 py-2 rounded"
          disabled={loading}
        >
          Экспорт бронирований (PDF)
        </button>
        <button
          onClick={() => handleExport('bookings', 'excel')}
          className="bg-green-600 text-white px-4 py-2 rounded"
          disabled={loading}
        >
          Экспорт бронирований (Excel)
        </button>
        <button
          onClick={() => handleExport('reviews', 'pdf')}
          className="bg-indigo-600 text-white px-4 py-2 rounded"
          disabled={loading}
        >
          Экспорт отзывов (PDF)
        </button>
        <button
          onClick={() => handleExport('reviews', 'excel')}
          className="bg-green-600 text-white px-4 py-2 rounded"
          disabled={loading}
        >
          Экспорт отзывов (Excel)
        </button>
      </div>
      {loading && <Spinner />}
    </div>
  );
};

const LogsViewer = () => {
  const [logs, setLogs] = React.useState<LogEntry[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [userFilter, setUserFilter] = React.useState('');
  const [dateFilter, setDateFilter] = React.useState('');
  const toast = useToast();

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await fetchLogs({ user: userFilter, date: dateFilter });
      setLogs(data);
    } catch {
      toast.showToast('Ошибка загрузки логов', 'error');
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    loadLogs();
    // eslint-disable-next-line
  }, [userFilter, dateFilter]);

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Логи действий</h2>
      <div className="flex gap-4 mb-4">
        <input
          type="text"
          value={userFilter}
          onChange={e => setUserFilter(e.target.value)}
          placeholder="Пользователь"
          className="border rounded px-2 py-1"
        />
        <input
          type="date"
          value={dateFilter}
          onChange={e => setDateFilter(e.target.value)}
          className="border rounded px-2 py-1"
        />
        <button onClick={loadLogs} className="bg-blue-600 text-white px-3 py-1 rounded">Обновить</button>
      </div>
      {loading && <Spinner />}
      <table className="min-w-full bg-white rounded shadow">
        <thead>
          <tr>
            <th className="p-2">Дата</th>
            <th className="p-2">Пользователь</th>
            <th className="p-2">Действие</th>
            <th className="p-2">Детали</th>
          </tr>
        </thead>
        <tbody>
          {logs.map(log => (
            <tr key={log.id}>
              <td className="p-2">{new Date(log.timestamp).toLocaleString()}</td>
              <td className="p-2">{log.user}</td>
              <td className="p-2">{log.action}</td>
              <td className="p-2">{log.details}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

const RolesManager = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [newRoleName, setNewRoleName] = useState('');
  const [newRolePerms, setNewRolePerms] = useState<Permission[]>([]);
  const [confirmDelete, setConfirmDelete] = useState<number | null>(null);
  const toast = useToast();

  useEffect(() => {
    loadData();
    // eslint-disable-next-line
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      const [rolesData, usersData] = await Promise.all([fetchRoles(), fetchUsers()]);
      setRoles(rolesData);
      setUsers(usersData);
    } catch (e) {
      toast.showToast('Ошибка загрузки данных', 'error');
    } finally {
      setLoading(false);
    }
  }

  const openEdit = (role: Role) => {
    setEditingRole(role);
    setNewRoleName(role.name);
    setNewRolePerms(role.permissions);
    setModalOpen(true);
  };
  const openCreate = () => {
    setEditingRole(null);
    setNewRoleName('');
    setNewRolePerms([]);
    setModalOpen(true);
  };
  const closeModal = () => setModalOpen(false);

  const saveRole = async () => {
    if (!newRoleName.trim()) return;
    setLoading(true);
    try {
      if (editingRole) {
        await updateRole({ ...editingRole, name: newRoleName, permissions: newRolePerms });
        toast.showToast('Роль обновлена', 'success');
      } else {
        await createRole({ name: newRoleName, permissions: newRolePerms });
        toast.showToast('Роль создана', 'success');
      }
      setModalOpen(false);
      await loadData();
    } catch {
      toast.showToast('Ошибка сохранения роли', 'error');
    } finally {
      setLoading(false);
    }
  };
  const requestDelete = (id: number) => setConfirmDelete(id);
  const confirmDeleteRole = async () => {
    if (confirmDelete == null) return;
    if (users.some(u => u.role === roles.find(r => r.id === confirmDelete)?.name)) {
      toast.showToast('Нельзя удалить роль, назначенную пользователям', 'error');
      setConfirmDelete(null);
      return;
    }
    setLoading(true);
    try {
      await deleteRole(confirmDelete);
      toast.showToast('Роль удалена', 'success');
      await loadData();
    } catch {
      toast.showToast('Ошибка удаления роли', 'error');
    } finally {
      setLoading(false);
      setConfirmDelete(null);
    }
  };
  const togglePerm = (perm: Permission) => {
    setNewRolePerms(perms => perms.includes(perm) ? perms.filter(p => p !== perm) : [...perms, perm]);
  };

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Роли и права</h2>
      <button onClick={openCreate} className="mb-4 bg-blue-600 text-white px-4 py-2 rounded">Создать роль</button>
      {loading && <Spinner />}
      <table className="min-w-full bg-white rounded shadow mb-6">
        <thead>
          <tr>
            <th className="p-2">Название</th>
            <th className="p-2">Права</th>
            <th className="p-2">Действия</th>
          </tr>
        </thead>
        <tbody>
          {roles.map(role => (
            <tr key={role.id}>
              <td className="p-2 font-bold">{role.name}</td>
              <td className="p-2 text-xs">
                {role.permissions.map(p => PERMISSIONS.find(pp => pp.key === p)?.label).join(', ')}
              </td>
              <td className="p-2">
                <button onClick={() => openEdit(role)} className="text-blue-600 hover:underline mr-2">Редактировать</button>
                <button onClick={() => requestDelete(role.id)} className="text-red-600 hover:underline">Удалить</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {modalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
          <div className="bg-white rounded shadow-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-bold mb-4">{editingRole ? 'Редактировать роль' : 'Создать роль'}</h3>
            <input value={newRoleName} onChange={e => setNewRoleName(e.target.value)} placeholder="Название роли" className="border rounded px-2 py-1 w-full mb-4" />
            <div className="mb-4">
              <div className="font-semibold mb-2">Права:</div>
              {PERMISSIONS.map(perm => (
                <label key={perm.key} className="block text-sm mb-1">
                  <input type="checkbox" checked={newRolePerms.includes(perm.key)} onChange={() => togglePerm(perm.key)} className="mr-2" />
                  {perm.label}
                </label>
              ))}
            </div>
            <div className="flex gap-2 justify-end">
              <button onClick={closeModal} className="px-4 py-2">Отмена</button>
              <button onClick={saveRole} className="bg-blue-600 text-white px-4 py-2 rounded">Сохранить</button>
            </div>
          </div>
        </div>
      )}
      {confirmDelete !== null && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white rounded shadow-lg p-6 w-full max-w-sm">
            <div className="mb-4">Вы уверены, что хотите удалить эту роль?</div>
            <div className="flex gap-2 justify-end">
              <button onClick={() => setConfirmDelete(null)} className="px-4 py-2">Отмена</button>
              <button onClick={confirmDeleteRole} className="bg-red-600 text-white px-4 py-2 rounded">Удалить</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const UsersManager = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [confirmDelete, setConfirmDelete] = useState<number | null>(null);
  const toast = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
    // eslint-disable-next-line
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      const [usersData, rolesData] = await Promise.all([fetchUsers(), fetchRoles()]);
      setUsers(usersData);
      setRoles(rolesData);
    } catch (e) {
      toast.showToast('Ошибка загрузки пользователей', 'error');
    } finally {
      setLoading(false);
    }
  }

  const handleDeleteUser = async (userId: number) => {
    setLoading(true);
    try {
      await deleteUser(userId);
      toast.showToast('Пользователь удалён', 'success');
      await loadData();
    } catch {
      toast.showToast('Ошибка удаления пользователя', 'error');
    } finally {
      setLoading(false);
      setConfirmDelete(null);
    }
  };

  const handleChangeRole = async (userId: number, roleId: number) => {
    setLoading(true);
    try {
      const role = roles.find(r => r.id === roleId);
      if (!role) return;
      await changeUserRole(userId, role.name);
      toast.showToast('Роль пользователя изменена', 'success');
      await loadData();
    } catch {
      toast.showToast('Ошибка смены роли', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
      {loading && <Spinner />}
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Имя пользователя</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Роль</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Последний вход</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Действия</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {users.map((user) => (
            <tr key={user.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{user.username}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{user.email}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <select value={roles.find(r => r.name === user.role)?.id || ''} onChange={e => handleChangeRole(user.id, Number(e.target.value))} className="border rounded px-2 py-1">
                  <option value="">Не выбрано</option>
                  {roles.map(role => (
                    <option key={role.id} value={role.id}>{role.name}</option>
                  ))}
                </select>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(user.last_login).toLocaleString()}</td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button onClick={() => setConfirmDelete(user.id)} className="text-red-600 hover:text-red-900">Удалить</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {confirmDelete !== null && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white rounded shadow-lg p-6 w-full max-w-sm">
            <div className="mb-4">Вы уверены, что хотите удалить этого пользователя?</div>
            <div className="flex gap-2 justify-end">
              <button onClick={() => setConfirmDelete(null)} className="px-4 py-2">Отмена</button>
              <button onClick={() => handleDeleteUser(confirmDelete)} className="bg-red-600 text-white px-4 py-2 rounded">Удалить</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const AdminPanel: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [roles, setRoles] = useState<Role[]>([]);
  const [userRole, setUserRole] = useState<Role | undefined>(undefined);

  useEffect(() => {
    // Получить роли (из API или локально)
    const loadedRoles = [
      { id: 1, name: 'Администратор', permissions: PERMISSIONS.map(p => p.key) },
      { id: 2, name: 'Менеджер', permissions: ['view_dashboard','manage_bookings','view_bookings','manage_reviews','view_reviews','export_data','view_logs','manage_services'] },
      { id: 3, name: 'Оператор', permissions: ['manage_bookings','view_bookings'] },
      { id: 4, name: 'Маркетолог', permissions: ['view_dashboard','view_reviews','manage_reviews','export_data'] },
    ];
    setRoles(loadedRoles);
    setUserRole(getCurrentUserRole(loadedRoles));
  }, []);

  // Массив вкладок с нужными правами
  const TABS = [
    { key: 'dashboard', label: 'Аналитика', perm: 'view_dashboard' },
    { key: 'bookings', label: 'Бронирования', perm: 'view_bookings' },
    { key: 'reviews', label: 'Отзывы', perm: 'view_reviews' },
    { key: 'export', label: 'Экспорт', perm: 'export_data' },
    { key: 'logs', label: 'Логи', perm: 'view_logs' },
    { key: 'roles', label: 'Роли и права', perm: 'manage_roles' },
    { key: 'users', label: 'Пользователи', perm: 'manage_users' }
  ];

  // Фильтруем вкладки по правам
  const visibleTabs = TABS.filter(tab => hasPermission(userRole, tab.perm as Permission));

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Панель администратора</h1>
          <Tab.Group selectedIndex={selectedTab} onChange={setSelectedTab}>
            <Tab.List className="flex space-x-1 rounded-xl bg-blue-900/20 p-1 mb-8">
              {visibleTabs.map((t) => (
                <Tab key={t.key} className={({ selected }) =>
                `w-full rounded-lg py-2.5 text-sm font-medium leading-5
                   ${selected ? 'bg-white text-blue-700 shadow' : 'text-blue-100 hover:bg-white/[0.12] hover:text-white'}`
              }>
                  {t.label}
              </Tab>
              ))}
            </Tab.List>
            <Tab.Panels>
              {visibleTabs.map(tab => {
                switch (tab.key) {
                  case 'dashboard': return <Tab.Panel key={tab.key}><Dashboard /></Tab.Panel>;
                  case 'bookings': return <Tab.Panel key={tab.key}><BookingsManager /></Tab.Panel>;
                  case 'reviews': return <Tab.Panel key={tab.key}><ReviewsManager /></Tab.Panel>;
                  case 'export': return <Tab.Panel key={tab.key}><ExportPanel /></Tab.Panel>;
                  case 'logs': return <Tab.Panel key={tab.key}><LogsViewer /></Tab.Panel>;
                  case 'roles': return <Tab.Panel key={tab.key}><RolesManager /></Tab.Panel>;
                  case 'users': return <Tab.Panel key={tab.key}><UsersManager /></Tab.Panel>;
                  default: return null;
                }
              })}
            </Tab.Panels>
          </Tab.Group>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel; 