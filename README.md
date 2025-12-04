<div align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/2534/2534204.png" width="100">
  
  # GMO Click Style FX Simulator
  
  <img src="https://img.shields.io/badge/python-3.x-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/GUI-Tkinter-green?logo=python" alt="Tkinter">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
  <img src="https://img.shields.io/badge/status-Active-success" alt="Status">

  <br>
  <a href="#-overview">Overview</a> •
  <a href="#-features">Features</a> •
  <a href="#-demo">Demo</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-author">Author</a>
  
  <br><br>
</div>

---

## 📖 Overview

**GMO Click Style FX Simulator** is a desktop trading application built with **Python** and **Tkinter**.
Designed to simulate the professional UI of Japanese securities platforms, featuring real-time rate updates, interactive charting, and high-performance rendering.

<div align="center">
  <img src="images/demo.gif" width="700" alt="Demo Animation">
</div>

---

## ✨ Features

* **📈 Professional UI:** Dark-mode interface inspired by real trading platforms.
* **⚡ Real-time Simulation:** Multi-threaded data fetching for seamless updates.
* **📊 Interactive Charts:** Candlestick charts powered by `mplfinance` with auto-resizing.
* **🛡️ Order System:** "Speed Order" interface for one-click trading simulation.

---

## 📸 Screenshots

| **Home View** | **Trade View** |
|:---:|:---:|
| <img src="images/home.png" width="400"> | <img src="images/trade.png" width="400"> |

| **Chart Analysis** | **Speed Order** |
|:---:|:---:|
| <img src="images/chart.png" width="400"> | <img src="images/order.png" width="400"> |

---

## 📦 Installation

```bash
# 1. Clone the repository
git clone [https://github.com/syxoxu/tradeSoft.git](https://github.com/syxoxu/tradeSoft.git)
cd tradeSoft

# 2. Install dependencies
pip install pandas numpy matplotlib mplfinance

# 3. Run the app
python main.py