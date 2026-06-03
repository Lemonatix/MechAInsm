#!/usr/bin/env python3
"""
MechAInsm - GNN Trainings-Pipeline
----------------------------------
Dieses Skript zeigt und demonstriert das tatsächliche Training eines 
Graph Neural Networks (GNN) auf molekularen Strukturen zur Klassifikation 
chemischer Verbindungsklassen.

Anforderungen:
- torch
- torch-geometric
- rdkit

Ausführung:
python scripts/train_gnn.py --epochs 20 --lr 0.01
"""

import os
import sys
import argparse

# 1. Dependency-Check
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    from rdkit import Chem
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False

try:
    from torch_geometric.loader import DataLoader
    from torch_geometric.data import Data, Batch
    from torch_geometric.nn import GCNConv, global_mean_pool
    HAS_PYG = True
except ImportError:
    HAS_PYG = False


def check_dependencies():
    """Überprüft die Abhängigkeiten und gibt Installationsanweisungen aus."""
    missing = []
    if not HAS_TORCH:
        missing.append("torch (PyTorch)")
    if not HAS_RDKIT:
        missing.append("rdkit")
    if not HAS_PYG:
        missing.append("torch-geometric (PyTorch Geometric)")
        
    if missing:
        print("=" * 70)
        print("❌ FEHLENDE ABHÄNGIGKEITEN ERKANNT")
        print("=" * 70)
        print("Um dieses GNN-Trainingsskript auszuführen, müssen folgende Bibliotheken")
        print("installiert sein:")
        for lib in missing:
            print(f"  - {lib}")
        print("\nSie können diese mit folgendem Befehl in Ihrem Terminal installieren:")
        print("  pip install torch torchvision")
        print("  pip install torch-geometric")
        print("  (RDKit ist bereits über requirements.txt installiert)")
        print("=" * 70)
        return False
    return True


# --- GNN Modell Definition ---
if HAS_TORCH and HAS_PYG:
    class ChemicalGNN(nn.Module):
        """
        Graph Neural Network zur Molekül-Klassifikation.
        Nutzt Graph Convolutional Layers (GCN) für Node Embeddings
        und globales Mean Pooling zur Graph-Repräsentation.
        """
        def __init__(self, num_node_features, hidden_dim, num_classes):
            super(ChemicalGNN, self).__init__()
            # GCN Layer 1: Aggregiert Nachbar-Atom-Features
            self.conv1 = GCNConv(num_node_features, hidden_dim)
            # GCN Layer 2: Aggregiert Features über 2-Hop-Nachbarschaften
            self.conv2 = GCNConv(hidden_dim, hidden_dim)
            # Fully Connected Layer zur Klassifikation des Moleküls
            self.fc = nn.Linear(hidden_dim, num_classes)

        def forward(self, data):
            x, edge_index, batch = data.x, data.edge_index, data.batch
            
            # 1. Node Feature Transformation (Graph-Faltung)
            x = self.conv1(x, edge_index)
            x = F.relu(x)
            x = F.dropout(x, p=0.1, training=self.training)
            
            x = self.conv2(x, edge_index)
            x = F.relu(x)
            
            # 2. Graph Readout (Globales Pooling über alle Atom-Nodes im Molekül)
            # Batch gibt an, welcher Node zu welchem Molekül im Minibatch gehört
            x = global_mean_pool(x, batch)
            
            # 3. Klassifikations-Layer
            x = self.fc(x)
            return x
else:
    class ChemicalGNN:
        """Fallback class when torch or torch-geometric are not installed."""
        def __init__(self, *args, **kwargs):
            pass
        def __call__(self, *args, **kwargs):
            return self
        def train(self, *args, **kwargs):
            pass
        def state_dict(self, *args, **kwargs):
            return {}
        def parameters(self, *args, **kwargs):
            return []


# --- Datenaufbereitung (SMILES zu Graph) ---
def smiles_to_graph(smiles: str, label: int = None):
    """
    Konvertiert ein Molekül aus der SMILES-Notation in ein 
    PyTorch Geometric Graph-Objekt (Data).
    
    Nodes = Atome
    Edges = Bindungen
    """
    if not HAS_RDKIT or not HAS_TORCH:
        return None
        
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    
    # 1. Node-Features extrahieren [Ordnungszahl, Bindigkeit, Formale Ladung]
    node_features = []
    for atom in mol.GetAtoms():
        node_features.append([
            float(atom.GetAtomicNum()),      # z.B. 6 für Kohlenstoff, 8 für Sauerstoff
            float(atom.GetTotalValence()),   # Anzahl der Bindungspartner
            float(atom.GetFormalCharge())    # Formale Ladung (+1, -1, 0)
        ])
    x = torch.tensor(node_features, dtype=torch.float)
    
    # 2. Edge-Index extrahieren (Konnektivität der Bindungen)
    edge_indices = []
    for bond in mol.GetBonds():
        u = bond.GetBeginAtomIdx()
        v = bond.GetEndAtomIdx()
        # Ungerichteter Graph: Bindung in beide Richtungen eintragen
        edge_indices.append([u, v])
        edge_indices.append([v, u])
        
    if len(edge_indices) > 0:
        edge_index = torch.tensor(edge_indices, dtype=torch.long).t().contiguous()
    else:
        # Fallback für einzelne Atome
        edge_index = torch.empty((2, 0), dtype=torch.long)
        
    # 3. Data-Objekt erstellen
    data = Data(x=x, edge_index=edge_index)
    
    # Klassen-Label hinzufügen
    if label is not None:
        data.y = torch.tensor([label], dtype=torch.long)
        
    return data


# --- Synthetischer Datensatz ---
def get_synthetic_dataset():
    """
    Erstellt einen in-memory Datensatz zur Klassifikation von funktionellen Gruppen:
    Klasse 0: Carbonsäuren / Ester (Carbonyl-haltig)
    Klasse 1: Alkohole / Ether
    Klasse 2: Halogenalkane / Alkene
    """
    raw_data = [
        # Klasse 0: Carbonyl-Verbindungen
        ("CC(=O)O", 0), ("CC(=O)OCC", 0), ("CC(=O)OC(C)C", 0), ("CCC(=O)O", 0), ("CC(=O)C", 0),
        # Klasse 1: Alkohole und Ether
        ("CCO", 1), ("CO", 1), ("CCOCC", 1), ("CCC(O)C", 1), ("CCCO", 1),
        # Klasse 2: Alkene und Halogenalkane
        ("CC=C", 2), ("C=C", 2), ("CCC=C", 2), ("CC(Cl)C", 2), ("CCC(Br)C", 2)
    ]
    
    dataset = []
    for smiles, label in raw_data:
        graph = smiles_to_graph(smiles, label)
        if graph is not None:
            dataset.append(graph)
            
    return dataset


# --- Training ---
def train_model(epochs=30, lr=0.01, hidden_dim=16):
    """Führt das Training des GNN-Modells aus."""
    print("🤖 Bereite Datensatz vor...")
    dataset = get_synthetic_dataset()
    if not dataset:
        print("Fehler beim Erstellen des Datensatzes.")
        return
        
    # Minibatch DataLoader
    loader = DataLoader(dataset, batch_size=4, shuffle=True)
    
    print(f"Datensatz geladen: {len(dataset)} Molekülgraphen.")
    print(f"Features pro Node (Atom): 3")
    print(f"Anzahl Klassen (Verbindungstypen): 3")
    
    # Modell initialisieren (3 Input-Features, hidden_dim Kanäle, 3 Ausgabeklassen)
    model = ChemicalGNN(num_node_features=3, hidden_dim=hidden_dim, num_classes=3)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    
    print("\n🚀 Starte GNN-Modelltraining...")
    model.train()
    
    for epoch in range(1, epochs + 1):
        total_loss = 0
        correct = 0
        for batch in loader:
            optimizer.zero_grad()
            out = model(batch)
            loss = criterion(out, batch.y)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item() * batch.num_graphs
            pred = out.argmax(dim=-1)
            correct += int((pred == batch.y).sum())
            
        epoch_loss = total_loss / len(dataset)
        accuracy = correct / len(dataset)
        
        if epoch == 1 or epoch % 5 == 0 or epoch == epochs:
            print(f"  Epoche {epoch:03d}/{epochs:03d} | Loss: {epoch_loss:.4f} | Trainings-Genauigkeit: {accuracy*100:.1f}%")
            
    # Modell exportieren
    os.makedirs("models", exist_ok=True)
    model_path = "models/chemical_gnn.pth"
    torch.save(model.state_dict(), model_path)
    print(f"\n✅ Training erfolgreich beendet! Modell gespeichert unter: {model_path}")
    print("Dieses Modell kann nun zur Klassifikation von Molekülgraphen verwendet werden.")


def main():
    parser = argparse.ArgumentParser(description="MechAInsm GNN Modell-Trainingspipeline")
    parser.add_argument("--epochs", type=int, default=30, help="Anzahl der Trainingsepochen")
    parser.add_argument("--lr", type=float, default=0.01, help="Lernrate für den Adam-Optimizer")
    parser.add_argument("--hidden_dim", type=int, default=16, help="Dimension der versteckten Layer")
    args = parser.parse_args()
    
    if not check_dependencies():
        sys.exit(1)
        
    train_model(epochs=args.epochs, lr=args.lr, hidden_dim=args.hidden_dim)


if __name__ == "__main__":
    main()
