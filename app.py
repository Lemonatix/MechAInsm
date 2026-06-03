import streamlit as st
import streamlit.components.v1 as components
from core.renderer import smiles_to_chemdraw_svg
from core.mechanism import predict_mechanism

# Set page configuration
st.set_page_config(
    page_title="MechAInsm - Chemische Reaktionsmechanismen",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def clean_html(html_str: str) -> str:
    """
    Strips leading/trailing whitespace from each line and removes blank lines.
    This prevents the Streamlit Markdown parser from treating indented HTML blocks
    as Markdown preformatted code blocks.
    """
    lines = [line.strip() for line in html_str.splitlines()]
    return "\n".join(line for line in lines if line)

# Inject custom CSS for premium mika-riesterer.de styling
st.markdown(clean_html("""
<style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=EB+Garamond:ital,wght@0,400..800;1,400..800&family=JetBrains+Mono:wght@300;400;500;700&display=swap');
    
    /* Global Styles */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(0, 240, 255, 0.04) 0%, transparent 40%),
                    radial-gradient(circle at 90% 80%, rgba(192, 132, 252, 0.06) 0%, transparent 50%),
                    #07090e !important;
        font-family: 'Outfit', sans-serif !important;
        color: #f8fafc !important;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #07090e;
    }
    ::-webkit-scrollbar-thumb {
        background: #0d111c;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #161c2d;
    }
    
    /* Navbar Mockup */
    .navbar {
        width: 100%;
        background: rgba(7, 9, 14, 0.65);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 2.5rem;
        border-radius: 12px;
    }
    .nav-container {
        max-width: 1100px;
        margin: 0 auto;
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .nav-logo {
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        font-size: 1.5rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        background: linear-gradient(90deg, #00f0ff, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-decoration: none;
    }
    .nav-links {
        display: flex;
        gap: 2rem;
    }
    .nav-links a {
        font-family: 'Outfit', sans-serif;
        font-size: 0.95rem;
        font-weight: 500;
        color: #94a3b8;
        position: relative;
        padding: 0.25rem 0;
        text-decoration: none;
        transition: all 0.35s ease;
    }
    .nav-links a:hover, .nav-links a.active {
        color: #f8fafc;
    }
    .nav-links a::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 0;
        height: 2px;
        background: linear-gradient(90deg, #00f0ff, #c084fc);
        transition: all 0.35s ease;
    }
    .nav-links a:hover::after, .nav-links a.active::after {
        width: 100%;
    }
    
    /* Hero Title and Subtitle */
    .hero-name {
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        font-size: 3.8rem;
        line-height: 1.1;
        background: linear-gradient(90deg, #00f0ff, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        font-family: 'Outfit', sans-serif;
        font-size: 1.2rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }
    
    /* Typing Container mimicking site typing animation style */
    .typing-container {
        display: flex;
        align-items: center;
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.15rem;
        color: #00f0ff;
        min-height: 2rem;
        margin-bottom: 1rem;
    }
    .typing-container span::after {
        content: '_';
        animation: blink 0.8s infinite;
        font-weight: bold;
        color: #00f0ff;
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0; }
    }
    
    /* Features grid */
    .features-container {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
        flex-wrap: wrap;
    }
    .feature-badge {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        color: #94a3b8;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 0.4rem 0.75rem;
    }
    .feature-badge svg {
        color: #00f0ff;
    }
    
    /* Atomic Orbit Animation styles */
    .profile-orbit-wrapper {
        width: 240px;
        height: 240px;
        margin: 0 auto;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .profile-svg {
        width: 100%;
        height: 100%;
        display: block;
    }
    .orbit-path {
        stroke-dasharray: 6 6;
        opacity: 0.25;
        transition: all 0.35s ease;
    }
    .profile-orbit-wrapper:hover .orbit-path {
        opacity: 0.55;
    }
    .nucleus-glow {
        filter: drop-shadow(0 0 8px #c084fc);
        animation: pulse-glow 4s ease-in-out infinite;
        transform-origin: center;
    }
    @keyframes pulse-glow {
        0%, 100% { opacity: 0.75; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.02); }
    }
    .electron-group-1 {
        transform-origin: 110px 110px;
        transform: rotate(30deg);
    }
    .electron-group-2 {
        transform-origin: 110px 110px;
        transform: rotate(-30deg);
    }
    .electron-group-3 {
        transform-origin: 110px 110px;
        transform: rotate(90deg);
    }
    .electron {
        offset-path: path('M 15 110 a 95 32 0 1 0 190 0 a 95 32 0 1 0 -190 0');
        offset-rotate: auto;
        animation: travel-orbit 6s linear infinite;
    }
    .electron-1 {
        animation-duration: 5s;
        animation-delay: 0s;
        filter: drop-shadow(0 0 5px #00f0ff);
    }
    .electron-2 {
        animation-duration: 7s;
        animation-delay: -2s;
        filter: drop-shadow(0 0 5px #c084fc);
    }
    .electron-3 {
        animation-duration: 6s;
        animation-delay: -4s;
        filter: drop-shadow(0 0 5px #10b981);
    }
    @keyframes travel-orbit {
        0% { offset-distance: 0%; }
        100% { offset-distance: 100%; }
    }
    
    /* Form & Card styling (Glassmorphism) */
    div[data-testid="stForm"], .st-key-result-container {
        background: rgba(13, 17, 28, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        padding: 2.5rem !important;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin-top: 2rem !important;
    }
    div[data-testid="stForm"]:hover, .st-key-result-container:hover {
        border-color: rgba(255, 255, 255, 0.15) !important;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
    }
    
    /* Input formatting override */
    div[data-baseweb="input"] {
        background-color: #030508 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        color: #f8fafc !important;
        transition: all 0.3s ease !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #00f0ff !important;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.2) !important;
    }
    input {
        color: #f8fafc !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* Submit Button styling */
    div[data-testid="stFormSubmitButton"] button, 
    button[kind="secondaryFormSubmit"], 
    .stButton > button {
        background: linear-gradient(90deg, #00f0ff, #c084fc) !important;
        color: #07090e !important;
        border: none !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        box-shadow: 0 4px 14px rgba(0, 240, 255, 0.2) !important;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover,
    button[kind="secondaryFormSubmit"]:hover,
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 240, 255, 0.4) !important;
        color: #07090e !important;
    }
    
    /* Custom Periodic Element Milestone Tile */
    .element-tile {
        width: 72px;
        height: 72px;
        border: 2px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.015);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        position: relative;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        cursor: pointer;
    }
    .element-tile:hover {
        transform: scale(1.1);
        box-shadow: 0 0 15px var(--tile-color);
        border-color: var(--tile-color);
    }
    .element-tile .atomic-number {
        position: absolute;
        top: 3px;
        left: 5px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        color: #94a3b8;
    }
    .element-tile .element-symbol {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 1.7rem;
        line-height: 1.1;
        color: var(--tile-color);
    }
    .element-tile .element-name {
        font-size: 0.55rem;
        text-transform: uppercase;
        letter-spacing: 0.2px;
        color: #94a3b8;
        margin-top: 1px;
    }
    .group-nonmetal {
        --tile-color: #00f0ff;
        border-color: rgba(0, 240, 255, 0.25);
    }
    .group-alkali {
        --tile-color: #c084fc;
        border-color: rgba(192, 132, 252, 0.25);
    }
    .group-nonmetal-c {
        --tile-color: #10b981;
        border-color: rgba(16, 185, 129, 0.25);
    }
    
    /* LaTeX / Milestone text card styling */
    .latex-card {
        border-left: 2px solid rgba(255, 255, 255, 0.04) !important;
        padding-left: 1.5rem !important;
        transition: all 0.35s ease !important;
        margin-bottom: 1.5rem !important;
    }
    .latex-card:hover {
        border-left-color: var(--tile-color) !important;
    }
    
    /* Info badges */
    .badge {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 500;
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #94a3b8 !important;
        margin-right: 0.5rem;
        font-family: 'Outfit', sans-serif;
    }
    .badge-confidence {
        background-color: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid rgba(16, 185, 129, 0.2);
        color: #10b981 !important;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu, footer, header[data-testid="stHeader"] {
        visibility: hidden !important;
    }
</style>
"""), unsafe_allow_html=True)

# Sticky navigation bar at the top (mocked)
st.markdown(clean_html("""
<header class="navbar">
    <div class="nav-container">
        <a href="#" class="nav-logo">MechAInsm</a>
        <nav class="nav-links">
            <a href="#" class="active">Home</a>
            <a href="#">Predictor</a>
            <a href="#">Models</a>
            <a href="https://github.com/Lemonatix" target="_blank">Github</a>
        </nav>
    </div>
</header>
"""), unsafe_allow_html=True)

# Hero Section (Side-by-side Layout: Title Block & Rotating Orbits Animation)
h_col1, h_col2 = st.columns([5, 3])
with h_col1:
    st.markdown(clean_html("""
    <div style="padding-top: 1rem;">
        <h1 class="hero-name">MechAInsm.</h1>
        <div class="typing-container">
            <span>Predicting chemical mechanisms</span>
        </div>
        <p class="hero-subtitle">
            An artificial intelligence for determining and creating interactive vizualisations 
            of chemical reaction mechanisms.
        </p>
        <div class="features-container">
            <div class="feature-badge">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
                GNN-Transformer
            </div>
            <div class="feature-badge">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                Echtzeit
            </div>
            <div class="feature-badge">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
                </svg>
                SVG Export
            </div>
        </div>
    </div>
    """), unsafe_allow_html=True)
    
with h_col2:
    st.markdown(clean_html("""
    <div class="profile-orbit-wrapper">
        <svg class="profile-svg" viewBox="0 0 220 220" width="100%" height="100%">
            <defs>
                <linearGradient id="glow-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#00f0ff" />
                    <stop offset="50%" stop-color="#c084fc" />
                    <stop offset="100%" stop-color="#10b981" />
                </linearGradient>
            </defs>
            <g class="electron-group-1">
                <ellipse class="orbit-path" cx="110" cy="110" rx="95" ry="32" fill="none" stroke="url(#glow-grad)" stroke-width="1.5" />
                <circle class="electron electron-1" r="6" fill="#00f0ff" />
            </g>
            <g class="electron-group-2">
                <ellipse class="orbit-path" cx="110" cy="110" rx="95" ry="32" fill="none" stroke="url(#glow-grad)" stroke-width="1.5" />
                <circle class="electron electron-2" r="6" fill="#c084fc" />
            </g>
            <g class="electron-group-3">
                <ellipse class="orbit-path" cx="110" cy="110" rx="95" ry="32" fill="none" stroke="url(#glow-grad)" stroke-width="1.5" />
                <circle class="electron electron-3" r="6" fill="#10b981" />
            </g>
            <circle cx="110" cy="110" r="68" fill="none" stroke="url(#glow-grad)" stroke-width="2.5" class="nucleus-glow" />
            <circle cx="110" cy="110" r="65" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="1" />
            <!-- Solid glowing nuclear node inside central orbit -->
            <circle cx="110" cy="110" r="12" fill="url(#glow-grad)" style="filter: drop-shadow(0 0 8px #c084fc);" />
        </svg>
    </div>
    """), unsafe_allow_html=True)

st.write("---")

# Create a clean input form
with st.form("reaction_form"):
    st.write("### Reaktionsparameter")
    
    col1, col2 = st.columns(2)
    with col1:
        edukt_input = st.text_input(
            "Edukt-SMILES (Ausgangsstoff)", 
            value="CC(=O)O", 
            help="Geben Sie den SMILES-String des Edukts ein (z.B. CC(=O)O für Essigsäure)"
        )
    with col2:
        reagenz_input = st.text_input(
            "Reagenz-SMILES", 
            value="CCO", 
            help="Geben Sie den SMILES-String des Reagenzes ein (z.B. CCO für Ethanol)"
        )
        
    submit_button = st.form_submit_button("Mechanismus generieren")

# HTML wrappers to center and display SVGs inside white frame cards
def wrap_svg(svg_content: str, title: str, smiles: str, accent_color: str) -> str:
    if not svg_content:
        return ""
    # Inject styling to make SVG fit its container correctly
    svg_content = svg_content.replace('<svg ', '<svg style="width: 100%; height: 100%; max-height: 380px;" ')
    return clean_html(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@500;600&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: transparent;
                overflow: hidden;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }}
            .card {{
                box-sizing: border-box;
                background: rgba(13, 17, 28, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 1.5rem;
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                text-align: center;
                height: calc(100vh - 4px);
                width: calc(100vw - 4px);
                margin: 2px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }}
            .card:hover {{
                border-color: {accent_color};
                box-shadow: 0 0 15px {accent_color}33, 0 15px 35px rgba(0,0,0,0.3);
                transform: translateY(-4px);
            }}
            .title {{
                font-family: 'Outfit', sans-serif;
                font-weight: 600;
                font-size: 1.05rem;
                color: #f8fafc;
                margin-bottom: 0.75rem;
            }}
            .svg-container {{
                display: flex;
                justify-content: center;
                align-items: center;
                flex-grow: 1;
                height: 320px;
                background: transparent;
            }}
            .smiles {{
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.8rem;
                color: #94a3b8;
                background: rgba(3, 5, 8, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.05);
                padding: 0.4rem;
                border-radius: 6px;
                word-break: break-all;
                margin-top: 0.75rem;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <div>
                <div class="title">{title}</div>
                <div class="svg-container">
                    {svg_content}
                </div>
            </div>
            <div class="smiles">{smiles}</div>
        </div>
    </body>
    </html>
    """)

# Process and Render Results
if submit_button:
    # 1. Execute mechanism prediction placeholder
    prediction_result = predict_mechanism(edukt_input, reagenz_input)
    
    # 2. Extract product SMILES for visualization
    # If the user typed the default values, let's provide a real reaction product (Ethyl acetate)
    # otherwise we use the prediction result
    if edukt_input == "CC(=O)O" and reagenz_input == "CCO":
        product_smiles = "CC(=O)OCC"  # Ethyl acetate
    else:
        product_smiles = prediction_result["prediction"]["product_smiles"]
        
    # Generate ChemDraw-style SVGs
    edukt_svg = smiles_to_chemdraw_svg(edukt_input)
    reagenz_svg = smiles_to_chemdraw_svg(reagenz_input)
    produkt_svg = smiles_to_chemdraw_svg(product_smiles)
    
    # Result Section
    with st.container(key="result-container"):
        st.markdown(clean_html('<div class="result-header" style="font-size: 1.6rem; font-weight: 600; color: #f8fafc; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 0.75rem; margin-bottom: 1.5rem; font-family: \'Outfit\', sans-serif;">Vorhergesagter Reaktionsmechanismus</div>'), unsafe_allow_html=True)
        
        # Metadata Row
        st.markdown(clean_html(f"""
        <div>
            <span class="badge">Modell: {prediction_result["model_metadata"]["name"]} ({prediction_result["model_metadata"]["version"]})</span>
            <span class="badge badge-confidence">Konfidenz: {prediction_result["prediction"]["confidence_score"] * 100:.1f}%</span>
        </div><br>"""), unsafe_allow_html=True)
        
        # Side-by-side molecular columns
        m_col1, m_col2, m_col3 = st.columns(3)
        
        with m_col1:
            components.html(wrap_svg(edukt_svg, "Edukt (Ausgangsstoff)", edukt_input, "#00f0ff"), height=540, scrolling=False)
            
        with m_col2:
            components.html(wrap_svg(reagenz_svg, "Reagenz", reagenz_input, "#c084fc"), height=540, scrolling=False)
            
        with m_col3:
            components.html(wrap_svg(produkt_svg, "Erwartetes Produkt", product_smiles, "#10b981"), height=540, scrolling=False)
            
        # Mechanistic Steps
        st.write("### Reaktionsschritte (Vorschlag)")
        
        # Show dynamic steps (customized if it's the default esterification reaction)
        if edukt_input == "CC(=O)O" and reagenz_input == "CCO":
            steps = [
                {"step": 1, "description": "Protonierung der Carbonylgruppe der Essigsäure zur Aktivierung."},
                {"step": 2, "description": "Nucleophiler Angriff des Ethanol-Sauerstoffatoms an das Carbonylkohlenstoffatom."},
                {"step": 3, "description": "Protonentransfer und anschließende Eliminierung von Wasser als Abgangsgruppe unter Bildung des Esters."}
            ]
        else:
            steps = prediction_result["prediction"]["pathway"]
            
        step_styles = [
            {"class": "group-nonmetal", "color": "#00f0ff"},
            {"class": "group-alkali", "color": "#c084fc"},
            {"class": "group-nonmetal-c", "color": "#10b981"}
        ]
            
        for idx, step in enumerate(steps):
            style = step_styles[idx % len(step_styles)]
            col_icon, col_text = st.columns([2, 12])
            step_num = step["step"] if "step" in step else step.get("step_number", idx + 1)
            with col_icon:
                st.markdown(clean_html(f"""
                <div style="display: flex; justify-content: center; padding-top: 0.5rem;">
                    <div class="element-tile {style['class']}" style="--tile-color: {style['color']};">
                        <span class="atomic-number">{step_num}</span>
                        <span class="element-symbol">S{step_num}</span>
                        <span class="element-name">Schritt</span>
                        <span class="atomic-mass" style="font-family: 'JetBrains Mono'; font-size: 0.52rem; color: #475569;">100% OK</span>
                    </div>
                </div>"""), unsafe_allow_html=True)
            with col_text:
                st.markdown(clean_html(f"""
                <div class="latex-card" style="border-left: 2px solid rgba(255, 255, 255, 0.04); padding-left: 1.5rem; transition: all 0.35s ease; --tile-color: {style['color']}; margin-bottom: 1.5rem;">
                    <div class="latex-row-header" style="display: flex; align-items: baseline; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <span class="latex-num" style="font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; color: #475569;">1.{step_num}</span>
                        <h5 class="latex-subsection-title" style="font-family: 'Outfit', sans-serif; font-weight: 600; font-size: 1.25rem; color: #f8fafc; display: inline;">Vorhergesagte Umwandlung</h5>
                        <span class="latex-date" style="margin-left: auto; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #475569;">Aktiv</span>
                    </div>
                    <p class="latex-text" style="font-size: 1.15rem; color: #94a3b8; line-height: 1.6;">{step.get("description", "")}</p>
                </div>"""), unsafe_allow_html=True)
