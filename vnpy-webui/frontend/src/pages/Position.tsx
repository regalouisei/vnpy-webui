# 持仓管理页面

import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Space, message, Statistic, Row, Col, Tag, Tooltip } from 'antd';
import { DollarOutlined, ArrowUpOutlined, ArrowDownOutlined, SyncOutlined } from '@ant-design/icons';
import axios from 'axios';

const Position: React.FC = () => {
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [totalPnl, setTotalPnl] = useState(0);
  const [totalVolume, setTotalVolume] = useState(0);

  // 获取持仓数据
  const fetchPositions = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/api/positions');
      const data = response.data.positions || [];
      setPositions(data);

      // 计算统计数据
      const totalPnl = data.reduce((sum, pos) => sum + (pos.unrealized_pnl || 0), 0);
      const totalVolume = data.reduce((sum, pos) => sum + (pos.volume || 0), 0);
      setTotalPnl(totalPnl);
      setTotalVolume(totalVolume);
    } catch (error) {
      message.error('获取持仓数据失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // 刷新持仓数据
  const refreshPosition = async (symbol: string) => {
    try {
      const response = await axios.post(`http://localhost:8000/api/positions/${symbol}/refresh`);
      message.success(response.data.message);
      fetchPositions();
    } catch (error) {
      message.error('刷新持仓失败');
      console.error(error);
    }
  };

  // 平仓
  const closePosition = async (symbol: string, direction: string) => {
    try {
      // TODO: 调用平仓 API
      message.success(`已发送平仓指令: ${symbol} ${direction}`);
    } catch (error) {
      message.error('平仓失败');
      console.error(error);
    }
  };

  useEffect(() => {
    fetchPositions();
  }, []);

  const columns = [
    {
      title: '合约代码',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 120,
    },
    {
      title: '合约名称',
      dataIndex: 'symbol_name',
      key: 'symbol_name',
      width: 150,
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
      title: '持仓量',
      dataIndex: 'volume',
      key: 'volume',
      width: 100,
      render: (volume: number) => volume.toLocaleString(),
    },
    {
      title: '开仓价',
      dataIndex: 'open_price',
      key: 'open_price',
      width: 100,
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '现价',
      dataIndex: 'last_price',
      key: 'last_price',
      width: 100,
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '浮动盈亏',
      dataIndex: 'unrealized_pnl',
      key: 'unrealized_pnl',
      width: 120,
      render: (pnl: number) => (
        <span style={{ color: pnl >= 0 ? '#52c41a' : '#f5222d', fontWeight: 'bold' }}>
          {pnl >= 0 ? '+' : ''}{pnl.toFixed(2)}
        </span>
      ),
    },
    {
      title: '盈亏比例',
      dataIndex: 'pnl_ratio',
      key: 'pnl_ratio',
      width: 100,
      render: (ratio: number) => (
        <span style={{ color: ratio >= 0 ? '#52c41a' : '#f5222d', fontWeight: 'bold' }}>
          {ratio >= 0 ? '+' : ''}{(ratio * 100).toFixed(2)}%
        </span>
      ),
    },
    {
      title: '保证金',
      dataIndex: 'margin',
      key: 'margin',
      width: 120,
      render: (margin: number) => margin.toFixed(2),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: any) => (
        <Space size="small">
          <Button type="link" size="small" onClick={() => refreshPosition(record.symbol)}>
            <SyncOutlined />
          </Button>
          <Button type="primary" size="small" onClick={() => closePosition(record.symbol, record.direction)}>
            平仓
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="持仓盈亏"
              value={totalPnl.toFixed(2)}
              precision={2}
              prefix="¥"
              valueStyle={{ color: totalPnl >= 0 ? '#3f8600' : '#cf1322', fontWeight: 'bold' }}
              prefix={totalPnl >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总持仓量"
              value={totalVolume}
              precision={0}
              suffix="手"
              valueStyle={{ fontWeight: 'bold' }}
              prefix={<DollarOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="持仓合约"
              value={positions.length}
              precision={0}
              suffix="个"
              valueStyle={{ fontWeight: 'bold' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="保证金占用"
              value={positions.reduce((sum, pos) => sum + (pos.margin || 0), 0).toFixed(2)}
              precision={2}
              prefix="¥"
              valueStyle={{ fontWeight: 'bold' }}
            />
          </Card>
        </Col>
      </Row>

      <Card
        title="持仓管理"
        style={{ marginTop: 16 }}
        extra={
          <Button type="primary" onClick={fetchPositions} loading={loading}>
            <SyncOutlined />
            刷新
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={positions}
          rowKey="symbol"
          loading={loading}
          pagination={{
            pageSize: 10,
            showTotal: true,
            showSizeChanger: true,
          }}
          scroll={{ x: 'max-content' }}
        />
      </Card>
    </div>
  );
};

export default Position;
