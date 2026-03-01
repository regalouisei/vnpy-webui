# 账户管理页面

import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Space, message, Statistic, Row, Col } from 'antd';
import { DollarOutlined, WalletOutlined, ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import axios from 'axios';

const Account: React.FC = () => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);

  // 获取账户数据
  const fetchAccounts = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/api/accounts');
      setAccounts(response.data.accounts || []);
    } catch (error) {
      message.error('获取账户数据失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // 刷新账户数据
  const refreshAccount = async (accountId: string) => {
    try {
      const response = await axios.post(`http://localhost:8000/api/accounts/${accountId}/refresh`);
      message.success(response.data.message);
      fetchAccounts();
    } catch (error) {
      message.error('刷新账户失败');
      console.error(error);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

  const columns = [
    {
      title: '账户ID',
      dataIndex: 'accountid',
      key: 'accountid',
    },
    {
      title: '账户类型',
      dataIndex: 'accounttype',
      key: 'accounttype',
    },
    {
      title: '余额',
      dataIndex: 'balance',
      key: 'balance',
      render: (text: number) => text.toFixed(2),
    },
    {
      title: '可用',
      dataIndex: 'available',
      key: 'available',
      render: (text: number) => text.toFixed(2),
    },
    {
      title: '冻结',
      dataIndex: 'frozen',
      key: 'frozen',
      render: (text: number) => text.toFixed(2),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space>
          <Button type="link" onClick={() => refreshAccount(record.accountid)}>
            刷新
          </Button>
        </Space>
      ),
    },
  ];

  // 计算统计
  const totalBalance = accounts.reduce((sum, acc) => sum + (acc.balance || 0), 0);
  const totalAvailable = accounts.reduce((sum, acc) => sum + (acc.available || 0), 0);
  const totalFrozen = accounts.reduce((sum, acc) => sum + (acc.frozen || 0), 0);

  return (
    <div style={{ padding: 24 }}>
      <Row gutter={16}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总余额"
              value={totalBalance.toFixed(2)}
              precision={2}
              prefix="¥"
              suffix="元"
              valueStyle={{ color: '#3f8600' }}
              prefix={<DollarOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="可用资金"
              value={totalAvailable.toFixed(2)}
              precision={2}
              prefix="¥"
              suffix="元"
              prefix={<WalletOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="冻结资金"
              value={totalFrozen.toFixed(2)}
              precision={2}
              prefix="¥"
              suffix="元"
              valueStyle={{ color: '#cf1322' }}
              prefix={<ArrowDownOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="账户数量"
              value={accounts.length}
              suffix="个"
              valueStyle={{ color: '#1890ff' }}
              prefix={<ArrowUpOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card
        title="账户管理"
        style={{ marginTop: 16 }}
        extra={
          <Button type="primary" onClick={fetchAccounts} loading={loading}>
            刷新
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={accounts}
          rowKey="accountid"
          loading={loading}
          pagination={{
            pageSize: 10,
            showTotal: true,
            showSizeChanger: true,
          }}
        />
      </Card>
    </div>
  );
};

export default Account;
