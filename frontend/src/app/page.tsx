'use client'

import { type FormEvent, useState } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'
import Link from 'next/link'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export default function Home() {
  const router = useRouter()
  const [originalUrl, setOriginalUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const token = localStorage.getItem('token')
      if (!token) {
        router.push('/login')
        return
      }

      const response = await axios.post(
        `${API_URL}/links/`,
        { original_url: originalUrl },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      )

      router.push(`/link/${response.data.short_code}`)
    } catch (err: any) {
      if (err.response?.status === 401) {
        router.push('/login')
      } else {
        setError(err.response?.data?.message || 'Failed to create short URL')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-center mb-2 text-gray-900 dark:text-white">
          URL Shortener
        </h1>
        <p className="text-gray-600 dark:text-gray-400 text-center mb-8">
          Shorten your links with analytics
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <input
              type="url"
              value={originalUrl}
              onChange={(e) => setOriginalUrl(e.target.value)}
              placeholder="Paste your long URL here..."
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
              required
            />
          </div>

          {error && (
            <p className="text-red-500 text-sm">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50"
          >
            {loading ? 'Shortening...' : 'Shorten URL'}
          </button>
        </form>

        <div className="mt-6 text-center space-y-2">
          <Link
            href="/login"
            className="block text-primary-600 hover:text-primary-700 dark:text-primary-400"
          >
            Login
          </Link>
          <Link
            href="/register"
            className="block text-primary-600 hover:text-primary-700 dark:text-primary-400"
          >
            Create an account
          </Link>
        </div>
      </div>
    </div>
  )
}
