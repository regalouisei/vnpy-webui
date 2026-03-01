# Redux Store

import { configureStore } from '@reduxjs/toolkit';

// 初始状态
interface Account {
    id: string;
    accountid: string;
    balance: number;
    available: number;
    frozen: number;
    currency: string;
}

interface Position {
    symbol: string;
    direction: string;
    volume: number;
    open_price: number;
    last_price: number;
    unrealized_pnl: number;
    pnl_ratio: number;
    margin: number;
}

interface Order {
    orderid: string;
    symbol: string;
    direction: string;
    offset: string;
    volume: number;
    price: number;
    status: string;
}

interface Quote {
    symbol: string;
    last_price: number;
    change: number;
    change_value: number;
    volume: number;
    bid_price_1: number;
    ask_price_1: number;
}

interface Strategy {
    id: string;
    name: string;
    class_name: string;
    status: string;
    created_at: string;
    started_at: string;
    stopped_at: string;
}

interface Backtest {
    id: string;
    strategy_name: string;
    symbol: string;
    start_date: string;
    end_date: string;
    status: string;
    total_pnl: number;
    return_rate: number;
    max_drawdown: number;
    win_rate: number;
    sharpe_ratio: number;
}

interface Trade {
    tradeid: string;
    symbol: string;
    direction: string;
    offset: string;
    price: number;
    volume: number;
    commission: number;
    trade_time: string;
}

interface AppState {
    accounts: Account[];
    positions: Position[];
    orders: Order[];
    quotes: Quote[];
    strategies: Strategy[];
    backtests: Backtest[];
    trades: Trade[];
    selectedAccount: Account | null;
    selectedPosition: Position | null;
    selectedQuote: Quote | null;
    selectedStrategy: Strategy | null;
    selectedBacktest: Backtest | null;
    connected: boolean;
    loading: boolean;
    error: string | null;
}

const initialState: AppState = {
    accounts: [],
    positions: [],
    orders: [],
    quotes: [],
    strategies: [],
    backtests: [],
    trades: [],
    selectedAccount: null,
    selectedPosition: null,
    selectedQuote: null,
    selectedStrategy: null,
    selectedBacktest: null,
    connected: false,
    loading: false,
    error: null,
};

// ==================== Slice ====================

const appSlice = createSlice({
    name: 'app',
    initialState,
    reducers: {
        // ==================== 账户 ====================
        setAccounts: (state, action: { payload: Account[] }) => {
            state.accounts = payload;
        },

        updateAccount: (state, action: { payload: Account }) => {
            state.accounts = state.accounts.map(acc => 
                acc.id === payload.id ? payload : acc
            );
            if (state.selectedAccount?.id === payload.id) {
                state.selectedAccount = payload;
            }
        },

        setSelectedAccount: (state, action: { payload: Account | null }) => {
            state.selectedAccount = payload;
        },

        // ==================== 持仓 ====================
        setPositions: (state, action: { payload: Position[] }) => {
            state.positions = payload;
        },

        updatePosition: (state, action: { payload: Position }) => {
            state.positions = state.positions.map(pos => 
                pos.symbol === payload.symbol ? payload : pos
            );
            if (state.selectedPosition?.symbol === payload.symbol) {
                state.selectedPosition = payload;
            }
        },

        setSelectedPosition: (state, action: { payload: Position | null }) => {
            state.selectedPosition = payload;
        },

        // ==================== 订单 ====================
        setOrders: (state, action: { payload: Order[] }) => {
            state.orders = payload;
        },

        updateOrder: (state, action: { payload: Order }) => {
            state.orders = state.orders.map(order => 
                order.orderid === payload.orderid ? payload : order
            );
        },

        // ==================== 行情 ====================
        setQuotes: (state, action: { payload: Quote[] }) => {
            state.quotes = payload;
        },

        updateQuote: (state, action: { payload: Quote }) => {
            state.quotes = state.quotes.map(quote => 
                quote.symbol === payload.symbol ? payload : quote
            );
            if (state.selectedQuote?.symbol === payload.symbol) {
                state.selectedQuote = payload;
            }
        },

        setSelectedQuote: (state, action: { payload: Quote | null }) => {
            state.selectedQuote = payload;
        },

        // ==================== 策略 ====================
        setStrategies: (state, action: { payload: Strategy[] }) => {
            state.strategies = payload;
        },

        updateStrategy: (state, action: { payload: Strategy }) => {
            state.strategies = state.strategies.map(strategy => 
                strategy.id === payload.id ? payload : strategy
            );
            if (state.selectedStrategy?.id === payload.id) {
                state.selectedStrategy = payload;
            }
        },

        setSelectedStrategy: (state, action: { payload: Strategy | null }) => {
            state.selectedStrategy = payload;
        },

        // ==================== 回测 ====================
        setBacktests: (state, action: { payload: Backtest[] }) => {
            state.backtests = payload;
        },

        updateBacktest: (state, action: { payload: Backtest }) => {
            state.backtests = state.backtests.map(backtest => 
                backtest.id === payload.id ? payload : backtest
            );
            if (state.selectedBacktest?.id === payload.id) {
                state.selectedBacktest = payload;
            }
        },

        setSelectedBacktest: (state, action: { payload: Backtest | null }) => {
            state.selectedBacktest = payload;
        },

        // ==================== 成交 ====================
        setTrades: (state, action: { payload: Trade[] }) => {
            state.trades = payload;
        },

        // ==================== 系统状态 ====================
        setConnected: (state, action: { payload: boolean }) => {
            state.connected = payload;
        },

        setLoading: (state, action: { payload: boolean }) => {
            state.loading = payload;
        },

        setError: (state, action: { payload: string | null }) => {
            state.error = payload;
        },

        clearError: (state) => {
            state.error = null;
        },

        // ==================== 通用 ====================
        reset: (state) => {
            state.accounts = [];
            state.positions = [];
            state.orders = [];
            state.quotes = [];
            state.strategies = [];
            state.backtests = [];
            state.trades = [];
            state.selectedAccount = null;
            state.selectedPosition = null;
            state.selectedQuote = null;
            state.selectedStrategy = null;
            state.selectedBacktest = null;
            state.connected = false;
            state.loading = false;
            state.error = null;
        },
    },
});

// 导出 actions
export const {
    setAccounts,
    updateAccount,
    setSelectedAccount,
    setPositions,
    updatePosition,
    setSelectedPosition,
    setOrders,
    updateOrder,
    setQuotes,
    updateQuote,
    setSelectedQuote,
    setStrategies,
    updateStrategy,
    setSelectedStrategy,
    setBacktests,
    updateBacktest,
    setSelectedBacktest,
    setTrades,
    setConnected,
    setLoading,
    setError,
    clearError,
    reset,
} = appSlice.actions;

// 导出 selector
export const selectAccounts = (state: { app: AppState }) => state.app.accounts;
export const selectPositions = (state: { app: AppState }) => state.app.positions;
export const selectOrders = (state: { app: AppState }) => state.app.orders;
export const selectQuotes = (state: { app: AppState }) => state.app.quotes;
export const selectStrategies = (state: { app: AppState }) => state.app.strategies;
export const selectBacktests = (state: { app: AppState }) => state.app.backtests;
export const selectTrades = (state: { app: AppState }) => state.app.trades;
export const selectSelectedAccount = (state: { app: AppState }) => state.app.selectedAccount;
export const selectSelectedPosition = (state: { app: AppState }) => state.app.selectedPosition;
export const selectSelectedQuote = (state: { app: AppState }) => state.app.selectedQuote;
export const selectSelectedStrategy = (state: { app: AppState }) => state.app.selectedStrategy;
export const selectSelectedBacktest = (state: { app: AppState }) => state.app.selectedBacktest;
export const selectConnected = (state: { app: AppState }) => state.app.connected;
export const selectLoading = (state: { app: AppState }) => state.app.loading;
export const selectError = (state: { app: AppState }) => state.app.error;

// 导出 reducer
export default appSlice.reducer;

// 导出 store
export const store = configureStore({
    reducer: {
        app: appSlice.reducer,
    },
});

// 导出类型
export type { Account, Position, Order, Quote, Strategy, Backtest, Trade, AppState };
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
