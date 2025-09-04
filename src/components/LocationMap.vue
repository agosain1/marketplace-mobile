<template>
  <div class="location-map-container">
    <div ref="mapContainer" class="map-container"></div>
    <!-- Fixed center crosshair -->
    <div class="center-marker">
      <q-icon name="place" size="32px" color="primary" />
    </div>
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
  }
})

const emit = defineEmits(['location-changed'])

const mapContainer = ref(null)
const gettingLocation = ref(false)
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
    zoom: props.zoom
  })

  // Handle map movement - emit new center coordinates
  map.on('moveend', () => {
    const center = map.getCenter()
    emit('location-changed', {
      latitude: center.lat,
      longitude: center.lng
    })
  })


  // If we have initial coordinates, set them
  if (props.latitude && props.longitude) {
    map.setCenter([props.longitude, props.latitude])
  }
})

// Watch for prop changes
watch(() => [props.latitude, props.longitude], ([newLat, newLng]) => {
  if (map && newLat && newLng) {
    map.setCenter([newLng, newLat])
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

    if (map) {
      map.setCenter([longitude, latitude])

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

.center-marker {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
  pointer-events: none;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}
</style>
