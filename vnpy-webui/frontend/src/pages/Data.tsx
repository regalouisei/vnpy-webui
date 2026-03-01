# 数据管理页面

import React, { useState } from 'react';
import { Card, Table, Button, Space, message, Upload, Row, Col, Modal, Form, Input, Select, DatePicker, Tabs, Alert } from 'antd';
import { UploadOutlined, DownloadOutlined, DatabaseOutlined, DeleteOutlined, SearchOutlined, SyncOutlined, FileExcelOutlined, FilePdfOutlined, FileMarkdownOutlined } from '@ant-design/icons';
import axios from 'axios';

const { TabPane } = Tabs;
const { Dragger } = Upload;

const Data: React.FC = () => {
  const [dataList, setDataList] = useState([]);
  const [importVisible, setImportVisible] = useState(false);
  const [exportVisible, setExportVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  // 获取数据列表
  const fetchData = async (params: any = {}) => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/api/data/bars', {
        params: {
          symbol: params.symbol,
          exchange: params.exchange,
          interval: params.interval,
          start: params.start,
          end: params.end,
        }
      });
      setDataList(response.data.bars || []);
    } catch (error) {
      message.error('获取数据失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // 导入数据
  const handleImport = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await axios.post('http://localhost:8000/api/data/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      message.success(response.data.message);
      fetchData();
    } catch (error) {
      message.error('数据导入失败');
      console.error(error);
    }
  };

  // 导出数据
  const handleExport = async (params: any) => {
    try {
      const response = await axios.post('http://localhost:8000/api/data/export', {
        symbol: params.symbol,
        exchange: params.exchange,
        interval: params.interval,
        format: params.format,
        start: params.start,
        end: params.end,
      });
      
      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = `${params.symbol}_${params.interval}.${params.format}`;
      link.click();
      
      message.success('数据导出成功');
    } catch (error) {
      message.error('数据导出失败');
      console.error(error);
    }
  };

  // 删除数据
  const handleDelete = async (params: any) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这些数据吗？',
      onOk: async () => {
        try {
          const response = await axios.delete('http://localhost:8000/api/data/clean', {
            data: {
              symbol: params.symbol,
              exchange: params.exchange,
              interval: params.interval,
              all: params.all,
            }
          });
          message.success(response.data.message);
          fetchData();
        } catch (error) {
          message.error('数据删除失败');
          console.error(error);
        }
      },
    });
  };

  // 导入表单提交
  const handleImportSubmit = async (values: any) => {
    setImportVisible(false);
    fetchData({
      symbol: values.symbol,
      exchange: values.exchange,
    });
  };

  // 导出表单提交
  const handleExportSubmit = async (values: any) => {
    setExportVisible(false);
    
    handleExport({
      symbol: values.symbol,
      exchange: values.exchange,
      interval: values.interval,
      format: values.format,
      start: values.start_date,
      end: values.end_date,
    });
  };

  const columns = [
    {
      title: '合约代码',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 120,
    },
    {
      title: '交易所',
      dataIndex: 'exchange',
      key: 'exchange',
      width: 100,
    },
    {
      title: '周期',
      dataIndex: 'interval',
      key: 'interval',
      width: 80,
    },
    {
      title: '时间',
      dataIndex: 'datetime',
      key: 'datetime',
      width: 150,
    },
    {
      title: '开',
      dataIndex: 'open_price',
      key: 'open_price',
      width: 100,
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '高',
      dataIndex: 'high_price',
      key: 'high_price',
      width: 100,
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '低',
      dataIndex: 'low_price',
      key: 'low_price',
      width: 100,
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '收',
      dataIndex: 'close_price',
      key: 'close_price',
      width: 100,
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '成交量',
      dataIndex: 'volume',
      key: 'volume',
      width: 100,
    },
    {
      title: '持仓量',
      dataIndex: 'open_interest',
      key: 'open_interest',
      width: 100,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card
        title="数据管理"
        extra={
          <Space>
            <Upload
              accept=".csv,.xlsx,.xls,.json"
              showUploadList={false}
              customRequest={({ file }) => handleImport(file)}
            >
              <Button icon={<UploadOutlined />}>导入数据</Button>
            </Upload>
            <Button icon={<DownloadOutlined />} onClick={() => setExportVisible(true)}>
              导出数据
            </Button>
            <Button icon={<SyncOutlined />} onClick={fetchData} loading={loading}>
              刷新
            </Button>
          </Space>
        }
      >
        <Alert
          message="支持导入 CSV、Excel、JSON 格式数据，可导出为多种格式"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />

        <Card
          title="查询条件"
          style={{ marginBottom: 16 }}
        >
          <Form form={form} layout="inline" onFinish={fetchData}>
            <Form.Item name="symbol" label="合约代码">
              <Input placeholder="例如: IC2602" />
            </Form.Item>
            <Form.Item name="exchange" label="交易所">
              <Select defaultValue="CFFEX" style={{ width: 150 }}>
                <Select.Option value="CFFEX">中金所</Select.Option>
                <Select.Option value="SHFE">上期所</Select.Option>
                <Select.Option value="DCE">大商所</Select.Option>
                <Select.Option value="CZCE">郑商所</Select.Option>
                <Select.Option value="SSE">上交所</Select.Option>
                <Select.Option value="SZSE">深交所</Select.Option>
              </Select>
            </Form.Item>
            <Form.Item name="interval" label="周期">
              <Select defaultValue="1m" style={{ width: 120 }}>
                <Select.Option value="tick">Tick</Select.Option>
                <Select.Option value="1m">1分钟</Select.Option>
                <Select.Option value="5m">5分钟</Select.Option>
                <Select.Option value="15m">15分钟</Select.Option>
                <Select.Option value="1h">1小时</Select.Option>
                <Select.Option value="1d">1天</Select.Option>
                <Select.Option value="1w">1周</Select.Option>
                <Select.Option value="1M">1月</Select.Option>
              </Select>
            </Form.Item>
            <Form.Item name="start_date" label="起始日期">
              <DatePicker style={{ width: 180 }} />
            </Form.Item>
            <Form.Item name="end_date" label="结束日期">
              <DatePicker style={{ width: 180 }} />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit">
                <SearchOutlined /> 查询
              </Button>
            </Form.Item>
          </Form>
        </Card>

        <Card
          title="数据列表"
          extra={
            <Space>
              <Button danger icon={<DeleteOutlined />} onClick={() => handleDelete({})}>
                清空数据
              </Button>
              <Button icon={<DatabaseOutlined />} onClick={() => handleDelete({ all: true })}>
                清空所有数据
              </Button>
            </Space>
          }
        >
          <Table
            columns={columns}
            dataSource={dataList}
            rowKey={(record) => `${record.symbol}_${record.datetime}`}
            loading={loading}
            pagination={{
              pageSize: 20,
              showTotal: true,
              showSizeChanger: true,
            }}
            scroll={{ x: 'max-content', y: 600 }}
          />
        </Card>
      </Card>

      {/* 导入数据弹窗 */}
      <Modal
        title="导入数据"
        open={importVisible}
        onCancel={() => setImportVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleImportSubmit}>
          <Form.Item label="上传文件">
            <Upload.Dragger
              name="file"
              multiple={false}
              accept=".csv,.xlsx,.xls,.json"
              beforeUpload={(file, fileList) => {
                return false;
              }}
              customRequest={({ file }) => {
                handleImport(file);
                return true;
              }}
            >
              <Button icon={<UploadOutlined />}>点击或拖拽文件</Button>
            </Upload.Dragger>
          </Form.Item>

          <Form.Item name="symbol" label="合约代码" rules={[{ required: true }]}>
            <Input placeholder="例如: IC2602" />
          </Form.Item>

          <Form.Item name="exchange" label="交易所" rules={[{ required: true }]}>
            <Select defaultValue="CFFEX">
              <Select.Option value="CFFEX">中金所</Select.Option>
              <Select.Option value="SHFE">上期所</Select.Option>
              <Select.Option value="DCE">大商所</Select.Option>
              <Select.Option value="CZCE">郑商所</Select.Option>
              <Select.Option value="SSE">上交所</Select.Option>
              <Select.Option value="SZSE">深交所</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 导出数据弹窗 */}
      <Modal
        title="导出数据"
        open={exportVisible}
        onCancel={() => setExportVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleExportSubmit}>
          <Form.Item name="symbol" label="合约代码">
            <Input placeholder="例如: IC2602" />
          </Form.Item>

          <Form.Item name="exchange" label="交易所">
            <Select defaultValue="CFFEX">
              <Select.Option value="CFFEX">中金所</Select.Option>
              <Select.Option value="SHFE">上期所</Select.Option>
              <Select.Option value="DCE">大商所</Select.Option>
              <Select.Option value="CZCE">郑商所</Select.Option>
              <Select.Option value="SSE">上交所</Select.Option>
              <Select.Option value="SZSE">深交所</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="interval" label="周期">
            <Select defaultValue="1m">
              <Select.Option value="tick">Tick</Select.Option>
              <Select.Option value="1m">1分钟</Select.Option>
              <Select.Option value="5m">5分钟</Select.Option>
              <Select.Option value="15m">15分钟</Select.Option>
              <Select.Option value="1h">1小时</Select.Option>
              <Select.Option value="1d">1天</Select.Option>
              <Select.Option value="1w">1周</Select.Option>
              <Select.Option value="1M">1月</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="start_date" label="起始日期">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item name="end_date" label="结束日期">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item name="format" label="导出格式">
            <Select defaultValue="csv">
              <Select.Option value="csv">CSV</Select.Option>
              <Select.Option value="excel">Excel</Select.Option>
              <Select.Option value="json">JSON</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              <DownloadOutlined /> 导出数据
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Data;
