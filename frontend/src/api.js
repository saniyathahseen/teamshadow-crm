import axios from 'axios';

// Use relative path so it works with both local dev and Docker (nginx proxy)
const API_BASE = process.env.REACT_APP_API_URL || '/api';

const API = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' }
});

// Add auth token to requests
API.interceptors.request.use(config => {
  const token = localStorage.getItem('ts_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
API.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('ts_token');
      localStorage.removeItem('ts_user');
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

// ============================================
// Auth
// ============================================
export const login = async (username, password) => {
  const { data } = await API.post('/auth/login', { username, password });
  localStorage.setItem('ts_token', data.access_token);
  localStorage.setItem('ts_user', JSON.stringify(data.user));
  return data;
};

export const logout = () => {
  localStorage.removeItem('ts_token');
  localStorage.removeItem('ts_user');
  window.location.reload();
};

// ============================================
// Dashboard
// ============================================
export const getDashboard = () => API.get('/dashboard').then(r => r.data);

// ============================================
// Customers
// ============================================
export const getCustomers = (search) => API.get(`/customers${search ? `?search=${search}` : ''}`).then(r => r.data);
export const createCustomer = (data) => API.post('/customers', data).then(r => r.data);
export const getCustomer = (id) => API.get(`/customers/${id}`).then(r => r.data);
export const updateCustomer = (id, data) => API.put(`/customers/${id}`, data).then(r => r.data);
export const deleteCustomer = (id) => API.delete(`/customers/${id}`).then(r => r.data);

// ============================================
// Inquiries
// ============================================
export const getInquiries = (params) => API.get('/inquiries', { params }).then(r => r.data);
export const createInquiry = (data) => API.post('/inquiries', data).then(r => r.data);
export const updateInquiry = (id, data) => API.put(`/inquiries/${id}`, data).then(r => r.data);
export const deleteInquiry = (id) => API.delete(`/inquiries/${id}`).then(r => r.data);

// ============================================
// Quotations
// ============================================
export const getQuotations = () => API.get('/quotations').then(r => r.data);
export const createQuotation = (data) => API.post('/quotations', data).then(r => r.data);
export const updateQuotation = (id, data) => API.put(`/quotations/${id}`, data).then(r => r.data);
export const deleteQuotation = (id) => API.delete(`/quotations/${id}`).then(r => r.data);
export const sendQuotation = (id) => API.put(`/quotations/${id}/send`).then(r => r.data);

// ============================================
// Bookings
// ============================================
export const getBookings = () => API.get('/bookings').then(r => r.data);
export const createBooking = (data) => API.post('/bookings', data).then(r => r.data);
export const updateBooking = (id, data) => API.put(`/bookings/${id}`, data).then(r => r.data);
export const deleteBooking = (id) => API.delete(`/bookings/${id}`).then(r => r.data);
export const updateBookingStatus = (id, status) => API.put(`/bookings/${id}/status?status=${status}`).then(r => r.data);

// ============================================
// Payments
// ============================================
export const getPayments = (bookingId) => API.get(`/payments${bookingId ? `?booking_id=${bookingId}` : ''}`).then(r => r.data);
export const createPayment = (data) => API.post('/payments', data).then(r => r.data);
export const updatePayment = (id, data) => API.put(`/payments/${id}`, data).then(r => r.data);
export const deletePayment = (id) => API.delete(`/payments/${id}`).then(r => r.data);

// ============================================
// Staff
// ============================================
export const getStaff = () => API.get('/staff').then(r => r.data);
export const createStaff = (data) => API.post('/staff', data).then(r => r.data);
export const updateStaff = (id, data) => API.put(`/staff/${id}`, data).then(r => r.data);
export const deleteStaff = (id) => API.delete(`/staff/${id}`).then(r => r.data);

// ============================================
// Editing Projects
// ============================================
export const getEditingProjects = () => API.get('/editing-projects').then(r => r.data);
export const createEditingProject = (data) => API.post('/editing-projects', data).then(r => r.data);
export const updateEditingProject = (id, data) => API.put(`/editing-projects/${id}`, data).then(r => r.data);
export const deleteEditingProject = (id) => API.delete(`/editing-projects/${id}`).then(r => r.data);
export const updateEditingStatus = (id, status) => API.put(`/editing-projects/${id}/status?status=${status}`).then(r => r.data);

// ============================================
// Users (Admin)
// ============================================
export const getUsers = () => API.get('/users').then(r => r.data);
export const createUser = (data) => API.post('/users', data).then(r => r.data);

// ============================================
// Tasks
// ============================================
export const getTasks = (params) => API.get('/tasks', { params }).then(r => r.data);
export const createTask = (data) => API.post('/tasks', data).then(r => r.data);
export const updateTask = (id, data) => API.put(`/tasks/${id}`, data).then(r => r.data);
export const staffUpdateTask = (id, data) => API.post(`/tasks/${id}/update`, data).then(r => r.data);
export const deleteTask = (id) => API.delete(`/tasks/${id}`).then(r => r.data);

// ============================================
// Leads (WhatsApp Inbox)
// ============================================
export const getLeads = (params) => API.get('/leads', { params }).then(r => r.data);
export const getLead = (id) => API.get(`/lead/${id}`).then(r => r.data);
export const updateLead = (id, data) => API.patch(`/lead/${id}`, data).then(r => r.data);
export const sendLeadMessage = (data) => API.post('/send-message', data).then(r => r.data);
export const exportLead = (id) => API.get(`/lead/${id}/export`).then(r => r.data);

// ============================================
// Activity
// ============================================
export const getActivity = () => API.get('/activity').then(r => r.data);

// ============================================
// Deliverables
// ============================================
export const getDeliverables = (bookingId) => API.get(`/deliverables${bookingId ? `?booking_id=${bookingId}` : ''}`).then(r => r.data);
export const createDeliverable = (data) => API.post('/deliverables', data).then(r => r.data);

// ============================================
// Expenses
// ============================================
export const getExpenses = (bookingId) => API.get(`/expenses${bookingId ? `?booking_id=${bookingId}` : ''}`).then(r => r.data);
export const createExpense = (data) => API.post('/expenses', data).then(r => r.data);

export default API;