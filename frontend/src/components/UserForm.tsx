import React, { useState, useEffect } from 'react';
import { UserRole } from '../models/user.type'; // Assuming you have this type defined

interface User {
  id?: number;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  password?: string;
}

interface UserFormProps {
  user: User | null;
  onSave: (user: User) => void;
  onCancel: () => void;
}

const UserForm: React.FC<UserFormProps> = ({ user, onSave, onCancel }) => {
  const [formData, setFormData] = useState<User>({
    username: '',
    email: '',
    full_name: '',
    role: UserRole.User,
    password: '',
  });

  useEffect(() => {
    if (user) {
      setFormData(user);
    }
  }, [user]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
      <div className="bg-white p-6 rounded-lg shadow-xl w-full max-w-md">
        <h2 className="text-2xl font-bold mb-4">{user ? 'Edit User' : 'Add User'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700">Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded"
              required
            />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700">Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded"
              required
            />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700">Full Name</label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded"
            />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700">Role</label>
            <select
              name="role"
              value={formData.role}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded"
            >
              <option value={UserRole.User}>User</option>
              <option value={UserRole.Manager}>Manager</option>
              <option value={UserRole.Admin}>Admin</option>
            </select>
          </div>
          <div className="mb-4">
            <label className="block text-gray-700">Password</label>
            <input
              type="password"
              name="password"
              value={formData.password || ''}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded"
              placeholder={user ? 'Leave blank to keep unchanged' : ''}
            />
          </div>
          <div className="flex justify-end gap-4">
            <button
              type="button"
              onClick={onCancel}
              className="bg-gray-300 text-gray-800 px-4 py-2 rounded hover:bg-gray-400"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Save
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UserForm;
