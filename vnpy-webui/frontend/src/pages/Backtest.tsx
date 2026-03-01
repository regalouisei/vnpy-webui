# 回测功能页面

import React, { useState, useEffect } from 'react';
import { Card, Form, Input, InputNumber, Button, Space, message, Statistic, Row, Col, Select, DatePicker, Slider, Tabs, Alert, Tag } from 'antd';
import { PlayCircleOutlined, PauseCircleOutlined, BarChartOutlined, DownloadOutlined, HistoryOutlined, SettingOutlined } from '@ant-design/icons';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const { RangePicker } = DatePicker;

const Backtest: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [backtests, setBacktests] = useState([]);
  const [selectedBacktest, setSelectedBacktest] = useState<any>(null);
  const [results, setResults] = useState<any>(null);
  const [equityCurve, setEquityCurve] = useState([]);

  // 运行回测
  const runBacktest = async (values: any) => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/backtest/run', {
        strategy_name: values.strategy_name,
        symbol: values.symbol,
        start_date: values.start_date.format('YYYY-MM-DD'),
        end_date: values.end_date.format('YYYY-MM-DD'),
        parameters: JSON.parse(values.parameters),
      });
      
      message.success('回测开始运行');
      fetchBacktests();
    } catch (error) {
      message.error('回测运行失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // 停止回测
  const stopBacktest = async (backtestId: string) => {
    try {
      const response = await axios.post(`http://localhost:8000/api/backtest/${backtestId}/stop`);
      message.success(response.data.message);
      fetchBacktests();
    } catch (error) {
      message.error('回测停止失败');
      console.error(error);
    }
  };

  // 获取回测结果
  const fetchBacktestResults = async (backtestId: string) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/backtest/results/${backtestId}`);
      setResults(response.data.results);
      setEquityCurve(response.data.results?.equity_curve || []);
    } catch (error) {
      message.error('获取回测结果失败');
      console.error(error);
    }
  };

  // 获取回测图表
  const fetchBacktestChart = async (backtestId: string) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/backtest/${backtestId}/chart`);
      setEquityCurve(response.data.chart?.equity || []);
    } catch (error) {
      message.error('获取回测图表失败');
      console.error(error);
    }
  };

  // 查看回测日志
  const viewBacktestLog = async (backtestId: string) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/backtest/results/${backtestId}`);
      message.info({
        title: '回测日志',
        content: (
          <div style={{ maxHeight: 400, overflow: 'auto', whiteSpace: 'pre-wrap' }}>
            {JSON.stringify(response.data.results, null, 2)}
          </div>
        ),
      });
    } catch (error) {
      message.error('查看日志失败');
      console.error(error);
    }
  };

  // 获取所有回测
  const fetchBacktests = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/api/backtest');
      setBacktests(response.data.backtests || []);
    } catch (error) {
      message.error('获取回测列表失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBacktests();
  }, []);

  return (
    <div style={{ padding: 24 }}>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
                title="总回测数"
                value={backtests.length}
                suffix="次"
                prefix={<HistoryOutlined />}
                valueStyle={{ fontWeight: 'bold' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
                title="运行中"
                value={backtests.filter(b => b.status === 'running').length}
                suffix="个"
                prefix={<PlayCircleOutlined />}
                valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
                title="已完成"
                value={backtests.filter(b => b.status === 'completed').length}
                suffix="次"
                prefix={<BarChartOutlined />}
                valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
                title="失败"
                value={backtests.filter(b => b.status === 'failed').length}
                suffix="次"
                prefix={<Alert type="error" style={{ margin: 0 }} />}
                valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Card title="回测参数" style={{ marginBottom: 16 }}>
            <Form form={form} layout="inline" onFinish={runBacktest}>
              <Form.Item
                name="strategy_name"
                label="策略名称"
                rules={[{ required: true, message: '请输入策略名称' }]}
              >
                <Select placeholder="请选择策略" style={{ width: 200 }}>
                  <Select.Option value="DoubleMaStrategy">双均线策略</Select.Option>
                  <Select.Option value="TripleMaStrategy">三均线策略</Select.Option>
                  <Select.Option value="BollChannelStrategy">布林通道策略</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="symbol"
                label="合约代码"
                rules={[{ required: true, message: '请输入合约代码' }]}
              >
                <Input placeholder="例如: IC2602" style={{ width: 150 }} />
              </Form.Item>

              <Form.Item
                name="start_date"
                label="起始日期"
                rules={[{ required: true, message: '请选择起始日期' }]}
              >
                <DatePicker style={{ width: 200 }} />
              </Form.Item>

              <Form.Item
                name="end_date"
                label="结束日期"
                rules={[{ required: true, message: '请选择结束日期' }]}
              >
                <DatePicker style={{ width: 200 }} />
              </Form.Item>

              <Form.Item
                name="parameters"
                label="策略参数"
                rules={[{ required: true, message: '请输入策略参数' }]}
              >
                <Input.TextArea
                  placeholder='{"fast_period": 5, "slow_period": 30}'
                  autoSize={{ minRows: 2, maxRows: 6 }}
                  style={{ width: 400, fontFamily: 'monospace' }}
                />
              </Form.Item>

              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading} icon={<PlayCircleOutlined />}>
                  运行回测
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Card title="回测列表" style={{ marginBottom: 16 }} extra={
            <Space>
              <Button type="primary" icon={<DownloadOutlined />}>
                导出报告
              </Button>
              <Button icon={<BarChartOutlined />} onClick={() => fetchBacktests()}>
                刷新
              </Button>
            </Space>
          }>
            <Table
              columns={[
                { title: '回测ID', dataIndex: 'id', key: 'id', width: 200 },
                { title: '策略名称', dataIndex: 'strategy_name', key: 'strategy_name', width: 150 },
                { title: '合约', dataIndex: 'symbol', key: 'symbol', width: 100 },
                { title: '起始日期', dataIndex: 'start_date', key: 'start_date', width: 120 },
                { title: '结束日期', dataIndex: 'end_date', key: 'end_date', width: 120 },
                { title: '状态', dataIndex: 'status', key: 'status', width: 100, render: (status: string) => {
                  if (status === 'running') {
                    return <Tag color="green">运行中</Tag>;
                  } else if (status === 'completed') {
                    return <Tag color="blue">已完成</Tag>;
                  } else if (status === 'failed') {
                    return <Tag color="red">失败</Tag>;
                  } else {
                    return <Tag color="default">{status}</Tag>;
                  }
                }},
                { title: '总收益', dataIndex: 'total_pnl', key: 'total_pnl', width: 100 },
                { title: '收益率', dataIndex: 'return_rate', key: 'return_rate', width: 100 },
                {
                  title: '操作',
                  key: 'action',
                  width: 250,
                  render: (_: any, record: any) => (
                    <Space size="small">
                      <Button type="link" size="small" onClick={() => stopBacktest(record.id)} disabled={record.status !== 'running'}>
                        <PauseCircleOutlined /> 停止
                      </Button>
                      <Button type="link" size="small" onClick={() => fetchBacktestResults(record.id)}>
                        <BarChartOutlined /> 结果
                      </Button>
                      <Button type="link" size="small" onClick={() => viewBacktestLog(record.id)}>
                        <SettingOutlined /> 日志
                      </Button>
                    </Space>
                  ),
                },
              ]}
              dataSource={backtests}
              rowKey="id"
              loading={loading}
              pagination={{
                pageSize: 10,
                showTotal: true,
                showSizeChanger: true,
              }}
              onRow={(record) => {
                setSelectedBacktest(record);
                fetchBacktestResults(record.id);
              }}
            />
          </Card>
        </Col>
      </Row>

      {results && (
        <Row gutter={16}>
          <Col span={12}>
            <Card title={`回测结果: ${results.backtest_id}`} style={{ marginBottom: 16 }}>
              <Row gutter={16} style={{ marginBottom: 16 }}>
                <Col span={6}>
                  <Card>
                    <Statistic
                          title="总收益率"
                          value={(results.return_rate || 0).toFixed(2)}
                          suffix="%"
                          precision={2}
                          prefix={results.return_rate >= 0 ? '+' : ''}
                          valueStyle={{ color: results.return_rate >= 0 ? '#52c41a' : '#f5222d' }}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                          title="夏普比率"
                          value={(results.sharpe_ratio || 0).toFixed(2)}
                          precision={2}
                          valueStyle={{ color: '#1890ff' }}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                          title="最大回撤"
                          value={(results.max_drawdown || 0).toFixed(2)}
                          suffix="%"
                          precision={2}
                          valueStyle={{ color: '#f5222d' }}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                          title="胜率"
                          value={(results.win_rate || 0).toFixed(2)}
                          suffix="%"
                          precision={2}
                          valueStyle={{ color: '#3f8600' }}
                    />
                  </Card>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={12}>
                  <Card title="收益曲线">
                    <ResponsiveContainer width="100%" height={400}>
                      <LineChart data={equityCurve}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="time" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="equity" stroke="#3f8600" dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </Card>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={12}>
                  <Card title="交易统计" style={{ marginTop: 16 }}>
                    <Alert
                      message="详细交易统计"
                      description={`总成交: ${results.total_trades || 0} 笔, 盈利交易: ${results.profitable_trades || 0} 笔, 亏损交易: ${results.loss_trades || 0} 笔`}
                      type="info"
                    />
                  </Card>
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>
      )}

      <Button
        type="primary"
        style={{ position: 'fixed', bottom: 24, right: 24 }}
        onClick={() => setSelectedBacktest(null)}
      >
        关闭
      </Button>
    </div>
  );
};

export default Backtest;
