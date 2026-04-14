'use client'

import { useEffect, useRef } from 'react'

interface MapLocation {
  latitude: number | null
  longitude: number | null
  city: string
  country: string
  isp: string
  timezone: string
}

interface IPLocationMapProps {
  location: MapLocation
}

export function IPLocationMap({ location }: IPLocationMapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)

  useEffect(() => {
    // Dynamically load Leaflet only when needed
    const loadMap = async () => {
      if (!mapRef.current || !location.latitude || !location.longitude) return

      // Load Leaflet CSS
      const link = document.createElement('link')
      link.rel = 'stylesheet'
      link.href = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css'
      document.head.appendChild(link)

      // Load Leaflet JS
      const script = document.createElement('script')
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js'
      script.onload = () => {
        if (window.L && mapRef.current) {
          // Initialize map
          if (!mapInstanceRef.current) {
            mapInstanceRef.current = window.L.map(mapRef.current).setView(
              [location.latitude, location.longitude],
              9
            )

            // Add OpenStreetMap tiles
            window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
              attribution: '© OpenStreetMap contributors',
              maxZoom: 19,
            }).addTo(mapInstanceRef.current)
          }

          // Add marker
          window.L.marker([location.latitude, location.longitude])
            .addTo(mapInstanceRef.current)
            .bindPopup(
              `<div class="text-sm">
                <strong>${location.city}, ${location.country}</strong><br/>
                📍 ${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}<br/>
                🏢 ${location.isp}
              </div>`
            )
            .openPopup()

          // Re-center map
          mapInstanceRef.current.setView([location.latitude, location.longitude], 9)
        }
      }
      document.head.appendChild(script)
    }

    loadMap()
  }, [location])

  if (!location.latitude || !location.longitude) {
    return (
      <div className="w-full h-96 bg-gray-700/30 rounded-lg border border-gray-600 flex items-center justify-center text-gray-400">
        📍 Map location unavailable (private IP or no geolocation data)
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div ref={mapRef} className="w-full h-96 rounded-lg border border-gray-600 overflow-hidden" />
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-sm">
        <div className="bg-gray-700/50 p-2 rounded">
          <p className="text-gray-400 text-xs">📍 Latitude</p>
          <p className="text-white font-mono">{location.latitude?.toFixed(4)}</p>
        </div>
        <div className="bg-gray-700/50 p-2 rounded">
          <p className="text-gray-400 text-xs">📍 Longitude</p>
          <p className="text-white font-mono">{location.longitude?.toFixed(4)}</p>
        </div>
        <div className="bg-gray-700/50 p-2 rounded">
          <p className="text-gray-400 text-xs">🕐 Timezone</p>
          <p className="text-white font-mono text-xs">{location.timezone || 'Unknown'}</p>
        </div>
        <div className="bg-gray-700/50 p-2 rounded">
          <p className="text-gray-400 text-xs">🏢 ISP</p>
          <p className="text-white font-mono text-xs">{location.isp || 'Unknown'}</p>
        </div>
      </div>
    </div>
  )
}
