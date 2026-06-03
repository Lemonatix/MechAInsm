# pyrefly: ignore [missing-import]
from rdkit import Chem
# pyrefly: ignore [missing-import]
from rdkit.Chem import rdDepictor
# pyrefly: ignore [missing-import]
from rdkit.Chem.Draw import rdMolDraw2D

def smiles_to_chemdraw_svg(smiles: str) -> str:
    """
    Converts a SMILES string into a ChemDraw-style SVG.
    Strictly calibrated to academic standards (similar to ACS Document 1996):
    - bondLength = 30
    - lineWidth = 1.8
    - fontSize = 12
    - sans-serif font
    - white background
    - pre-kekulized molecule
    """
    if not smiles or not isinstance(smiles, str) or smiles.strip() == "":
        return ""
        
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        # Return a clean error SVG rather than failing
        return (
            f'<svg width="400" height="400" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="100%" height="100%" fill="white"/>'
            f'<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" '
            f'font-family="sans-serif" font-size="14" fill="#d9534f">Ungültiges SMILES: {smiles}</text>'
            f'</svg>'
        )

    # Make a copy and kekulize the molecule
    mol = Chem.Mol(mol)
    try:
        Chem.Kekulize(mol)
    except Exception:
        # Fallback to original aromatic molecule if kekulization fails
        pass

    # Compute 2D coordinates for drawing
    rdDepictor.Compute2DCoords(mol)

    # Initialize the SVG drawing canvas (400x400)
    drawer = rdMolDraw2D.MolDraw2DSVG(400, 400)
    opts = drawer.drawOptions()

    # Apply strict academic rendering options (ACS style)
    opts.fixedBondLength = 30.0
    opts.bondLineWidth = 1.8
    opts.minFontSize = 12
    opts.fixedFontSize = 12
    
    # Transparent background for seamless dark integration
    opts.setBackgroundColour((0.0, 0.0, 0.0, 0.0))
    opts.clearBackground = True

    # Custom atom palette for dark mode contrast (inspired by mika-riesterer.de theme)
    opts.updateAtomPalette({
        1: (0.9, 0.9, 0.9),       # Hydrogen: light gray
        6: (0.97, 0.98, 0.99),   # Carbon/Bonds: off-white
        7: (0.22, 0.74, 0.97),   # Nitrogen: cyan-blue
        8: (0.96, 0.25, 0.37),   # Oxygen: red-rose
        9: (0.2, 0.83, 0.60),    # Fluorine: green-mint
        15: (0.98, 0.57, 0.24),  # Phosphorus: orange
        16: (0.98, 0.75, 0.14),  # Sulfur: yellow-gold
        17: (0.06, 0.73, 0.50),  # Chlorine: green
        35: (0.97, 0.44, 0.44),  # Bromine: light-red
        53: (0.75, 0.52, 0.99),  # Iodine: purple
    })

    # Render molecule to SVG
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()

    return drawer.GetDrawingText()
