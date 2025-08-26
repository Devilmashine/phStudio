import React, { useState, useEffect, useCallback } from 'react';
import userService from '../../services/userService';
import AdminTable from './AdminTable';
import AdminForm from './AdminForm';
import SearchFilter from './SearchFilter';
import { UserRole } from '../../models/user.type';

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
}

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [filteredUsers, setFilteredUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      const response = await userService.getUsers();
      setUsers(response.data);
      setFilteredUsers(response.data);
    } catch (err) {
      setError('Failed to fetch users.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleSearch = (query: string) => {
    if (!query) {
      setFilteredUsers(users);
      return;
    }
    
    const filtered = users.filter(user => 
      user.username.toLowerCase().includes(query.toLowerCase()) ||
      user.email.toLowerCase().includes(query.toLowerCase()) ||
      user.full_name.toLowerCase().includes(query.toLowerCase())
    );
    
    setFilteredUsers(filtered);
  };

  const handleFilter = (filters: Record<string, any>) => {
    let result = [...users];
    
    if (filters.role) {
      result = result.filter(user => user.role === filters.role);
    }
    
    setFilteredUsers(result);
  };

  const handleAddUser = () => {
    setEditingUser(null);
    setIsModalOpen(true);
  };

  const handleEditUser = (user: User) => {
    setEditingUser(user);
    setIsModalOpen(true);
  };

  const handleDeleteUser = async (user: User) => {
    if (window.confirm('Вы уверены, что хотите удалить этого пользователя?')) {
      try {
        await userService.deleteUser(user.id);
        fetchUsers(); // Refresh the list
      } catch (err) {
        setError('Failed to delete user.');
        console.error(err);
      }
    }
  };

  const handleSaveUser = async (userData: Record<string, any>) => {
    try {
      const user = userData as User;
      if (editingUser) {
        await userService.updateUser(editingUser.id, user);
      } else {
        await userService.createUser(user);
      }
      fetchUsers(); // Refresh the list
      setIsModalOpen(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save user.');
      console.error(err);
    }
  };

  const userFields = [
    { name: 'username', label: 'Имя пользователя', type: 'text', required: true },
    { name: 'email', label: 'Email', type: 'email', required: true },
    { name: 'full_name', label: 'Полное имя', type: 'text' },
    { 
      name: 'role', 
      label: 'Роль', 
      type: 'select', 
      required: true,
      options: [
        { value: UserRole.User, label: 'Пользователь' },
        { value: UserRole.Manager, label: 'Менеджер' },
        { value: UserRole.Admin, label: 'Администратор' }
      ]
    },
    { name: 'password', label: 'Пароль', type: 'password', required: false }
  ];

  const userColumns = [
    { key: 'id', title: 'ID' },
    { key: 'username', title: 'Имя пользователя' },
    { key: 'email', title: 'Email' },
    { key: 'full_name', title: 'Полное имя' },
    { 
      key: 'role', 
      title: 'Роль',
      render: (value: UserRole) => {
        switch (value) {
          case UserRole.Admin: return 'Администратор';
          case UserRole.Manager: return 'Менеджер';
          case UserRole.User: return 'Пользователь';
          default: return value;
        }
      }
    }
  ];

  const filterOptions = [
    {
      key: 'role',
      label: 'Роль',
      type: 'select',
      options: [
        { value: UserRole.User, label: 'Пользователь' },
        { value: UserRole.Manager, label: 'Менеджер' },
        { value: UserRole.Admin, label: 'Администратор' }
      ]
    }
  ];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md bg-red-50 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Ошибка</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Управление пользователями</h1>
          <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
            Список всех пользователей системы и управление ими.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            type="button"
            onClick={handleAddUser}
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto"
          >
            Добавить пользователя
          </button>
        </div>
      </div>

      <SearchFilter 
        onSearch={handleSearch} 
        onFilter={handleFilter}
        placeholder="Поиск пользователей..."
        filters={filterOptions}
      />

      <AdminTable
        columns={userColumns}
        data={filteredUsers}
        onEdit={handleEditUser}
        onDelete={handleDeleteUser}
      />

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full max-h-screen overflow-y-auto">
            <div className="px-4 py-5 sm:px-6 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                {editingUser ? 'Редактировать пользователя' : 'Добавить пользователя'}
              </h3>
            </div>
            <div className="px-4 py-5 sm:p-6">
              <AdminForm
                fields={userFields}
                initialValues={editingUser || {}}
                onSubmit={handleSaveUser}
                onCancel={() => setIsModalOpen(false)}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagement;