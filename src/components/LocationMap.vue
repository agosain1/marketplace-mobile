<template>
  <div class="location-map-container">
    <div ref="mapContainer" class="map-container"></div>
    <div class="map-controls">
      <q-btn
        @click="centerOnCurrentLocation"
        icon="my_location"
        round
        color="primary"
        size="sm"
        :loading="gettingLocation"
        class="center-btn"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

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
  }
})

const emit = defineEmits(['location-changed'])

const mapContainer = ref(null)
const gettingLocation = ref(false)
let map = null
let marker = null

onMounted(() => {
  if (!import.meta.env.VITE_MAPBOX_ACCESS_TOKEN) {
    console.error('Mapbox access token is required')
    return
  }

  mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN

  // Initialize map
  map = new mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/mapbox/streets-v12',
    center: [props.longitude || -122.4194, props.latitude || 37.7749], // Default to SF
    zoom: props.zoom
  })

  // Add marker
  marker = new mapboxgl.Marker({
    draggable: true,
    color: '#1976d2'
  })
    .setLngLat([props.longitude || -122.4194, props.latitude || 37.7749])
    .addTo(map)

  // Handle marker drag
  marker.on('dragend', () => {
    const lngLat = marker.getLngLat()
    emit('location-changed', {
      latitude: lngLat.lat,
      longitude: lngLat.lng
    })
  })

  // Handle map click
  map.on('click', (e) => {
    const { lng, lat } = e.lngLat
    marker.setLngLat([lng, lat])
    emit('location-changed', {
      latitude: lat,
      longitude: lng
    })
  })

  // If we have initial coordinates, set them
  if (props.latitude && props.longitude) {
    map.setCenter([props.longitude, props.latitude])
    marker.setLngLat([props.longitude, props.latitude])
  }
})

// Watch for prop changes
watch(() => [props.latitude, props.longitude], ([newLat, newLng]) => {
  if (map && marker && newLat && newLng) {
    map.setCenter([newLng, newLat])
    marker.setLngLat([newLng, newLat])
  }
})

const centerOnCurrentLocation = async () => {
  if (!navigator.geolocation) {
    console.error('Geolocation not supported')
    return
  }

  gettingLocation.value = true

  try {
    const position = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000
      })
    })

    const { latitude, longitude } = position.coords
    
    if (map && marker) {
      map.setCenter([longitude, latitude])
      marker.setLngLat([longitude, latitude])
      
      emit('location-changed', {
        latitude,
        longitude
      })
    }
  } catch (error) {
    console.error('Error getting location:', error)
  } finally {
    gettingLocation.value = false
  }
}

onUnmounted(() => {
  if (map) {
    map.remove()
  }
})
</script>

<style scoped>
.location-map-container {
  position: relative;
  width: 100%;
  height: 300px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
}

.map-container {
  width: 100%;
  height: 100%;
}

.map-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1;
}

.center-btn {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
}
</style>