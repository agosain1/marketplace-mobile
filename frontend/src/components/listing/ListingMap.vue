<template>
  <div class="location-map">
    <Map.OlMap v-if="latitude && longitude" style="width: 100%; height: 100%">
      <Map.OlView :center="apxCoords" :zoom="13" projection="EPSG:4326" />
      <Layers.OlTileLayer>
        <Sources.OlSourceXYZ url="https://{a-c}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png" />
        <!-- <Sources.OlSourceOSM /> -->
      </Layers.OlTileLayer>

      <Layers.OlVectorLayer>
        <Sources.OlSourceVector>
          <Map.OlFeature>
            <Geometries.OlGeomCircle :center="apxCoords" :radius="0.01" />
            <Styles.OlStyle>
              <Styles.OlStyleStroke color="#006f20" :width="3" />
              <Styles.OlStyleFill color="#006f2033" />
            </Styles.OlStyle>
          </Map.OlFeature>
        </Sources.OlSourceVector>
      </Layers.OlVectorLayer>
    </Map.OlMap>
    <div v-else class="missing-location">Location not available</div>
  </div>
</template>

<script setup lang="ts">
import { Map, Layers, Sources, Geometries, Styles } from 'vue3-openlayers';

const { longitude, latitude } = defineProps<{
  longitude: number | undefined;
  latitude: number | undefined;
}>();

const apxCoords = clampLonLat([Number(longitude), Number(latitude)]);

// utility function that should be moved to it's own file
function clampLonLat(value: [number, number]) {
  const lon = Math.max(-180, Math.min(180, value[0]));
  const lat = Math.max(-90, Math.min(90, value[1]));
  return [lon, lat];
}
</script>

<style scoped lang="scss">
.location-map {
  width: 100%;
  aspect-ratio: 16/9;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.missing-location {
  background-color: $secondary;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.circle {
  stroke: #ff0000 !important;
  fill: rgba(255, 0, 0, 0.3) !important;
}
</style>
