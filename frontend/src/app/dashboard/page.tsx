'use client'

import { type FormEvent, useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { linksAPI, analyticsAPI, extractListData } from '@/lib/api'
import { QRCodeSVG } from 'qrcode.react'
import { IPLocationWidget } from '@/components/IPLocationWidget'

interface LinkData {
  id: number
  original_url: string
  short_code: string
  short_url: string
  title: string
  click_count: number
  created_at: string
  is_active: boolean
}

interface DeviceAccess {
  id: number
  ip_address: string
  device_model: string
  device_type: string
  access_count: number
  last_access: string
}

interface Analytics {
  total_links: number
  total_clicks: number
  total_unique_clicks: number
  clicks_today: number
}

export default function DashboardPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [showQR, setShowQR] = useState<string | null>(null)
  const [expandedLink, setExpandedLink] = useState<number | null>(null)
  const [showIPLocations, setShowIPLocations] = useState<number | null>(null)
  const [newLink, setNewLink] = useState({ original_url: '', title: '', custom_slug: '' })
  const [showForm, setShowForm] = useState(false)

  const { data: linksRawData, isLoading } = useQuery({
    queryKey: ['links'],
    queryFn: () => linksAPI.getList(),
    select: (response: any) => {
      const data = response.data
      if (Array.isArray(data)) return data
      if (data?.results && Array.isArray(data.results)) return data.results
      return []
    },
  })

  const links: LinkData[] = linksRawData || []

  const { data: analytics } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => analyticsAPI.getSummary().then((r) => r.data),
  })

  const { data: deviceDataMap } = useQuery<Record<number, DeviceAccess[]>>({
    queryKey: ['devices', links.map((l) => l.id).join(',')],
    queryFn: async () => {
      const map: Record<number, DeviceAccess[]> = {}
      for (const link of links) {
        try {
          const response = await analyticsAPI.getDeviceAccess(link.id)
          map[link.id] = extractListData<DeviceAccess>(response.data)
        } catch (error) {
          map[link.id] = []
        }
      }
      return map
    },
    enabled: links.length > 0,
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => linksAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['links'] })
      queryClient.invalidateQueries({ queryKey: ['analytics'] })
      setShowForm(false)
      setNewLink({ original_url: '', title: '', custom_slug: '' })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => linksAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['links'] })
      queryClient.invalidateQueries({ queryKey: ['analytics'] })
    },
  })

  const handleCreate = (e: FormEvent) => {
    e.preventDefault()
    createMutation.mutate(newLink)
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    alert('Copied!')
  }

  const getDeviceIcon = (deviceType: string) => {
    switch (deviceType) {
      case 'mobile':
        return '📱'
      case 'tablet':
        return '📱'
      case 'desktop':
        return '💻'
      default:
        return '🖥️'
    }
  }

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
    }
  }, [router])

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800">
      {/* Header */}
      <header className="bg-gray-800/80 backdrop-blur-md border-b border-gray-700 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-white">Dashboard</h1>
            <p className="text-sm text-gray-300">Manage your links</p>
          </div>
          <div className="flex gap-4">
            <Link
              href="/"
              className="px-4 py-2 text-gray-300 hover:text-white rounded-lg hover:bg-gray-700 transition"
            >
              Home
            </Link>
            <button
              onClick={() => {
                localStorage.removeItem('token')
                router.push('/')
              }}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        {analytics && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-blue-500 transition">
              <p className="text-gray-400 text-sm">Total Links</p>
              <p className="text-3xl font-bold text-white mt-2">{analytics.total_links}</p>
            </div>
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-purple-500 transition">
              <p className="text-gray-400 text-sm">Total Clicks</p>
              <p className="text-3xl font-bold text-white mt-2">{analytics.total_clicks}</p>
            </div>
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-pink-500 transition">
              <p className="text-gray-400 text-sm">Unique Clicks</p>
              <p className="text-3xl font-bold text-white mt-2">{analytics.total_unique_clicks}</p>
            </div>
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-green-500 transition">
              <p className="text-gray-400 text-sm">Today's Clicks</p>
              <p className="text-3xl font-bold text-white mt-2">{analytics.clicks_today}</p>
            </div>
          </div>
        )}

        {/* Create Button */}
        <button
          onClick={() => setShowForm(!showForm)}
          className="mb-8 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition font-semibold"
        >
          {showForm ? 'Cancel' : '+ Create New Link'}
        </button>

        {/* Create Form */}
        {showForm && (
          <div className="mb-8 bg-gray-800 p-6 rounded-xl border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4">Create New Link</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <input
                type="url"
                placeholder="Enter your long URL"
                value={newLink.original_url}
                onChange={(e) => setNewLink({ ...newLink, original_url: e.target.value })}
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:border-blue-500 outline-none"
                required
              />
              <input
                type="text"
                placeholder="Title (optional)"
                value={newLink.title}
                onChange={(e) => setNewLink({ ...newLink, title: e.target.value })}
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:border-blue-500 outline-none"
              />
              <input
                type="text"
                placeholder="Custom slug (optional)"
                value={newLink.custom_slug}
                onChange={(e) => setNewLink({ ...newLink, custom_slug: e.target.value })}
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:border-blue-500 outline-none"
              />
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold disabled:opacity-50"
              >
                {createMutation.isPending ? 'Creating...' : 'Create Link'}
              </button>
            </form>
          </div>
        )}

        {/* Links List */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-white mb-4">Your Links</h2>
          {isLoading ? (
            <div className="text-center py-8 text-gray-400">Loading...</div>
          ) : links.length === 0 ? (
            <div className="text-center py-12 bg-gray-800 rounded-xl border border-gray-700">
              <p className="text-gray-400">No links yet. Create one!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {links.map((link) => {
                const deviceEntries = deviceDataMap?.[link.id] ?? []

                return (
                <div key={link.id} className="bg-gray-800 rounded-lg border border-gray-700 hover:border-gray-600 transition">
                  <div className="p-4">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <a
                          href={link.short_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-400 hover:text-blue-300 font-semibold break-all"
                        >
                          /{link.short_code}
                        </a>
                        <p className="text-gray-400 text-sm truncate mt-1">{link.original_url}</p>
                        {link.title && <p className="text-gray-300 text-sm mt-1">{link.title}</p>}
                        <p className="text-gray-500 text-xs mt-2">
                          Clicks: {link.click_count} | Created: {new Date(link.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex gap-2 flex-wrap sm:flex-nowrap">
                        <button
                          onClick={() => copyToClipboard(link.short_url)}
                          className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition"
                        >
                          Copy
                        </button>
                        <button
                          onClick={() => setShowQR(showQR === link.short_code ? null : link.short_code)}
                          className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded transition"
                        >
                          QR
                        </button>
                        <button
                          onClick={() => setExpandedLink(expandedLink === link.id ? null : link.id)}
                          className="px-3 py-1 bg-cyan-600 hover:bg-cyan-700 text-white text-sm rounded transition"
                        >
                          📱 Devices
                        </button>
                        <button
                          onClick={() => setShowIPLocations(showIPLocations === link.id ? null : link.id)}
                          className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition"
                        >
                          🌍 Map
                        </button>
                        <button
                          onClick={() => deleteMutation.mutate(link.id)}
                          className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition"
                        >
                          Delete
                        </button>
                      </div>
                    </div>

                    {/* QR Code */}
                    {showQR === link.short_code && (
                      <div className="mt-4 flex justify-center">
                        <div className="bg-white p-3 rounded-lg">
                          <QRCodeSVG value={link.short_url} size={120} />
                        </div>
                      </div>
                    )}

                    {/* Device Access Info */}
                    {expandedLink === link.id && (
                      <div className="mt-6 pt-4 border-t border-gray-700">
                        <h3 className="text-lg font-semibold text-white mb-3">📱 Device Access ({deviceEntries.length})</h3>
                        {deviceEntries.length === 0 ? (
                          <p className="text-gray-400 text-sm">No device data yet</p>
                        ) : (
                          <div className="space-y-2 max-h-96 overflow-y-auto">
                            {deviceEntries.map((device) => (
                              <div
                                key={device.id}
                                className="bg-gray-700 p-3 rounded-lg border border-gray-600 hover:border-gray-500 transition"
                              >
                                <div className="flex items-start justify-between gap-2">
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                      <span className="text-xl">{getDeviceIcon(device.device_type)}</span>
                                      <p className="text-white font-semibold">{device.device_model}</p>
                                      <span className="text-xs bg-gray-600 px-2 py-1 rounded text-gray-200">
                                        {device.device_type}
                                      </span>
                                    </div>
                                    <p className="text-sm text-gray-300">
                                      🌐 IP: <span className="font-mono">{device.ip_address}</span>
                                    </p>
                                    <p className="text-xs text-gray-400 mt-1">
                                      Accessed: {device.access_count}x | Last: {new Date(device.last_access).toLocaleDateString()}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* IP Location Widget */}
                    {showIPLocations === link.id && (
                      <div className="mt-6 pt-4 border-t border-gray-700">
                        <IPLocationWidget linkId={link.id} linkShortCode={link.short_code} />
                      </div>
                    )}
                  </div>
                </div>
                )
              })}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
