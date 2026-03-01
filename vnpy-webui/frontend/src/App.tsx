# React 主应用（更新版 - 添加所有路由）

import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Layout, ConfigProvider, theme } from 'antd';
import { UserOutlined, DashboardOutlined, LineChartOutlined, BarChartOutlined, SettingOutlined, DollarOutlined, DatabaseOutlined } from '@ant-design/icons';
import zhCN from 'antd/locale/zh_CN';
import 'antd/dist/reset.css';

// 导入页面组件
import Account from './pages/Account';
import Position from './pages/Position';
import Quote from './pages/Quote';
import Strategy from './pages/Strategy';
import Backtest from './pages/Backtest';
import Trade from './pages/Trade';
import Data from './pages/Data';
import Report from './pages/Report';

import './App.css';

const { Content, Sider, Header } = Layout;
const { Title } = Typography;

// 菜单项
const menuItems = [
    {
        key: '/',
        icon: <DashboardOutlined />,
        label: <Link to="/">控制台</Link>,
    },
    {
        key: '/accounts',
        icon: <UserOutlined />,
        label: <Link to="/accounts">账户管理</Link>,
    },
    {
        key: '/positions',
        icon: <DollarOutlined />,
        label: <Link to="/positions">持仓管理</Link>,
    },
    {
        key: '/quotes',
        icon: <LineChartOutlined />,
        label: <Link to="/quotes">行情显示</Link>,
    },
    {
        key: '/strategies',
        icon: <BarChartOutlined />,
        label: <Link to="/strategies">策略管理</Link>,
    },
    {
        key: '/backtest',
        icon: <SettingOutlined />,
        label: <Link to="/backtest">回测功能</Link>,
    },
    {
        key: '/trade',
        icon: <DollarOutlined />,
        label: <Link to="/trade">交易</Link>,
    },
    {
        key: '/data',
        icon: <DatabaseOutlined />,
        label: <Link to="/data">数据管理</Link>,
    },
    {
        key: '/reports',
        icon: <BarChartOutlined />,
        label: <Link to="/reports">报表分析</Link>,
    },
];

const App: React.FC = () => {
    const [collapsed, setCollapsed] = useState(false);
    const [loading, setLoading] = useState(true);
    const [backendStatus, setBackendStatus] = useState('unknown');
    const location = useLocation();

    // 检查后端连接
    useEffect(() => {
        const checkBackend = async () => {
            try {
                const response = await fetch('http://localhost:8000/health', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                const data = await response.json();
                if (data.status === 'ok') {
                    setLoading(false);
                    setBackendStatus('connected');
                }
            } catch (error) {
                console.error('后端连接失败:', error);
                setLoading(false);
                setBackendStatus('disconnected');
            }
        };

        checkBackend();
        
        // 每 30 秒检查一次后端连接
        const interval = setInterval(checkBackend, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <ConfigProvider
            locale={zhCN}
            theme={{
                algorithm: theme.defaultAlgorithm,
                token: {
                    colorBgContainer: '#ffffff',
                    colorBgLayout: '#ffffff',
                    colorPrimary: '#1890ff',
                },
            }}
        >
            <BrowserRouter>
                <Layout style={{ minHeight: '100vh' }}>
                    <Layout.Sider
                        collapsible
                        collapsed={collapsed}
                        onCollapse={(value) => setCollapsed(value)}
                        theme={{
                            token: {
                                colorBgContainer: colorBgContainer,
                            },
                        }}
                        width={250}
                        style={{
                            overflow: 'auto',
                            height: '100vh',
                            position: 'fixed',
                            left: 0,
                            top: 0,
                            bottom: 0,
                            transition: 'all 0.2s',
                        }}
                    >
                        <div style={{ 
                            height: 64, 
                            background: '#001529', 
                            display: 'flex', 
                            alignItems: 'center', 
                            color: 'white', 
                            fontSize: 18, 
                            fontWeight: 'bold',
                            justifyContent: 'center',
                        }}>
                            <span style={{ fontSize: 20, marginRight: 8 }}>VnPy</span>
                            <span style={{ fontSize: 14 }}>Web UI</span>
                        </div>
                        <div style={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            justifyContent: 'center',
                            padding: '8px',
                            marginBottom: '8px',
                        }}>
                            <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px',
                            }}>
                                <div style={{
                                    width: 10,
                                    height: 10,
                                    borderRadius: '50%',
                                    backgroundColor: backendStatus === 'connected' ? '#52c41a' : '#f5222d',
                                }} />
                                <span style={{ 
                                    fontSize: 12, 
                                    color: backendStatus === 'connected' ? '#52c41a' : '#f5222d',
                                    fontWeight: 'bold',
                                }}>
                                    {backendStatus === 'connected' ? '在线' : '离线'}
                                </span>
                            </div>
                        </div>
                    </Layout.Sider>

                    <Layout style={{ marginLeft: collapsed ? 80 : 250, transition: 'all 0.2s' }}>
                        <Header style={{ 
                            background: '#001529', 
                            padding: 0, 
                            position: 'sticky', 
                            top: 0, 
                            zIndex: 1, 
                            height: 64,
                            display: 'flex',
                            alignItems: 'center',
                        }}>
                            <div style={{ 
                                color: 'white', 
                                fontSize: 20, 
                                fontWeight: 'bold', 
                                padding: '0 24px',
                                flex: 1,
                            }}>
                                VnPy Web UI
                            </div>
                        </Header>

                        <Content style={{ margin: '24px', overflow: 'auto', minHeight: 'calc(100vh - 64px)' }}>
                            {loading ? (
                                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', minHeight: '500px' }}>
                                    <div style={{ textAlign: 'center' }}>
                                        <div style={{ fontSize: 48, marginBottom: 16 }}>🔄</div>
                                        <div style={{ fontSize: 24, color: '#666', marginBottom: 8 }}>正在连接后端...</div>
                                        <div style={{ fontSize: 14, color: '#999' }}>首次连接可能需要几秒钟</div>
                                        <div style={{ fontSize: 14, color: '#999' }}>请稍候...</div>
                                    </div>
                                </div>
                            ) : (
                                <Routes>
                                    <Route path="/" element={<div>
                                        <h2>欢迎使用 VnPy Web UI</h2>
                                        <div style={{ marginTop: 24 }}>
                                            <p style={{ fontSize: 16, lineHeight: '1.8', marginBottom: 16 }}>
                                                这是一个功能完整的量化交易平台 Web 界面，支持以下功能：
                                            </p>
                                            <ul style={{ lineHeight: '2' }}>
                                                <li>📊 账户管理</li>
                                                <li>📈 持仓管理</li>
                                                <li>📉 行情显示（实时 K 线）</li>
                                                <li>🤖 策略管理（支持 CTA 策略）</li>
                                                <li>📊 回测功能（参数优化、性能报告）</li>
                                                <li>💰 交易功能（下单、撤单、成交查询）</li>
                                                <li>📊 数据管理（导入、导出、查询）</li>
                                                <li>📊 报表分析（收益分析、风险报告、月度报告）</li>
                                            </ul>
                                            <div style={{ marginTop: 32, padding: 24, background: '#f0f2f5', borderRadius: 8 }}>
                                                <h3 style={{ marginBottom: 16, color: '#1890ff', fontSize: 18 }}>
                                                    🚀 开始使用
                                                </h3>
                                                <p style={{ marginBottom: 16 }}>
                                                    请从左侧菜单选择您想要使用的功能：
                                                </p>
                                                <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                                                    <a href="/accounts" style={{
                                                        padding: '12px 24px',
                                                        background: '#fff',
                                                        borderRadius: 6,
                                                        color: '#1890ff',
                                                        border: '1px solid #1890ff',
                                                        textDecoration: 'none',
                                                        fontWeight: 'bold',
                                                    }}>
                                                        查看账户
                                                    </a>
                                                    <a href="/positions" style={{
                                                        padding: '12px 24px',
                                                        background: '#fff',
                                                        borderRadius: 6,
                                                        color: '#1890ff',
                                                        border: '1px solid #1890ff',
                                                        textDecoration: 'none',
                                                        fontWeight: 'bold',
                                                    }}>
                                                        查看持仓
                                                    </a>
                                                    <a href="/quotes" style={{
                                                        padding: '12px 24px',
                                                        background: '#fff',
                                                        borderRadius: 6,
                                                        color: '#1890ff',
                                                        border: '1px solid #1890ff',
                                                        textDecoration: 'none',
                                                        fontWeight: 'bold',
                                                    }}>
                                                        查看行情
                                                    </a>
                                                </div>
                                            </div>
                                        </div>
                                    </div>} />
                                    <Route path="/accounts" element={<Account />} />
                                    <Route path="/positions" element={<Position />} />
                                    <Route path="/quotes" element={<Quote />} />
                                    <Route path="/strategies" element={<Strategy />} />
                                    <Route path="/backtest" element={<Backtest />} />
                                    <Route path="/trade" element={<Trade />} />
                                    <Route path="/data" element={<Data />} />
                                    <Route path="/reports" element={<Report />} />
                                </Routes>
                            )}
                        </Content>
                    </Layout>
                </Layout>
            </BrowserRouter>
        </ConfigProvider>
    );
};

export default App;
