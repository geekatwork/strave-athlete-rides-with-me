import axios from "axios";
import { getAccessToken } from "./authService";

const BASE_URL = "https://www.strava.com/api/v3";

// Function to make a request to Strava's API with authorization
async function makeStravaRequest(endpoint: string, params = {}) {
  const token = await getAccessToken(); // Ensure a valid token
  const headers = { Authorization: `Bearer ${token}` };

  try {
    const response = await axios.get(`${BASE_URL}${endpoint}`, { headers, params });
    return response.data;
  } catch (error: any) {
    console.error(`❌ Strava API error (${endpoint}):`, error.response?.data);
    return null;
  }
}

// Function to get participants of a specific activity
// Note: Strava's API only provides the activity creator (athlete) in the activity details.
// For group activities, it doesn't expose other participant IDs.
// This function returns the activity creator's ID as the primary participant.
export async function getActivityParticipants(activityId: number): Promise<number[]> {
  const activity = await makeStravaRequest(`/activities/${activityId}`);
  if (!activity || activity.athlete_count <= 1) {
    return [];
  }
  // Return the activity creator's athlete ID
  return activity.athlete?.id ? [activity.athlete.id] : [];
}
