# 行情显示页面

import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Space, message, Row, Col, Input, Select, Tag, Spin } from 'antd';
import { LineChartOutlined, SyncOutlined } from '@ant-design/icons';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Quote: React.FC = () => {
  const [quotes, setQuotes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedSymbols, setSelectedSymbols] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [refreshInterval, setRefreshInterval] = useState(1000);

  // 获取行情数据
  const fetchQuotes = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/api/quotes');
      setQuotes(response.data.quotes || []);
      updateChartData(response.data.quotes || []);
    } catch (error) {
      message.error('获取行情数据失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // 订阅行情
  const subscribeQuote = async (symbol: string, exchange: string) => {
    try {
      const response = await axios.post('http://localhost:8000/api/quotes/subscribe', {
        symbol,
        exchange
      });
      message.success(response.data.message);
      fetchQuotes();
    } catch (error) {
      message.error('订阅行情失败');
      console.error(error);
    }
  };

  // 取消订阅
  const unsubscribeQuote = async (symbol: string) => {
    try {
      const response = await axios.post('http://localhost:8000/api/quotes/unsubscribe', {
        symbol
      });
      message.success(response.data.message);
      fetchQuotes();
    } catch (error) {
      message.error('取消订阅失败');
      console.error(error);
    }
  };

  // 更新图表数据
  const updateChartData = (quotesData: any[]) => {
    // TODO: 实现 K 线数据生成
    setChartData([]);
  };

  // 自动刷新
  useEffect(() => {
    const interval = setInterval(() => {
      fetchQuotes();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [refreshInterval]);

  useEffect(() => {
    fetchQuotes();
  }, []);

  const columns = [
    {
      title: '合约代码',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 120,
    },
    {
      title: '最新价',
      dataIndex: 'last_price',
      key: 'last_price',
      width: 100,
      render: (price: number) => price ? price.toFixed(2) : '-',
    },
    {
      title: '涨跌幅',
      dataIndex: 'change',
      key: 'change',
      width: 80,
      render: (change: number) => (
        <span style={{ color: change >= 0 ? '#52c41a' : '#f5222d', fontWeight: 'bold' }}>
          {change >= 0 ? '+' : ''}{change?.toFixed(2)}%
        </span>
      ),
    },
    {
      title: '涨跌额',
      dataIndex: 'change_value',
      key: 'change_value',
      width: 100,
      render: (value: number) => (
        <span style={{ color: value >= 0 ? '#52c41a' : '#f5222d', fontWeight: 'bold' }}>
          {value >= 0 ? '+' : ''}{value?.toFixed(2)}
        </span>
      ),
    },
    {
      title: '成交量',
      dataIndex: 'volume',
      key: 'volume',
      width: 120,
      render: (volume: number) => volume ? volume.toLocaleString() : '-',
    },
    {
      title: '买一价',
      dataIndex: 'bid_price_1',
      key: 'bid_price_1',
      width: 100,
      render: (price: number) => price ? price.toFixed(2) : '-',
    },
    {
      title: '卖一价',
      dataIndex: 'ask_price_1',
      key: 'ask_price_1',
      width: 100,
      render: (price: number) => price ? price.toFixed(2) : '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: string) => {
        if (status === 'active') {
          return <Tag color="green">交易中</Tag>;
        } else if (status === 'suspended') {
          return <Tag color="orange">暂停</Tag>;
        } else {
          return <Tag color="gray">休市</Tag>;
        }
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: any) => (
        <Space size="small">
          <Button type="primary" size="small" onClick={() => subscribeQuote(record.symbol, record.exchange)}>
            订阅
          </Button>
          <Button size="small" onClick={() => unsubscribeQuote(record.symbol)}>
            取消
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card
            title="行情订阅"
            extra={
              <Space>
                <Input
                  placeholder="输入合约代码"
                  style={{ width: 150 }}
                  onSearch={(value) => {
                    if (value) {
                      const quote = quotes.find(q => q.symbol === value);
                      if (quote) {
                        subscribeQuote(quote.symbol, quote.exchange);
                      }
                    }
                  }
                  }}
                  allowClear
                  enterButton
                />
                <Select
                  defaultValue="all"
                  style={{ width: 150 }}
                  onChange={(value) => {
                    if (value === 'all') {
                      setSelectedSymbols([]);
                    } else if (value === 'long') {
                      setSelectedSymbols(['IC2602', 'IF2602']);
                    } else if (value === 'short') {
                      setSelectedSymbols(['IC2602']);
                    }
                  }}
                  options={[
                    { value: 'all', label: '全部' },
                    { value: 'long', label: '多头' },
                    { value: 'short', label: '空头' },
                  ]}
                />
                <Select
                  defaultValue="1s"
                  style={{ width: 120 }}
                  onChange={(value) => {
                    if (value === '1s') {
                      setRefreshInterval(1000);
                    } else if (value === '3s') {
                      setRefreshInterval(3000);
                    } else if (value === '5s') {
                      setRefreshInterval(5000);
                    }
                  }}
                  options={[
                    { value: '1s', label: '1秒' },
                    { value: '3s', label: '3秒' },
                    { value: '5s', label: '5秒' },
                    { value: 'stop', label: '停止' },
                  ]}
                />
                <Button type="primary" icon={<SyncOutlined />} onClick={fetchQuotes} loading={loading}>
                  刷新
                </Button>
              </Space>
            }
          >
            <Table
              columns={columns}
              dataSource={quotes}
              rowKey="symbol"
              loading={loading}
              pagination={{
                pageSize: 10,
                showTotal: true,
                showSizeChanger: true,
              }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={24}>
          <Card
            title="K 线图"
            style={{ height: 400 }}
          >
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" domain={['time']} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="price" stroke="#8884d8" dot={false} />
              </LineChart>
            </ResponsiveContainer>
            {chartData.length === 0 && (
              <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: 300,
                color: '#999'
              }}>
                <LineChartOutlined style={{ fontSize: 48, marginBottom: 16 }} />
                <div style={{ fontSize: 16 }}>暂无数据</div>
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Quote;
