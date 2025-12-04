# FX Trading Simulator (Desktop GUI)

A desktop FX trading simulation application built with Python and Tkinter.
Designed with a modern dark-mode GUI inspired by professional Japanese trading platforms (e.g., GMO Click Securities), featuring real-time rate updates and interactive charting.

![Demo App Animation](https://via.placeholder.com/800x450?text=Please+Upload+Demo+GIF+Here)
## 📖 Overview

This project was developed to demonstrate **desktop GUI application development** and **asynchronous data handling**.
It includes a built-in dummy data generator, allowing the application to run immediately without requiring external API keys or internet access.

## ✨ Key Features

* **Authentication System:** User registration and login functionality (Local data management via CSV).
* **Multi-View Interface:**
    * **Home:** Asset summary and grid menu.
    * **Trade:** Real-time rate list with color-coded indicators (Red/Blue) for price fluctuations.
    * **Speed Order:** UI designed for one-click ordering.
    * **Chart:** Interactive candlestick charts using `mplfinance` (Auto-resizing).
    * **Market:** News feed list.
* **Asynchronous Architecture:** Utilizing `threading` to fetch data in the background, ensuring the GUI never freezes.
* **Optimized Rendering:** Implemented logic to update only changed values to prevent screen flickering.

## 🛠 Tech Stack

* **Language:** Python 3.x
* **GUI Framework:** Tkinter
* **Data Processing:** Pandas, NumPy
* **Visualization:** Matplotlib, mplfinance
* **Concurrency:** Threading

## 📦 Installation & Usage

### 1. Clone the repository
```bash
git clone [https://github.com/syxoxu/tradeSoft.git](https://github.com/syxoxu/tradeSoft.git)
cd tradeSoft