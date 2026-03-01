# 自定义 Hooks

import { useDispatch, useSelector } from 'react-redux';
import { useEffect, useCallback, useRef } from 'react';
import {
    fetchAccounts as fetchAccountsApi,
    fetchPositions as fetchPositionsApi,
    fetchQuotes as fetchQuotesApi,
    fetchStrategies as fetchStrategiesApi,
    fetchBacktests as fetchBacktestsApi,
} from '../api';
import {
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
    setLoading,
    setError,
} from '../store';
import {
    onTick,
    onQuote,
    onOrder,
    onTrade,
    onPosition,
    onAccount,
    connect as connectSocket,
    disconnect as disconnectSocket,
    subscribeQuote,
    unsubscribeQuote,
} from '../socket';
import { RootState, AppDispatch } from '../store';

// ==================== 账户 Hooks ====================

export const useAccounts = () => {
    const dispatch = useDispatch<AppDispatch>();
    const accounts = useSelector((state: RootState) => state.app.accounts);
    const selectedAccount = useSelector((state: RootState) => state.app.selectedAccount);
    const loading = useSelector((state: RootState) => state.app.loading;

    const fetchAccounts = useCallback(async () => {
        try {
            dispatch(setLoading(true));
            const response = await fetchAccountsApi();
            dispatch(setAccounts(response.accounts || []));
        } catch (error: any) {
            dispatch(setError(`获取账户失败: ${error.message}`));
        } finally {
            dispatch(setLoading(false));
        }
    }, [dispatch]);

    const refreshAccount = useCallback(async (accountId: string) => {
        try {
            dispatch(setLoading(true));
            const response = await fetchAccountsApi();
            dispatch(updateAccount(response.account));
            dispatch(setError(null));
        } catch (error: any) {
            dispatch(setError(`刷新账户失败: ${error.message}`));
        } finally {
            dispatch(setLoading(false));
        }
    }, [dispatch]);

    useEffect(() => {
        fetchAccounts();
    }, [fetchAccounts]);

    // WebSocket: 监听账户更新
    useEffect(() => {
        const handleAccount = (data: any) => {
            dispatch(updateAccount(data));
        };

        onAccount(handleAccount);
        return () => {
            // 移除监听器
        };
    }, [dispatch]);

    return { accounts, selectedAccount, loading, fetchAccounts, refreshAccount };
};

export const useSelectAccount = () => {
    const dispatch = useDispatch<AppDispatch>();

    const selectAccount = useCallback((account: any) => {
        dispatch(setSelectedAccount(account));
    }, [dispatch]);

    return { selectAccount };
};

// ==================== 持仓 Hooks ====================

export const usePositions = () => {
    const dispatch = useDispatch<AppDispatch>();
    const positions = useSelector((state: RootState) => state.app.positions);
    const selectedPosition = useSelector((state: RootState) => state.app.selectedPosition;
    const loading = useSelector((state: RootState) => state.app.loading;

    const fetchPositions = useCallback(async () => {
        try {
            dispatch(setLoading(true));
            const response = await fetchPositionsApi();
            dispatch(setPositions(response.positions || []));
        } catch (error: any) {
            dispatch(setError(`获取持仓失败: ${error.message}`));
        } finally {
            dispatch(setLoading(false));
        }
    }, [dispatch]);

    const refreshPosition = useCallback(async (symbol: string) => {
        try {
            dispatch(setLoading(true));
            const response = await fetchPositionsApi();
            const position = response.positions.find((pos: any) => pos.symbol === symbol);
            if (position) {
                dispatch(updatePosition(position));
            }
            dispatch(setError(null));
        } catch (error: any) {
            dispatch(setError(`刷新持仓失败: ${error.message}`));
        } finally {
            dispatch(setLoading(false));
        }
    }, [dispatch]);

    useEffect(() => {
        fetchPositions();
    }, [fetchPositions]);

    // WebSocket: 监听持仓更新
    useEffect(() => {
        const handlePosition = (data: any) => {
            dispatch(updatePosition(data));
        };

        const handlePositions = (data: any[]) => {
            dispatch(setPositions(data));
        };

        onPosition(handlePosition);
        onPositions(handlePositions);
        return () => {
            // 移除监听器
        };
    }, [dispatch]);

    return { positions, selectedPosition, loading, fetchPositions, refreshPosition };
};

export const useSelectPosition = () => {
    const dispatch = useDispatch<AppDispatch>();

    const selectPosition = useCallback((position: any) => {
        dispatch(setSelectedPosition(position));
    }, [dispatch]);

    return { selectPosition };
};

// ==================== 行情 Hooks ====================

export const useQuotes = () => {
    const dispatch = useDispatch<AppDispatch>();
    const quotes = useSelector((state: RootState) => state.app.quotes;
    const selectedQuote = useSelector((state: RootState) => state.app.selectedQuote;
    const loading = useSelector((state: RootState) => state.app.loading;

    const fetchQuotes = useCallback(async () => {
        try {
            dispatch(setLoading(true));
            const response = await fetchQuotesApi();
            dispatch(setQuotes(response.quotes || []));
        } catch (error: any) {
            dispatch(setError(`获取行情失败: ${error.message}`));
        } finally {
            dispatch(setLoading(false));
        }
    }, [dispatch]);

    const subscribe = useCallback(async (symbol: string, exchange: string) => {
        try {
            await subscribeQuote(symbol, exchange);
        } catch (error: any) {
            dispatch(setError(`订阅行情失败: ${error.message}`));
        }
    }, [dispatch]);

    const unsubscribe = useCallback(async (symbol: string) => {
        try {
            await unsubscribeQuote(symbol);
        } catch (error: any) {
            dispatch(setError(`取消订阅失败: ${error.message}`));
        }
    }, [dispatch]);

    useEffect(() => {
        fetchQuotes();
    }, [fetchQuotes]);

    // WebSocket: 监听行情更新
    useEffect(() => {
        const handleTick = (data: any) => {
            dispatch(updateQuote(data));
        };

        const handleQuote = (data: any) => {
            dispatch(updateQuote(data));
        };

        const handleQuotes = (data: any[]) => {
            // 批量更新
            data.forEach(quote => {
                dispatch(updateQuote(quote));
            });
        };

        onTick(handleTick);
        onQuote(handleQuote);
        onQuotes(handleQuotes);

        // 定时刷新（每 5 秒）
        const interval = setInterval(() => {
            fetchQuotes();
        }, 5000);

        return () => {
            // 移除监听器和定时器
            clearInterval(interval);
        };
    }, [dispatch, fetchQuotes]);

    return { quotes, selectedQuote, loading, fetchQuotes, subscribe, unsubscribe };
};

export const useSelectQuote = () => {
    const dispatch = useDispatch<AppDispatch>();

    const selectQuote = useCallback((quote: any) => {
        dispatch(setSelectedQuote(quote));
    }, [dispatch]);

    return { selectQuote };
};

// ==================== 策略 Hooks ====================

export const useStrategies = () => {
    const dispatch = useDispatch<AppDispatch>();
    const strategies = useSelector((state: RootState) => state.app.strategies;
    const selectedStrategy = useSelector((state: RootState) => state.app.selectedStrategy;
    const loading = useSelector((state: RootState) => state.app.loading;

    const fetchStrategies = useCallback(async () => {
        try {
            dispatch(setLoading(true));
            const response = await fetchStrategiesApi();
            dispatch(setStrategies(response.strategies || []));
        } catch (error: any) {
            dispatch(setError(`获取策略失败: ${error.message}`));
        } finally {
            dispatch(setLoading(false));
        }
    }, [dispatch]);

    const startStrategy = useCallback(async (strategyId: string) => {
        try {
            dispatch(setLoading(true));
            const response = await fetchStrategiesApi();
            const strategy = response.strategies.find((s: any) => s.id === strategyId);
            if (strategy) {
                strategy.status = 'running';
                dispatch(updateStrategy(strategy));
            }
            dispatch(setError(null));
        } catch (error: any) {
            dispatch(setError(`启动策略失败: ${error.message}`));
        } finally {
            dispatch(setLoading(false));
        }
    }, [dispatch]);

    const stopStrategy = useCallback(async (strategyId: string) => {
        try {
            dispatch(setLoading(true));
            const response = await fetchStrategiesApi();
            const strategy = response.strategies.find((s: any) => s.id === strategyId);
            if (strategy) {
                strategy.status = 'stopped';
                dispatch(updateStrategy(strategy));
            }
            dispatch(setError(null));
        } catch (error: any) {
            dispatch(setError(`停止策略失败: ${error.message}`));
        } finally {
            dispatch(setLoading(false));
        }
    }, [dispatch]);

    useEffect(() => {
        fetchStrategies();
    }, [fetchStrategies]);

    // WebSocket: 监听策略更新
    useEffect(() => {
        const handleStrategyStart = (data: any) => {
            dispatch(updateStrategy(data));
        };

        const handleStrategyStop = (data: any) => {
            dispatch(updateStrategy(data));
        };

        const handleStrategyLog = (data: string) => {
            console.log('策略日志:', data);
        };

        const handleStrategyError = (data: string) => {
            dispatch(setError(data));
        };

        onStrategyStart(handleStrategyStart);
        onStrategyStop(handleStrategyStop);
        onStrategyLog(handleStrategyLog);
        onStrategyError(handleStrategyError);

        return () => {
            // 移除监听器
        };
    }, [dispatch]);

    return { strategies, selectedStrategy, loading, fetchStrategies, startStrategy, stopStrategy };
};

export const useSelectStrategy = () => {
    const dispatch = useDispatch<AppDispatch>();

    const selectStrategy = useCallback((strategy: any) => {
        dispatch(setSelectedStrategy(strategy));
    }, [dispatch]);

    return { selectStrategy };
};

// ==================== 回测 Hooks ====================

export const useBacktests = () => {
    const dispatch = useDispatch<AppDispatch>();
    const backtests = useSelector((state: RootState) => state.app.backtests;
    const selectedBacktest = useSelector((state: RootState) => state.app.selectedBacktest;
    const loading = useSelector((state: RootState) => state.app.loading;

    const fetchBacktests = useCallback(async () => {
        try {
            dispatch(setLoading(true));
            const response = await fetchBacktestsApi();
            dispatch(setBacktests(response.backtests || []));
        } catch (error: any) {
            dispatch(setError(`获取回测失败: ${error.message}`));
        } finally {
            dispatch(setLoading(false));
        }
    }, [dispatch]);

    useEffect(() => {
        fetchBacktests();
    }, [fetchBacktests]);

    return { backtests, selectedBacktest, loading, fetchBacktests };
};

export const useSelectBacktest = () => {
    const dispatch = useDispatch<AppDispatch>();

    const selectBacktest = useCallback((backtest: any) => {
        dispatch(setSelectedBacktest(backtest));
    }, [dispatch]);

    return { selectBacktest };
};

// ==================== 交易 Hooks ====================

export const useOrders = () => {
    const dispatch = useDispatch<AppDispatch>();
    const orders = useSelector((state: RootState) => state.app.orders;
    const loading = useSelector((state: RootState) => state.app.loading;

    const fetchOrders = useCallback(async () => {
        try {
            dispatch(setLoading(true));
            const response = await fetchStrategiesApi();
            dispatch(setOrders(response.orders || []));
        } catch (error: any) {
            dispatch(setError(`获取订单失败: ${error.message}`));
        } finally {
            dispatch(setLoading(false));
        }
    }, [dispatch]);

    useEffect(() => {
        fetchOrders();
    }, [fetchOrders]);

    // WebSocket: 监听订单更新
    useEffect(() => {
        const handleOrder = (data: any) => {
            dispatch(updateOrder(data));
        };

        const handleOrders = (data: any[]) => {
            dispatch(setOrders(data));
        };

        onOrder(handleOrder);
        onOrders(handleOrders);

        return () => {
            // 移除监听器
        };
    }, [dispatch]);

    return { orders, loading, fetchOrders };
};

export const useTrades = () => {
    const dispatch = useDispatch<AppDispatch>();
    const trades = useSelector((state: RootState) => state.app.trades;

    // WebSocket: 监听成交更新
    useEffect(() => {
        const handleTrade = (data: any) => {
            console.log('新成交:', data);
        };

        const handleTrades = (data: any[]) => {
            dispatch(setTrades(data));
        };

        onTrade(handleTrade);
        onTrades(handleTrades);

        return () => {
            // 移除监听器
        };
    }, [dispatch]);

    return { trades };
};

// ==================== WebSocket Hooks ====================

export const useWebSocket = () => {
    const dispatch = useDispatch<AppDispatch>();
    const connected = useSelector((state: RootState) => state.app.connected;
    const error = useSelector((state: RootState) => state.app.error;

    const connect = useCallback(() => {
        try {
            dispatch(setLoading(true));
            connectSocket();
            
            // 监听连接事件
            onConnect(() => {
                dispatch(setConnected(true));
                dispatch(setError(null));
            });

            onDisconnect(() => {
                dispatch(setConnected(false));
                dispatch(setError('WebSocket 已断开'));
            });

            onConnectError((error: any) => {
                dispatch(setConnected(false));
                dispatch(setError(`WebSocket 连接失败: ${error}`));
            });
            
            onError((error: any) => {
                dispatch(setError(`WebSocket 错误: ${error}`));
            });
        } catch (error: any) {
            dispatch(setError(`连接失败: ${error.message}`));
        } finally {
            dispatch(setLoading(false));
        }
    }, [dispatch]);

    const disconnect = useCallback(() => {
        disconnectSocket();
        dispatch(setConnected(false));
    }, [dispatch]);

    return { connected, error, connect, disconnect };
};

// ==================== 通知 Hooks ====================

export const useNotification = () => {
    const [notification, setNotification] = useState({
        type: 'info' as 'info' | 'success' | 'warning' | 'error',
        message: '',
        duration: 3000,
        visible: false,
    });

    const showNotification = useCallback((
        type: 'info' | 'success' | 'warning' | 'error',
        message: string,
        duration = 3000
    ) => {
        setNotification({
            type,
            message,
            duration,
            visible: true,
        });

        setTimeout(() => {
            setNotification(prev => ({ ...prev, visible: false }));
        }, duration);
    }, []);

    return { notification, showNotification };
};

// ==================== 媒体查询 Hooks ====================

export const useBreakpoint = () => {
    const [isSmall, setIsSmall] = useState(window.innerWidth < 768);

    useEffect(() => {
        const handleResize = () => {
            setIsSmall(window.innerWidth < 768);
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    return { isSmall };
};

export const useLocalStorage = (key: string, initialValue: any) => {
    const [storedValue, setStoredValue] = useState(() => {
        try {
            const item = window.localStorage.getItem(key);
            return item ? JSON.parse(item) : initialValue;
        } catch (error) {
            return initialValue;
        }
    });

    const setValue = (value: any) => {
        try {
            setStoredValue(value);
            window.localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Error setting localStorage key', key, error);
        }
    };

    return [storedValue, setValue];
};

export const useInterval = (callback: () => void, delay: number | null) => {
    const savedCallback = useRef(callback);
    const savedDelay = useRef(delay);

    useEffect(() => {
        savedCallback.current = callback;
        savedDelay.current = delay;
    }, [callback, delay]);

    useEffect(() => {
        if (savedDelay.current !== null) {
            const id = setInterval(() => {
                savedCallback.current();
            }, savedDelay.current);
            return () => clearInterval(id);
        }
    }, [savedDelay, savedCallback.current]);
};
