import MetaTrader5 as mt5
import sys

def run_diagnostic():
    # 1. INITIALIZE CONNECTION
    if not mt5.initialize():
        print(f"MT5 Initialization failed. Error code: {mt5.last_error()}")
        sys.exit()

    symbol = "EURUSD"
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select {symbol}. Error code: {mt5.last_error()}")
        mt5.shutdown()
        sys.exit()

    # 2. PULL ACCOUNT ENVIRONMENT
    account_info = mt5.account_info()
    if account_info is None:
        print(f"Failed to get account info. Error code: {mt5.last_error()}")
        mt5.shutdown()
        sys.exit()

    print("\n" + "="*40)
    print("      MT5 ENVIRONMENT DIAGNOSTIC")
    print("="*40)
    print("--- 1. ACCOUNT SPECS ---")
    print(f"Balance:       {account_info.balance} {account_info.currency}")
    print(f"Leverage:      1:{account_info.leverage}")
    print(f"Free Margin:   {account_info.margin_free}")
    print(f"Margin Mode:   {account_info.margin_mode}")

    # 3. PULL SYMBOL ENVIRONMENT (The likely culprit)
    sym_info = mt5.symbol_info(symbol)
    if sym_info is None:
        print(f"Failed to get symbol info for {symbol}.")
        mt5.shutdown()
        sys.exit()

    print("\n--- 2. SYMBOL SPECS (EURUSD) ---")
    print(f"Contract Size: {sym_info.trade_contract_size}")
    print(f"Digits:        {sym_info.digits}")
    print(f"Point:         {sym_info.point}")
    print(f"Tick Size:     {sym_info.trade_tick_size}")
    print(f"Tick Value:    {sym_info.trade_tick_value} (Critical Variable)")
    print(f"Max Volume:    {sym_info.volume_max} (If 50, this is the cap being hit)")
    print(f"Volume Step:   {sym_info.volume_step}")
    print(f"Stops Level:   {sym_info.trade_stops_level}")

    # 4. SIMULATE THE EXACT TRADE MATH
    print("\n--- 3. MATH SIMULATION ---")
    # Using the exact numbers from your log: Balance ~179450, SL distance ~472 points
    risk_percent = 0.5
    risk_money = account_info.balance * (risk_percent / 100.0)
    
    # Simulating Entry 1.08714 to SL 1.08242 (Distance of 0.00472)
    sl_price_dist = 0.00472 
    
    print(f"Target Risk:   ${risk_money:.2f} (0.5%)")
    print(f"SL Distance:   {sl_price_dist} in price")

    # The equation
    if sym_info.trade_tick_size == 0 or sym_info.trade_tick_value == 0:
        print("\nERROR IDENTIFIED: Tick Size or Tick Value is returning 0 from the broker.")
        print("This causes a division-by-zero, throwing the lot size to infinity (capped at 50).")
    else:
        ticks = sl_price_dist / sym_info.trade_tick_size
        value_per_lot = ticks * sym_info.trade_tick_value
        calculated_lots = risk_money / value_per_lot if value_per_lot > 0 else 0
        
        print(f"Ticks in SL:   {ticks}")
        print(f"Cost per Lot:  ${value_per_lot:.2f}")
        print(f"Raw Lot Size:  {calculated_lots}")

    mt5.shutdown()

if __name__ == '__main__':
    run_diagnostic()