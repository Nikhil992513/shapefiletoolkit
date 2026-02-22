"""
Delete Duplicate Geometries Tool

Removes duplicate overlapping polygon geometries where the overlapping
geometry contains the same area (within configured tolerances), similar
to QGIS "Delete duplicate geometries" behavior.
"""

import streamlit as st
import geopandas as gpd
from typing import Tuple
from core.base_tool import BaseTool
from core.utils_io import get_gdf_from_upload, create_temp_directory, create_shapefile_zip
from core.utils_geo import get_crs_info


class DeleteDuplicateGeometriesTool(BaseTool):
    @property
    def name(self) -> str:
        return "Delete Duplicate Geometries"

    @property
    def description(self) -> str:
        return "Remove duplicate/overlapping polygon geometries that contain the same area."

    @property
    def icon(self) -> str:
        return "🧹"

    def render_ui(self) -> None:
        st.header(f"{self.icon} {self.name}")
        st.markdown(self.description)
        st.divider()

        st.subheader("📁 Step 1: Upload Shapefile")
        uploaded_file = st.file_uploader(
            "Upload a ZIP file containing a single polygon shapefile",
            type=["zip"],
            key="delete_dup_upload"
        )

        if uploaded_file is None:
            return

        with create_temp_directory() as temp_dir:
            gdf, msg = get_gdf_from_upload(uploaded_file, temp_dir)
            if gdf is None:
                st.error(msg)
                return

            st.success(msg)

            # Basic info
            st.subheader("📊 Shapefile Info")
            crs_info = get_crs_info(gdf)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Features", len(gdf))
            with col2:
                st.write(f"CRS: {crs_info['epsg']} - {crs_info['name']}")

            # Ensure polygon geometries
            geom_types = gdf.geometry.type.unique()
            if not all(gt in ["Polygon", "MultiPolygon"] for gt in geom_types):
                st.error("This tool only supports Polygon / MultiPolygon geometries.")
                return

            with st.expander("📋 Sample attributes", expanded=False):
                st.dataframe(gdf.head(10), use_container_width=True)

            st.subheader("⚙️ Settings")
            st.markdown("Two polygons are considered duplicates when the intersection area equals the smaller polygon's area (within tolerances).")

            area_tolerance = st.number_input(
                "Area difference tolerance (%)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1,
                help="Allowed percent difference between areas to consider equal (0 = exact)"
            )

            overlap_threshold = st.number_input(
                "Overlap threshold (%)",
                min_value=0.0,
                max_value=100.0,
                value=100.0,
                step=0.1,
                help="Minimum intersection / smaller-area percent required to call as duplicate (100 = complete containment)"
            )

            attr_strategy = st.radio(
                "When duplicates are removed, keep attributes from:",
                ["First occurrence", "Last occurrence"],
                index=0
            )

            if st.button("Run Delete Duplicate Geometries", type="primary"):
                try:
                    result_gdf, report = self._delete_duplicates(
                        gdf,
                        area_tol_pct=area_tolerance,
                        overlap_pct_threshold=overlap_threshold,
                        keep_first=(attr_strategy == "First occurrence")
                    )

                    st.success("Processing complete")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Original", report["total"])
                    with col2:
                        st.metric("Removed", report["removed"])
                    with col3:
                        st.metric("Remaining", report["remaining"])

                    with st.expander("📋 Details", expanded=True):
                        st.write(report["details"])

                    # Downloads
                    base_name = f"dedup_{uploaded_file.name.replace('.zip','') }"
                    zip_path = create_shapefile_zip(result_gdf, base_name, temp_dir)
                    with open(zip_path, "rb") as f:
                        st.download_button(
                            label="Download deduplicated shapefile (ZIP)",
                            data=f.read(),
                            file_name=f"{base_name}.zip",
                            mime="application/zip"
                        )

                    csv_data = result_gdf.drop(columns=["geometry"]).to_csv(index=False)
                    st.download_button(
                        label="Download attributes as CSV",
                        data=csv_data,
                        file_name=f"{base_name}.csv",
                        mime="text/csv"
                    )

                except Exception as e:
                    st.error(f"Error: {str(e)}")

    def _delete_duplicates(
        self,
        gdf: gpd.GeoDataFrame,
        area_tol_pct: float = 0.0,
        overlap_pct_threshold: float = 100.0,
        keep_first: bool = True,
    ) -> Tuple[gpd.GeoDataFrame, dict]:
        """
        Core duplicate-deletion logic.
        - Uses spatial index for candidates
        - Two features considered duplicates if:
            * Areas differ by <= area_tol_pct of the smaller area
            * Intersection area / smaller area >= overlap_pct_threshold
        """
        df = gdf.copy().reset_index(drop=True)
        df["_area"] = df.geometry.area

        sindex = df.sindex
        n = len(df)
        to_remove = set()
        groups = []

        for i in range(n):
            if i in to_remove:
                continue
            geom_i = df.at[i, "geometry"]
            area_i = df.at[i, "_area"]

            # find candidates whose bbox intersects
            candidate_idxs = list(sindex.intersection(geom_i.bounds))
            group = [i]

            for j in candidate_idxs:
                if j <= i or j in to_remove:
                    continue
                geom_j = df.at[j, "geometry"]
                area_j = df.at[j, "_area"]

                if area_i == 0 or area_j == 0:
                    continue

                # area difference relative to smaller polygon
                area_diff_pct = abs(area_i - area_j) / min(area_i, area_j) * 100.0
                if area_diff_pct > area_tol_pct:
                    continue

                inter = geom_i.intersection(geom_j)
                if inter.is_empty:
                    continue

                overlap_pct = inter.area / min(area_i, area_j) * 100.0
                if overlap_pct >= overlap_pct_threshold:
                    group.append(j)
                    to_remove.add(j)

            if len(group) > 1:
                groups.append(group)

        # Decide removals based on keep_first
        removed_indices = []
        for grp in groups:
            if keep_first:
                # keep first entry, remove others
                removed_indices.extend(grp[1:])
            else:
                removed_indices.extend(grp[:-1])

        removed_set = set(removed_indices)
        result_df = df.loc[[i for i in range(len(df)) if i not in removed_set]].copy()
        result_df = result_df.drop(columns=["_area"]).reset_index(drop=True)

        report = {
            "total": n,
            "removed": len(removed_set),
            "remaining": len(result_df),
            "groups": len(groups),
            "details": f"Found {len(groups)} duplicate group(s). Removed {len(removed_set)} feature(s)."
        }

        return result_df, report
