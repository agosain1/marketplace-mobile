<template>
  <div class="listing-location-map-container">
    <div ref="mapContainer" class="map-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { MAPBOX_ACCESS_TOKEN } from '../../constants.js'

const props = defineProps({
  latitude: {
    type: Number,
    default: null
  },
  longitude: {
    type: Number,
    default: null
  },
  zoom: {
    type: Number,
    default: 13
  },
  location: {
    type: String,
    default: ''
  }
})

const mapContainer = ref(null)
let map = null

onMounted(() => {
  if (!MAPBOX_ACCESS_TOKEN) {
    console.error('Mapbox access token is required')
    return
  }

  mapboxgl.accessToken = MAPBOX_ACCESS_TOKEN

  // Initialize map
  map = new mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/mapbox/streets-v12',
    center: [props.longitude || -122.4194, props.latitude || 37.7749], // Default to SF
    zoom: props.zoom,
    interactive: true // Allow panning/zooming but no location selection
  })

  // Add light blue circle marker when map loads
  map.on('load', () => {
    addLocationMarker()
  })
})

const updateLocationMarker = () => {
  if (!map || !props.latitude || !props.longitude) return

  // Calculate radius based on zoom level (minimum 1.5 miles, increases as zoom decreases)
  const currentZoom = map.getZoom()
  const baseRadius = 1.5 // minimum radius in miles
  const zoomFactor = Math.max(1, (15 - currentZoom) * 0.5) // Scale factor based on zoom
  const radiusInMiles = baseRadius * zoomFactor
  const radiusInMeters = radiusInMiles * 1609.34 // Convert miles to meters

  // Create a circle polygon using turf-like calculations
  const createCircle = (center, radiusMeters, points = 64) => {
    const coords = []
    const distanceX = radiusMeters / (111320 * Math.cos(center[1] * Math.PI / 180))
    const distanceY = radiusMeters / 110540

    for (let i = 0; i < points; i++) {
      const angle = (i / points) * 2 * Math.PI
      const x = center[0] + (distanceX * Math.cos(angle))
      const y = center[1] + (distanceY * Math.sin(angle))
      coords.push([x, y])
    }
    coords.push(coords[0]) // Close the polygon
    return coords
  }

  const circleCoords = createCircle([props.longitude, props.latitude], radiusInMeters)

  // Remove existing circle if it exists
  if (map.getLayer('location-circle-fill')) {
    map.removeLayer('location-circle-fill')
  }
  if (map.getLayer('location-circle-stroke')) {
    map.removeLayer('location-circle-stroke')
  }
  if (map.getSource('location-circle')) {
    map.removeSource('location-circle')
  }

  // Add a source for the circle
  map.addSource('location-circle', {
    type: 'geojson',
    data: {
      type: 'FeatureCollection',
      features: [{
        type: 'Feature',
        geometry: {
          type: 'Polygon',
          coordinates: [circleCoords]
        }
      }]
    }
  })

  // Add circle layer
  map.addLayer({
    id: 'location-circle-fill',
    type: 'fill',
    source: 'location-circle',
    paint: {
      'fill-color': '#4FC3F7', // Light blue color
      'fill-opacity': 0.3
    }
  })

  // Add circle border
  map.addLayer({
    id: 'location-circle-stroke',
    type: 'line',
    source: 'location-circle',
    paint: {
      'line-color': '#29B6F6',
      'line-width': 2,
      'line-opacity': 0.8
    }
  })
}

const addLocationMarker = () => {
  if (!map || !props.latitude || !props.longitude) return

  updateLocationMarker()

  // Listen for zoom changes to update circle size
  map.on('zoom', updateLocationMarker)

  // Center the map on the location
  map.setCenter([props.longitude, props.latitude])
}

// Watch for prop changes
watch(() => [props.latitude, props.longitude], ([newLat, newLng]) => {
  if (map && newLat && newLng) {
    // Add new circle at new location
    addLocationMarker()
  }
})

onUnmounted(() => {
  if (map) {
    map.remove()
  }
})
</script>

<style scoped>
.listing-location-map-container {
  position: relative;
  width: 100%;
  height: 350px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
}

.map-container {
  width: 100%;
  height: 100%;
}
</style>
