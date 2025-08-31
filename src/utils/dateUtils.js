/**
 * Format a date string to display in the user's local timezone
 * @param {string} dateString - ISO date string from the database
 * @returns {string} Formatted date string in user's timezone
 */
export function formatDate(dateString) {
  if (!dateString) return 'N/A'

  try {
    // Ensure the date string is treated as UTC if it doesn't have timezone info
    let date
    if (dateString.includes('T') && !dateString.includes('Z') && !dateString.includes('+')) {
      // If it's ISO format but missing timezone, assume it's UTC
      date = new Date(dateString + 'Z')
    } else {
      date = new Date(dateString)
    }

    // Verify the date is valid
    if (isNaN(date.getTime())) {
      throw new Error('Invalid date')
    }

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
      hour12: true,
      timeZoneName: 'short'
    })

    return formattedDate
  } catch (error) {
    console.error('Error formatting date:', error, 'Input:', dateString)
    return 'Invalid date'
  }
}
