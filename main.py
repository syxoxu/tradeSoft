import tkinter as tk
from tkinter import ttk
import threading
import time
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import csv
import math

# --- グラフ描画用 ---
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplfinance as mpf

# ---------------------------------------------------------
# 設定・定数・配色 (GMOクリック証券風ダークテーマ)
# ---------------------------------------------------------
CSV_FILE = "login.csv"
UPDATE_INTERVAL = 1000  # 更新間隔 (ms) = 1秒

# 配色定義
COLOR_BG_LOGIN = "#0e1629"     # ログイン画面背景
COLOR_PANEL_LOGIN = "#1c2640"  # ログインパネル背景
COLOR_BTN_LOGIN = "#f3c648"    # ログインボタン
COLOR_BTN_DEMO = "#58aebf"     # デモボタン
COLOR_BTN_ACC = "#222222"      # 口座開設ボタン

COLOR_BG_MAIN = "#0e1629"      # メイン背景
COLOR_HEADER = "#050a15"       # ヘッダー/フッター
COLOR_PANEL_BG = "#1c2640"     # パネル背景
COLOR_PANEL_WHITE = "#ffffff"  # 情報パネル
COLOR_TEXT_MAIN = "#ffffff"
COLOR_ACCENT_RED = "#e74c3c"   # Ask/上昇
COLOR_ACCENT_BLUE = "#3498db"  # Bid/下落
COLOR_ACCENT_GOLD = "#f39c12"
COLOR_BTN_MENU = "#24345e"

# フォント設定
FONT_L = ("Meiryo UI", 16, "bold")
FONT_M = ("Meiryo UI", 12)
FONT_S = ("Meiryo UI", 10)
FONT_NUM_L = ("Arial", 28, "bold")
FONT_NUM_M = ("Arial", 18, "bold")
FONT_NUM_S = ("Arial", 14, "bold")

# ---------------------------------------------------------
# 共通関数
# ---------------------------------------------------------
def center_window(window, width, height):
    """ウィンドウを画面中央に配置"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

# ---------------------------------------------------------
# データ管理クラス
# ---------------------------------------------------------
class DataManager:
    @staticmethod
    def fetch_real_data():
        """外部モジュールまたはダミーからデータを取得"""
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
        # FXダミー
        fx_data = []
        for pair in ['USD_JPY', 'EUR_JPY', 'GBP_JPY', 'TRY_JPY']:
            base = 150.0 if 'USD' in pair else 160.0
            bid = base + random.uniform(-0.1, 0.1)
            fx_data.append({
                'symbol': pair, 'bid': bid, 'ask': bid + 0.003, 
                'high': bid + 0.5, 'low': bid - 0.5
            })
        
        # Cryptoダミー
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
# 各画面（タブ）のクラス
# ---------------------------------------------------------

class HomeView(tk.Frame):
    """【ホーム】 資産状況とメニュー"""
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
    """【トレード】 リアルタイムレート一覧 (軽量化済み)"""
    def __init__(self, master):
        super().__init__(master, bg=COLOR_BG_MAIN)
        self.rate_labels = {} 
        self.prev_values = {} # チラつき防止用の前回値保存
        self.create_layout()

    def create_layout(self):
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        # --- レート表 ---
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
            
            # ラベル生成・配置
            self.rate_labels[f"{pair}_bid"] = tk.Label(left_panel, text="-", font=FONT_NUM_S, bg=COLOR_BG_MAIN, fg=COLOR_ACCENT_BLUE)
            self.rate_labels[f"{pair}_bid"].grid(row=i, column=1, sticky="e", padx=5)

            self.rate_labels[f"{pair}_ask"] = tk.Label(left_panel, text="-", font=FONT_NUM_S, bg=COLOR_BG_MAIN, fg=COLOR_ACCENT_RED)
            self.rate_labels[f"{pair}_ask"].grid(row=i, column=2, sticky="e", padx=5)

            self.rate_labels[f"{pair}_high"] = tk.Label(left_panel, text="-", font=FONT_S, bg=COLOR_BG_MAIN, fg="white")
            self.rate_labels[f"{pair}_high"].grid(row=i, column=3, sticky="e", padx=5)

            self.rate_labels[f"{pair}_low"] = tk.Label(left_panel, text="-", font=FONT_S, bg=COLOR_BG_MAIN, fg="white")
            self.rate_labels[f"{pair}_low"].grid(row=i, column=4, sticky="e", padx=5)
            
            ttk.Separator(left_panel, orient="horizontal").grid(row=i*10+5, column=0, columnspan=5, sticky="ew", pady=0)

        # --- 建玉一覧 ---
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
        """データ更新処理"""
        try:
            # 1. FX
            for sym in ["USD_JPY", "EUR_JPY", "GBP_JPY", "TRY_JPY"]:
                row = fx_df.loc[fx_df['symbol'] == sym]
                if not row.empty:
                    self._update_row(sym.replace("_", "/"), row.iloc[0], is_crypto=False)

            # 2. Crypto
            for sym in ["BTC_JPY", "ETH_JPY", "XRP_JPY", "DOGE_JPY"]:
                row = crypto_df.loc[crypto_df['symbol'] == sym]
                if not row.empty:
                    self._update_row(sym.replace("_", "/"), row.iloc[0], is_crypto=True)

            # 3. BTC/USD 計算
            usd = fx_df.loc[fx_df['symbol'] == 'USD_JPY']
            btc = crypto_df.loc[crypto_df['symbol'] == 'BTC_JPY']
            
            if not usd.empty and not btc.empty:
                u_ask = float(usd.iloc[0]['ask'])
                u_bid = float(usd.iloc[0]['bid'])
                b_bid = float(btc.iloc[0]['bid'])
                b_ask = float(btc.iloc[0]['ask'])
                
                # クロスレート
                calc_bid = b_bid / u_ask
                calc_ask = b_ask / u_bid
                data = {'bid': calc_bid, 'ask': calc_ask, 'high': 0, 'low': 0}
                self._update_row("BTC/USD", pd.Series(data), is_crypto=False)

        except Exception:
            pass

    def _update_row(self, pair, data, is_crypto):
        """値が変わった場合のみラベルを更新する（チラつき防止）"""
        fmt = "{:,.0f}" if is_crypto and "BTC" in pair else "{:,.3f}"
        if pair == "BTC/USD": fmt = "{:,.2f}"

        vals = {
            'bid': fmt.format(float(data['bid'])),
            'ask': fmt.format(float(data['ask'])),
            'high': fmt.format(float(data.get('high', 0))),
            'low': fmt.format(float(data.get('low', 0)))
        }

        if f"{pair}_bid" in self.rate_labels:
            self._set_text(f"{pair}_bid", vals['bid'])
            self._set_text(f"{pair}_ask", vals['ask'])
            if float(data.get('high', 0)) > 0: self._set_text(f"{pair}_high", vals['high'])
            if float(data.get('low', 0)) > 0: self._set_text(f"{pair}_low", vals['low'])

    def _set_text(self, key, text):
        """前回と同じ値なら更新しない"""
        if self.prev_values.get(key) != text:
            self.rate_labels[key].config(text=text)
            self.prev_values[key] = text


class SpeedOrderView(tk.Frame):
    """【スピード注文】"""
    def __init__(self, master):
        super().__init__(master, bg=COLOR_BG_MAIN)
        self.create_layout()

    def create_layout(self):
        container = tk.Frame(self, bg=COLOR_BG_MAIN)
        container.pack(expand=True)
        tk.Label(container, text="🇺🇸🇯🇵 USD/JPY", font=("Arial", 24, "bold"), fg="white", bg=COLOR_BG_MAIN).pack(pady=10)

        rate_frame = tk.Frame(container, bg=COLOR_BG_MAIN)
        rate_frame.pack(pady=20)

        tk.Button(rate_frame, text="BID (売)\n155.497", font=("Arial", 20, "bold"),
                  bg=COLOR_ACCENT_BLUE, fg="white", width=15, height=3, relief="flat").pack(side="left", padx=10)
        tk.Label(rate_frame, text="0.2", font=("Arial", 14), fg="white", bg="#333", width=4).pack(side="left")
        tk.Button(rate_frame, text="ASK (買)\n155.499", font=("Arial", 20, "bold"),
                  bg=COLOR_ACCENT_RED, fg="white", width=15, height=3, relief="flat").pack(side="left", padx=10)

        ctrl_frame = tk.Frame(container, bg=COLOR_PANEL_BG, padx=20, pady=20)
        ctrl_frame.pack(fill="x", pady=20)
        tk.Label(ctrl_frame, text="取引数量 (×10,000)", font=FONT_M, fg="white", bg=COLOR_PANEL_BG).pack()
        tk.Spinbox(ctrl_frame, from_=1, to=100, font=("Arial", 20), width=10, justify="center").pack(pady=10)
        tk.Button(ctrl_frame, text="全決済", bg="#555", fg="white", font=FONT_M, width=20).pack(pady=10)


class MarketView(tk.Frame):
    """【マーケット】"""
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
    """【チャート】 軽量化・リサイズ対応済み"""
    def __init__(self, master):
        super().__init__(master, bg=COLOR_BG_MAIN)
        self.chart_frame = None
        self.resize_timer = None
        self.create_layout()

    def create_layout(self):
        ctrl_bar = tk.Frame(self, bg=COLOR_HEADER, height=40)
        ctrl_bar.pack(fill="x", side="top")
        tk.Label(ctrl_bar, text="USD/JPY 1分足", font=FONT_M, fg="white", bg=COLOR_HEADER).pack(side="left", padx=20)
        
        self.chart_frame = tk.Frame(self, bg="black")
        self.chart_frame.pack(fill="both", expand=True)
        
        self.draw_chart()
        self.chart_frame.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        """リサイズ時の負荷軽減（デバウンス処理）"""
        if self.resize_timer:
            self.after_cancel(self.resize_timer)
        self.resize_timer = self.after(500, self.draw_chart)

    def draw_chart(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        df = DataManager.get_ohlc(100)
        mc = mpf.make_marketcolors(up=COLOR_ACCENT_RED, down=COLOR_ACCENT_BLUE, 
                                   edge='inherit', wick='inherit', volume='in')
        s = mpf.make_mpf_style(marketcolors=mc, base_mpf_style='nightclouds', gridstyle=':')
        fig, axes = mpf.plot(df, type='candle', style=s, volume=False, returnfig=True, figsize=(10, 6))
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


# ---------------------------------------------------------
# メインアプリ
# ---------------------------------------------------------
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title("GMO Click FX Style - PC Version")
        self.configure(bg=COLOR_BG_MAIN)
        center_window(self, 1280, 800)

        # 1. フッター
        self.create_footer()
        
        # 2. コンテナ (リサイズ追従設定を追加)
        self.container = tk.Frame(self, bg=COLOR_BG_MAIN)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)    # 【重要】
        self.container.grid_columnconfigure(0, weight=1) # 【重要】

        # 各画面
        self.frames = {}
        for F in (HomeView, TradeView, SpeedOrderView, MarketView, ChartView):
            page_name = F.__name__
            frame = F(master=self.container)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.running = False
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def start(self, username):
        """ログイン後に呼び出されるメソッド"""
        self.deiconify()
        self.show_frame("TradeView")
        
        # ユーザー名表示などが必要ならここで行う
        self.title(f"Trading View - {username}")

        # データ更新ループ開始
        self.running = True
        self.update_data()

    def create_footer(self):
        footer = tk.Frame(self, bg=COLOR_HEADER, height=60)
        footer.pack(side="bottom", fill="x")
        tabs = [("🏠 ホーム", "HomeView"), ("📈 トレード", "TradeView"),
                ("⚡ スピード", "SpeedOrderView"), ("🌏 マーケット", "MarketView"), ("📉 チャート", "ChartView")]
        for text, view_name in tabs:
            btn = tk.Button(footer, text=text, font=("Meiryo UI", 11, "bold"),
                            bg=COLOR_HEADER, fg="#aaa", bd=0, activebackground="#222", activeforeground="white",
                            command=lambda name=view_name: self.show_frame(name))
            btn.pack(side="left", fill="both", expand=True)

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def update_data(self):
        """データ更新ループ (スレッド + after)"""
        if not self.running: return
        threading.Thread(target=self._fetch_and_update, daemon=True).start()
        self.after(UPDATE_INTERVAL, self.update_data)

    def _fetch_and_update(self):
        fd, fg = DataManager.fetch_real_data()
        if not fd.empty and not fg.empty:
            self.after(0, lambda: self.frames["TradeView"].update_table(fd, fg))

    def on_close(self):
        self.running = False
        plt.close('all')
        self.destroy()
        sys.exit()

# ---------------------------------------------------------
# ログイン画面
# ---------------------------------------------------------
class Login:
    def __init__(self, master, main):
        self.master = master
        self.main = main
        self.widgets = []
        self.create_widgets()

    def create_widgets(self):
        self.master.configure(bg=COLOR_BG_LOGIN)
        
        # ロゴ
        logo_frame = tk.Frame(self.master, bg=COLOR_BG_LOGIN, pady=30)
        logo_frame.pack(fill="x")
        logo_inner = tk.Frame(logo_frame, bg=COLOR_BG_LOGIN)
        logo_inner.pack()
        tk.Label(logo_inner, text="GMOクリック", font=("Arial", 20, "bold"), fg="white", bg=COLOR_BG_LOGIN).pack(side="left")
        tk.Label(logo_inner, text=" FX ", font=("Arial", 18, "bold", "italic"), fg="white", bg="#dba11c").pack(side="left", padx=5)

        # 入力フォーム
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
        self.master.after(500, lambda: [self.main.start(username), self.master.destroy()])

# ---------------------------------------------------------
# 起動処理
# ---------------------------------------------------------
if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass

    app = MainApp()
    
    # 1. ログイン用のウィンドウ枠を先に作る
    login_window = tk.Toplevel(app)
    login_window.title("Login")
    login_window.configure(bg=COLOR_BG_MAIN)
    center_window(login_window, 1000, 750) # ログイン画面は縦長
    login_window.protocol("WM_DELETE_WINDOW", sys.exit)

    # 2. 「ウィンドウ枠」と「アプリ本体」の2つを渡す
    login = Login(login_window, app)

    app.mainloop()