import tkinter as tk
from tkinter import ttk
import threading
import time
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import math

# --- Graphing ---
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplfinance as mpf

# ---------------------------------------------------------
# Constants & Colors (GMO Click Securities Style)
# ---------------------------------------------------------
CSV_FILE = "login.csv"
UPDATE_INTERVAL = 1000  # ms (1.0 second)

# Color Palette
COLOR_BG_MAIN = "#0e1629"
COLOR_HEADER = "#050a15"
COLOR_PANEL_BG = "#1c2640"
COLOR_PANEL_WHITE = "#ffffff"
COLOR_TEXT_MAIN = "#ffffff"
COLOR_TEXT_BLACK = "#000000"
COLOR_ACCENT_RED = "#e74c3c"
COLOR_ACCENT_BLUE = "#3498db"
COLOR_ACCENT_GOLD = "#f39c12"
COLOR_BTN_MENU = "#24345e"

# Fonts
FONT_L = ("Meiryo UI", 16, "bold")
FONT_M = ("Meiryo UI", 12)
FONT_S = ("Meiryo UI", 10)
FONT_NUM_L = ("Arial", 28, "bold")
FONT_NUM_M = ("Arial", 18, "bold")
FONT_NUM_S = ("Arial", 14, "bold")

# ---------------------------------------------------------
# Common Functions
# ---------------------------------------------------------
def center_window(window, width, height):
    """Centers the window on the screen"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

# ---------------------------------------------------------
# Data Manager
# ---------------------------------------------------------
class DataManager:
    @staticmethod
    def fetch_real_data():
        """Fetches data from external module or returns dummy"""
        try:
            import repRateModu01
            fd = repRateModu01.fetch_get_FXrate()
            fg = repRateModu01.fetch_get_Cryptorate()
            return fd, fg
        except ImportError:
            return DataManager.create_dummy_dataframe()
        except Exception as e:
            print(f"Data Fetch Error: {e}")
            return pd.DataFrame(), pd.DataFrame()

    @staticmethod
    def create_dummy_dataframe():
        # FX Dummy
        fx_data = []
        for pair in ['USD_JPY', 'EUR_JPY', 'GBP_JPY', 'TRY_JPY']:
            base = 150.0 if 'USD' in pair else 160.0
            bid = base + random.uniform(-0.1, 0.1)
            fx_data.append({
                'symbol': pair, 'bid': bid, 'ask': bid + 0.003, 
                'high': bid + 0.5, 'low': bid - 0.5
            })
        
        # Crypto Dummy
        crypto_data = []
        for pair in ['BTC_JPY', 'ETH_JPY', 'XRP_JPY', 'DOGE_JPY']:
            base = 14000000 if 'BTC' in pair else 500000
            bid = base + random.uniform(-100, 100)
            crypto_data.append({
                'symbol': pair, 'bid': bid, 'ask': bid + 100, 
                'high': bid * 1.01, 'low': bid * 0.99, 'volume': 1000
            })
            
        return pd.DataFrame(fx_data), pd.DataFrame(crypto_data)

    @staticmethod
    def get_ohlc(periods=60):
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=periods)
        index = pd.date_range(start=start_time, periods=periods, freq='1min')
        base = 155.50
        close = base + np.cumsum(np.random.randn(periods) * 0.05)
        high = close + np.random.rand(periods) * 0.03
        low = close - np.random.rand(periods) * 0.03
        open_ = close - np.random.randn(periods) * 0.02
        df = pd.DataFrame({
            'Open': open_, 'High': high, 'Low': low, 'Close': close,
            'Volume': np.random.randint(100, 1000, size=periods)
        }, index=index)
        return df

    @staticmethod
    def get_news():
        titles = [
            "米GDP速報値、市場予想を上回る", "日銀総裁「緩和的な金融環境を維持」",
            "ドル円、一時156円台へ上昇", "欧州中銀、利下げ観測が後退",
            "【市況】東京市場、前場は小幅反落", "原油先物、供給懸念で上昇"
        ]
        news_data = []
        t = datetime.now()
        for title in titles:
            t_str = t.strftime("%m/%d %H:%M")
            news_data.append((t_str, title))
            t -= timedelta(minutes=random.randint(10, 60))
        return news_data

# ---------------------------------------------------------
# View Classes
# ---------------------------------------------------------

class HomeView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLOR_BG_MAIN)
        self.create_layout()

    def create_layout(self):
        info_frame = tk.Frame(self, bg=COLOR_PANEL_WHITE, padx=20, pady=15)
        info_frame.pack(fill="x", padx=20, pady=20)
        for i in range(4): info_frame.columnconfigure(i, weight=1)

        def add_info(col, label, val_text, color="black", size=14):
            f = tk.Frame(info_frame, bg=COLOR_PANEL_WHITE)
            f.grid(row=0, column=col, sticky="nsew", padx=10)
            tk.Label(f, text=label, font=("Meiryo UI", 10), fg="#666", bg=COLOR_PANEL_WHITE).pack(anchor="w")
            tk.Label(f, text=val_text, font=("Arial", size, "bold"), fg=color, bg=COLOR_PANEL_WHITE).pack(anchor="e")

        add_info(0, "余力", "9,788,123円")
        add_info(1, "時価評価総額", "14,198,000円")
        add_info(2, "評価損益", "+1,091,000円", COLOR_ACCENT_RED)
        add_info(3, "証拠金維持率", "321.95%", "blue")

        menu_frame = tk.Frame(self, bg=COLOR_BG_MAIN)
        menu_frame.pack(fill="both", expand=True, padx=20)
        menus = [("✉️", "お知らせ"), ("To", "入出金/振替"), ("⚙️", "注文設定"), ("📓", "トレード日記"),
                 ("🔔", "アラート"), ("💰", "スワップ"), ("📄", "報告書"), ("👤", "登録情報"),
                 ("ℹ️", "ヘルプ"), ("🔧", "設定"), ("❓", "問い合わせ"), ("🔒", "ログアウト")]
        cols = 6
        for i in range(cols): menu_frame.columnconfigure(i, weight=1)
        for i, (icon, text) in enumerate(menus):
            r, c = i // cols, i % cols
            btn_f = tk.Frame(menu_frame, bg=COLOR_BG_MAIN, padx=5, pady=5)
            btn_f.grid(row=r, column=c, sticky="nsew")
            btn = tk.Button(btn_f, text=f"{icon}\n{text}", font=FONT_M, bg=COLOR_BTN_MENU, fg="white", 
                            relief="flat", activebackground="#354675", activeforeground="white")
            btn.pack(fill="both", expand=True, ipady=20)


class TradeView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLOR_BG_MAIN)
        self.rate_labels = {} 
        self.prev_values = {} # To avoid unnecessary updates
        self.create_layout()

    def create_layout(self):
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        # Left: Rates
        left_panel = tk.Frame(self, bg=COLOR_BG_MAIN, padx=10, pady=10)
        left_panel.grid(row=0, column=0, sticky="nsew")

        tk.Label(left_panel, text="リアルタイムレート一覧", font=FONT_M, bg=COLOR_BG_MAIN, fg="white").grid(row=0, column=0, columnspan=5, sticky="w", pady=5)

        headers = ["通貨ペア", "Bid (売)", "Ask (買)", "High", "Low"]
        for idx, h in enumerate(headers):
            tk.Label(left_panel, text=h, font=FONT_S, bg=COLOR_BG_MAIN, fg="#888").grid(row=1, column=idx, sticky="ew", padx=5)

        self.display_pairs = [
            "USD/JPY", "EUR/JPY", "GBP/JPY", "TRY/JPY",
            "BTC/JPY", "ETH/JPY", "XRP/JPY", "DOGE/JPY",
            "BTC/USD"
        ]

        for i, pair in enumerate(self.display_pairs, start=2):
            tk.Label(left_panel, text=pair, font=FONT_M, bg=COLOR_BG_MAIN, fg="white").grid(row=i, column=0, sticky="w", pady=8, padx=5)
            
            self.rate_labels[f"{pair}_bid"] = tk.Label(left_panel, text="-", font=FONT_NUM_S, bg=COLOR_BG_MAIN, fg=COLOR_ACCENT_BLUE)
            self.rate_labels[f"{pair}_bid"].grid(row=i, column=1, sticky="e", padx=5)

            self.rate_labels[f"{pair}_ask"] = tk.Label(left_panel, text="-", font=FONT_NUM_S, bg=COLOR_BG_MAIN, fg=COLOR_ACCENT_RED)
            self.rate_labels[f"{pair}_ask"].grid(row=i, column=2, sticky="e", padx=5)

            self.rate_labels[f"{pair}_high"] = tk.Label(left_panel, text="-", font=FONT_S, bg=COLOR_BG_MAIN, fg="white")
            self.rate_labels[f"{pair}_high"].grid(row=i, column=3, sticky="e", padx=5)

            self.rate_labels[f"{pair}_low"] = tk.Label(left_panel, text="-", font=FONT_S, bg=COLOR_BG_MAIN, fg="white")
            self.rate_labels[f"{pair}_low"].grid(row=i, column=4, sticky="e", padx=5)
            
            ttk.Separator(left_panel, orient="horizontal").grid(row=i*10+5, column=0, columnspan=5, sticky="ew", pady=0)

        # Right: Positions
        right_panel = tk.Frame(self, bg=COLOR_BG_MAIN, padx=10, pady=10)
        right_panel.grid(row=0, column=1, sticky="nsew")

        tab_box = tk.Frame(right_panel, bg=COLOR_BG_MAIN)
        tab_box.pack(fill="x", pady=5)
        for t in ["建玉サマリ", "建玉一覧", "注文一覧", "約定履歴"]:
            tk.Button(tab_box, text=t, font=FONT_S, bg="#333", fg="white", width=10).pack(side="left", padx=1)

        cols = ("通貨", "売買", "数量", "損益")
        tree = ttk.Treeview(right_panel, columns=cols, show="headings", height=15)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=COLOR_PANEL_BG, foreground="white", fieldbackground=COLOR_PANEL_BG, rowheight=30)
        style.configure("Treeview.Heading", background="#333", foreground="white", font=FONT_S)
        
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=60, anchor="center")

        tree.pack(fill="both", expand=True)
        tree.insert("", "end", values=("USD/JPY", "買", "10,000", "+12,500"))

    def update_table(self, fx_df, crypto_df):
        try:
            for sym in ["USD_JPY", "EUR_JPY", "GBP_JPY", "TRY_JPY"]:
                row = fx_df.loc[fx_df['symbol'] == sym]
                if not row.empty:
                    self._update_row(sym.replace("_", "/"), row.iloc[0], is_crypto=False)

            for sym in ["BTC_JPY", "ETH_JPY", "XRP_JPY", "DOGE_JPY"]:
                row = crypto_df.loc[crypto_df['symbol'] == sym]
                if not row.empty:
                    self._update_row(sym.replace("_", "/"), row.iloc[0], is_crypto=True)

            usd = fx_df.loc[fx_df['symbol'] == 'USD_JPY']
            btc = crypto_df.loc[crypto_df['symbol'] == 'BTC_JPY']
            
            if not usd.empty and not btc.empty:
                u_ask = float(usd.iloc[0]['ask'])
                u_bid = float(usd.iloc[0]['bid'])
                b_bid = float(btc.iloc[0]['bid'])
                b_ask = float(btc.iloc[0]['ask'])
                
                calc_bid = b_bid / u_ask
                calc_ask = b_ask / u_bid
                
                data = {'bid': calc_bid, 'ask': calc_ask, 'high': 0, 'low': 0}
                self._update_row("BTC/USD", pd.Series(data), is_crypto=False)

        except Exception:
            pass

    def _update_row(self, pair, data, is_crypto):
        fmt = "{:,.0f}" if is_crypto and "BTC" in pair else "{:,.3f}"
        if pair == "BTC/USD": fmt = "{:,.2f}"

        # Optimization: Only update if text has changed
        vals = {
            'bid': fmt.format(float(data['bid'])),
            'ask': fmt.format(float(data['ask'])),
            'high': fmt.format(float(data.get('high', 0))),
            'low': fmt.format(float(data.get('low', 0)))
        }

        # Compare with previous values to reduce flickering
        if f"{pair}_bid" in self.rate_labels:
            self._set_text(f"{pair}_bid", vals['bid'])
            self._set_text(f"{pair}_ask", vals['ask'])
            if float(data.get('high', 0)) > 0: self._set_text(f"{pair}_high", vals['high'])
            if float(data.get('low', 0)) > 0: self._set_text(f"{pair}_low", vals['low'])

    def _set_text(self, key, text):
        if self.prev_values.get(key) != text:
            self.rate_labels[key].config(text=text)
            self.prev_values[key] = text


class SpeedOrderView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLOR_BG_MAIN)
        self.create_layout()

    def create_layout(self):
        container = tk.Frame(self, bg=COLOR_BG_MAIN)
        container.pack(expand=True)
        header = tk.Frame(container, bg=COLOR_BG_MAIN)
        header.pack(fill="x", pady=10)
        tk.Label(header, text="🇺🇸🇯🇵 USD/JPY", font=("Arial", 24, "bold"), fg="white", bg=COLOR_BG_MAIN).pack()

        rate_frame = tk.Frame(container, bg=COLOR_BG_MAIN)
        rate_frame.pack(pady=20)

        btn_bid = tk.Button(rate_frame, text="BID (売)\n155.497", font=("Arial", 20, "bold"),
                            bg=COLOR_ACCENT_BLUE, fg="white", width=15, height=3, relief="flat")
        btn_bid.pack(side="left", padx=10)

        tk.Label(rate_frame, text="0.2", font=("Arial", 14), fg="white", bg="#333", width=4).pack(side="left")

        btn_ask = tk.Button(rate_frame, text="ASK (買)\n155.499", font=("Arial", 20, "bold"),
                            bg=COLOR_ACCENT_RED, fg="white", width=15, height=3, relief="flat")
        btn_ask.pack(side="left", padx=10)

        ctrl_frame = tk.Frame(container, bg=COLOR_PANEL_BG, padx=20, pady=20)
        ctrl_frame.pack(fill="x", pady=20)
        tk.Label(ctrl_frame, text="取引数量 (×10,000)", font=FONT_M, fg="white", bg=COLOR_PANEL_BG).pack()
        spin = tk.Spinbox(ctrl_frame, from_=1, to=100, font=("Arial", 20), width=10, justify="center")
        spin.pack(pady=10)
        tk.Button(ctrl_frame, text="全決済", bg="#555", fg="white", font=FONT_M, width=20).pack(pady=10)


class MarketView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLOR_BG_MAIN)
        self.create_layout()

    def create_layout(self):
        tk.Label(self, text="マーケットニュース", font=FONT_L, fg="white", bg=COLOR_BG_MAIN).pack(pady=10, padx=20, anchor="w")
        list_frame = tk.Frame(self, bg=COLOR_BG_MAIN, padx=20)
        list_frame.pack(fill="both", expand=True)
        cols = ("日時", "タイトル")
        tree = ttk.Treeview(list_frame, columns=cols, show="headings")
        tree.heading("日時", text="日時")
        tree.heading("タイトル", text="タイトル")
        tree.column("日時", width=150, anchor="center")
        tree.column("タイトル", width=800, anchor="w")
        tree.pack(fill="both", expand=True, pady=10)
        news = DataManager.get_news()
        for date, title in news:
            tree.insert("", "end", values=(date, title))


class ChartView(tk.Frame):
    """【チャート】 ローソク足表示（軽量化対策済み）"""
    def __init__(self, master):
        super().__init__(master, bg=COLOR_BG_MAIN)
        self.chart_frame = None
        self.resize_timer = None  # 【追加】再描画待ちタイマー
        self.create_layout()

    def create_layout(self):
        ctrl_bar = tk.Frame(self, bg=COLOR_HEADER, height=40)
        ctrl_bar.pack(fill="x", side="top")
        tk.Label(ctrl_bar, text="USD/JPY 1分足", font=FONT_M, fg="white", bg=COLOR_HEADER).pack(side="left", padx=20)
        
        self.chart_frame = tk.Frame(self, bg="black")
        self.chart_frame.pack(fill="both", expand=True)
        
        # 初回描画
        self.draw_chart()

        # 【追加】サイズ変更イベントを監視
        self.chart_frame.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        """サイズ変更中に何度も描画されるのを防ぐ処理"""
        # 前回の予約があればキャンセル（「まだ描画するな！」）
        if self.resize_timer:
            self.after_cancel(self.resize_timer)
        
        # 0.5秒後に描画を予約（マウスを止めたら描画されるようになる）
        self.resize_timer = self.after(500, self.draw_chart)

    def draw_chart(self):
        # 既存のグラフがあれば削除（メモリリーク防止）
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        df = DataManager.get_ohlc(100)
        mc = mpf.make_marketcolors(up=COLOR_ACCENT_RED, down=COLOR_ACCENT_BLUE, 
                                   edge='inherit', wick='inherit', volume='in')
        s = mpf.make_mpf_style(marketcolors=mc, base_mpf_style='nightclouds', gridstyle=':')
        
        # チャート生成
        fig, axes = mpf.plot(df, type='candle', style=s, volume=False, returnfig=True, figsize=(10, 6))
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
# ---------------------------------------------------------
# Main App
# ---------------------------------------------------------
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title("GMO Click FX Style - PC Version")
        self.configure(bg=COLOR_BG_MAIN)
        center_window(self, 1280, 800)

        self.create_footer()
        
        self.container = tk.Frame(self, bg=COLOR_BG_MAIN)
        self.container.pack(side="top", fill="both", expand=True)

        # 【追加】ここから：コンテナ内のグリッドを伸縮可能にする設定
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (HomeView, TradeView, SpeedOrderView, MarketView, ChartView):
            page_name = F.__name__
            frame = F(master=self.container)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("TradeView")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.running = True
        # Start data loop
        self.update_data()

    def create_footer(self):
        footer = tk.Frame(self, bg=COLOR_HEADER, height=60)
        footer.pack(side="bottom", fill="x")
        tabs = [
            ("🏠 ホーム", "HomeView"), ("📈 トレード", "TradeView"),
            ("⚡ スピード", "SpeedOrderView"), ("🌏 マーケット", "MarketView"),
            ("📉 チャート", "ChartView")
        ]
        for text, view_name in tabs:
            btn = tk.Button(footer, text=text, font=("Meiryo UI", 11, "bold"),
                            bg=COLOR_HEADER, fg="#aaa", bd=0, activebackground="#222", activeforeground="white",
                            command=lambda name=view_name: self.show_frame(name))
            btn.pack(side="left", fill="both", expand=True)

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        #  - Conceptually, this brings the frame to the top of the stack.

    def update_data(self):
        """Fetch data and update UI in a loop"""
        if not self.running: return

        # Running in a separate thread to prevent UI freezing during fetch
        threading.Thread(target=self._fetch_and_update, daemon=True).start()
        
        # Schedule next update
        self.after(UPDATE_INTERVAL, self.update_data)

    def _fetch_and_update(self):
        fd, fg = DataManager.fetch_real_data()
        if not fd.empty and not fg.empty:
            # Schedule the UI update on the main thread
            self.after(0, lambda: self.frames["TradeView"].update_table(fd, fg))

    def on_close(self):
        self.running = False
        plt.close('all')
        self.destroy()
        sys.exit()

# ---------------------------------------------------------
# Login Window
# ---------------------------------------------------------
class LoginWindow(tk.Toplevel):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.title("Login")
        self.configure(bg=COLOR_BG_MAIN)
        center_window(self, 400, 600)
        self.protocol("WM_DELETE_WINDOW", sys.exit)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="GMOクリック FX", font=("Arial", 24, "bold"), bg=COLOR_BG_MAIN, fg="white").pack(pady=50)
        tk.Label(self, text="ユーザーID", bg=COLOR_BG_MAIN, fg="white").pack()
        self.entry_id = tk.Entry(self, font=FONT_M)
        self.entry_id.pack(pady=5)
        tk.Label(self, text="パスワード", bg=COLOR_BG_MAIN, fg="white").pack()
        self.entry_pw = tk.Entry(self, font=FONT_M, show="*")
        self.entry_pw.pack(pady=5)
        tk.Button(self, text="ログイン", font=FONT_M, bg=COLOR_ACCENT_GOLD, fg="white", width=20,
                  command=self.do_login).pack(pady=30)

    def do_login(self):
        self.destroy()
        self.main_app.deiconify()

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass

    app = MainApp()
    login = LoginWindow(app)
    app.mainloop()