import React, { useEffect, useState } from 'react'
import { productAPI } from '../services/api'

function ReviewTabs({ productId, refreshTrigger }) {
  const [activeTab, setActiveTab] = useState('positive')
  const [reviews, setReviews] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadReviews()
  }, [productId, activeTab, refreshTrigger])

  const loadReviews = async () => {
    setLoading(true)
    try {
      const response = await productAPI.getReviews(productId, activeTab)
      setReviews(response.data.reviews)
      setSummary(response.data.summary)
    } catch (error) {
      console.error('Error loading reviews:', error)
    } finally {
      setLoading(false)
    }
  }

  const tabs = [
    { key: 'positive', label: 'Positive Reviews', color: 'green' },
    { key: 'negative', label: 'Negative Reviews', color: 'red' },
    { key: 'shadow', label: 'Shadow Reviews', color: 'gray' },
  ]

  return (
    <div>
      <h2 className="text-3xl font-bold text-gray-900 mb-6">
        Customer Reviews
      </h2>

      <div className="mb-6 border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`pb-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.key
                  ? `border-${tab.color}-500 text-${tab.color}-600`
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {summary && activeTab === 'negative' && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <h3 className="text-lg font-semibold text-red-900 mb-2">
            {summary.title} ({summary.count})
          </h3>
          <ul className="list-disc list-inside space-y-1">
            {summary.top_issues.map((issue, index) => (
              <li key={index} className="text-red-800 text-sm">
                {issue}
              </li>
            ))}
          </ul>
        </div>
      )}

      {loading ? (
        <div className="text-center py-8">
          <div className="text-gray-600">Loading reviews...</div>
        </div>
      ) : reviews.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-gray-500">No reviews in this category yet.</div>
        </div>
      ) : (
        <div className="space-y-6">
          {reviews.map((review) => (
            <div key={review.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="font-semibold text-gray-900">
                      {review.reviewer_name}
                    </span>
                    {review.is_verified_purchase && (
                      <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                        Verified Purchase
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="text-yellow-500">
                      {'⭐'.repeat(review.rating)}
                    </div>
                    <span className="text-sm text-gray-500">
                      {new Date(review.submitted_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                <div className="text-sm text-gray-500">
                  Score: {review.value_score.toFixed(1)}
                </div>
              </div>

              <p className="text-gray-700 mb-3">{review.review_text}</p>

              {review.automatic_response && (
                <div className="mt-4 pl-4 border-l-4 border-blue-500 bg-blue-50 p-3 rounded">
                  <p className="text-sm font-medium text-blue-900 mb-1">
                    Store Response:
                  </p>
                  <p className="text-sm text-blue-800">
                    {review.automatic_response}
                  </p>
                </div>
              )}

              <div className="mt-4 flex items-center space-x-4 text-sm">
                <button className="text-gray-600 hover:text-blue-600">
                  Helpful ({review.helpful_count})
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ReviewTabs
