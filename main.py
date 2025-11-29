import csv
import tkinter as tk
from tkinter import ttk
import threading
import time
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- 追加ライブラリ ---
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplfinance as mpf

# ---------------------------------------------------------
# 設定・定数
# ---------------------------------------------------------
CSV_FILE = "login.csv"
UPDATE_INTERVAL = 1.0

# 配色定義 (GMOクリック証券風)
COLOR_BG_LOGIN = "#0e1629"     # ログイン画面背景（濃紺）
COLOR_PANEL_LOGIN = "#1c2640"  # トグルスイッチなどのパネル背景
COLOR_BTN_LOGIN = "#f3c648"    # ログインボタン（金色）
COLOR_BTN_DEMO = "#58aebf"     # デモ取引ボタン（青緑）
COLOR_BTN_ACC = "#222222"      # 口座開設ボタン（黒系）

COLOR_BG_MAIN = "#0e1629"
COLOR_PANEL_BG = "#ffffff"
COLOR_BTN_MENU = "#24345e"
COLOR_TEXT_MAIN = "#000000"
COLOR_TEXT_SUB = "#666666"
COLOR_CHART_BG = "#131722"

# ---------------------------------------------------------
# 便利関数: ウィンドウを画面中央に配置する
# ---------------------------------------------------------
def center_window(window, width, height):
    """ウィンドウを指定サイズで画面中央に配置する"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

# ---------------------------------------------------------
# ダミーデータ生成
# ---------------------------------------------------------
try:
    import repRateModu01
except ImportError:
    import random
    class repRateModu01:
        @staticmethod
        def fetch_get_FXrate():
            bid = 150.00 + random.uniform(-0.2, 0.2)
            ask = bid + 0.003
            return pd.DataFrame({
                'symbol': ['USD_JPY'],
                'bid': [bid],
                'ask': [ask]
            })

def create_dummy_ohlc_data(periods=100):
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=periods)
    index = pd.date_range(start=start_time, periods=periods, freq='1min')
    base_price = 150.00
    np.random.seed(42)
    changes = np.random.randn(periods) * 0.05
    close = base_price + np.cumsum(changes)
    high = close + np.random.rand(periods) * 0.03
    low = close - np.random.rand(periods) * 0.03
    open_ = close - changes * 0.5
    df = pd.DataFrame({
        'Open': open_, 'High': high, 'Low': low, 'Close': close,
        'Volume': np.random.randint(100, 1000, size=periods)
    }, index=index)
    return df

# ---------------------------------------------------------
# ログイン画面クラス
# ---------------------------------------------------------
class Login:
    def __init__(self, master, main):
        self.master = master
        self.main = main
        self.widgets = []
        self.create_widgets()

    def create_widgets(self):
        self.master.configure(bg=COLOR_BG_LOGIN)
        
        # ロゴエリア
        logo_frame = tk.Frame(self.master, bg=COLOR_BG_LOGIN, pady=30)
        logo_frame.pack(fill="x")
        logo_inner = tk.Frame(logo_frame, bg=COLOR_BG_LOGIN)
        logo_inner.pack()
        tk.Label(logo_inner, text="GMOクリック", font=("Arial", 20, "bold"), fg="white", bg=COLOR_BG_LOGIN).pack(side="left")
        tk.Label(logo_inner, text=" FX ", font=("Arial", 18, "bold", "italic"), fg="white", bg="#dba11c").pack(side="left", padx=5)

        # 入力フォームエリア
        input_frame = tk.Frame(self.master, bg=COLOR_BG_LOGIN, padx=30)
        input_frame.pack(fill="x", pady=10)

        # ユーザーID
        row1 = tk.Frame(input_frame, bg=COLOR_BG_LOGIN)
        row1.pack(fill="x")
        tk.Label(row1, text="ユーザーID/ログイン名", font=("Arial", 9), fg="white", bg=COLOR_BG_LOGIN).pack(side="left")
        self.var_save_id = tk.BooleanVar(value=True)
        tk.Checkbutton(row1, text="保存", var=self.var_save_id, bg=COLOR_BG_LOGIN, fg="white", 
                              selectcolor=COLOR_BG_LOGIN, activebackground=COLOR_BG_LOGIN, activeforeground="white").pack(side="right")
        self.name_entry = tk.Entry(input_frame, font=("Arial", 14), width=30)
        self.name_entry.pack(fill="x", pady=(2, 15))

        # パスワード
        row2 = tk.Frame(input_frame, bg=COLOR_BG_LOGIN)
        row2.pack(fill="x")
        tk.Label(row2, text="ログインパスワード", font=("Arial", 9), fg="white", bg=COLOR_BG_LOGIN).pack(side="left")
        self.var_save_pass = tk.BooleanVar(value=True)
        tk.Checkbutton(row2, text="保存", var=self.var_save_pass, bg=COLOR_BG_LOGIN, fg="white", 
                              selectcolor=COLOR_BG_LOGIN, activebackground=COLOR_BG_LOGIN, activeforeground="white").pack(side="right")
        self.pass_entry = tk.Entry(input_frame, show="*", font=("Arial", 14), width=30)
        self.pass_entry.pack(fill="x", pady=(2, 10))

        # 設定パネル
        panel_frame = tk.Frame(self.master, bg=COLOR_PANEL_LOGIN, padx=15, pady=5)
        panel_frame.pack(fill="x", padx=30, pady=10)
        p_row1 = tk.Frame(panel_frame, bg=COLOR_PANEL_LOGIN, pady=5)
        p_row1.pack(fill="x")
        tk.Label(p_row1, text="自動ログイン", font=("Arial", 10), fg="white", bg=COLOR_PANEL_LOGIN).pack(side="left")
        self.draw_toggle(p_row1, is_on=False).pack(side="right")
        tk.Frame(panel_frame, height=1, bg="#444").pack(fill="x")
        p_row2 = tk.Frame(panel_frame, bg=COLOR_PANEL_LOGIN, pady=5)
        p_row2.pack(fill="x")
        tk.Label(p_row2, text="生体認証ログイン", font=("Arial", 10), fg="white", bg=COLOR_PANEL_LOGIN).pack(side="left")
        self.draw_toggle(p_row2, is_on=True).pack(side="right")

        tk.Label(self.master, text="ユーザーID・ログインパスワードをお忘れの場合", 
                 font=("Arial", 9), fg="#aaa", bg=COLOR_BG_LOGIN, cursor="hand2").pack(pady=10)

        # ログインボタン
        btn_frame = tk.Frame(self.master, bg=COLOR_BG_LOGIN, padx=30, pady=10)
        btn_frame.pack(fill="x")
        self.login_button = tk.Button(btn_frame, text="ログイン", command=self.login, 
                                      font=("Arial", 14, "bold"), bg=COLOR_BTN_LOGIN, fg="white", 
                                      relief="flat", cursor="hand2", activebackground="#e0b030")
        self.login_button.pack(fill="x", ipady=5)

        tk.Label(self.master, text="GMOクリック FXneo Ver. 1.23.0 ...", font=("Arial", 7), fg="#888", bg=COLOR_BG_LOGIN).pack(side="bottom", pady=(0, 60))

        # フッター
        footer_frame = tk.Frame(self.master, bg="#111", height=60)
        footer_frame.pack(side="bottom", fill="x")
        f_btn_area = tk.Frame(footer_frame, bg="#111", padx=10, pady=10)
        f_btn_area.pack(fill="both", expand=True)
        self.reg_button = tk.Button(f_btn_area, text="無料で口座開設", command=self.register,
                                    font=("Arial", 10, "bold"), bg=COLOR_BTN_ACC, fg="white", relief="flat")
        self.reg_button.pack(side="left", fill="both", expand=True, padx=5, ipady=5)
        self.demo_button = tk.Button(f_btn_area, text="デモ取引を始める", command=self.master.destroy,
                                     font=("Arial", 10, "bold"), bg=COLOR_BTN_DEMO, fg="white", relief="flat")
        self.demo_button.pack(side="left", fill="both", expand=True, padx=5, ipady=5)

    def draw_toggle(self, parent, is_on):
        c = tk.Canvas(parent, width=40, height=20, bg=COLOR_PANEL_LOGIN, highlightthickness=0)
        fill_color = "#4cd964" if is_on else "#999"
        c.create_oval(2, 2, 18, 18, fill=fill_color, outline="")
        c.create_oval(22, 2, 38, 18, fill=fill_color, outline="")
        c.create_rectangle(10, 2, 30, 18, fill=fill_color, outline="")
        circle_x = 30 if is_on else 10
        c.create_oval(circle_x-7, 3, circle_x+7, 17, fill="white", outline="")
        return c

    def login(self):
        username = self.name_entry.get()
        password = self.pass_entry.get()
        try:
            with open(CSV_FILE, 'r') as f:
                csv_data = csv.reader(f)
                for user in csv_data:
                    if len(user) >= 2 and user[0] == username and user[1] == password:
                        self.success(username)
                        return
        except FileNotFoundError:
            pass
        self.fail()

    def register(self):
        username = self.name_entry.get()
        password = self.pass_entry.get()
        if username and password:
            with open(CSV_FILE, 'a', newline='') as f:
                csv.writer(f).writerow([username, password])

    def fail(self):
        self.login_button.config(bg="red", text="失敗")
        self.master.after(1000, lambda: self.login_button.config(bg=COLOR_BTN_LOGIN, text="ログイン"))

    def success(self, username):
        self.login_button.config(bg="#4cd964", text="成功！")
        def switch_screen():
            self.main.start(username)
            self.master.destroy()
        self.master.after(500, switch_screen)


# ---------------------------------------------------------
# メインアプリ画面クラス
# ---------------------------------------------------------
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.font_main = ("Meiryo UI", 12) if sys.platform == "win32" else ("Helvetica", 12)
        self.font_bold = ("Meiryo UI", 12, "bold") if sys.platform == "win32" else ("Helvetica", 12, "bold")
        self.font_small = ("Meiryo UI", 9) if sys.platform == "win32" else ("Helvetica", 9)
        
        self.var_yoryoku = tk.StringVar(value="0円")
        self.var_jika = tk.StringVar(value="0円")
        self.var_sonneki = tk.StringVar(value="0円")
        self.var_rate_bid = tk.StringVar(value="---")
        self.var_rate_ask = tk.StringVar(value="---")
        
        self.main_content_frame = None
        self.chart_content_frame = None

    def start(self, username):
        self.deiconify()
        self.title("Trading View - GMO Style")
        self.configure(bg=COLOR_BG_MAIN)
        
        # 【追加】メイン画面も中央に配置 (サイズは400x750)
        center_window(self, 1000, 750)

        self.main_content_frame = tk.Frame(self, bg=COLOR_BG_MAIN)
        self.main_content_frame.pack(fill="both", expand=True, side="top")

        # ヘッダー
        header_frame = tk.Frame(self.main_content_frame, bg=COLOR_BG_MAIN, height=50)
        header_frame.pack(fill="x", pady=10)
        tk.Label(header_frame, text="GMOクリック FX", font=("Arial", 18, "bold", "italic"), bg=COLOR_BG_MAIN, fg="white").pack()

        # 情報パネル
        info_frame = tk.Frame(self.main_content_frame, bg=COLOR_PANEL_BG, padx=15, pady=10)
        info_frame.pack(fill="x", padx=10, pady=5)
        info_frame.columnconfigure(1, weight=1)

        def create_row(parent, row, label_text, var, color=COLOR_TEXT_MAIN, is_bold=False):
            f = self.font_bold if is_bold else self.font_main
            tk.Label(parent, text=label_text, font=self.font_main, bg=COLOR_PANEL_BG, fg=COLOR_TEXT_SUB).grid(row=row, column=0, sticky="w", pady=2)
            tk.Label(parent, textvariable=var, font=f, bg=COLOR_PANEL_BG, fg=color).grid(row=row, column=1, sticky="e", pady=2)

        create_row(info_frame, 0, "余力", self.var_yoryoku)
        create_row(info_frame, 1, "時価評価総額", self.var_jika, is_bold=True)
        ttk.Separator(info_frame, orient="horizontal").grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        create_row(info_frame, 3, "評価損益", self.var_sonneki)
        tk.Label(info_frame, text="USD/JPY (Bid)", font=self.font_main, bg=COLOR_PANEL_BG, fg=COLOR_TEXT_SUB).grid(row=4, column=0, sticky="w", pady=2)
        tk.Label(info_frame, textvariable=self.var_rate_bid, font=self.font_bold, bg=COLOR_PANEL_BG, fg="red").grid(row=4, column=1, sticky="e", pady=2)

        # メニュー
        menu_frame = tk.Frame(self.main_content_frame, bg=COLOR_BG_MAIN)
        menu_frame.pack(fill="both", expand=True, padx=10, pady=10)
        for i in range(3): menu_frame.columnconfigure(i, weight=1)
        menu_items = [("✉️", "お知らせ"), ("🔢", "余力確認"), ("💴", "入出金/振替"),
                      ("⚙️", "注文設定"), ("📓", "トレード日記"), ("🔔", "アラート/通知"),
                      ("💰", "スワップ"), ("📄", "精算表・報告書"), ("👤", "登録情報"),
                      ("ℹ️", "ヘルプ"), ("🔧", "設定"), ("❓", "問い合わせ")]
        for idx, (icon, text) in enumerate(menu_items):
            row, col = idx // 3, idx % 3
            f = tk.Frame(menu_frame, bg=COLOR_BG_MAIN, padx=2, pady=2)
            f.grid(row=row, column=col, sticky="nsew")
            tk.Button(f, text=f"{icon}\n{text}", font=self.font_small, bg=COLOR_BTN_MENU, fg="white", 
                      relief="flat", activebackground="#354675", activeforeground="white").pack(fill="both", expand=True, ipady=10)

        # フッター
        self.footer_frame = tk.Frame(self, bg="#050a15", height=60)
        self.footer_frame.pack(side="bottom", fill="x")
        footer_items = [("🏠\nホーム", self.show_main_screen), ("📈\nトレード", None),
                        ("⚡\nスピード", None), ("🌏\nマーケット", None),
                        ("📉\nチャート", self.show_chart_screen)]
        for text, cmd in footer_items:
            tk.Button(self.footer_frame, text=text, font=("Arial", 8), bg="#050a15", fg="#888", borderwidth=0, 
                      activebackground="#050a15", activeforeground="white", command=cmd).pack(side="left", fill="both", expand=True)

        self.stop_flag = False
        self.data_thread = threading.Thread(target=self.update_data_loop)
        self.data_thread.daemon = True
        self.data_thread.start()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def show_main_screen(self):
        if self.chart_content_frame: self.chart_content_frame.pack_forget()
        if self.main_content_frame: self.main_content_frame.pack(fill="both", expand=True, side="top")

    def show_chart_screen(self):
        if self.main_content_frame: self.main_content_frame.pack_forget()
        if self.chart_content_frame is None: self.create_chart_screen()
        self.chart_content_frame.pack(fill="both", expand=True, side="top")

    def create_chart_screen(self):
        self.chart_content_frame = tk.Frame(self, bg=COLOR_CHART_BG)
        h = tk.Frame(self.chart_content_frame, bg=COLOR_CHART_BG, height=40)
        h.pack(fill="x", side="top")
        tk.Button(h, text="＜ 戻る", font=self.font_main, bg=COLOR_CHART_BG, fg="white", borderwidth=0,
                  command=self.show_main_screen).pack(side="left", padx=10, pady=5)
        tk.Label(h, text="USD/JPY 1分足", font=self.font_bold, bg=COLOR_CHART_BG, fg="white").pack(side="left", padx=20)

        mc = mpf.make_marketcolors(up='r', down='g', edge='i', wick='i', volume='in', inherit=True)
        s  = mpf.make_mpf_style(marketcolors=mc, base_mpf_style='nightclouds', gridstyle=':')
        df = create_dummy_ohlc_data(periods=60)
        fig = mpf.figure(style=s, figsize=(8, 6), tight_layout=True)
        ax1 = fig.add_subplot(1,1,1)
        mpf.plot(df, type='candle', ax=ax1, volume=False, show_nontrading=False)
        canvas = FigureCanvasTkAgg(fig, master=self.chart_content_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_data_loop(self):
        while not self.stop_flag:
            try:
                fd = repRateModu01.fetch_get_FXrate()
                usd_data = fd.loc[fd['symbol'] == 'USD_JPY']
                if not usd_data.empty:
                    bid = float(usd_data.iloc[0]['bid'])
                    ask = float(usd_data.iloc[0]['ask'])
                    try:
                        self.var_rate_bid.set(f"{bid:.3f}")
                        self.var_rate_ask.set(f"{ask:.3f}")
                    except: pass
            except: pass
            time.sleep(UPDATE_INTERVAL)

    def on_close(self):
        self.stop_flag = True
        plt.close('all')
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass

    main_app = MainApp()
    
    # ログインウィンドウの設定
    login_window = tk.Toplevel(main_app)
    login_window.title("Login")
    login_window.configure(background="#0e1629")
    
    # 【追加】ログインウィンドウを中央に配置 
    center_window(login_window, 1000, 750)

    login_window.protocol("WM_DELETE_WINDOW", lambda: sys.exit())

    login_manager = Login(login_window, main_app)
    main_app.mainloop()