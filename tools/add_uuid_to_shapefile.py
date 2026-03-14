"""
Tool for adding a UUID column to a shapefile with a custom column name.
"""

import streamlit as st
import geopandas as gpd
import uuid
from core.base_tool import BaseTool
from core.utils_io import get_gdf_from_upload, create_temp_directory, create_shapefile_zip

class AddUUIDToShapefileTool(BaseTool):
    """
    Tool for adding a UUID column to a shapefile.
    """
    @property
    def name(self) -> str:
        return "Add UUID Column"

    @property
    def description(self) -> str:
        return "Add a column of UUIDs to your shapefile with a custom column name."

    @property
    def icon(self) -> str:
        return "🆔"

    def render_ui(self) -> None:
        st.header(f"{self.icon} {self.name}")
        st.markdown(self.description)
        st.divider()

        st.subheader("📁 Step 1: Upload Shapefile")
        uploaded_file = st.file_uploader(
            "Upload a ZIP file containing your shapefile",
            type=['zip'],
            key="uuid_upload"
        )

        if uploaded_file is not None:
            with create_temp_directory() as temp_dir:
                gdf, message = get_gdf_from_upload(uploaded_file, temp_dir)
                if gdf is None:
                    st.error(f"❌ {message}")
                    return
                st.success(f"✅ {message}")

                st.subheader("⚙️ Step 2: UUID Column Name")
                uuid_col = st.text_input(
                    "Enter the name for the UUID column",
                    value="uuid",
                    help="E.g. village_uuid, district_uuid, mandal_uuid, etc."
                )

                st.subheader("🚀 Step 3: Add UUIDs and Download")
                if st.button("Add UUIDs", type="primary", use_container_width=True):
                    try:
                        with st.spinner("Adding UUIDs..."):
                            gdf[uuid_col] = [str(uuid.uuid4()) for _ in range(len(gdf))]
                            output_path = create_shapefile_zip(gdf, "uuid_added", temp_dir)
                            with open(output_path, 'rb') as f:
                                output_data = f.read()
                            st.success("✅ UUIDs added successfully!")
                            st.download_button(
                                label="⬇️ Download Shapefile with UUIDs",
                                data=output_data,
                                file_name="uuid_added_shapefile.zip",
                                mime="application/zip",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            st.info("👆 Upload a shapefile ZIP file to get started.")
