# Portfolio

**Rishard Dukes's Online Portfolio**  
Computational Science Grad • AI/ML & Software • Evolving IT Technician/Software Engineer from Florida State University (B.S.)

---

*Projects you can actually use.*
That has grown into my motto. I’m a hard-working engineer who delivers clean, well-documented code that solves real problems. I’ve built numerical-methods toolkits, computer-vision pipelines, and ML demos—and I still get hands-on with practical IT work like connectivity checks and troubleshooting. I value clarity, reliability, and results.

📫 **Contacts:**  
- [LinkedIn](https://www.linkedin.com/in/rishard-dukes/)  
- [GitHub](https://github.com/RishardDukes)  
- [Email](mailto:scholasticdukes@gmail.com)

---

## 🧰 Core Skills
- **Programming:** Python, C++, MATLAB, HTML, Javascript 
- **ML/AI:** PCA (from scratch), CNNs (basics), clustering (K-Means), SOMs, regression  
- **Numerical Methods:** Trapezoidal, Simpson’s, Forward/Backward Euler, Adams–Bashforth, BDF, Runge–Kutta  
- **Image/Signal:** OpenCV, image I/O, pixel manipulation, watermarking  
- **Tools:** Git/GitHub, VS Code, Google Colab, Virtualenv, Jupyter  
- **IT Knowledge:** Networking fundamentals, ping/latency testing, Windows setup & support  

---

## 🚀 Quickstart

To run any of the projects in this portfolio:

```bash
# 1. Clone the repo
git clone https://github.com/RishardDukes/portfolio.git
cd portfolio

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run a demo (choose one)
python numerical_methods/numerical_demo.py
python pca_faces/pca_faces_demo.py
python kmeans_watermark/watermark_demo.py
python som_mammograms/som_demo.py
python ping_monitor/ping_demo.py
```
---
## 📂 Highlighted Projects

### Numerical Integration & ODE Solvers — *Error & Convergence Suite*
**What is it?**  
A mini-library implementing Trapezoidal/Simpson’s rules and ODE solvers utilizing relative error tables, log–log plots, and empirical convergence orders.  
**Tech Involved:** Python, NumPy, Matplotlib  
**Repo:** [View Project](numerical_methods)

---

### Face Recognition via PCA (AT&T Dataset)
**What is it?**  
PCA from scratch for face dimensionality reduction and classification utilizing a data loader for PGM images, eigenfaces, projection + custom distance classifier.  
**Tech Involved:** Python, NumPy, SciPy, Matplotlib  
**Repo:** [View Project](pca_faces)

---

### Image Watermarking with K-Means
**What is it?**  
Embed and extract a visible watermark using K-Means on image channels/blocks utilizing a pipeline to insert a smiley PNG watermark and recover it; analysis of quality vs. compression.  
**Tech Involved:** Python, OpenCV, NumPy  
**Repo:** [View Project](kmeans_watermark)

---

### Ping & Network Monitor Script
**What is it?**  
Quick connectivity checker with clean terminal output and summary utilizing ICMP pings, latency stats, reachable/unreachable reporting.  
**Tech Involved:** Python (subprocess), Windows/PowerShell notes  
**Repo:** [View Project](ping_monitor)

---

### SOM for Mammographic Image Patterns
**What is it?**  
Pattern discovery on medical imaging using Self-Organizing Maps (demo currently uses sklearn digits for proof of concept).  
**Tech Involved:** Python, scikit-learn, sklearn_som, Matplotlib  
**Repo:** [View Project](som_mammograms)

---

### Workout Tracker — Widget + CLI *(Additional Project)*
**What is it?**  
Local SQLite workout logger with a small Flask widget UI and a simple CLI for adding sets and plotting progress.  
**Tech Involved:** Python, Flask, Matplotlib, SQLite  
**Repo:** [View Project](additional_projects/workout_tracker)

---

### Ping Checker 2.0 — Async uptime + HTML report *(Additional Project)*
**What is it?**  
Asynchronous TCP host checks with SQLite history and a static HTML report (no external dependencies).  
**Tech Involved:** Python stdlib (`asyncio`, `sqlite3`, `argparse`, `pathlib`)  
**Repo:** [View Project](additional_projects/ping_checker_2)

