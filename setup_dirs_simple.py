#!/usr/bin/env python3
import os

# 策略目录
strategies_dir = "/root/.openclaw/workspace/quant-factory/strategies"
os.makedirs(strategies_dir, exist_ok=True)

# Station 目录
station_dir = "/root/.openclaw/workspace/quant-factory/veighna_station"
os.makedirs(station_dir, exist_ok=True)

print("策略目录:", strategies_dir)
print("Station 目录:", station_dir)
