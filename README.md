# Strava Athlete Rides With Me 🚴

A tool to find all cycling/running activities you've done with a specific athlete on Strava over 20+ years. Built as a heartfelt gift to celebrate shared adventures.

## 📖 The Story

My daughters surprised me with a beautiful framed composite image of all my cycling routes from the previous year—a masterpiece they'd spent weeks painstakingly manually downloading, converting, and stitching together in a design app.

Inspired by their creativity, I wanted to create something similar but better: **a visual record of all the unique rides my best mate and I have completed together over the last 20 years.** Rather than spending weeks on manual work, I built this tool in a weekend to automatically find and compile our shared activities directly from Strava's API.

The result: a dataset of shared adventures that could be used to generate a beautiful visualization—a perfect present for his 65th birthday celebrating two decades of friendship, fitness, and fun on the bike.

## ✨ What It Does

This tool:
- ✅ Connects to your Strava account via OAuth
- ✅ Scans your entire activity history
- ✅ Finds all activities with a specific athlete (or athletes)
- ✅ Displays results in an organized table with activity name, date, and participants
- ✅ Respects Strava's rate limits with automatic backoff

## 🏗️ How It Works

1. **Authentication**: Uses Strava OAuth token refresh flow to maintain a valid access token
2. **Activity Fetching**: Iterates through your activity history page by page (30 activities per page)
3. **Participant Detection**: For each multi-athlete activity, checks if your target athlete participated
4. **Rate Limiting**: Implements exponential backoff if Strava's API rate limits are hit
5. **Results**: Outputs all found shared activities in a formatted table

### Strava API Limitations

⚠️ **Important**: Strava's API only provides the activity creator's ID in the activity details endpoint. For group activities, individual participant lists are not exposed through the standard API. This tool returns activities where the target athlete was the creator. For activities where you're looking for shared group rides, you may need additional manual verification through Strava's web interface.

## 📋 Requirements

- **Node.js**: v16 or higher
- **npm**: comes with Node.js
- **Strava Account**: with activity history
- **Strava API Credentials**: (see Setup section)

## 🚀 Setup Instructions

### Step 1: Create Strava API Application

1. Go to [Strava Settings > API](https://www.strava.com/settings/api)
2. Create a new application (fill in the form):
   - **Application Name**: `Strava Athlete Rides` (or your preferred name)
   - **Website**: `http://localhost` (for personal use)
   - **Authorization Callback Domain**: `localhost`
3. Note your **Client ID** and **Client Secret**

### Step 2: Get Refresh Token

To obtain your refresh token, you'll need to complete OAuth flow. Here's a simple method:

1. **Replace the values** in this authorization URL (use your Client ID):
   ```
   https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read_all
   ```

2. **Visit the URL** in your browser and authorize the app
3. You'll be redirected to a URL like:
   ```
   http://localhost/exchange_token?code=abc123...&scope=activity:read_all
   ```
4. **Save the `code` value** - you'll use it in the next step

5. **Exchange the code for tokens** using curl or Postman:
   ```bash
   curl -X POST https://www.strava.com/api/v3/oauth/token \
     -d client_id=YOUR_CLIENT_ID \
     -d client_secret=YOUR_CLIENT_SECRET \
     -d code=YOUR_CODE \
     -d grant_type=authorization_code
   ```

6. The response will include your **`refresh_token`** - save this securely

### Step 3: Get Target Athlete ID(s)

1. Go to [Strava](https://www.strava.com)
2. Visit the athlete's profile you want to search for
3. Look at the URL: `strava.com/athletes/12345` - the number is their Athlete ID
4. Note down one or more athlete IDs (comma-separated for multiple athletes)

### Step 4: Configure Environment

1. Copy `.example-env` to `.env`:
   ```bash
   cp .example-env .env
   ```

2. Edit `.env` and add your values:
   ```env
   STRAVA_CLIENT_ID=your_client_id
   STRAVA_CLIENT_SECRET=your_client_secret
   STRAVA_REFRESH_TOKEN=your_refresh_token
   TARGET_ATHLETES=12345,67890
   ```

3. **NEVER commit `.env` to version control** - it contains sensitive credentials

### Step 5: Install Dependencies

```bash
npm install
```

### Step 6: Compile TypeScript (Optional)

```bash
npm run build
```

## ▶️ Usage

Run the tool:

```bash
npm start
```

Or directly with ts-node:

```bash
npx ts-node src/index.ts
```

### Example Output

```
Searching for shared activities...
  Fetched 30 activities from page 1
  Fetched 30 activities from page 2
  Fetched 12 activities from page 3
✅ Found 47 shared activities:

┌─────────────────┬──────────────────────┬──────────────────────┬──────────────────┐
│ (index)         │ id                   │ name                 │ date             │
├─────────────────┼──────────────────────┼──────────────────────┼──────────────────┤
│ 0               │ 5123456789           │ Morning Ride         │ 2024-03-15       │
│ 1               │ 5987654321           │ Weekend Adventure    │ 2024-03-10       │
│ 2               │ 5555555555           │ Spring Tour          │ 2024-03-05       │
└─────────────────┴──────────────────────┴──────────────────────┴──────────────────┘
```

## 🔒 Security & Privacy

✅ **Safe Practices**:
- Keep Strava credentials in `.env`
- `.env` is ignored by git and should never be committed
- All sensitive data stays in environment variables
- No credentials are logged to console
- Tokens are only used for API authentication

If credentials are ever exposed, immediately regenerate your Strava API credentials and update your local `.env`.

## 🐛 Troubleshooting

### "Missing Strava API credentials in .env file!"

**Solution**: Ensure all three variables are set in `.env`:
- `STRAVA_CLIENT_ID`
- `STRAVA_CLIENT_SECRET`
- `STRAVA_REFRESH_TOKEN`

### "Rate limit exceeded. Waiting..."

**What's happening**: Strava's API has rate limits (~600 requests per 15 minutes). The tool will automatically wait and retry.

**To speed up**: Reduce the number of target athletes or run during off-peak times.

### "No shared activities found"

**Possible causes**:
- The target athlete hasn't done any activities with you that were logged in Strava
- The athlete's ID is incorrect
- Activities might be private and not visible to the API

**Solution**: Verify the athlete ID and check Strava's privacy settings

### "Error refreshing Strava token"

**Causes**: Your refresh token has expired or is invalid

**Solution**:
1. Go back to Step 2 (Get Refresh Token) in Setup
2. Regenerate your refresh token
3. Update `.env`

## 📊 Use Cases for Results

Once you have the list of shared activities, you can:

- 📸 **Create a visualization**: Generate a map of all shared route outlines
- 📈 **Create statistics**: Total distance, elevation, time spent together
- 🎨 **Design a gift**: Frame the data as a beautiful infographic or print
- 📊 **Generate reports**: Analyze trends over 20+ years

## 🛠️ Project Structure

```
strava-athlete-rides-with-me/
├── src/
│   ├── index.ts              # Main entry point - find shared activities
│   ├── authService.ts        # OAuth token management
│   └── stravaService.ts      # Strava API calls
├── scripts/
│   ├── rename-gpx.py         # Convert .fit.gz bulk export → date-named GPX files
│   ├── export_gpx_to_svg.py  # Render GPX routes to SVG images via QGIS
│   ├── svgs-to-pdf.py        # Combine SVGs into a print-ready A2 PDF grid
│   └── run_qgis_script.bat   # Windows launcher for the QGIS export script
├── data/
│   ├── activities/            # Raw Strava bulk export (.fit.gz, .gpx)
│   │   └── converted/        # Auto-converted date-named GPX files + activities.csv
│   ├── gpx/                   # Curated GPX files for the final visualization
│   ├── svg/                   # Generated SVG route images (one per ride)
│   └── combined/              # Final combined PDF output
├── .env                       # Your credentials (NEVER commit)
├── .env.example               # Template for .env
├── .gitignore
├── package.json
├── tsconfig.json
└── README.md
```

## 🗺️ Data Transformation Pipeline

The end-to-end process goes from raw Strava data to a framed print. There are two data sources — **automated bulk export** and **manually created GPX files** — which are merged into the final curated set.

### Overview

```
Strava Bulk Export (.fit.gz)  ──→  rename-gpx.py  ──→  date-named GPX files
                                                              │
Manual GPX files (pre-Strava / holidays)  ─────────────────── ┤
                                                              ▼
                                                    Curated GPX set (data/gpx/)
                                                              │
                                                    export_gpx_to_svg.py (QGIS)
                                                              │
                                                              ▼
                                                    SVG route images (data/svg/)
                                                              │
                                                    svgs-to-pdf.py
                                                              │
                                                              ▼
                                                    Print-ready A2 PDF grid
```

### Step 1: Find Shared Activities

Run `npm start` to query the Strava API and identify all rides shared with the target athlete. This produces a list of activity IDs and dates.

### Step 2: Bulk Export from Strava

Download your full Strava data export (Settings → My Account → Download or Delete Your Account → Request Your Archive). This gives a ZIP of all activities as `.fit.gz` and `.gpx` files, which go into `data/activities/`.

### Step 3: Convert FIT Files to GPX

```bash
python scripts/rename-gpx.py
```

This script:
- Decompresses each `.fit.gz` file
- Extracts metadata (date, distance, elevation) from the FIT session data
- Converts timestamps from UTC to NZ time (`Pacific/Auckland`) to get the local activity date
- Uses [GPSBabel](https://www.gpsbabel.org/) to convert `.fit` → `.gpx`
- Renames output files by date (`YYYYMMDD.gpx`)
- Writes a summary CSV (`activities.csv`) with distance and elevation for each ride

**Requirements**: Python 3, `fitparse`, `pytz`, [GPSBabel](https://www.gpsbabel.org/) installed at `C:\Program Files\GPSBabel\gpsbabel.exe`

### Step 4: Manually Created GPX Files

Some rides predate Strava or were recorded on devices that didn't sync. These were manually created as GPX files and placed directly into `data/gpx/`:

- **Pre-Strava rides (2010)**: Monthly GPX files (`20100101.gpx` – `20101001.gpx`) reconstructed from old GPS device data or ride logs. These represent the earliest shared rides before either athlete used Strava.
- **Holiday / trip rides**: Multi-day cycling trips (e.g., consecutive dates in Feb–Mar 2018) where GPX tracks were exported directly from the Strava web interface or a GPS device rather than through the bulk export pipeline.
- **Duplicate date handling**: When multiple rides occur on the same date, files use a suffix format (`20210412.1.gpx`, `20210412.2.gpx`).

### Step 5: Curate the Final GPX Set

Manually copy the shared rides from `data/activities/converted/` into `data/gpx/`, alongside any manually created GPX files. The `data/gpx/` folder should contain only the ~108 rides that will appear in the final print — one GPX file per shared ride, named by date.

### Step 6: Convert GPX to SVG

```bash
scripts\run_qgis_script.bat
```

Or run directly via QGIS Python:
```bash
C:\OSGeo4W\bin\python-qgis.bat scripts/export_gpx_to_svg.py
```

This script:
- Opens each GPX file as a QGIS vector layer
- Renders the track in Strava orange (`#FC4C02`) on a transparent background
- Exports a 1000×1000 SVG for each ride into `data/svg/`

**Requirements**: [QGIS](https://qgis.org/) installed via OSGeo4W at `C:\OSGeo4W\`

### Step 7: Combine SVGs into Print PDF

```bash
python scripts/svgs-to-pdf.py
```

This script:
- Loads all SVGs sorted by date (newest first)
- Arranges them in a 9×12 grid (108 rides) on a black A2 page
- Scales each route proportionally to fit its grid cell
- Outputs a print-ready PDF at `data/combined/combined_a2_1page_black.pdf`

**Requirements**: Python 3, `svglib`, `reportlab`

## 💡 Tips for Best Results

1. **Start with a single athlete** to test the setup before adding multiple
2. **Run during off-peak hours** if you hit rate limits
3. **Check date formats** in the output to verify results are correct
4. **Export results**: Pipe output to a file for further processing:
   ```bash
   npm start > shared_activities.txt 2>&1
   ```

## 🤝 Contributing

This is a personal project created in a weekend, but improvements are welcome! Feel free to:

- Report bugs or issues
- Suggest improvements for rate limiting or performance
- Add support for additional Strava metrics
- Improve the visualization pipeline

## 📝 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## 🎉 Acknowledgments

Built with ❤️ for cycling buddies, inspired by a daughters' handmade gift.

---

**Questions?** Check the Troubleshooting section above or review the inline code comments for implementation details.
