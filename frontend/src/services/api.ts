import axios, { AxiosResponse } from "axios";
import type {
  User,
  LoginCredentials,
  RegisterData,
  AuthResponse,
  IOU,
  IOUCreate,
  Debt,
  DebtCreate,
  Notification,
  ApiError,
} from "@/types/api";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("auth_token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

// Authentication API
export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response: AxiosResponse<AuthResponse> = await api.post(
      "/auth/login/",
      credentials,
    );
    if (response.data.token || response.data.access) {
      const token = response.data.token || response.data.access;
      localStorage.setItem("auth_token", token!);
      localStorage.setItem("user", JSON.stringify(response.data.user));
    }
    return response.data;
  },

  register: async (data: RegisterData): Promise<AuthResponse> => {
    const response: AxiosResponse<AuthResponse> = await api.post(
      "/auth/register/",
      data,
    );
    if (response.data.token || response.data.access) {
      const token = response.data.token || response.data.access;
      localStorage.setItem("auth_token", token!);
      localStorage.setItem("user", JSON.stringify(response.data.user));
    }
    return response.data;
  },

  logout: async (): Promise<void> => {
    try {
      await api.post("/auth/logout/");
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      localStorage.removeItem("auth_token");
      localStorage.removeItem("user");
    }
  },

  getCurrentUser: async (): Promise<User> => {
    const response: AxiosResponse<User> = await api.get("/auth/profile/");
    return response.data;
  },
};

// IOU API
export const iouApi = {
  getAll: async (): Promise<PaginatedResponse<IOU[]>> => {
    const response: AxiosResponse<PaginatedResponse<IOU[]>> =
      await api.get("/ious/");
    return response.data;
  },

  getById: async (id: string): Promise<IOU> => {
    const response: AxiosResponse<IOU> = await api.get(`/ious/${id}/`);
    return response.data;
  },

  create: async (data: IOUCreate): Promise<IOU> => {
    const response: AxiosResponse<IOU> = await api.post("/ious/", data);
    return response.data;
  },

  update: async (id: string, data: Partial<IOUCreate>): Promise<IOU> => {
    const response: AxiosResponse<IOU> = await api.patch(`/ious/${id}/`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/ious/${id}/`);
  },
};

// Debt API
export const debtApi = {
  getAll: async (): Promise<PaginatedResponse<Debt[]>> => {
    const response: AxiosResponse<PaginatedResponse<Debt[]>> =
      await api.get("/debts/");
    return response.data;
  },

  getAllWithSearch: async (search: string): Promise<PaginatedResponse<Debt[]>> => {
    const response: AxiosResponse<PaginatedResponse<Debt[]>> =
      await api.get("/debts/", { params: { search } });
    return response.data;
  },

  getById: async (id: string): Promise<Debt> => {
    const response: AxiosResponse<Debt> = await api.get(`/debts/${id}/`);
    return response.data;
  },

  create: async (data: DebtCreate): Promise<Debt> => {
    const response: AxiosResponse<Debt> = await api.post("/debts/", data);
    return response.data;
  },

  update: async (id: string, data: Partial<DebtCreate>): Promise<Debt> => {
    const response: AxiosResponse<Debt> = await api.patch(
      `/debts/${id}/`,
      data,
    );
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/debts/${id}/`);
  },
};

// Notifications API
export const notificationApi = {
  getAll: async (): Promise<Notification[]> => {
    const response: AxiosResponse<Notification[]> =
      await api.get("/notifications/");
    return response.data;
  },

  markAsRead: async (id: string): Promise<Notification> => {
    const response: AxiosResponse<Notification> = await api.patch(
      `/notifications/${id}/`,
      { read: true },
    );
    return response.data;
  },
};

export default api;
