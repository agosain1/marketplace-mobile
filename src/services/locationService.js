export const locationService = {
  getCurrentPosition() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported by this browser'))
        return
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy
          })
        },
        (error) => {
          let errorMessage = 'Unable to get location'
          
          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorMessage = 'Location access denied by user'
              break
            case error.POSITION_UNAVAILABLE:
              errorMessage = 'Location information unavailable'
              break
            case error.TIMEOUT:
              errorMessage = 'Location request timed out'
              break
          }
          
          reject(new Error(errorMessage))
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000
        }
      )
    })
  },

  async getLocationName(latitude, longitude) {
    try {
      const response = await fetch(
        `https://api.opencagedata.com/geocode/v1/json?q=${latitude}+${longitude}&key=${import.meta.env.VITE_OPENCAGE_API_KEY}`
      )
      
      if (!response.ok) {
        throw new Error('Geocoding service unavailable')
      }
      
      const data = await response.json()
      
      if (data.results && data.results.length > 0) {
        const result = data.results[0]
        return result.formatted || `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`
      }
      
      return `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`
    } catch (error) {
      console.warn('Geocoding failed:', error)
      return `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`
    }
  }
}