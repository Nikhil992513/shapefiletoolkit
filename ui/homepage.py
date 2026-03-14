"""
Homepage/dashboard layout for the Shapefile Toolkit.
"""

import streamlit as st
from typing import Dict, List, Any
# Global CSS Styling

def render_homepage(tools: List[Any]) -> None:

    # Inject CSS safely on every render
    st.markdown("""
    <style>
    .hero-container {
        text-align: center;
        padding: 3rem 0;
    }

    .hero-title {
        font-size: 3.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #00ffff, #00ff99, #00ffff);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 4s linear infinite;
    }

    .hero-subtitle {
        font-size: 1.3rem;
        color: #bbbbbb;
        margin-top: 10px;
    }

    @keyframes shine {
        to { background-position: 200% center; }
    }

    .tool-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        border: 1px solid rgba(0, 255, 255, 0.3);
        transition: all 0.3s ease;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.15);
        min-height: 220px;
        position: relative;
        overflow: hidden;
    }

    .tool-card:hover {
        transform: translateY(-12px) scale(1.03);
        box-shadow:
            0 0 20px rgba(0, 255, 255, 0.4),
            0 0 40px rgba(255, 0, 200, 0.4);
    }

    .tool-icon {
        font-size: 3rem;
        margin-bottom: 10px;
    }

    .tool-card h3 {
        color: #00ffff;
        margin-bottom: 10px;
    }

    .tool-card p {
        color: #cccccc;
    }
     
    </style>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <h1 class="hero-title">🗺️ Shapefile Toolkit</h1>
        <p class="hero-subtitle">GIS Utilities in Your Browser</p>
    </div>
    """, unsafe_allow_html=True)

    # Introduction
    st.markdown("""
Welcome to the *Shapefile Toolkit* – a powerful web application for performing common 
shapefile operations without the need for desktop GIS software. Upload your shapefiles, 
choose an operation, and download the results instantly.

All processing happens in your browser session. Your data is never stored on our servers.
    """)

    st.divider()

   

    # Tools section
    st.subheader("🛠️ Available Tools")
    st.markdown("Select a tool below to get started:")
    
    # Create tool cards in a grid
    cols_per_row = 2
    
    for i in range(0, len(tools), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            tool_idx = i + j
            if tool_idx < len(tools):
                tool = tools[tool_idx]
                card_info = tool.get_card_info()
                
                with col:
                  render_tool_card(
                      icon=card_info['icon'],
                      name=card_info['name'],
                      description=card_info['description'],
                      tool_key=f"tool_{tool_idx}",
                      delay=tool_idx * 150
                  )
    
    # Footer
    st.divider()
    
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0; color: #666;'>
            <p>
                <strong>Shapefile Toolkit</strong> v1.0.0<br>
                Made with ❤️ by <strong> NikhilReddy Malireddy  </strong>
            </p>
            <p style='font-size: 0.9rem;'>
                💡 Tip: All tools support ZIP files containing shapefile components (.shp, .shx, .dbf, .prj)
            </p>
        </div>
    """, unsafe_allow_html=True)


def render_tool_card(icon: str, name: str, description: str, tool_key: str, delay: int = 0) -> None:

    st.markdown(f"""
    <div class="tool-card fade-in" style="animation-delay:{delay}ms;">
        <div class="tool-icon">{icon}</div>
        <h3>{name}</h3>
        <p>{description}</p>
    """, unsafe_allow_html=True)

    if st.button(f"🚀 Open {name}", key=f"btn_{tool_key}", use_container_width=True):
        st.session_state.selected_tool = tool_key   # ✅ FIXED
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)