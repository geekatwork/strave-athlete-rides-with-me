import { getActivityParticipants } from "./stravaService";
import dotenv from "dotenv";
import axios from "axios";
import { getAccessToken } from "./authService";

dotenv.config();

// ⚠️ SECURITY: Never log TARGET_ATHLETE_IDS as it may be used to identify individuals
const TARGET_ATHLETE_IDS = process.env.TARGET_ATHLETES
  ? process.env.TARGET_ATHLETES.split(",").map((id) => {
      const parsed = Number(id.trim());
      if (isNaN(parsed)) {
        throw new Error("❌ Invalid athlete ID in TARGET_ATHLETES - must be comma-separated numbers");
      }
      return parsed;
    })
  : [];

if (TARGET_ATHLETE_IDS.length === 0) {
  throw new Error("❌ Missing TARGET_ATHLETES in .env file!");
}

interface SharedActivity {
  id: number;
  name: string;
  date: string;
  athletes: number[];
}

// Helper function to delay execution
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

async function findSharedActivities() {
  console.log(`Searching for shared activities...`);

  let page = 1;
  const perPage = 30;
  const sharedActivities: SharedActivity[] = [];

  try {
    // Fetch activities page by page
    while (true) {
      const token = await getAccessToken(); // Ensure a valid token
      const headers = { Authorization: `Bearer ${token}` };

      const activities = await fetchActivities(page, perPage, headers);

      if (activities.length === 0) break; // Exit loop if no activities on this page
      
      console.log(`  Fetched ${activities.length} activities from page ${page}`);

      // Process each activity's participants
      for (const activity of activities) {
        if (activity.athlete_count > 1) {
          const participants = await getActivityParticipants(activity.id);
          const sharedWith = participants.filter((id) =>
            TARGET_ATHLETE_IDS.includes(id)
          );

          if (sharedWith.length > 0) {
            sharedActivities.push({
              id: activity.id,
              name: activity.name,
              date: activity.start_date_local,
              athletes: sharedWith,
            });
          }
        }
      }

      page++; // Go to the next page
    }

    // Output the shared activities
    if (sharedActivities.length > 0) {
      console.log(`\n✅ Found ${sharedActivities.length} shared activities:`);
      console.table(sharedActivities);
    } else {
      console.log("\n✅ No shared activities found.");
    }
  } catch (error: any) {
    console.error("❌ Error finding shared activities:", error.message);
    process.exit(1);
  }
}

// Fetch activities page by page with rate limit handling
async function fetchActivities(page: number, perPage: number, headers: Record<string, string>, retries = 0): Promise<any[]> {
    try {
      const response = await axios.get("https://www.strava.com/api/v3/athlete/activities", {
        headers,
        params: { page, per_page: perPage },
      });
  
      // Return activities data
      return response.data;
    } catch (error: any) {
      if (error.response && error.response.status === 429) {
        // Get retry time from the 'Retry-After' header (in seconds)
        const retryAfter = error.response.headers["retry-after"] || 900;
        const waitTime = parseInt(retryAfter, 10) * 1000;
  
        // Exponential backoff strategy
        const backoffTime = Math.pow(2, retries) * 1000;
        const totalWaitTime = Math.max(waitTime, backoffTime); // Choose the larger of the two
  
        console.log(`❌ Rate limit exceeded. Waiting ${Math.round(totalWaitTime / 60000)} minute(s)...`);
  
        await delay(totalWaitTime + 1000); // Wait until rate limit resets or backoff time elapses
  
        // Retry after waiting
        return await fetchActivities(page, perPage, headers, retries + 1);
      }
  
      console.error(`❌ Error fetching activities on page ${page}: ${error.message}`);
      return [];
    }
  }
  
  findSharedActivities();