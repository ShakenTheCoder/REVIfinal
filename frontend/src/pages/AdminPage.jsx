import React, { useEffect, useState } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { adminAPI } from '../services/api'

function AdminPage() {
  const location = useLocation()

  const tabs = [
    { path: '/admin', label: 'All Reviews' },
    { path: '/admin/shadow', label: 'Shadow Reviews' },
    { path: '/admin/rejected', label: 'Rejected Reviews' },
    { path: '/admin/support', label: 'Support Tickets' },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Admin Panel
        </h1>
        <p className="text-gray-600">
          Manage reviews and support tickets
        </p>
      </div>

      <div className="mb-6 border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <Link
              key={tab.path}
              to={tab.path}
              className={`pb-4 px-1 border-b-2 font-medium text-sm ${
                location.pathname === tab.path
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </Link>
          ))}
        </nav>
      </div>

      <Routes>
        <Route path="/" element={<AllReviewsTab />} />
        <Route path="/shadow" element={<ShadowReviewsTab />} />
        <Route path="/rejected" element={<RejectedReviewsTab />} />
        <Route path="/support" element={<SupportTicketsTab />} />
      </Routes>
    </div>
  )
}

function AllReviewsTab() {
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)

  useEffect(() => {
    loadReviews()
  }, [])

  const loadReviews = async () => {
    try {
      const response = await adminAPI.getAllReviews()
      setReviews(response.data.reviews)
      setTotal(response.data.total)
    } catch (error) {
      console.error('Error loading reviews:', error)
    } finally {
      setLoading(false)
    }
  }

  const getCategoryColor = (category) => {
    const colors = {
      public_positive: 'bg-green-100 text-green-800',
      public_negative: 'bg-red-100 text-red-800',
      support: 'bg-yellow-100 text-yellow-800',
      shadow: 'bg-gray-100 text-gray-800',
      rejected: 'bg-red-100 text-red-800',
    }
    return colors[category] || 'bg-gray-100 text-gray-800'
  }

  if (loading) {
    return <div className="text-center py-8">Loading reviews...</div>
  }

  return (
    <div>
      <div className="mb-4 text-sm text-gray-600">
        Total reviews: {total}
      </div>

      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Reviewer
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Rating
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Review
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Category
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Score
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {reviews.map((review) => (
              <tr key={review.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {review.reviewer_name}
                  </div>
                  <div className="text-sm text-gray-500">
                    {review.reviewer_email}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-yellow-500">
                    {'⭐'.repeat(review.rating)}
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900 max-w-md truncate">
                    {review.review_text}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {review.category && (
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getCategoryColor(review.category)}`}>
                      {review.category}
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {review.value_score ? review.value_score.toFixed(1) : 'N/A'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(review.submitted_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function ShadowReviewsTab() {
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadReviews()
  }, [])

  const loadReviews = async () => {
    try {
      const response = await adminAPI.getShadowReviews()
      setReviews(response.data.reviews)
    } catch (error) {
      console.error('Error loading shadow reviews:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading shadow reviews...</div>
  }

  return (
    <div>
      <div className="mb-4 text-sm text-gray-600">
        Total shadow reviews: {reviews.length}
      </div>

      <div className="space-y-4">
        {reviews.map((review) => (
          <div key={review.id} className="bg-white shadow-md rounded-lg p-6">
            <div className="flex justify-between items-start mb-3">
              <div>
                <div className="font-semibold text-gray-900">
                  {review.reviewer_name}
                </div>
                <div className="text-sm text-yellow-500">
                  {'⭐'.repeat(review.rating)}
                </div>
              </div>
              <span className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded">
                Shadow
              </span>
            </div>
            <p className="text-gray-700 mb-2">{review.review_text}</p>
            <p className="text-sm text-gray-500 italic">{review.reason}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

function RejectedReviewsTab() {
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadReviews()
  }, [])

  const loadReviews = async () => {
    try {
      const response = await adminAPI.getRejectedReviews()
      setReviews(response.data.reviews)
    } catch (error) {
      console.error('Error loading rejected reviews:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading rejected reviews...</div>
  }

  return (
    <div>
      <div className="mb-4 text-sm text-gray-600">
        Total rejected reviews: {reviews.length}
      </div>

      <div className="space-y-4">
        {reviews.map((review) => (
          <div key={review.id} className="bg-white shadow-md rounded-lg p-6">
            <div className="flex justify-between items-start mb-3">
              <div>
                <div className="font-semibold text-gray-900">
                  {review.reviewer_name}
                </div>
                <div className="text-sm text-yellow-500">
                  {'⭐'.repeat(review.rating)}
                </div>
              </div>
              <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                Rejected
              </span>
            </div>
            <p className="text-gray-700 mb-2">{review.review_text}</p>
            <div className="mt-3 p-3 bg-red-50 rounded">
              <p className="text-sm font-medium text-red-900">Rejection Reason:</p>
              <p className="text-sm text-red-800">{review.reason}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function SupportTicketsTab() {
  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTickets()
  }, [])

  const loadTickets = async () => {
    try {
      const response = await adminAPI.getSupportTickets()
      setTickets(response.data.tickets)
    } catch (error) {
      console.error('Error loading tickets:', error)
    } finally {
      setLoading(false)
    }
  }

  const getPriorityColor = (priority) => {
    const colors = {
      high: 'bg-red-100 text-red-800',
      normal: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800',
    }
    return colors[priority] || 'bg-gray-100 text-gray-800'
  }

  const getStatusColor = (status) => {
    const colors = {
      open: 'bg-blue-100 text-blue-800',
      assigned: 'bg-purple-100 text-purple-800',
      resolved: 'bg-green-100 text-green-800',
      closed: 'bg-gray-100 text-gray-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  if (loading) {
    return <div className="text-center py-8">Loading tickets...</div>
  }

  return (
    <div>
      <div className="mb-4 text-sm text-gray-600">
        Total tickets: {tickets.length}
      </div>

      <div className="space-y-4">
        {tickets.map((ticket) => (
          <div key={ticket.id} className="bg-white shadow-md rounded-lg p-6">
            <div className="flex justify-between items-start mb-3">
              <div>
                <div className="font-semibold text-gray-900">
                  Ticket #{ticket.id.slice(0, 8)}
                </div>
                <div className="text-sm text-gray-600">
                  {ticket.customer_email}
                </div>
              </div>
              <div className="flex space-x-2">
                <span className={`text-xs px-2 py-1 rounded ${getPriorityColor(ticket.priority)}`}>
                  {ticket.priority}
                </span>
                <span className={`text-xs px-2 py-1 rounded ${getStatusColor(ticket.status)}`}>
                  {ticket.status}
                </span>
              </div>
            </div>
            <p className="text-gray-700 mb-3">{ticket.issue_description}</p>
            {ticket.assigned_to && (
              <p className="text-sm text-gray-600">
                Assigned to: <span className="font-medium">{ticket.assigned_to}</span>
              </p>
            )}
            <p className="text-xs text-gray-500 mt-2">
              Created: {new Date(ticket.created_at).toLocaleString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default AdminPage
