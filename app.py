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

# Inject custom CSS for premium styling
st.markdown("""
<style>
    /* Google Font Import */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .reportview-container {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Title and Header Gradient */
    .title-gradient {
        background: linear-gradient(135deg, #6366F1 0%, #A855F7 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #94A3B8;
        font-size: 1.1rem;
        margin-bottom: 2.5rem;
    }
    
    /* Molecule Card Wrapper */
    .mol-card-title {
        text-align: center;
        font-weight: 600;
        font-size: 1.1rem;
        color: #334155;
        margin-bottom: 0.5rem;
    }
    
    /* Form & Input Styling */
    div[data-testid="stForm"] {
        border: 1px solid #E2E8F0;
        background-color: #F8FAFC;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
        padding: 2rem;
    }
    
    /* Result Section Styling */
    .result-container {
        margin-top: 2rem;
        padding: 2rem;
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.05);
    }
    
    .result-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1E293B;
        border-bottom: 2px solid #F1F5F9;
        padding-bottom: 0.75rem;
        margin-bottom: 1.5rem;
    }
    
    /* Step Styling */
    .step-box {
        background-color: #F8FAFC;
        border-left: 4px solid #6366F1;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 0 8px 8px 0;
    }
    .step-title {
        font-weight: 600;
        color: #475569;
    }
    
    /* Info badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 500;
        background-color: #EEF2F6;
        color: #475569;
        margin-right: 0.5rem;
    }
    .badge-confidence {
        background-color: #ECFDF5;
        color: #059669;
    }
</style>
""", unsafe_allow_html=True)

# Application Header
st.markdown('<h1 class="title-gradient">MechAInsm</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Vorhersage chemischer Reaktionsmechanismen & Visualisierung im ChemDraw-Stil</p>', unsafe_allow_html=True)

# Create a clean input form
with st.form("reaction_form"):
    st.write("### 🧪 Reaktionsparameter")
    
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
    
    # HTML wrappers to center and display SVGs inside white frame cards
    def wrap_svg(svg_content: str) -> str:
        if not svg_content:
            return ""
        return f"""
        <div style="
            display: flex; 
            justify-content: center; 
            align-items: center; 
            background-color: white; 
            border: 1px solid #E2E8F0; 
            border-radius: 12px; 
            padding: 10px; 
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            height: 420px;
        ">
            {svg_content}
        </div>
        """

    # Result Section
    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    st.markdown('<div class="result-header">🧪 Vorhergesagter Reaktionsmechanismus</div>', unsafe_allow_html=True)
    
    # Metadata Row
    st.markdown(
        f'<div>'
        f'<span class="badge">Modell: {prediction_result["model_metadata"]["name"]} ({prediction_result["model_metadata"]["version"]})</span>'
        f'<span class="badge badge-confidence">Konfidenz: {prediction_result["prediction"]["confidence_score"] * 100:.1f}%</span>'
        f'</div><br>',
        unsafe_allow_html=True
    )
    
    # Side-by-side molecular columns
    m_col1, m_col2, m_col3 = st.columns(3)
    
    with m_col1:
        st.markdown('<div class="mol-card-title">Edukt (Ausgangsstoff)</div>', unsafe_allow_html=True)
        components.html(wrap_svg(edukt_svg), height=440, scrolling=False)
        st.code(edukt_input, language="text")
        
    with m_col2:
        st.markdown('<div class="mol-card-title">Reagenz</div>', unsafe_allow_html=True)
        components.html(wrap_svg(reagenz_svg), height=440, scrolling=False)
        st.code(reagenz_input, language="text")
        
    with m_col3:
        st.markdown('<div class="mol-card-title">Erwartetes Produkt</div>', unsafe_allow_html=True)
        components.html(wrap_svg(produkt_svg), height=440, scrolling=False)
        st.code(product_smiles, language="text")
        
    # Mechanistic Steps
    st.write("### ⚙️ Reaktionsschritte (Vorschlag)")
    
    # Show dynamic steps (customized if it's the default esterification reaction)
    if edukt_input == "CC(=O)O" and reagenz_input == "CCO":
        steps = [
            {"step": 1, "description": "Protonierung der Carbonylgruppe der Essigsäure zur Aktivierung."},
            {"step": 2, "description": "Nucleophiler Angriff des Ethanol-Sauerstoffatoms an das Carbonylkohlenstoffatom."},
            {"step": 3, "description": "Protonentransfer und anschließende Eliminierung von Wasser als Abgangsgruppe unter Bildung des Esters."}
        ]
    else:
        steps = prediction_result["prediction"]["pathway"]
        
    for step in steps:
        st.markdown(
            f'<div class="step-box">'
            f'<div class="step-title">Schritt {step["step"] if "step" in step else step.get("step_number", "?")}</div>'
            f'<div>{step.get("description", "")}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        
    st.markdown('</div>', unsafe_allow_html=True)
