'use client'

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { analyticsAPI, extractListData } from '@/lib/api'
import { IPLocationMap } from './IPLocationMap'

interface IPLocation {
  id: number
  ip_address: string
  device_model: string
  device_type: string
  access_count: number
  last_access: string
  country: string
  country_code: string
  city: string
  region: string
  latitude: number | null
  longitude: number | null
  timezone: string
  isp: string
}

interface IPLocationWidgetProps {
  linkId: number
  linkShortCode: string
}

interface IPStats {
  total_unique_ips: number
  total_accesses: number
  countries: string[]
  cities: string[]
}

export function IPLocationWidget({ linkId, linkShortCode }: IPLocationWidgetProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [countryFilter, setCountryFilter] = useState('')
  const [cityFilter, setCityFilter] = useState('')
  const [deviceTypeFilter, setDeviceTypeFilter] = useState('')
  const [sortBy, setSortBy] = useState('access_count')
  const [sortOrder, setSortOrder] = useState('desc')
  const [expandedIp, setExpandedIp] = useState<string | null>(null)

  const { data: ipLocations = [], isLoading } = useQuery<IPLocation[]>({
    queryKey: ['ipLocations', linkId],
    queryFn: async () => {
      try {
        const response = await analyticsAPI.getIPLocations(linkId)
        return extractListData<IPLocation>(response.data)
      } catch (error) {
        console.error('Failed to fetch IP locations:', error)
        return []
      }
    },
  })

  const { data: ipStats } = useQuery<IPStats | null>({
    queryKey: ['ipStats', linkId],
    queryFn: async () => {
      try {
        const response = await analyticsAPI.getIPStats(linkId)
        return response.data as IPStats
      } catch (error) {
        console.error('Failed to fetch IP stats:', error)
        return null
      }
    },
  })

  // Filter and search
  const filteredData = useMemo(() => {
    let filtered = [...ipLocations]

    if (searchTerm) {
      filtered = filtered.filter(
        (item: IPLocation) =>
          item.ip_address.includes(searchTerm) ||
          item.country.toLowerCase().includes(searchTerm.toLowerCase()) ||
          item.city.toLowerCase().includes(searchTerm.toLowerCase()) ||
          item.isp.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    if (countryFilter) {
      filtered = filtered.filter((item: IPLocation) => item.country_code === countryFilter)
    }

    if (cityFilter) {
      filtered = filtered.filter((item: IPLocation) =>
        item.city.toLowerCase().includes(cityFilter.toLowerCase())
      )
    }

    if (deviceTypeFilter) {
      filtered = filtered.filter((item: IPLocation) => item.device_type === deviceTypeFilter)
    }

    // Sort
    filtered.sort((a: IPLocation, b: IPLocation) => {
      let aVal: any = a[sortBy as keyof IPLocation]
      let bVal: any = b[sortBy as keyof IPLocation]

      if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase()
        bVal = (bVal as string).toLowerCase()
      }

      if (sortOrder === 'asc') {
        return aVal > bVal ? 1 : aVal < bVal ? -1 : 0
      } else {
        return aVal < bVal ? 1 : aVal > bVal ? -1 : 0
      }
    })

    return filtered
  }, [ipLocations, searchTerm, countryFilter, cityFilter, deviceTypeFilter, sortBy, sortOrder])

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

  const getCountryFlag = (countryCode: string) => {
    if (!countryCode || countryCode.length !== 2) return '🌍'
    return String.fromCodePoint(
      ...countryCode
        .toUpperCase()
        .split('')
        .map((char) => 127397 + char.charCodeAt(0))
    )
  }

  if (isLoading) {
    return <div className="text-gray-400">Loading IP locations...</div>
  }

  return (
    <div className="space-y-6">
      {/* Stats Summary */}
      {ipStats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gray-700/50 p-4 rounded-lg border border-gray-600">
            <p className="text-gray-400 text-sm">Unique IPs</p>
            <p className="text-2xl font-bold text-white mt-1">{ipStats.total_unique_ips}</p>
          </div>
          <div className="bg-gray-700/50 p-4 rounded-lg border border-gray-600">
            <p className="text-gray-400 text-sm">Total Accesses</p>
            <p className="text-2xl font-bold text-white mt-1">{ipStats.total_accesses}</p>
          </div>
          <div className="bg-gray-700/50 p-4 rounded-lg border border-gray-600">
            <p className="text-gray-400 text-sm">Countries</p>
            <p className="text-2xl font-bold text-white mt-1">{ipStats.countries.length}</p>
          </div>
          <div className="bg-gray-700/50 p-4 rounded-lg border border-gray-600">
            <p className="text-gray-400 text-sm">Cities</p>
            <p className="text-2xl font-bold text-white mt-1">{ipStats.cities.length}</p>
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Search</label>
          <input
            type="text"
            placeholder="Search by IP, country, city, ISP..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:border-blue-500 outline-none"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Country</label>
            <input
              type="text"
              placeholder="Filter by country code"
              value={countryFilter}
              onChange={(e) => setCountryFilter(e.target.value.toUpperCase())}
              maxLength={2}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:border-blue-500 outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">City</label>
            <input
              type="text"
              placeholder="Filter by city"
              value={cityFilter}
              onChange={(e) => setCityFilter(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:border-blue-500 outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Device Type</label>
            <select
              value={deviceTypeFilter}
              onChange={(e) => setDeviceTypeFilter(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:border-blue-500 outline-none"
            >
              <option value="">All Types</option>
              <option value="mobile">Mobile</option>
              <option value="tablet">Tablet</option>
              <option value="desktop">Desktop</option>
            </select>
          </div>
        </div>

        {/* Sort Options */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Sort By</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:border-blue-500 outline-none"
            >
              <option value="access_count">Most Accessed</option>
              <option value="last_access">Recent Access</option>
              <option value="country">Country</option>
              <option value="city">City</option>
              <option value="ip_address">IP Address</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Order</label>
            <select
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:border-blue-500 outline-none"
            >
              <option value="desc">Descending</option>
              <option value="asc">Ascending</option>
            </select>
          </div>
        </div>
      </div>

      {/* IP List */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-700 flex justify-between items-center">
          <h3 className="text-lg font-semibold text-white">
            IP Locations ({filteredData.length})
          </h3>
          <span className="text-sm text-gray-400">Range Limited: {Math.min(filteredData.length, 1000)}</span>
        </div>

        {filteredData.length === 0 ? (
          <div className="px-4 py-8 text-center text-gray-400">No IP locations found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-700/50 border-b border-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left text-gray-300">IP Address</th>
                  <th className="px-4 py-3 text-left text-gray-300">Location</th>
                  <th className="px-4 py-3 text-left text-gray-300">Device</th>
                  <th className="px-4 py-3 text-left text-gray-300">Accesses</th>
                  <th className="px-4 py-3 text-left text-gray-300">Last Access</th>
                  <th className="px-4 py-3 text-center text-gray-300">Details</th>
                </tr>
              </thead>
              <tbody>
                {filteredData.slice(0, 1000).map((location: IPLocation) => (
                  <tr key={location.id} className="border-b border-gray-700 hover:bg-gray-700/30">
                    <td className="px-4 py-3">
                      <code className="text-blue-400 bg-gray-900 px-2 py-1 rounded text-xs">
                        {location.ip_address}
                      </code>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{getCountryFlag(location.country_code)}</span>
                        <div className="text-sm">
                          <div className="text-white font-medium">{location.country}</div>
                          <div className="text-gray-400">{location.city}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span>{getDeviceIcon(location.device_type)}</span>
                        <div className="text-sm">
                          <div className="text-white">{location.device_type}</div>
                          <div className="text-gray-400 text-xs">{location.device_model}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="bg-blue-900/40 text-blue-300 px-3 py-1 rounded-full text-sm font-medium">
                        {location.access_count}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-sm text-gray-400">
                        {new Date(location.last_access).toLocaleString()}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() =>
                          setExpandedIp(expandedIp === location.ip_address ? null : location.ip_address)
                        }
                        className="text-blue-400 hover:text-blue-300 font-medium"
                      >
                        {expandedIp === location.ip_address ? '▼' : '▶'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Expanded Details with Map */}
            {expandedIp && (
              <div className="bg-gray-700/30 p-4 border-t border-gray-700 space-y-4">
                {(() => {
                  const location = filteredData.find(
                    (loc: IPLocation) => loc.ip_address === expandedIp
                  )
                  if (!location) return null

                  return (
                    <div className="space-y-4">
                      {/* Show Map */}
                      <div>
                        <h4 className="text-sm font-semibold text-white mb-2">📍 Location Map</h4>
                        <IPLocationMap location={{
                          latitude: location.latitude,
                          longitude: location.longitude,
                          city: location.city,
                          country: location.country,
                          isp: location.isp,
                          timezone: location.timezone,
                        }} />
                      </div>

                      {/* Detailed Information */}
                      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                        <div className="bg-gray-800 p-3 rounded border border-gray-600">
                          <p className="text-gray-400 text-xs">🏢 ISP</p>
                          <p className="text-white font-medium text-sm mt-1">{location.isp || 'Unknown'}</p>
                        </div>
                        <div className="bg-gray-800 p-3 rounded border border-gray-600">
                          <p className="text-gray-400 text-xs">🕐 Timezone</p>
                          <p className="text-white font-medium text-sm mt-1">{location.timezone || 'Unknown'}</p>
                        </div>
                        <div className="bg-gray-800 p-3 rounded border border-gray-600">
                          <p className="text-gray-400 text-xs">🗺️ Region</p>
                          <p className="text-white font-medium text-sm mt-1">{location.region || 'N/A'}</p>
                        </div>
                        <div className="bg-gray-800 p-3 rounded border border-gray-600">
                          <p className="text-gray-400 text-xs">📊 Device Type</p>
                          <p className="text-white font-medium text-sm mt-1">{location.device_type}</p>
                        </div>
                        <div className="bg-gray-800 p-3 rounded border border-gray-600">
                          <p className="text-gray-400 text-xs">📱 Device Model</p>
                          <p className="text-white font-medium text-sm mt-1">{location.device_model}</p>
                        </div>
                        <div className="bg-gray-800 p-3 rounded border border-gray-600">
                          <p className="text-gray-400 text-xs">🌐 IP Address</p>
                          <p className="text-white font-mono text-sm mt-1">{location.ip_address}</p>
                        </div>
                      </div>

                      {/* Access History Summary */}
                      <div className="bg-blue-900/20 border border-blue-700/30 rounded p-3">
                        <p className="text-blue-300 text-sm">
                          <strong>Access History:</strong> {location.access_count}x accessed since {new Date(location.last_access).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  )
                })()}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
