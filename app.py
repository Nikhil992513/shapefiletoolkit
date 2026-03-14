"""
Shapefile Toolkit - Main Streamlit Application

A production-ready web application for performing common shapefile operations.
"""

import streamlit as st
from typing import Dict, Any

# Import tools
from tools import (
    ShapefileToCSVTool,
    MergeShapefilesTool,
    AddShapefilesTool,
    ReprojectShapefileTool,
    ExcelToCSVTool,
)

# Newly added duplicate-deletion tool
from tools import DeleteDuplicateGeometriesTool

# Import UI components5
from ui.homepage import render_homepage
from ui.layout import apply_custom_css


# ============================================================================
# Configuration and Setup
# ============================================================================

st.set_page_config( 
    page_title="Shapefile Toolkit",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': """
            # Shapefile Toolkit
            
            A powerful web application for performing common shapefile operations.
            
            **Version:** 1.0.0
            
            Made with ❤️ by ** NikhilReddy MaliReddy**
        """
    }
    
)
def futuristic_css():
     st.markdown("""
    <style>
    #particles-js {
    position: fixed;
    width: 100%;
    height: 100%;
    z-index: -1;
}
    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #000000);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: white;
    }

    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
.stApp {
    animation: fadeInPage 1.5s ease-in;
}

@keyframes fadeInPage {
    from { opacity: 0; }
    to { opacity: 1; }
}
    .card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 30px;
    transition: 0.4s ease;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 0 20px rgba(0,255,255,0.1);
    animation: float 4s ease-in-out infinite;
}
                

    .card:hover {
        transform: translateY(-10px) scale(1.03);
        box-shadow: 0 0 40px rgba(255,0,200,0.6);
    }

    div.stButton > button {
        background: linear-gradient(90deg, #00f5ff, #ff00c8);
        border: none;
        border-radius: 30px;
        color: white;
        font-weight: bold;
        padding: 12px 25px;
        transition: 0.3s;
    }

    div.stButton > button:hover {
        transform: scale(1.1);
        box-shadow: 0 0 20px #ff00c8;
    }

    section[data-testid="stSidebar"] {
        background: rgba(0,0,0,0.6);
        backdrop-filter: blur(10px);
    }

    </style>
    """, unsafe_allow_html=True)



# ============================================================================
# Tool Registry
# ============================================================================

class ToolRegistry:
    """
    Simple registry for managing tool instances.
    """

    def __init__(self):
        self._tools = {}

    def register_tool(self, key: str, tool):
        self._tools[key] = tool

    def get_tool(self, key: str):
        return self._tools.get(key)

    def get_all_tools(self):
        return self._tools

    def get_tools_list(self):
        return list(self._tools.values())

def initialize_tools() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register_tool("tool_0", ShapefileToCSVTool())
    registry.register_tool("tool_1", MergeShapefilesTool())
    registry.register_tool("tool_2", AddShapefilesTool())
    registry.register_tool("tool_3", ReprojectShapefileTool())
    registry.register_tool("tool_4", ExcelToCSVTool())
    registry.register_tool("tool_5", DeleteDuplicateGeometriesTool())

    from tools import AddUUIDToShapefileTool, LatLongToDecimalUTMTool
    registry.register_tool("tool_6", AddUUIDToShapefileTool())
    registry.register_tool("tool_7", LatLongToDecimalUTMTool())

    return registry
    
    # Note: TemplateTool is not registered as it's just a template
    # To add it, uncomment the following line:
    # from tools.template_tool import TemplateTool
    # registry.register_tool("tool_4", TemplateTool())
    
    return registry


# ============================================================================
# Session State Management
# ============================================================================

def initialize_session_state() -> None:
    """Initialize session state variables."""
    if 'selected_tool' not in st.session_state:
        st.session_state.selected_tool = None


# ============================================================================
# Sidebar Navigation
# ============================================================================

def render_sidebar(registry: ToolRegistry) -> None:
    """
    Render the sidebar navigation.
    
    Args:
        registry: ToolRegistry instance
    """
    with st.sidebar:
        st.markdown("## 🗺️ Shapefile Toolkit")
        st.markdown("---")
        
        # Home button
        if st.button("🏠 Home", use_container_width=True, type="secondary"):
            st.session_state.selected_tool = None
            st.rerun()
        
        st.markdown("### 🛠️ Tools")
        
        # Tool navigation buttons
        tools = registry.get_all_tools()
        for key, tool in tools.items():
            card_info = tool.get_card_info()
            button_label = f"{card_info['icon']} {card_info['name']}"
            
            # Highlight selected tool
            button_type = "primary" if st.session_state.selected_tool == key else "secondary"
            
            if st.button(button_label, key=f"nav_{key}", use_container_width=True, type=button_type):
                st.session_state.selected_tool = key
                st.rerun()
        
        st.markdown("---")
        
        # Info section
        st.markdown("""
            ### ℹ️ About
            
            **Shapefile Toolkit** helps you perform common GIS operations on shapefiles directly in your browser.
            
            **Features:**
            - 📊 Export to CSV
            - 🔗 Merge shapefiles
            - ➕ Combine shapefiles
            - 🌐 Reproject CRS
            
            **Privacy:** All processing happens in your browser. Your data is never stored.
        """)
        
        st.markdown("---")
        st.caption("Version 1.0.0")


# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application entry point."""

    # ✅ Always initialize session state properly
    if "selected_tool" not in st.session_state:
        st.session_state.selected_tool = None

    # Apply CSS every rerun
    apply_custom_css()
    futuristic_css()

    # Initialize tools
    registry = initialize_tools()

    # Render sidebar
    render_sidebar(registry)

    # Main content
    selected_tool_key = st.session_state.get("selected_tool")

    if selected_tool_key is None:
        render_homepage(registry.get_tools_list())
    else:
        tool = registry.get_tool(selected_tool_key)

        if tool:
            tool.render_ui()

            st.divider()
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("⬅️ Back to Home", use_container_width=True):
                    st.session_state.selected_tool = None
                    st.rerun()
        else:
            st.session_state.selected_tool = None
            st.rerun()

    # ✅ FOOTER (Your Name)
    st.markdown("""
<style>
.footer-fixed {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    text-align: center;
    padding: 12px 0;
    font-size: 16px;
    font-weight: 500;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(8px);
    border-top: 1px solid rgba(255,255,255,0.1);
    z-index: 1000;
}
.footer-text {
    background: linear-gradient(90deg, #00ffff, #ff00c8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>

<div class="footer-fixed">
    <span class="footer-text">
            Made with ❤️ by  NikhilReddy MaliReddy
    </span>
</div>
""", unsafe_allow_html=True)


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    main()
