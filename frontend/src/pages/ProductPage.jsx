import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { productAPI, reviewAPI } from '../services/api'
import ReviewForm from '../components/ReviewForm'
import ReviewTabs from '../components/ReviewTabs'

function ProductPage() {
  const { id } = useParams()
  const [product, setProduct] = useState(null)
  const [rating, setRating] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  useEffect(() => {
    loadProduct()
    loadRating()
  }, [id, refreshTrigger])

  const loadProduct = async () => {
    try {
      const response = await productAPI.getById(id)
      setProduct(response.data)
    } catch (error) {
      console.error('Error loading product:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadRating = async () => {
    try {
      const response = await productAPI.getRating(id)
      setRating(response.data)
    } catch (error) {
      console.error('Error loading rating:', error)
    }
  }

  const handleReviewSubmitted = () => {
    setRefreshTrigger(prev => prev + 1)
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl text-gray-600">Loading product...</div>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl text-red-600">Product not found</div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-12">
        <div>
          <img
            src={product.image_url}
            alt={product.title}
            className="w-full rounded-lg shadow-lg"
          />
        </div>

        <div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            {product.title}
          </h1>
          
          {rating && rating.total_reviews > 0 && (
            <div className="mb-4 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
              <div className="flex items-center space-x-4">
                <div>
                  <div className="text-4xl font-bold text-blue-600">
                    {rating.weighted_rating.toFixed(1)}
                  </div>
                  <div className="text-xs text-gray-600">Weighted Rating</div>
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <div className="text-yellow-500 text-xl">
                      {'⭐'.repeat(Math.round(rating.weighted_rating))}
                    </div>
                  </div>
                  <div className="text-sm text-gray-700">
                    Based on {rating.total_reviews} review{rating.total_reviews !== 1 ? 's' : ''}
                  </div>
                  <div className="text-xs text-gray-600">
                    {(rating.positive_ratio * 100).toFixed(0)}% positive • 
                    Confidence: {(rating.confidence_score * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
              <div className="mt-2 text-xs text-gray-500">
                🤖 AI-weighted: Detailed, specific reviews have more influence
              </div>
            </div>
          )}
          
          <p className="text-3xl font-bold text-blue-600 mb-6">
            ${product.price} {product.currency}
          </p>
          <p className="text-gray-700 mb-6">
            {product.long_description || product.description}
          </p>

          {product.keypoints && product.keypoints.length > 0 && (
            <div className="mb-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Key Features:
              </h3>
              <ul className="list-disc list-inside space-y-2">
                {product.keypoints.map((point, index) => (
                  <li key={index} className="text-gray-700">
                    {point}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      <div className="border-t pt-12">
        <ReviewForm
          productId={product.id}
          onReviewSubmitted={handleReviewSubmitted}
        />
      </div>

      <div className="border-t pt-12 mt-12">
        <ReviewTabs productId={product.id} refreshTrigger={refreshTrigger} />
      </div>
    </div>
  )
}

export default ProductPage
