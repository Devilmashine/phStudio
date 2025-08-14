import api from './api';

const API_URL = '/api/auth/users';

const getUsers = () => {
  return api.get(API_URL);
};

const createUser = (userData) => {
  return api.post(API_URL, userData);
};

const updateUser = (userId, userData) => {
  return api.put(`${API_URL}/${userId}`, userData);
};

const deleteUser = (userId) => {
  return api.delete(`${API_URL}/${userId}`);
};

const userService = {
  getUsers,
  createUser,
  updateUser,
  deleteUser,
};

export default userService;
