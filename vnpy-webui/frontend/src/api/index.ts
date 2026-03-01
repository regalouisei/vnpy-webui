# API 客户端

import axios, { AxiosResponse } from 'axios';

// 创建 axios 实例
const api = axios.create({
    baseURL: 'http://localhost:8000',
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// 请求拦截器
api.interceptors.request.use(
    (config) => {
        // 添加 token
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 响应拦截器
api.interceptors.response.use(
    (response: AxiosResponse) => {
        return response.data;
    },
    (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
    }
);

// 账户 API
export const accountApi = {
    // 获取所有账户
    getAccounts: async () => {
        return await api.get('/api/accounts');
    },

    // 获取账户详情
    getAccount: async (accountId: string) => {
        return await api.get(`/api/accounts/${accountId}`);
    },

    // 获取账户余额
    getAccountBalance: async (accountId: string) => {
        return await api.get(`/api/accounts/${accountId}/balance`);
    },

    // 刷新账户
    refreshAccount: async (accountId: string) => {
        return await api.post(`/api/accounts/${accountId}/refresh`);
    },
};

// 持仓 API
export const positionApi = {
    // 获取所有持仓
    getPositions: async () => {
        return await api.get('/api/positions');
    },

    // 获取持仓详情
    getPosition: async (symbol: string) => {
        return await api.get(`/api/positions/${symbol}`);
    },

    // 获取持仓盈亏
    getPositionPnl: async (symbol: string) => {
        return await api.get(`/api/positions/${symbol}/pnl`);
    },

    // 刷新持仓
    refreshPosition: async (symbol: string) => {
        return await api.post(`/api/positions/${symbol}/refresh`);
    },

    // 平仓
    closePosition: async (symbol: string, direction: string, volume: number, price?: number) => {
        return await api.post('/api/trade/orders', {
            symbol,
            direction,
            offset: 'close',
            volume,
            order_type: price ? 'limit' : 'market',
            price: price || 0,
        });
    },
};

// 合约 API
export const contractApi = {
    // 获取所有合约
    getContracts: async () => {
        return await api.get('/api/contracts');
    },

    // 获取合约详情
    getContract: async (symbol: string) => {
        return await api.get(`/api/contracts/${symbol}`);
    },

    // 获取合约 tick
    getContractTick: async (symbol: string) => {
        return await api.get(`/api/contracts/${symbol}/tick`);
    },

    // 订阅合约行情
    subscribeContract: async (symbol: string, exchange: string) => {
        return await api.post('/api/quotes/subscribe', {
            symbol,
            exchange,
        });
    },

    // 取消订阅
    unsubscribeContract: async (symbol: string) => {
        return await api.post('/api/quotes/unsubscribe', {
            symbol,
        });
    },
};

// 行情 API
export const quoteApi = {
    // 获取所有行情
    getQuotes: async () => {
        return await api.get('/api/quotes');
    },

    // 获取指定合约行情
    getQuote: async (symbol: string) => {
        return await api.get(`/api/quotes/${symbol}`);
    },

    // 订阅行情
    subscribeQuote: async (symbol: string, exchange: string) => {
        return await api.post('/api/quotes/subscribe', {
            symbol,
            exchange,
        });
    },

    // 取消订阅
    unsubscribeQuote: async (symbol: string) => {
        return await api.post('/api/quotes/unsubscribe', {
            symbol,
        });
    },
};

// 策略 API
export const strategyApi = {
    // 获取所有策略
    getStrategies: async () => {
        return await api.get('/api/strategies');
    },

    // 获取策略详情
    getStrategy: async (strategyId: string) => {
        return await api.get(`/api/strategies/${strategyId}`);
    },

    // 创建策略
    createStrategy: async (strategyData: {
        name: string;
        class_name: string;
        parameters: any;
    }) => {
        return await api.post('/api/strategies', strategyData);
    },

    // 删除策略
    deleteStrategy: async (strategyId: string) => {
        return await api.delete(`/api/strategies/${strategyId}`);
    },

    // 启动策略
    startStrategy: async (strategyId: string) => {
        return await api.post(`/api/strategies/${strategyId}/start`);
    },

    // 停止策略
    stopStrategy: async (strategyId: string) => {
        return await api.post(`/api/strategies/${strategyId}/stop`);
    },

    // 获取策略日志
    getStrategyLog: async (strategyId: string) => {
        return await api.get(`/api/strategies/${strategyId}/log`);
    },
};

// 回测 API
export const backtestApi = {
    // 获取所有回测
    getBacktests: async () => {
        return await api.get('/api/backtest');
    },

    // 获取回测详情
    getBacktest: async (backtestId: string) => {
        return await api.get(`/api/backtest/${backtestId}`);
    },

    // 运行回测
    runBacktest: async (backtestData: {
        strategy_name: string;
        symbol: string;
        start_date: string;
        end_date: string;
        parameters: any;
    }) => {
        return await api.post('/api/backtest/run', backtestData);
    },

    // 停止回测
    stopBacktest: async (backtestId: string) => {
        return await api.post(`/api/backtest/${backtestId}/stop`);
    },

    // 获取回测结果
    getBacktestResults: async (backtestId: string) => {
        return await api.get(`/api/backtest/${backtestId}/results`);
    },

    // 获取回测图表
    getBacktestChart: async (backtestId: string) => {
        return await api.get(`/api/backtest/${backtestId}/chart`);
    },
};

// 交易 API
export const tradeApi = {
    // 获取所有订单
    getOrders: async () => {
        return await api.get('/api/trade/orders');
    },

    // 获取订单详情
    getOrder: async (orderId: string) => {
        return await api.get(`/api/trade/orders/${orderId}`);
    },

    // 下单
    createOrder: async (orderData: {
        symbol: string;
        direction: string;
        offset: string;
        volume: number;
        price?: number;
        order_type?: string;
    }) => {
        return await api.post('/api/trade/orders', orderData);
    },

    // 撤单
    cancelOrder: async (orderId: string) => {
        return await api.delete(`/api/trade/orders/${orderId}`);
    },

    // 获取所有成交
    getTrades: async () => {
        return await api.get('/api/trade/trades');
    },

    // 获取成交详情
    getTrade: async (tradeId: string) => {
        return await api.get(`/api/trade/trades/${tradeId}`);
    },
};

// 数据 API
export const dataApi = {
    // 获取 K 线数据
    getBars: async (params: {
        symbol: string;
        exchange: string;
        interval?: string;
        start?: string;
        end?: string;
    }) => {
        return await api.get('/api/data/bars', { params });
    },

    // 获取 Tick 数据
    getTicks: async (params: {
        symbol: string;
        exchange: string;
        start?: string;
        end?: string;
    }) => {
        return await api.get('/api/data/ticks', { params });
    },

    // 导入数据
    importData: async (file: File, params: {
        symbol: string;
        exchange: string;
        interval?: string;
    }) => {
        const formData = new FormData();
        formData.append('file', file);
        if (params.symbol) formData.append('symbol', params.symbol);
        if (params.exchange) formData.append('exchange', params.exchange);
        if (params.interval) formData.append('interval', params.interval);

        return await api.post('/api/data/import', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    },

    // 导出数据
    exportData: async (exportData: {
        symbol: string;
        exchange: string;
        interval?: string;
        format: string;
        start?: string;
        end?: string;
    }) => {
        return await api.post('/api/data/export', exportData, {
            responseType: 'blob',
        });
    },

    // 清理数据
    cleanData: async (params: {
        symbol?: string;
        exchange?: string;
        interval?: string;
        all?: boolean;
    }) => {
        return await api.delete('/api/data/clean', { data: params });
    },
};

// 报表 API
export const reportApi = {
    // 获取性能报告
    getPerformanceReport: async () => {
        return await api.get('/api/reports/performance');
    },

    // 获取风险报告
    getRiskReport: async () => {
        return await api.get('/api/reports/risk');
    },

    // 获取月度报告
    getMonthlyReport: async (year: number, month: number) => {
        return await api.get(`/api/reports/monthly/${year}/${month}`);
    },

    // 获取回撤报告
    getDrawdownReport: async () => {
        return await api.get('/api/reports/drawdown');
    },

    // 获取资产配置报告
    getAllocationReport: async () => {
        return await api.get('/api/reports/allocation');
    },
};

// 导出所有 API
export const apiService = {
    account: accountApi,
    position: positionApi,
    contract: contractApi,
    quote: quoteApi,
    strategy: strategyApi,
    backtest: backtestApi,
    trade: tradeApi,
    data: dataApi,
    report: reportApi,
};

// 导出默认
export default apiService;
