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
    
    # White background
    opts.backgroundColour = rdMolDraw2D.DrawColour(1.0, 1.0, 1.0, 1.0)
    opts.clearBackground = True

    # Render molecule to SVG
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()

    return drawer.GetDrawingText()
