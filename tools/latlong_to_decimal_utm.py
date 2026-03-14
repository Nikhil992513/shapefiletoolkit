"""
Tool for converting Lat/Long in DMS or Decimal to Decimal Degrees and UTM, output as CSV.
"""

import streamlit as st
import pandas as pd
import numpy as np
from core.base_tool import BaseTool
from core.utils_io import create_temp_directory
from pyproj import Proj, Transformer
import re

# Helper: DMS to Decimal Degrees

def dms_to_dd(dms_str):
    # Accepts formats like 78°55'44.294"E or 78 55 44.294 E or 78.92897
    dms_str = str(dms_str).strip()
    if re.match(r"^-?\\d+(?:\\.\\d+)?$", dms_str):
        return float(dms_str)
    dms = re.split(r"[°'\"\s]+", dms_str)
    dms = [d for d in dms if d]
    if len(dms) < 3:
        return np.nan
    deg, mins, secs = map(float, dms[:3])
    sign = -1 if '-' in dms_str or any(s in dms_str for s in ['W', 'S']) else 1
    return sign * (abs(deg) + mins/60 + secs/3600)

# Helper: Lat/Lon to UTM

def latlon_to_utm(lat, lon):
    if np.isnan(lat) or np.isnan(lon):
        return np.nan, np.nan, ''
    zone_number = int((lon + 180) / 6) + 1
    proj_str = f"+proj=utm +zone={zone_number} +datum=WGS84 +units=m +no_defs"
    proj = Proj(proj_str)
    easting, northing = proj(lon, lat)
    return easting, northing, zone_number

class LatLongToDecimalUTMTool(BaseTool):
    @property
    def name(self):
        return "LatLong to Decimal/UTM"

    @property
    def description(self):
        return "Convert latitude/longitude in DMS or decimal to decimal degrees and UTM. Output as CSV."

    @property
    def icon(self):
        return "🌐"

    def render_ui(self):
        st.header(f"{self.icon} {self.name}")
        st.markdown(self.description)
        st.divider()

        st.subheader("📁 Step 1: Upload CSV")
        uploaded_file = st.file_uploader(
            "Upload a CSV file with latitude and longitude columns",
            type=['csv'],
            key="latlong_csv_upload"
        )

        if uploaded_file is not None:
            # Try utf-8, fallback to latin1
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='latin1')
            st.success(f"✅ Uploaded: {uploaded_file.name} ({len(df)} rows)")
            st.write(df.head())

            st.subheader("⚙️ Step 2: Column Selection")
            lat_col = st.selectbox("Select Latitude column", df.columns, key="lat_col")
            lon_col = st.selectbox("Select Longitude column", df.columns, key="lon_col")

            st.subheader("🚀 Step 3: Convert and Download")
            if st.button("Convert and Download CSV", type="primary", use_container_width=True):
                with st.spinner("Converting coordinates..."):
                    df['lat_dd'] = df[lat_col].apply(dms_to_dd)
                    df['lon_dd'] = df[lon_col].apply(dms_to_dd)
                    utm_results = df.apply(lambda row: latlon_to_utm(row['lat_dd'], row['lon_dd']), axis=1)
                    df['utm_easting'] = utm_results.apply(lambda x: x[0])
                    df['utm_northing'] = utm_results.apply(lambda x: x[1])
                    df['utm_zone'] = utm_results.apply(lambda x: x[2])
                    with create_temp_directory() as temp_dir:
                        out_path = f"{temp_dir}/latlong_converted.csv"
                        df.to_csv(out_path, index=False)
                        with open(out_path, 'rb') as f:
                            st.download_button(
                                label="⬇️ Download Converted CSV",
                                data=f.read(),
                                file_name="latlong_converted.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                    st.success("✅ Conversion complete!")
        else:
            st.info("👆 Upload a CSV file to get started.")
