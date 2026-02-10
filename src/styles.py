APP_STYLES = """
<style>
    .stApp {
        background-color: #121212;
        color: #FFFAF0;
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, .st-subheader {
        color: #FFB300 !important;
        font-family: 'Manrope', sans-serif;
        font-weight: 600;
    }
    .mood-box {
        background-color: #1E1E1E;
        color: #FFFAF0;
        border: 1px solid #4B4B4B;
        border-left: 6px solid #FFB300;
        border-radius: 8px;
        padding: 0 20px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .mood-box span:first-child { 
        font-weight: 500; font-size: 18px; color: #B3B3B3; 
    }
    .mood-box span:last-child { 
        font-weight: 800; font-size: 20px; color: #FFB300; text-transform: uppercase; 
    }
    .stButton > button {
        background-color: #1B263B;
        color: #FFFAF0;
        border: 1px solid #FFB300;
        font-size: 14px;
        font-weight: 700;
        border-radius: 6px;
        height: 45px;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.2s;
    }
    .stButton > button:hover {
        background-color: #FFB300;
        color: #0D1B2A;
        border-color: #FFB300;
    }
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #0E0E0E; color: #666;
        text-align: center; padding: 10px; font-size: 12px;
        border-top: 1px solid #333; z-index: 999;
    }
</style>
"""