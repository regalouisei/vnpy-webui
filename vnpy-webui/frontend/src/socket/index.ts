# WebSocket 客户端

import { io, Socket } from 'socket.io-client';

// 创建 socket 实例
const socket = io('http://localhost:8000', {
    transports: ['websocket'],
    upgrade: false,
});

// WebSocket 连接
export const connect = () => {
    socket.connect();
    console.log('WebSocket 已连接');
};

// 断开连接
export const disconnect = () => {
    socket.disconnect();
    console.log('WebSocket 已断开');
};

// 检查连接状态
export const isConnected = (): boolean => {
    return socket.connected;
};

// 事件监听器
type EventCallback = (data: any) => void;

interface EventListeners {
    [eventName: string]: Set<EventCallback>;
}

// 存储事件监听器
const eventListeners: EventListeners = {};

// 添加事件监听器
export const addEventListener = (eventName: string, callback: EventCallback) => {
    if (!eventListeners[eventName]) {
        eventListeners[eventName] = new Set();
        socket.on(eventName, callback);
    }
    eventListeners[eventName].add(callback);
};

// 移除事件监听器
export const removeEventListener = (eventName: string, callback: EventCallback) => {
    if (eventListeners[eventName]) {
        eventListeners[eventName].delete(callback);
        if (eventListeners[eventName].size === 0) {
            socket.off(eventName);
        }
    }
};

// 清理所有监听器
export const removeAllListeners = () => {
    Object.keys(eventListeners).forEach(eventName => {
        socket.off(eventName);
    });
    Object.keys(eventListeners).forEach(key => {
        delete eventListeners[key];
    });
};

// ==================== 行情事件 ====================

// 监听 tick 数据
export const onTick = (callback: (tick: any) => void) => {
    addEventListener('tick', callback);
};

// 监听行情推送
export const onQuote = (callback: (quote: any) => void) => {
    addEventListener('quote', callback);
};

// 监听 tick 数据流
export const onTickStream = (callback: (data: any) => void) => {
    addEventListener('tick_stream', callback);
};

// ==================== 订单事件 ====================

// 监听订单更新
export const onOrder = (callback: (order: any) => void) => {
    addEventListener('order', callback);
};

// 监听订单成交
export const onOrderTraded = (callback: (data: any) => void) => {
    addEventListener('order_traded', callback);
};

// 监听订单拒绝
export const onOrderRejected = (callback: (data: any) => void) => {
    addEventListener('order_rejected', callback);
};

// 监听订单取消
export const onOrderCancelled = (callback: (data: any) => void) => {
    addEventListener('order_cancelled', callback);
};

// 监听所有订单更新
export const onOrders = (callback: (orders: any[]) => void) => {
    addEventListener('orders', callback);
};

// ==================== 成交事件 ====================

// 监听新成交
export const onTrade = (callback: (trade: any) => void) => {
    addEventListener('trade', callback);
};

// 监听成交更新
export const onTradeUpdate = (callback: (trade: any) => void) => {
    addEventListener('trade_update', callback);
};

// 监听所有成交
export const onTrades = (callback: (trades: any[]) => void) => {
    addEventListener('trades', callback);
};

// ==================== 持仓事件 ====================

// 监听持仓更新
export const onPosition = (callback: (position: any) => void) => {
    addEventListener('position', callback);
};

// 监听持仓盈亏变化
export const onPositionPnl = (callback: (data: any) => void) => {
    addEventListener('position_pnl', callback);
};

// 监听所有持仓
export const onPositions = (callback: (positions: any[]) => void) => {
    addEventListener('positions', callback);
};

// ==================== 账户事件 ====================

// 监听账户更新
export const onAccount = (callback: (account: any) => void) => {
    addEventListener('account', callback);
};

// 监听余额变化
export const onBalance = (callback: (balance: any) => void) => {
    addEventListener('balance', callback);
};

// 监听可用资金变化
export const onAvailable = (callback: (available: any) => void) => {
    addEventListener('available', callback);
};

// ==================== 策略事件 ====================

// 监听策略启动
export const onStrategyStart = (callback: (data: any) => void) => {
    addEventListener('strategy_start', callback);
};

// 监听策略停止
export const onStrategyStop = (callback: (data: any) => void) => {
    addEventListener('strategy_stop', callback);
};

// 监听策略日志
export const onStrategyLog = (callback: (log: string) => void) => {
    addEventListener('strategy_log', callback);
};

// 监听策略错误
export const onStrategyError = (callback: (error: string) => void) => {
    addEventListener('strategy_error', callback);
};

// ==================== 系统事件 ====================

// 监听连接状态
export const onConnect = (callback: () => void) => {
    socket.on('connect', callback);
};

// 监听断开连接
export const onDisconnect = (callback: () => void) => {
    socket.on('disconnect', callback);
};

// 监听连接错误
export const onConnectError = (callback: (error: any) => void) => {
    socket.on('connect_error', callback);
};

// 监听服务器错误
export const onError = (callback: (error: any) => void) => {
    socket.on('error', callback);
};

// ==================== 通用方法 ====================

// 发送订阅行情请求
export const subscribeQuote = (symbol: string, exchange: string) => {
    socket.emit('subscribe_quote', { symbol, exchange });
};

// 发送取消订阅请求
export const unsubscribeQuote = (symbol: string) => {
    socket.emit('unsubscribe_quote', { symbol });
};

// 发送心跳
export const sendHeartbeat = () => {
    socket.emit('heartbeat', { timestamp: Date.now() });
};

// 导出 socket 实例
export { socket as default };
