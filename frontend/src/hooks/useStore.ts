import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: number;
  email: string;
  full_name: string | null;
  role: 'citizen' | 'officer' | 'field_worker' | 'admin';
  ward_id: number | null;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      login: (token, user) => set({ token, user, isAuthenticated: true }),
      logout: () => set({ user: null, token: null, isAuthenticated: false }),
    }),
    {
      name: 'civicpulse-auth',
    }
  )
);

interface Report {
  id: number;
  title: string;
  description: string | null;
  latitude: number;
  longitude: number;
  category: string | null;
  severity: number;
  status: string;
  priority_score: number;
  ai_confidence: number;
  reporter_id: number;
  assignee_id: number | null;
  created_at: string;
  photo_before_url: string | null;
  photo_after_url: string | null;
}

interface ReportsState {
  reports: Report[];
  currentReport: Report | null;
  loading: boolean;
  error: string | null;
  setReports: (reports: Report[]) => void;
  setCurrentReport: (report: Report | null) => void;
  addReport: (report: Report) => void;
  updateReport: (report: Report) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useReportsStore = create<ReportsState>((set) => ({
  reports: [],
  currentReport: null,
  loading: false,
  error: null,
  setReports: (reports) => set({ reports }),
  setCurrentReport: (report) => set({ currentReport: report }),
  addReport: (report) => set((state) => ({ reports: [report, ...state.reports] })),
  updateReport: (report) =>
    set((state) => ({
      reports: state.reports.map((r) => (r.id === report.id ? report : r)),
      currentReport: state.currentReport?.id === report.id ? report : state.currentReport,
    })),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}));
