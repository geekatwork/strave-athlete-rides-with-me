import os
import gzip
import shutil
import datetime
from fitparse import FitFile # type: ignore
import subprocess
import pytz # type: ignore
import csv
from datetime import timezone

# --- Paths ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

input_folder = os.path.join(project_root, "data", "activities")
output_folder = os.path.join(project_root, "data", "activities", "converted")
temp_folder = os.path.join(output_folder, "temp")
csv_output = os.path.join(output_folder, "activities.csv")
gpsbabel_path = r"C:\Program Files\GPSBabel\gpsbabel.exe"

os.makedirs(output_folder, exist_ok=True)
os.makedirs(temp_folder, exist_ok=True)

# Clear the output folder
for f in os.listdir(output_folder):
    path = os.path.join(output_folder, f)
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
os.makedirs(temp_folder, exist_ok=True)

# --- Extract metadata from .fit file ---
def extract_metadata(fit_path):
    fitfile = FitFile(fit_path)
    distance = None
    elevation_gain = None
    activity_date = None

    for record in fitfile.get_messages("session"):
        timestamp = record.get_value("start_time")
        if timestamp:
            # Convert from UTC to NZ time
            start_time_utc = timestamp.replace(tzinfo=timezone.utc)
            nz_time = start_time_utc.astimezone(pytz.timezone("Pacific/Auckland"))
            activity_date = nz_time.strftime("%Y%m%d")

        dist = record.get_value("total_distance")
        if dist is not None:
            distance = round(dist / 1000, 2)  # convert meters to km

        elev = record.get_value("total_ascent")
        if elev is not None:
            elevation_gain = int(elev)

    return activity_date, distance, elevation_gain

# --- Prepare CSV ---
with open(csv_output, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Filename", "Distance_km", "Elevation_gain_m"])

    # --- Process all .fit.gz files ---
    for file in os.listdir(input_folder):
        if file.endswith(".fit.gz"):
            gz_path = os.path.join(input_folder, file)
            temp_fit = os.path.join(temp_folder, os.path.splitext(file)[0])

            # Unzip .fit.gz to .fit
            with gzip.open(gz_path, 'rb') as f_in, open(temp_fit, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

            # Get metadata from .fit
            try:
                date_str, distance_km, elevation_m = extract_metadata(temp_fit)
            except Exception as e:
                print(f"Error reading {file}: {e}")
                continue

            gpx_output = os.path.join(output_folder, f"{date_str}.gpx")

            # Convert to GPX using GPSBabel
            cmd = [
                gpsbabel_path,
                "-i", "garmin_fit",
                "-f", temp_fit,
                "-o", "gpx",
                "-F", gpx_output
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Failed: {file}\n{result.stderr}")
                continue
            else:
                print(f"Converted: {file} → {os.path.basename(gpx_output)}")

            # Write CSV row
            writer.writerow([f"{date_str}.gpx", distance_km or "", elevation_m or ""])

# --- Cleanup ---
shutil.rmtree(temp_folder)
