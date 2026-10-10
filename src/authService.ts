import axios from "axios";
import dotenv from "dotenv";

dotenv.config();

const STRAVA_TOKEN_URL = "https://www.strava.com/api/v3/oauth/token";

const CLIENT_ID = process.env.STRAVA_CLIENT_ID;
const CLIENT_SECRET = process.env.STRAVA_CLIENT_SECRET;
let REFRESH_TOKEN = process.env.STRAVA_REFRESH_TOKEN;
let ACCESS_TOKEN = "";

// ⚠️ SECURITY: Never log CLIENT_ID, CLIENT_SECRET, or REFRESH_TOKEN
// These are sensitive credentials that should only exist in .env files
if (!CLIENT_ID || !CLIENT_SECRET || !REFRESH_TOKEN) {
  throw new Error("❌ Missing Strava API credentials in .env file!");
}

// Function to refresh the access token
export async function refreshAccessToken(): Promise<string> {
  try {
    const response = await axios.post(STRAVA_TOKEN_URL, {
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
      refresh_token: REFRESH_TOKEN,
      grant_type: "refresh_token",
    });

    ACCESS_TOKEN = response.data.access_token;
    REFRESH_TOKEN = response.data.refresh_token; // Update refresh token in memory

    // ⚠️ NOTE: The new REFRESH_TOKEN is stored in memory only.
    // On app restart, the refreshed token will be lost and .env will be used.
    // For production use with persistent token storage, consider persisting to a .env file or secure storage.

    console.log("✅ Strava Access Token Refreshed!");
    return ACCESS_TOKEN;
  } catch (error: any) {
    console.error("❌ Error refreshing Strava token:", error.response?.data);
    throw new Error("Failed to refresh Strava access token.");
  }
}

// Function to get the current access token (refresh if needed)
export async function getAccessToken(): Promise<string> {
  if (!ACCESS_TOKEN) {
    return await refreshAccessToken();
  }
  return ACCESS_TOKEN;
}
