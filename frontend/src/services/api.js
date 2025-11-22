import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const productAPI = {
  getAll: () => api.get('/products'),
  getById: (id) => api.get(`/products/${id}`),
  getReviews: (id, tab = 'positive', includeShadow = false) => 
    api.get(`/products/${id}/reviews/public?tab=${tab}&include_shadow=${includeShadow}`),
  getRating: (id) => api.get(`/products/${id}/rating`),
}

export const reviewAPI = {
  submit: (data) => api.post('/reviews', data),
}

export const adminAPI = {
  getAllReviews: (skip = 0, limit = 50) => api.get(`/admin/reviews/all?skip=${skip}&limit=${limit}`),
  getShadowReviews: () => api.get('/admin/reviews/shadow'),
  getRejectedReviews: () => api.get('/admin/reviews/rejected'),
  getReviewDetail: (id) => api.get(`/admin/reviews/${id}`),
  getSupportTickets: (status = null) => {
    const url = status ? `/admin/support?status=${status}` : '/admin/support'
    return api.get(url)
  },
  assignTicket: (ticketId, assignedTo) => api.post(`/admin/tickets/${ticketId}/assign`, { assigned_to: assignedTo }),
  overrideReview: (reviewId, data) => api.post(`/admin/reviews/${reviewId}/override`, data),
}

export default api
