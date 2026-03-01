# 策略管理页面

import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Space, message, Modal, Form, Input, Select, InputNumber, Row, Col, Tag, Statistic, Switch } from 'antd';
import { PlayCircleOutlined, PauseCircleOutlined, SettingOutlined, DeleteOutlined, EditOutlined, BarChartOutlined, DownloadOutlined } from '@ant-design/icons';
import axios from 'axios';

const Strategy: React.FC = () => {
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingStrategy, setEditingStrategy] = useState<any>(null);
  const [form] = Form.useForm();

  // 获取策略列表
  const fetchStrategies = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/api/strategies');
      setStrategies(response.data.strategies || []);
    } catch (error) {
      message.error('获取策略列表失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // 创建策略
  const handleCreate = () => {
    setEditingStrategy({ class_name: '', parameters: {} });
    setModalVisible(true);
  };

  // 编辑策略
  const handleEdit = (strategy: any) => {
    setEditingStrategy(strategy);
    setModalVisible(true);
  };

  // 删除策略
  const handleDelete = async (strategyId: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个策略吗？',
      onOk: async () => {
        try {
          await axios.delete(`http://localhost:8000/api/strategies/${strategyId}`);
          message.success('策略删除成功');
          fetchStrategies();
        } catch (error) {
          message.error('策略删除失败');
          console.error(error);
        }
      },
    });
  };

  // 启动策略
  const handleStart = async (strategyId: string) => {
    try {
      const response = await axios.post(`http://localhost:8000/api/strategies/${strategyId}/start`);
      message.success(response.data.message);
      fetchStrategies();
    } catch (error) {
      message.error('策略启动失败');
      console.error(error);
    }
  };

  // 停止策略
  const handleStop = async (strategyId: string) => {
    try {
      const response = await axios.post(`http://localhost:8000/api/strategies/${strategyId}/stop`);
      message.success(response.data.message);
      fetchStrategies();
    } catch (error) {
      message.error('策略停止失败');
      console.error(error);
    }
  };

  // 查看策略日志
  const handleViewLog = async (strategyId: string) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/strategies/${strategyId}/log`);
      Modal.info({
        title: '策略日志',
        content: (
          <div style={{ maxHeight: 600, overflow: 'auto' }}>
            {response.data.logs.map((log: string, index: number) => (
              <div key={index} style={{ marginBottom: 8, fontSize: 12 }}>
                {log}
              </div>
            ))}
          </div>
        ),
        width: 800,
      });
    } catch (error) {
      message.error('获取策略日志失败');
      console.error(error);
    }
  };

  // 提交表单
  const handleSubmit = async (values: any) => {
    try {
      if (editingStrategy.id) {
        // 编辑
        await axios.put(`http://localhost:8000/api/strategies/${editingStrategy.id}`, {
          name: values.name,
          class_name: values.class_name,
          parameters: values.parameters,
        });
        message.success('策略更新成功');
      } else {
        // 创建
        await axios.post('http://localhost:8000/api/strategies', {
          name: values.name,
          class_name: values.class_name,
          parameters: values.parameters,
        });
        message.success('策略创建成功');
      }
      setModalVisible(false);
      setEditingStrategy(null);
      fetchStrategies();
    } catch (error) {
      message.error('策略操作失败');
      console.error(error);
    }
  };

  useEffect(() => {
    fetchStrategies();
  }, []);

  const columns = [
    {
      title: '策略ID',
      dataIndex: 'id',
      key: 'id',
      width: 200,
    },
    {
      title: '策略名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: '类名',
      dataIndex: 'class_name',
      key: 'class_name',
      width: 200,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        if (status === 'running') {
          return <Tag color="green">运行中</Tag>;
        } else if (status === 'stopped') {
          return <Tag color="red">已停止</Tag>;
        } else {
          return <Tag color="default">{status}</Tag>;
        }
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text: string) => text.substring(0, 16),
    },
    {
      title: '操作',
      key: 'action',
      width: 250,
      render: (_: any, record: any) => (
        <Space size="small">
          <Button type="link" size="small" icon={<BarChartOutlined />} onClick={() => handleViewLog(record.id)}>
            日志
          </Button>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Button type="link" size="small" icon={<PlayCircleOutlined />} onClick={() => handleStart(record.id)}>
            启动
          </Button>
          <Button type="link" size="small" icon={<PauseCircleOutlined />} onClick={() => handleStop(record.id)}>
            停止
          </Button>
          <Button type="link" size="small" danger icon={<DeleteOutlined />} onClick={() => handleDelete(record.id)}>
            删除
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
              title="策略总数"
              value={strategies.length}
              suffix="个"
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="运行中"
              value={strategies.filter(s => s.status === 'running').length}
              suffix="个"
              prefix={<PlayCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已停止"
              value={strategies.filter(s => s.status === 'stopped').length}
              suffix="个"
              prefix={<PauseCircleOutlined />}
              valueStyle={{ color: '#f5222d' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="空闲"
              value={strategies.filter(s => s.status === 'created').length}
              suffix="个"
              prefix={<SettingOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card
        title="策略管理"
        style={{ marginTop: 16 }}
        extra={
          <Space>
            <Button type="primary" icon={<DownloadOutlined />}>
              导出策略
            </Button>
            <Button type="primary" icon={<SettingOutlined />}>
              参数优化
            </Button>
            <Button type="primary" onClick={fetchStrategies} loading={loading} icon={<BarChartOutlined />}>
              刷新
            </Button>
            <Button type="primary" onClick={handleCreate}>
              创建策略
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={strategies}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showTotal: true,
            showSizeChanger: true,
          }}
          scroll={{ x: 'max-content' }}
        />
      </Card>

      <Modal
        title={editingStrategy?.id ? '编辑策略' : '创建策略'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="name"
            label="策略名称"
            rules={[{ required: true, message: '请输入策略名称' }]}
          >
            <Input placeholder="请输入策略名称" />
          </Form.Item>

          <Form.Item
            name="class_name"
            label="策略类名"
            rules={[{ required: true, message: '请输入策略类名' }]}
          >
            <Select placeholder="请选择策略类名">
              <Select.Option value="DoubleMaStrategy">双均线策略</Select.Option>
              <Select.Option value="TripleMaStrategy">三均线策略</Select.Option>
              <Select.Option value="BollChannelStrategy">布林通道策略</Select.Option>
              <Select.Option value="TurtleTradingStrategy">海龟交易策略</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item label="策略参数">
            <Input.TextArea
              placeholder='{"fast_period": 5, "slow_period": 30}'
              autoSize={{ minRows: 4, maxRows: 12 }}
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Strategy;
