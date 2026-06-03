import os
import json
import urllib.request
import urllib.error

# Lightweight custom .env reader to keep everything zero-dependency
def load_env(env_path=".env"):
    """Loads environment variables from a .env file if it exists."""
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "=" in line:
                            key, val = line.split("=", 1)
                            # Strip spaces and quotes
                            os.environ[key.strip()] = val.strip().strip('"').strip("'")
        except Exception:
            pass

# Load environment variables (e.g. GEMINI_API_KEY)
load_env()

def predict_mechanism(edukt_smiles: str, reagenz_smiles: str, api_key: str = None) -> dict:
    """
    Predicts chemical reaction mechanism using the Gemini API.
    Returns structured JSON with product, byproduct, and intermediate steps.
    
    Args:
        edukt_smiles (str): SMILES of the starting material / reactant.
        reagenz_smiles (str): SMILES of the reagent.
        api_key (str): Optional API key passed from UI. If not set, checks env.
        
    Returns:
        dict: Reaction prediction payload or error dictionary.
    """
    # Normalize input
    edukt_smiles = edukt_smiles.strip()
    reagenz_smiles = reagenz_smiles.strip()
    
    # 1. Default esterification fallback for out-of-the-box demo
    # Acetic acid + Ethanol -> Ethyl acetate + Water
    if edukt_smiles == "CC(=O)O" and reagenz_smiles == "CCO":
        return {
            "status": "success",
            "model_metadata": {
                "name": "Esterification-Demo-Fallback",
                "version": "1.0",
                "description": "Statische Vorschau für die Veresterung (Demo ohne API-Key)."
            },
            "prediction": {
                "product_smiles": "CC(=O)OCC",
                "byproduct_smiles": "O",
                "confidence_score": 1.0,
                "pathway": [
                    {
                        "step": 1,
                        "description": "Protonierung der Carbonylgruppe der Essigsäure zur Aktivierung.",
                        "intermediate_smiles": "CC(=[OH+])O"
                    },
                    {
                        "step": 2,
                        "description": "Nucleophiler Angriff des Ethanol-Sauerstoffatoms an das Carbonylkohlenstoffatom unter Bildung eines tetraedrischen Intermediats.",
                        "intermediate_smiles": "CC(O)(O)[OH+]CCO"
                    },
                    {
                        "step": 3,
                        "description": "Protonentransfer und anschließende Eliminierung von Wasser als Abgangsgruppe unter Bildung des Esters (Ethylacetat).",
                        "intermediate_smiles": "CC(=O)OCC"
                    }
                ]
            }
        }

    # 2. Get API key (first check explicitly passed key, then env variable)
    key_to_use = api_key or os.environ.get("GEMINI_API_KEY")
    if not key_to_use:
        return {
            "status": "no_api_key",
            "error_message": "Kein Gemini-API-Schlüssel konfiguriert. Bitte geben Sie einen Schlüssel in der Seitenleiste ein oder setzen Sie GEMINI_API_KEY als Umgebungsvariable."
        }

    # 3. Call Gemini API via urllib
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key_to_use}"
    
    prompt = f"""
You are an expert organic chemist. Predict the chemical reaction product and step-by-step mechanism pathway for:
Reactant (Edukt) SMILES: {edukt_smiles}
Reagent SMILES: {reagenz_smiles}

Respond ONLY with a valid JSON object matching this schema:
{{
  "status": "success",
  "model_metadata": {{
    "name": "Gemini-1.5-Flash",
    "version": "1.5",
    "description": "AI predicted reaction pathway and intermediates"
  }},
  "prediction": {{
    "product_smiles": "SMILES of primary organic product",
    "byproduct_smiles": "SMILES of byproduct",
    "confidence_score": 0.0 to 1.0,
    "pathway": [
      {{
        "step": 1,
        "description": "Detailed explanation of step 1 in German",
        "intermediate_smiles": "SMILES of the chemical structure representing this intermediate/reactant state in this step"
      }}
    ]
  }}
}}

If the input is chemically nonsensical or the reaction is impossible, return:
{{
  "status": "error",
  "error_message": "Detailed explanation of why this reaction is invalid or cannot be predicted in German"
}}

Strict rules:
1. Make sure all SMILES (product_smiles, byproduct_smiles, and intermediate_smiles for each step) are chemically valid and parseable by RDKit.
2. The description in pathway steps MUST be written in German.
3. Keep the number of mechanism steps reasonable (usually 2 to 4 steps).
4. Do NOT wrap the JSON response in ```json ``` markdown code blocks. Return ONLY the raw JSON string.
"""

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = response.read().decode("utf-8")
            res_json = json.loads(res_data)
            
            # Extract the generated text
            candidate = res_json.get("candidates", [{}])[0]
            part = candidate.get("content", {}).get("parts", [{}])[0]
            text = part.get("text", "").strip()
            
            # Parse the text returned by Gemini (which is a JSON string)
            prediction = json.loads(text)
            return prediction
            
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
            err_json = json.loads(err_body)
            msg = err_json.get("error", {}).get("message", str(e))
        except Exception:
            msg = str(e)
        return {
            "status": "error",
            "error_message": f"Gemini API HTTP-Fehler ({e.code}): {msg}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Unerwarteter Fehler bei der API-Anfrage: {str(e)}"
        }
