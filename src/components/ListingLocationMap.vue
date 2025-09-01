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
let marker = null

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

const addLocationMarker = () => {
  if (!map || !props.latitude || !props.longitude) return

  // Add a source for the circle
  map.addSource('location-circle', {
    type: 'geojson',
    data: {
      type: 'FeatureCollection',
      features: [{
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [props.longitude, props.latitude]
        }
      }]
    }
  })

  // Add circle layer
  map.addLayer({
    id: 'location-circle-fill',
    type: 'circle',
    source: 'location-circle',
    paint: {
      'circle-radius': 50, // Radius in pixels
      'circle-color': '#4FC3F7', // Light blue color
      'circle-opacity': 0.3,
      'circle-stroke-width': 2,
      'circle-stroke-color': '#29B6F6',
      'circle-stroke-opacity': 0.8
    }
  })

  // Center the map on the location
  map.setCenter([props.longitude, props.latitude])
}

// Watch for prop changes
watch(() => [props.latitude, props.longitude], ([newLat, newLng]) => {
  if (map && newLat && newLng) {
    // Remove existing circle if it exists
    if (map.getLayer('location-circle-fill')) {
      map.removeLayer('location-circle-fill')
    }
    if (map.getSource('location-circle')) {
      map.removeSource('location-circle')
    }
    
    // Add new circle
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