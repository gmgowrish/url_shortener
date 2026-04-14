'use client'

import { useParams, useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { linksAPI } from '@/lib/api'
import { QRCodeSVG } from 'qrcode.react'

interface LinkData {
  id: number
  original_url: string
  short_code: string
  short_url: string
  title: string
  click_count: number
  created_at: string
}

export default function LinkDetailPage() {
  const params = useParams()
  const router = useRouter()
  const shortCode = params.short_code as string

  const { data: link, isLoading } = useQuery({
    queryKey: ['link', shortCode],
    queryFn: async () => {
      const response = await linksAPI.getList()
      const data = response.data
      const links: LinkData[] = Array.isArray(data)
        ? data
        : Array.isArray(data?.results)
          ? data.results
          : []

      return links.find((item) => item.short_code === shortCode) ?? null
    },
    enabled: !!shortCode,
  })

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Loading...</p>
      </div>
    )
  }

  if (!link) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Link not found</h1>
          <Link href="/dashboard" className="text-primary-600 hover:underline">
            Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-2xl mx-auto px-4">
        <Link
          href="/dashboard"
          className="text-primary-600 hover:underline mb-4 inline-block"
        >
          &larr; Back to Dashboard
        </Link>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h1 className="text-2xl font-bold mb-4 dark:text-white">
            {link.title || link.short_code}
          </h1>

          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Short URL</p>
              <a
                href={link.short_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-600 hover:underline text-lg"
              >
                {link.short_url}
              </a>
            </div>

            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Original URL</p>
              <p className="break-all dark:text-white">{link.original_url}</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Total Clicks</p>
                <p className="text-2xl font-bold">{link.click_count}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Created</p>
                <p className="text-lg">{new Date(link.created_at).toLocaleDateString()}</p>
              </div>
            </div>

            <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <p className="text-sm font-medium mb-2 dark:text-white">QR Code</p>
              <QRCodeSVG value={link.short_url} size={200} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
