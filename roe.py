try:
    import yfinance as yf
except ModuleNotFoundError as exc:  # pragma: no cover - import guard
    yf = None
    _YFINANCE_IMPORT_ERROR = exc
else:
    _YFINANCE_IMPORT_ERROR = None

try:
    import pandas as pd
except ModuleNotFoundError as exc:  # pragma: no cover - import guard
    pd = None
    _PANDAS_IMPORT_ERROR = exc
else:
    _PANDAS_IMPORT_ERROR = None


def get_equity_net_income_roe(ticker_symbol: str):
    if yf is None:
        raise ModuleNotFoundError(
            "yfinance is not installed. Install it with: ./.venv/bin/pip install yfinance"
        ) from _YFINANCE_IMPORT_ERROR
    if pd is None:
        raise ModuleNotFoundError(
            "pandas is not installed. Install it with: ./.venv/bin/pip install pandas"
        ) from _PANDAS_IMPORT_ERROR

    ticker = yf.Ticker(ticker_symbol)

    # 財務諸表の取得（年次）
    income_stmt = ticker.financials      # 損益計算書 (P/L)
    balance_sheet = ticker.balance_sheet  # 貸借対照表 (B/S)

    if income_stmt.empty or balance_sheet.empty:
        print(f"[{ticker_symbol}] データの取得に失敗しました。")
        return

    # 日付（決算期）を揃える
    common_dates = income_stmt.columns.intersection(balance_sheet.columns)

    records = []

    # 時価総額 (Market Cap) を取得
    market_cap = ticker.info.get('marketCap')

    for date in common_dates:
        year_str = date.strftime('%Y-%m')

        # 純利益 (Net Income)
        net_income = income_stmt.loc['Net Income Common Stockholders', date]

        # 純資産 (Stockholders Equity)
        equity = balance_sheet.loc['Stockholders Equity', date]

        if equity and net_income:
            # ROEの計算
            roe = net_income / equity

            # PBRの計算
            pbr = None
            if market_cap is not None and equity > 0:
                pbr = market_cap / equity

            # 1/PER (利回り) の計算 (ROE / PBR)
            inverse_per = None
            if roe is not None and pbr is not None and pbr > 0:
                inverse_per = roe / pbr # 1/PER = ROE / PBR

            records.append({
                "決算年月": year_str,
                "純資産 (B$) ": round(equity / 1e9, 2),
                "純利益 (B$) ": round(net_income / 1e9, 2),
                "ROE (%)": f"{roe * 100:.2f}%",
                "PBR (倍)": round(pbr, 2) if pbr is not None else "N/A",
                "1/PER (%)": f"{inverse_per * 100:.2f}%" if inverse_per is not None else "N/A"
            })

    df = pd.DataFrame(records)
    print(f"\n==================== {ticker_symbol} の財務データ ====================")
    print(df.to_string(index=False))


def main():
    # ここに表示したい銘柄のティッカーシンボルをリストで指定します。
    # 米国株はティッカーシンボルのみ、日本株はティッカーシンボルに'.T'を付けます。
    ticker_list = [
        "NVDA",       # NVIDIA
        "3087.T",     # ドトール・日レスホールディングス
        "7203.T"      # トヨタ自動車
        # 他にも追加したい銘柄があればここに追加してください
    ]

    for ticker_symbol in ticker_list:
        get_equity_net_income_roe(ticker_symbol)


if __name__ == "__main__":
    main()
