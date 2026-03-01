# 交易页面

import React, { useState, useEffect } from 'react';
import { Card, Form, Input, InputNumber, Select, Button, Space, message, Statistic, Row, Col, Tabs, Table, Modal, InputNumber } from 'antd';
import { ShoppingCartOutlined, SendOutlined, StopOutlined, ClearOutlined, DeleteOutlined, DownloadOutlined } from '@ant-design/icons';
import axios from 'axios';
import type { TabsProps } from 'antd';

const { TabPane } = Tabs;

const Trade: React.FC = () => {
  const [orders, setOrders] = useState([]);
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(false);
  const [orderVisible, setOrderVisible] = useState(false);
  const [form] = Form.useForm();
  const [activeTab, setActiveTab] = useState('1');

  // 下单
  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/trade/orders', {
        symbol: values.symbol,
        direction: values.direction,
        offset: values.offset,
        volume: values.volume,
        price: values.price,
        order_type: values.order_type,
      });
      message.success('订单已提交');
      form.resetFields();
      setOrderVisible(false);
    } catch (error) {
      message.error('下单失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // 撤单
  const handleCancelOrder = async (orderId: string) => {
    try {
      const response = await axios.delete(`http://localhost:8000/api/trade/orders/${orderId}`);
      message.success(response.data.message);
      fetchOrders();
    } catch (error) {
      message.error('撤单失败');
      console.error(error);
    }
  };

  // 获取订单和成交
  const fetchOrders = async () => {
    setLoading(true);
    try {
      const ordersResponse = await axios.get('http://localhost:8000/api/trade/orders');
      const tradesResponse = await axios.get('http://localhost:8000/api/trade/trades');
      setOrders(ordersResponse.data.orders || []);
      setTrades(tradesResponse.data.trades || []);
    } catch (error) {
      message.error('获取数据失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  // 订单表格列
  const orderColumns = [
    {
      title: '订单号',
      dataIndex: 'orderid',
      key: 'orderid',
      width: 180,
    },
    {
      title: '合约代码',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 120,
    },
    {
      title: '方向',
      dataIndex: 'direction',
      key: 'direction',
      width: 80,
      render: (direction: string) => {
        if (direction === 'long') {
          return <Tag color="green">多</Tag>;
        } else if (direction === 'short') {
          return <Tag color="red">空</Tag>;
        }
        return <Tag>{direction}</Tag>;
      },
    },
    {
      title: '开平',
      dataIndex: 'offset',
      key: 'offset',
      width: 80,
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '数量',
      dataIndex: 'volume',
      key: 'volume',
      width: 80,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        if (status === 'submitted') {
          return <Tag color="blue">已报</Tag>;
        } else if (status === 'traded') {
          return <Tag color="green">已成</Tag>;
        } else if (status === 'cancelled') {
          return <Tag color="red">已撤</Tag>;
        } else if (status === 'rejected') {
          return <Tag color="orange">拒单</Tag>;
        }
        return <Tag>{status}</Tag>;
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_: any, record: any) => (
        <Space size="small">
          {record.status === 'submitted' && (
            <Button type="link" size="small" danger onClick={() => handleCancelOrder(record.orderid)}>
              撤单
            </Button>
          )}
          <Button type="link" size="small" onClick={() => {
            Modal.info({
              title: '订单详情',
              content: (
                <div>
                  <p>订单号: {record.orderid}</p>
                  <p>合约: {record.symbol}</p>
                  <p>方向: {record.direction}</p>
                  <p>价格: {record.price}</p>
                  <p>数量: {record.volume}</p>
                  <p>状态: {record.status}</p>
                </div>
              ),
            });
          }}>
            详情
          </Button>
        </Space>
      ),
    },
  ];

  // 成交表格列
  const tradeColumns = [
    {
      title: '成交号',
      dataIndex: 'tradeid',
      key: 'tradeid',
      width: 180,
    },
    {
      title: '合约代码',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 120,
    },
    {
      title: '方向',
      dataIndex: 'direction',
      key: 'direction',
      width: 80,
    },
    {
      title: '开平',
      dataIndex: 'offset',
      key: 'offset',
      width: 80,
    },
    {
      title: '成交价',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '数量',
      dataIndex: 'volume',
      key: 'volume',
      width: 80,
    },
    {
      title: '手续费',
      dataIndex: 'commission',
      key: 'commission',
      width: 100,
      render: (commission: number) => commission.toFixed(2),
    },
    {
      title: '时间',
      dataIndex: 'trade_time',
      key: 'trade_time',
      width: 150,
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日成交量"
              value={trades.reduce((sum, trade) => sum + (trade.volume || 0), 0)}
              suffix="手"
              valueStyle={{ fontWeight: 'bold' }}
              prefix={<ShoppingCartOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日成交额"
              value={trades.reduce((sum, trade) => sum + (trade.volume * trade.price), 0).toFixed(2)}
              suffix="元"
              precision={2}
              valueStyle={{ fontWeight: 'bold' }}
              prefix={<DownloadOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="成交笔数"
              value={trades.length}
              suffix="笔"
              valueStyle={{ fontWeight: 'bold' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="委托笔数"
              value={orders.length}
              suffix="笔"
              valueStyle={{ fontWeight: 'bold' }}
            />
          </Card>
        </Col>
      </Row>

      <Card
        title="交易管理"
        style={{ marginBottom: 16 }}
        extra={
          <Space>
            <Button type="primary" icon={<SendOutlined />} onClick={() => setOrderVisible(true)}>
              下单
            </Button>
            <Button icon={<ClearOutlined />} onClick={form.resetFields}>
              重置
            </Button>
            <Button icon={<DownloadOutlined />} onClick={fetchOrders} loading={loading}>
              刷新
            </Button>
          </Space>
        }
      >
        <Tabs activeKey={activeTab} onChange={setActiveTab} type="card" style={{ marginBottom: 16 }}>
          <TabPane tabKey="1" tab="委托" icon={<ShoppingCartOutlined />}>
            <Table
              columns={orderColumns}
              dataSource={orders}
              rowKey="orderid"
              loading={loading}
              pagination={{
                pageSize: 10,
                showTotal: true,
                showSizeChanger: true,
              }}
              scroll={{ x: 'max-content' }}
            />
          </TabPane>
          <TabPane tabKey="2" tab="成交" icon={<DownloadOutlined />}>
            <Table
              columns={tradeColumns}
              dataSource={trades}
              rowKey="tradeid"
              loading={loading}
              pagination={{
                pageSize: 10,
                showTotal: true,
                showSizeChanger: true,
              }}
              scroll={{ x: 'max-content' }}
            />
          </TabPane>
        </Tabs>
      </Card>

      <Modal
        title="下单"
        open={orderVisible}
        onCancel={() => setOrderVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            order_type: 'limit',
            direction: 'long',
            offset: 'open',
          }}
        >
          <Form.Item
            name="symbol"
            label="合约代码"
            rules={[{ required: true, message: '请输入合约代码' }]}
          >
            <Input placeholder="例如: IC2602" />
          </Form.Item>

          <Form.Item
            name="direction"
            label="方向"
            rules={[{ required: true, message: '请选择方向' }]}
          >
            <Select>
              <Select.Option value="long">买入</Select.Option>
              <Select.Option value="short">卖出</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="offset"
            label="开平"
            rules={[{ required: true, message: '请选择开平' }]}
          >
            <Select>
              <Select.Option value="open">开仓</Select.Option>
              <Select.Option value="close">平仓</Select.Option>
              <Select.Option value="close_today">平今</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="order_type"
            label="委托类型"
            rules={[{ required: true, message: '请选择委托类型' }]}
          >
            <Select>
              <Select.Option value="limit">限价</Select.Option>
              <Select.Option value="market">市价</Select.Option>
              <Select.Option value="stop">条件单</Select.Option>
              <Select.Option value="fok">FOK</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="price"
            label="价格"
            rules={[{ required: true, message: '请输入价格' }]}
            dependencies={['order_type']}
          >
            {({ getFieldValue }) => (
              <InputNumber
                disabled={getFieldValue('order_type') === 'market'}
                placeholder="请输入价格"
                precision={2}
                min={0}
              />
            )}
          </Form.Item>

          <Form.Item
            name="volume"
            label="数量"
            rules={[{ required: true, message: '请输入数量' }]}
          >
            <InputNumber
              placeholder="请输入数量"
              min={1}
              precision={0}
              style={{ width: '100%' }}
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              <SendOutlined /> 提交订单
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Trade;
