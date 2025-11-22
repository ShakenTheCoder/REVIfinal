import React, { useState } from 'react'
import { reviewAPI } from '../services/api'

function ReviewForm({ productId, onReviewSubmitted }) {
  const [formData, setFormData] = useState({
    reviewer_name: '',
    reviewer_email: '',
    rating: 5,
    review_text: '',
    is_verified_purchase: false,
  })
  const [submitting, setSubmitting] = useState(false)
  const [message, setMessage] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setMessage(null)

    try {
      const response = await reviewAPI.submit({
        product_id: productId,
        ...formData,
      })

      setMessage({
        type: 'success',
        text: response.data.message,
      })

      setFormData({
        reviewer_name: '',
        reviewer_email: '',
        rating: 5,
        review_text: '',
        is_verified_purchase: false,
      })

      if (onReviewSubmitted) {
        setTimeout(() => onReviewSubmitted(), 1000)
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to submit review',
      })
    } finally {
      setSubmitting(false)
    }
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        Write a Review
      </h2>

      {message && (
        <div
          className={`mb-6 p-4 rounded-md ${
            message.type === 'success'
              ? 'bg-green-50 text-green-800 border border-green-200'
              : 'bg-red-50 text-red-800 border border-red-200'
          }`}
        >
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="reviewer_name" className="block text-sm font-medium text-gray-700 mb-1">
              Name (optional)
            </label>
            <input
              type="text"
              id="reviewer_name"
              name="reviewer_name"
              value={formData.reviewer_name}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Your name"
            />
          </div>

          <div>
            <label htmlFor="reviewer_email" className="block text-sm font-medium text-gray-700 mb-1">
              Email (optional)
            </label>
            <input
              type="email"
              id="reviewer_email"
              name="reviewer_email"
              value={formData.reviewer_email}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="your@email.com"
            />
          </div>
        </div>

        <div>
          <label htmlFor="rating" className="block text-sm font-medium text-gray-700 mb-1">
            Rating
          </label>
          <select
            id="rating"
            name="rating"
            value={formData.rating}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value={5}>⭐⭐⭐⭐⭐ (5 stars)</option>
            <option value={4}>⭐⭐⭐⭐ (4 stars)</option>
            <option value={3}>⭐⭐⭐ (3 stars)</option>
            <option value={2}>⭐⭐ (2 stars)</option>
            <option value={1}>⭐ (1 star)</option>
          </select>
        </div>

        <div>
          <label htmlFor="review_text" className="block text-sm font-medium text-gray-700 mb-1">
            Review
          </label>
          <textarea
            id="review_text"
            name="review_text"
            value={formData.review_text}
            onChange={handleChange}
            rows={5}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Share your experience with this product..."
            required
          />
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="is_verified_purchase"
            name="is_verified_purchase"
            checked={formData.is_verified_purchase}
            onChange={handleChange}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="is_verified_purchase" className="ml-2 block text-sm text-gray-700">
            I am a verified purchaser
          </label>
        </div>

        <button
          type="submit"
          disabled={submitting}
          className={`w-full py-3 px-4 rounded-md font-semibold text-white ${
            submitting
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700'
          } transition-colors duration-200`}
        >
          {submitting ? 'Submitting...' : 'Submit Review'}
        </button>
      </form>
    </div>
  )
}

export default ReviewForm
