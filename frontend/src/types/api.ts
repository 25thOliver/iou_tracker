export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
}

export interface LoginCredentials {
  username_or_email: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name?: string;
  last_name?: string;
}

export interface AuthResponse {
  user: User;
  token?: string;
  access?: string;
  refresh?: string;
}

export interface IOU {
  id: number;
  amount: number;
  description: string;
  debtor: string;
  creditor: string;
  due_date: string;
  created_at: string;
  updated_at: string;
  status: "pending" | "paid" | "cancelled";
  is_owed_to_me: boolean;
}

export interface IOUCreate {
  amount: number;
  description: string;
  debtor: string;
  creditor: string;
  due_date: string;
}

export interface Debt {
  id: number;
  amount: number;
  description: string;
  debtor: string;
  creditor: string;
  due_date: string;
  created_at: string;
  updated_at: string;
  status: "pending" | "paid" | "cancelled";
  is_owed_to_me: boolean;
}

export interface DebtCreate {
  amount: number;
  description: string;
  debtor: string;
  creditor: string;
  due_date: string;
}

export interface Notification {
  id: number;
  title: string;
  message: string;
  read: boolean;
  created_at: string;
  notification_type:
    | "iou_created"
    | "iou_updated"
    | "debt_created"
    | "debt_updated"
    | "payment_reminder";
  related_object_id?: number;
}

export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
  status: number;
}
