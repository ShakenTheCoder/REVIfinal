import React, { useEffect, useState } from 'react'
import { productAPI } from '../services/api'

function ReviewTabs({ productId, refreshTrigger }) {
  const [activeTab, setActiveTab] = useState('positive')
  const [reviews, setReviews] = useState([])
  const [insights, setInsights] = useState(null)
  const [loading, setLoading] = useState(true)
  const [includeShadow, setIncludeShadow] = useState(true)

  useEffect(() => {
    loadReviews()
  }, [productId, activeTab, refreshTrigger, includeShadow])

  const loadReviews = async () => {
    setLoading(true)
    try {
      const response = await productAPI.getReviews(productId, activeTab, includeShadow)
      setReviews(response.data.reviews)
      setInsights(response.data.insights)
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

      {activeTab !== 'shadow' && (
        <div className="mb-4 flex justify-between items-center">
          <label className="flex items-center space-x-2 text-sm text-gray-600">
            <input
              type="checkbox"
              checked={includeShadow}
              onChange={(e) => setIncludeShadow(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span>Include shadow-banned reviews (lower quality)</span>
          </label>
        </div>
      )}

      {insights && (activeTab === 'positive' || activeTab === 'negative') && (
        <div className={`mb-6 p-6 rounded-lg shadow-md ${
          activeTab === 'positive' 
            ? 'bg-green-50 border border-green-200' 
            : 'bg-red-50 border border-red-200'
        }`}>
          <div className="flex items-start space-x-3 mb-4">
            <div className={`text-2xl ${activeTab === 'positive' ? 'text-green-600' : 'text-red-600'}`}>
              🤖
            </div>
            <div className="flex-1">
              <h3 className={`text-xl font-bold mb-2 ${
                activeTab === 'positive' ? 'text-green-900' : 'text-red-900'
              }`}>
                AI Insights Summary
              </h3>
              <p className={`text-sm mb-3 ${
                activeTab === 'positive' ? 'text-green-800' : 'text-red-800'
              }`}>
                {insights.summary}
              </p>
            </div>
          </div>

          {insights.key_themes && insights.key_themes.length > 0 && (
            <div className="mb-4">
              <h4 className={`text-sm font-semibold mb-2 ${
                activeTab === 'positive' ? 'text-green-900' : 'text-red-900'
              }`}>
                Key Themes Mentioned:
              </h4>
              <div className="flex flex-wrap gap-2">
                {insights.key_themes.map((theme, index) => (
                  <span
                    key={index}
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      activeTab === 'positive'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {theme.name} ({theme.mentions})
                  </span>
                ))}
              </div>
            </div>
          )}

          {insights.common_points && insights.common_points.length > 0 && (
            <div>
              <h4 className={`text-sm font-semibold mb-2 ${
                activeTab === 'positive' ? 'text-green-900' : 'text-red-900'
              }`}>
                {activeTab === 'positive' ? 'Common Praise:' : 'Common Issues:'}
              </h4>
              <ul className="list-disc list-inside space-y-1">
                {insights.common_points.map((point, index) => (
                  <li key={index} className={`text-sm ${
                    activeTab === 'positive' ? 'text-green-800' : 'text-red-800'
                  }`}>
                    "{point}"
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-500">
            Based on {insights.review_count} reviews with avg. quality score of {insights.average_value_score}
          </div>
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
            <div 
              key={review.id} 
              className={`rounded-lg shadow-md p-6 ${
                review.is_shadow 
                  ? 'bg-gray-50 border-2 border-gray-300' 
                  : 'bg-white'
              }`}
            >
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
                    {review.is_shadow && (
                      <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">
                        Lower Quality
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
                <div className="text-sm">
                  <span className={`font-medium ${
                    review.value_score >= 70 ? 'text-green-600' :
                    review.value_score >= 50 ? 'text-yellow-600' :
                    'text-gray-600'
                  }`}>
                    Quality: {review.value_score.toFixed(1)}
                  </span>
                </div>
              </div>

              <p className={`mb-3 ${review.is_shadow ? 'text-gray-600' : 'text-gray-700'}`}>
                {review.review_text}
              </p>

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
