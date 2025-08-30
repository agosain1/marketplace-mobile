/**
 * Format a date string to display in the user's local timezone
 * @param {string} dateString - ISO date string from the database
 * @returns {string} Formatted date string in user's timezone
 */
export function formatDate(dateString) {
  if (!dateString) return 'N/A'
  
  try {
    const date = new Date(dateString)
    
    // Get user's timezone
    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone
    
    // Format the date in user's timezone
    const formattedDate = date.toLocaleDateString('en-US', {
      timeZone: userTimezone,
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    })
    
    return formattedDate
  } catch (error) {
    console.error('Error formatting date:', error)
    return 'Invalid date'
  }
}

/**
 * Get user's timezone for display purposes
 * @returns {string} User's timezone (e.g., "America/New_York")
 */
export function getUserTimezone() {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone
  } catch (error) {
    console.error('Error getting user timezone:', error)
    return 'UTC'
  }
}

/**
 * Get timezone abbreviation (e.g., "EST", "PST")
 * @returns {string} Timezone abbreviation
 */
export function getTimezoneAbbreviation() {
  try {
    const date = new Date()
    const formatter = new Intl.DateTimeFormat('en-US', {
      timeZoneName: 'short'
    })
    
    const parts = formatter.formatToParts(date)
    const timeZonePart = parts.find(part => part.type === 'timeZoneName')
    
    return timeZonePart ? timeZonePart.value : 'UTC'
  } catch (error) {
    console.error('Error getting timezone abbreviation:', error)
    return 'UTC'
  }
}