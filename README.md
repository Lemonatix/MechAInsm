# MechAInsm 🧪

**MechAInsm** (Mechanical AI for Chemistry) ist eine interaktive Streamlit-Webanwendung zur Vorhersage chemischer Reaktionsmechanismen und zur automatischen Visualisierung von Molekülstrukturen im akademischen ChemDraw-Stil (ACS-Dokument-1996-Standard).

---

## 🚀 Features

- **ACS-konforme 2D-Visualisierung**: Automatische Generierung hochauflösender SVG-Moleküldarstellungen aus SMILES-Strings unter Verwendung von RDKit (kalibriert auf akademische Standards: feste Bindungslängen, präzise Schriftgrößen und klare Kekulizierung).
- **Interaktive Eingabe**: Einfache Angabe von Edukten und Reagenzien via SMILES-Notations-Eingabefeldern.
- **Mechanistische Reaktionsschritte**: Strukturierte und nachvollziehbare Darstellung der einzelnen Reaktionsschritte und Zwischenprodukte.
- **Modernes Premium-UI**: Ein ansprechendes Design mit harmonischen Farbverläufen, klaren Cards und reaktiven UI-Elementen basierend auf der Schriftart *Outfit*.

---

## 📁 Projektstruktur

```text
MechAInsm/
├── app.py                  # Hauptdatei der Streamlit-Anwendung (UI & Layout)
├── core/
│   ├── renderer.py         # SMILES-zu-SVG Konvertierung (ACS/ChemDraw-Stil)
│   └── mechanism.py        # Vorhersage-Engine (aktuell strukturierter Platzhalter)
└── requirements.txt        # Python-Paketabhängigkeiten
```

---

## 🛠️ Installation & Ausführung

### Voraussetzungen
Stelle sicher, dass Python 3.9+ installiert ist.

### 1. Repository klonen & Verzeichnis wechseln
```bash
git clone <repository-url>
cd MechAInsm
```

### 2. Abhängigkeiten installieren
Die Anwendung benötigt `streamlit` und `rdkit`. Installiere sie über:
```bash
pip install -r requirements.txt
```

### 3. Anwendung starten
Starte den lokalen Streamlit-Server:
```bash
streamlit run app.py
```
Die Anwendung öffnet sich daraufhin automatisch in deinem Standardbrowser unter `http://localhost:8501`.

---

## 🧪 Nutzung

1. **Edukt eingeben**: Trage das Ausgangsstoff-SMILES ein (z. B. `CC(=O)O` für Essigsäure).
2. **Reagenz eingeben**: Trage das Reagenz-SMILES ein (z. B. `CCO` für Ethanol).
3. **Generieren**: Klicke auf **Mechanismus generieren**.
4. **Ergebnis analysieren**: Die Anwendung rendert die 2D-Strukturen für Ausgangsstoffe und das erwartete Produkt (z. B. Ethylacetat) und listet die vorgeschlagenen mechanistischen Reaktionsschritte auf.

---

## 🔮 Nächste Schritte

Um das Projekt von einem Prototyp in ein vollwertiges wissenschaftliches Tool zu überführen, sind folgende Schritte geplant:

### 1. Integration echter ML-Modelle für die Reaktionsvorhersage
* **Ersetzung des Platzhalters** in `core/mechanism.py` durch eine Schnittstelle zu Deep-Learning-Modellen.
* **GNNs & Transformer**: Integration von Open-Source-Modellen wie *Molecular Transformer* oder *RXN Mapper* zur präzisen Vorhersage von Reaktionsprodukten und Übergangszuständen.

### 2. Dynamische Generierung von Reaktionsschritten
* Statt vordefinierter Schrittfolgen soll das ML-Modell die tatsächlichen Intermediate (Zwischenprodukte) als SMILES zurückliefern, welche dann ebenfalls dynamisch gerendert werden.

### 3. Visualisierung von Elektronenverschiebungs-Pfeilen
* Implementierung eines erweiterten Renderers, der gekrümmte Pfeile (Curved Arrows) zur Darstellung des Elektronenflusses (nucleophiler Angriff, Abgangsgruppen-Eliminierung) in den mechanistischen Schritten einzeichnet.

### 4. Validierung und Fehlerbehandlung
* Echtzeit-Validierung eingegebener SMILES-Strings vor dem Absenden des Formulars zur Vermeidung von Darstellungsfehlern.
* Automatische Korrektur einfacher Notationsfehler (SMILES-Sanitizing).

### 5. Export- und Dokumentations-Schnittstelle
* Funktion zum Herunterladen der Reaktionsgleichung und der Einzelschritte als hochauflösendes PDF oder ZIP-Archiv mit SVG/PNG-Grafiken für Publikationen.