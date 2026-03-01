#!/bin/bash

# 启动脚本
# 使用方法:
# ./start.sh

echo "🚀 启动 VnPy Web UI..."

# 激活虚拟环境
echo "📍 激活虚拟环境..."
eval "$(conda shell.bash hook)"
conda activate vnpy-webui

# 启动后端服务器
echo "📍 启动后端服务器..."
cd backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "后端 PID: $BACKEND_PID"

# 启动前端服务器
echo "📍 启动前端服务器..."
cd ../frontend
nohup npm start > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端 PID: $FRONTEND_PID"

# 保存 PID
echo $BACKEND_PID > /tmp/backend.pid
echo $FRONTEND_PID > /tmp/frontend.pid

echo "✅ 所有服务器已启动！"
echo ""
echo "后端地址: http://localhost:8000"
echo "前端地址: http://localhost:3000"
echo ""
echo "后端日志: /tmp/backend.log"
echo "前端日志: /tmp/frontend.log"
echo ""
echo "停止服务器: ./stop.sh"
