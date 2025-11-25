import apiClient from './client';

export interface LoginData {
  username: string;
  password: string;
}

export interface User {
  id: number;
  username: string;
  email: string | null;
  role: string;
  quota: number;
  created_at: string;
  last_login: string | null;
  theme: string;
  language: string;
  accent_color: string;
  icon_size: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export const authApi = {
  login: async (data: LoginData): Promise<TokenResponse> => {
    const response = await apiClient.post('/api/auth/login', data);
    return response.data;
  },

  register: async (data: LoginData & { email?: string }): Promise<User> => {
    const response = await apiClient.post('/api/auth/register', data);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/api/auth/logout');
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get('/api/auth/me');
    return response.data;
  },

  changePassword: async (oldPassword: string, newPassword: string): Promise<void> => {
    await apiClient.put('/api/auth/password', {
      old_password: oldPassword,
      new_password: newPassword,
    });
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await apiClient.put('/api/auth/profile', data);
    return response.data;
  },

  updateSettings: async (settings: Partial<User>): Promise<User> => {
    const response = await apiClient.put('/api/auth/settings', settings);
    return response.data;
  },
};
