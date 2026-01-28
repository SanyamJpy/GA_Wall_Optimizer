# GA Wall Optimizer – Adaptive Genetic Algorithm for Wall Design Optimization

Optimize multi-layer wall assemblies using a custom-built Genetic Algorithm to minimize GWP while meeting thermal constraints. The algorithm evolves wall configurations across generations to find the most efficient design.

---

## 🔍 Project Overview

- Evolves wall layer thicknesses and materials using GA principles (selection, crossover, mutation).
- Evaluates fitness based on thermal coefficient and total GWP.
- Visualizes convergence and optimal parameters using real-time plots.
- Modular and customizable for different building envelopes.

---

## 🛠️ Requirements

- Python 3.8+
- `matplotlib` (for visualization)
- Git (to clone the repo)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/SanyamJpy/GA_Wall_Optimizer.git
cd GA_Wall_Optimizer
### 2. Install dependencies (if not installed already)
pip install matplotlib
### 3. Run the algorithm
python main.py

---

## ⚙️ Customization
Edit main.py to tweak:
- 'population': Number of wall variants per generation (default:30)
- 'generations': Total number of evolutionary cycles (default:20)
- 'mut_start': Adaptive mutation start rate (default:0.5)
- 'mut_end': Adaptive mutation start rate (default:0.1)

---

##  Improvements and suggestions are welcome :)


```
