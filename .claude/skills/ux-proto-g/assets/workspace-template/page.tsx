import {
  Alert, Badge, Breadcrumb, Button, Card, Checkbox, ConfigProvider, DatePicker,
  Descriptions, Divider, Drawer, Dropdown, Empty, Flex, Form, Input, InputNumber,
  Layout, Menu, Modal, Pagination, Popconfirm, Progress, Radio, Result, Select,
  Space, Statistic, Steps, Switch, Table, Tabs, Tag, Timeline, Tree, TreeSelect,
  Typography, Upload, Row, Col, message
} from "antd";
import type { ButtonProps } from "antd";
import { themeConfig } from "./theme/theme-config.generated.mjs";

const rows = [{ key: "1", name: "Baseline record", status: "Ready" }];
const columns = [
  { title: "Name", dataIndex: "name", key: "name" },
  { title: "Status", dataIndex: "status", key: "status" }
];
const treeData = [{ title: "Root", key: "root", value: "root", children: [{ title: "Child", key: "child", value: "child" }] }];

export default function Page() {
  const feedbackProbeProps: ButtonProps = { onClick: () => void message.success("Ant Design root feedback API is available") };
  return (
    <ConfigProvider theme={{ ...themeConfig, zeroRuntime: true }}>
      <main className="page-shell">
        <Typography.Title level={2}>UX Proto Ant Design public surface</Typography.Title>
        <Alert title="Public Ant Design components use the pinned shared runtime." type="success" showIcon />
        <Flex vertical gap={16}>
          <Card title="Content and status">
            <Space wrap>
              <Badge count={3}><Button>Badge host</Button></Badge>
              <Tag color="blue">Ready</Tag>
              <Statistic title="Processed" value={42} />
              <Progress percent={64} className="primitive-progress" />
            </Space>
            <Divider />
            <Descriptions items={[{ key: "owner", label: "Owner", children: "Design system" }]} />
            <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No additional records" />
            <Result status="success" title="Default result state" />
          </Card>

          <Card title="Data entry">
            <Form layout="vertical">
              <Form.Item label="Name"><Input defaultValue="Prototype" /></Form.Item>
              <Form.Item label="Quantity"><InputNumber defaultValue={2} /></Form.Item>
              <Form.Item label="Date"><DatePicker /></Form.Item>
              <Form.Item label="Category"><Select defaultValue="a" options={[{ value: "a", label: "Category A" }]} /></Form.Item>
              <Form.Item label="Hierarchy"><TreeSelect treeData={treeData} defaultValue="child" /></Form.Item>
              <Checkbox defaultChecked>Enabled</Checkbox>
              <Radio.Group defaultValue="a" options={[{ value: "a", label: "A" }, { value: "b", label: "B" }]} />
              <Switch defaultChecked />
              <Upload beforeUpload={() => false} fileList={[]}><Button>Select file</Button></Upload>
            </Form>
          </Card>

          <Card title="Navigation and hierarchy">
            <Breadcrumb items={[{ title: "Home" }, { title: "Baseline" }]} />
            <Menu mode="horizontal" selectedKeys={["overview"]} items={[{ key: "overview", label: "Overview" }, { key: "details", label: "Details" }]} />
            <Tabs items={[{ key: "one", label: "Tab one", children: "Tab content" }]} />
            <Steps current={1} items={[{ title: "Created" }, { title: "Review" }, { title: "Done" }]} />
            <Timeline items={[{ children: "Created" }, { children: "Reviewed" }]} />
            <Tree defaultExpandAll treeData={treeData} />
            <Pagination defaultCurrent={1} total={25} pageSize={10} />
          </Card>

          <Card title="Table and actions">
            <Table columns={columns} dataSource={rows} pagination={false} />
            <Space wrap>
              <Button type="primary">Primary action</Button>
              <Button {...feedbackProbeProps}>Feedback API probe</Button>
              <Dropdown menu={{ items: [{ key: "edit", label: "Edit" }] }}><Button>More</Button></Dropdown>
              <Popconfirm title="Confirm action?"><Button>Delete</Button></Popconfirm>
            </Space>
          </Card>

          <Row gutter={16}>
            <Col span={6}><Layout.Sider width={120}>Sider</Layout.Sider></Col>
            <Col span={18}><Layout.Content>Layout content</Layout.Content></Col>
          </Row>
        </Flex>
        <Modal open={false} title="Modal baseline" />
        <Drawer open={false} title="Drawer baseline" />
      </main>
    </ConfigProvider>
  );
}
