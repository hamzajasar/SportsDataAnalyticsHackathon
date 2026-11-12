import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useClub } from '@/state/club'
import { useShareSuggestions } from '@/api/queries'
import { useT } from '@/i18n'
import { QueryState } from '@/components/common/QueryState'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

// Fix default Leaflet marker icons for bundlers
delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const clubIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

const venueIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [20, 33],
  iconAnchor: [10, 33],
  popupAnchor: [1, -28],
  shadowSize: [33, 33],
  className: 'opacity-70',
})

function RecenterMap({ lat, lon }: { lat: number; lon: number }) {
  const map = useMap()
  useEffect(() => {
    map.setView([lat, lon])
  }, [map, lat, lon])
  return null
}

const RADII = [5, 10, 25]

export function SharePage() {
  const { club, isSample } = useClub()
  const [radius, setRadius] = useState(10)
  const { t } = useT()

  const lat = club?.lat ?? 43.846_4
  const lon = club?.lon ?? 18.394_9
  const clubName = isSample ? t('common.sampleClub') : (club?.name ?? t('common.yourClub'))

  const suggestions = useShareSuggestions(lat, lon, radius)
  const data = suggestions.data

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold">{t('share.title')}</h2>
          <p className="text-sm text-muted-foreground">{t('share.desc')}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">{t('share.radius')}</span>
          {RADII.map((r) => (
            <Button
              key={r}
              variant={radius === r ? 'default' : 'outline'}
              size="sm"
              onClick={() => setRadius(r)}
            >
              {r} km
            </Button>
          ))}
        </div>
      </div>

      {/* Map */}
      <div className="overflow-hidden rounded-lg border" style={{ height: 360 }}>
        <MapContainer
          center={[lat, lon]}
          zoom={12}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={false}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="© <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"
          />
          <RecenterMap lat={lat} lon={lon} />
          <Marker position={[lat, lon]} icon={clubIcon}>
            <Popup>{clubName}</Popup>
          </Marker>
          {data?.shared_pitch.map((v) => (
            <Marker key={v.id} position={[v.lat, v.lon]} icon={venueIcon}>
              <Popup>
                <strong>{v.name ?? v.leisure}</strong>
                {v.distance_km != null && (
                  <> · {t('share.kmAway', { km: v.distance_km.toFixed(1) })}</>
                )}
              </Popup>
            </Marker>
          ))}
          {data?.carpool_partners.map((v) => (
            <Marker key={v.id} position={[v.lat, v.lon]} icon={venueIcon}>
              <Popup>
                <strong>{v.name ?? v.leisure}</strong>
                {v.distance_km != null && (
                  <> · {t('share.kmAway', { km: v.distance_km.toFixed(1) })}</>
                )}
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      <QueryState isLoading={suggestions.isLoading} error={suggestions.error}>
        <div className="grid gap-4 sm:grid-cols-2">
          {/* Shared pitches */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">{t('share.pitchesTitle')}</CardTitle>
              <CardDescription>
                {t('share.pitchesCount', { count: data?.shared_pitch.length ?? 0, radius })}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {(data?.shared_pitch.length ?? 0) === 0 ? (
                <p className="text-sm text-muted-foreground">{t('share.noPitches')}</p>
              ) : (
                <ul className="space-y-2">
                  {data!.shared_pitch.map((v) => (
                    <li key={v.id} className="flex items-center justify-between gap-2 text-sm">
                      <span>
                        {v.name ?? v.leisure}
                        {v.name && (
                          <span className="ml-1 text-xs text-muted-foreground">({v.leisure})</span>
                        )}
                      </span>
                      {v.distance_km != null && (
                        <Badge variant="outline">{v.distance_km.toFixed(1)} km</Badge>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>

          {/* Carpool partners */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">{t('share.carpoolTitle')}</CardTitle>
              <CardDescription>
                {t('share.carpoolCount', { count: data?.carpool_partners.length ?? 0, radius })}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {(data?.carpool_partners.length ?? 0) === 0 ? (
                <p className="text-sm text-muted-foreground">{t('share.noClubs')}</p>
              ) : (
                <ul className="space-y-2">
                  {data!.carpool_partners.map((v) => (
                    <li key={v.id} className="flex items-center justify-between gap-2 text-sm">
                      <span>{v.name ?? v.leisure}</span>
                      {v.distance_km != null && (
                        <Badge variant="outline">{v.distance_km.toFixed(1)} km</Badge>
                      )}
                    </li>
                  ))}
                </ul>
              )}
              {data && <p className="mt-3 text-xs text-muted-foreground">{data.note}</p>}
            </CardContent>
          </Card>
        </div>
      </QueryState>
      <p className="text-xs text-muted-foreground">
        Venue data: © OpenStreetMap contributors (ODbL). Partners are a heuristic — verify before
        reaching out.
      </p>
    </div>
  )
}
