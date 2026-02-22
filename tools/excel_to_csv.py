"""
Tool for converting Excel sheets to CSV format.
"""

import os
import io
import pandas as pd
import streamlit as st
from typing import Optional, List
from core.base_tool import BaseTool
from core.utils_io import create_temp_directory


class ExcelToCSVTool(BaseTool):
    @property
    def name(self) -> str:
        return "Excel to CSV"

    @property
    def description(self) -> str:
        return "Convert an Excel sheet (.xls/.xlsx) to CSV with selectable separator and columns."

    @property
    def icon(self) -> str:
        return "📥➡️📄"

    def render_ui(self) -> None:
        st.header(f"{self.icon} {self.name}")
        st.markdown(self.description)
        st.divider()

        if 'excel_df' not in st.session_state:
            st.session_state.excel_df = None
            st.session_state.excel_filename = None
            st.session_state.excel_sheet_names = []
            st.session_state.excel_selected_sheet = None

        uploaded = st.file_uploader(
            "Upload an Excel file",
            type=['xls', 'xlsx'],
            help="Upload an .xls or .xlsx file",
            key="excel_upload"
        )

        if uploaded is None:
            # clear state
            if st.session_state.excel_df is not None:
                st.session_state.excel_df = None
                st.session_state.excel_filename = None
                st.session_state.excel_sheet_names = []
                st.session_state.excel_selected_sheet = None
            return

        # If new file uploaded
        if st.session_state.excel_filename != uploaded.name:
            try:
                with st.spinner("Reading Excel file..."):
                    # Use ExcelFile to get sheet names without reading all sheets
                    excel_file = pd.ExcelFile(uploaded)
                    sheet_names = excel_file.sheet_names

                    st.session_state.excel_sheet_names = sheet_names
                    st.session_state.excel_filename = uploaded.name
                    # default to first sheet
                    st.session_state.excel_selected_sheet = sheet_names[0] if sheet_names else None
                    st.session_state.excel_df = None

                    st.success(f"Loaded workbook with {len(sheet_names)} sheet(s)")
            except Exception as e:
                st.error(f"Error reading Excel file: {str(e)}")
                return

        # Sheet selection
        if st.session_state.excel_sheet_names:
            sheet = st.selectbox(
                "Select sheet",
                options=st.session_state.excel_sheet_names,
                index=st.session_state.excel_sheet_names.index(st.session_state.excel_selected_sheet) if st.session_state.excel_selected_sheet in st.session_state.excel_sheet_names else 0,
                key="excel_sheet_select"
            )

            st.session_state.excel_selected_sheet = sheet

            # Load the selected sheet into a DataFrame
            try:
                df = pd.read_excel(uploaded, sheet_name=sheet)
                st.session_state.excel_df = df
            except Exception as e:
                st.error(f"Error loading sheet: {str(e)}")
                return

            # Preview
            st.subheader("📋 Preview")
            if st.session_state.excel_df is None or st.session_state.excel_df.empty:
                st.warning("Selected sheet is empty.")
                return

            preview_df = st.session_state.excel_df.head(10)
            st.dataframe(preview_df, use_container_width=True)
            st.caption(f"Showing first 10 of {len(st.session_state.excel_df)} rows")

            # Export options
            st.subheader("⚙️ Export Options")
            separator_options = {
                "Comma (,)": ",",
                "Semicolon (;)": ";",
                "Pipe (|)": "|",
                "Tab": "\t",
                "Custom": "custom",
            }

            sep_choice = st.selectbox("Output Separator", options=list(separator_options.keys()), index=0, key="excel_sep_choice")
            if sep_choice == "Custom":
                custom_sep = st.text_input("Enter custom separator", value=",", max_chars=5, key="excel_custom_sep")
                separator = custom_sep
            else:
                separator = separator_options[sep_choice]

            select_all = st.checkbox("Select all columns", value=True, key="excel_select_all")
            cols = list(st.session_state.excel_df.columns)
            if select_all:
                selected_columns = cols
            else:
                selected_columns = st.multiselect("Select columns to export", options=cols, default=cols, key="excel_columns_select")

            if not selected_columns:
                st.warning("Please select at least one column to export.")
                return

            # Generate
            st.subheader("💾 Export")
            if st.button("Convert to CSV", type="primary", use_container_width=True, key="excel_convert_btn"):
                try:
                    with st.spinner("Generating CSV..."):
                        df_out = st.session_state.excel_df[selected_columns].copy()

                        # Write to temp file and provide download
                        with create_temp_directory() as tmpdir:
                            out_path = os.path.join(tmpdir, "exported_sheet.csv")
                            df_out.to_csv(out_path, sep=separator, index=False)

                            with open(out_path, 'rb') as f:
                                csv_bytes = f.read()

                        st.success("CSV generated")
                        st.download_button(
                            label="⬇️ Download CSV",
                            data=csv_bytes,
                            file_name=f"{os.path.splitext(st.session_state.excel_filename)[0]}_{sheet}.csv",
                            mime="text/csv",
                            use_container_width=True,
                            key="excel_download_btn"
                        )
                except Exception as e:
                    st.error(f"Error generating CSV: {str(e)}")
