(function () {
  var globalKey = "__SAAS_OFFLINE_PAYLOAD__";
  var payload = {"tree":{"root":"node_0","elements":{"node_3":{"key":"node_3","type":"XFTTopBar","props":{},"parentKey":"node_2"},"node_2":{"key":"node_2","type":"Header","props":{"style":{"height":"48px"}},"children":["node_3"],"parentKey":"node_1"},"node_6":{"key":"node_6","type":"Menu","props":{"mode":"inline","theme":"light","defaultSelectedKeys":["1-1"],"items":[{"key":"1","label":"人力资源管理","icon":"UserOutlined","children":[{"key":"1-1","label":"成员管理"},{"key":"1-2","label":"组织架构"},{"key":"1-3","label":"职位管理"}]},{"key":"2","label":"招聘管理","icon":"TeamOutlined","children":[{"key":"2-1","label":"职位发布"},{"key":"2-2","label":"候选人库"},{"key":"2-3","label":"面试流程"}]},{"key":"3","label":"绩效管理","icon":"AppstoreOutlined","children":[{"key":"3-1","label":"考核周期"},{"key":"3-2","label":"绩效结果"},{"key":"3-3","label":"绩效申诉"}]},{"key":"4","label":"培训发展","icon":"SettingOutlined","children":[{"key":"4-1","label":"培训计划"},{"key":"4-2","label":"学习地图"},{"key":"4-3","label":"认证管理"}]},{"key":"5","label":"薪酬福利","icon":"UserOutlined","children":[{"key":"5-1","label":"薪资核算"},{"key":"5-2","label":"福利方案"},{"key":"5-3","label":"个税申报"}]},{"key":"6","label":"考勤管理","icon":"TeamOutlined","children":[{"key":"6-1","label":"排班管理"},{"key":"6-2","label":"打卡记录"},{"key":"6-3","label":"请假审批"}]},{"key":"7","label":"员工关系","icon":"AppstoreOutlined","children":[{"key":"7-1","label":"合同管理"},{"key":"7-2","label":"异动管理"},{"key":"7-3","label":"离职管理"}]},{"key":"8","label":"组织人才","icon":"SettingOutlined","children":[{"key":"8-1","label":"人才盘点"},{"key":"8-2","label":"继任计划"},{"key":"8-3","label":"关键岗位"}]},{"key":"9","label":"合规风控","icon":"UserOutlined","children":[{"key":"9-1","label":"制度中心"},{"key":"9-2","label":"审计日志"},{"key":"9-3","label":"权限审批"}]}],"style":{"height":"100%","minHeight":0,"overflowY":"auto","overflowX":"hidden"}},"parentKey":"node_5"},"node_5":{"key":"node_5","type":"Sider","props":{"theme":"light","style":{"backgroundColor":"#ffffff","height":"100%","minHeight":0,"overflowY":"auto","overflowX":"hidden","width":"188px"}},"children":["node_6"],"parentKey":"node_4"},"node_12":{"key":"node_12","type":"Input","props":{"placeholder":"搜索组织","allowClear":true,"style":{"flex":1,"minWidth":0,"borderTopRightRadius":0,"borderBottomRightRadius":0}},"parentKey":"node_11"},"node_14":{"key":"node_14","type":"span","props":{"children":"搜索"},"parentKey":"node_13"},"node_13":{"key":"node_13","type":"Button","props":{"type":"default","style":{"borderTopLeftRadius":0,"borderBottomLeftRadius":0,"marginLeft":"-1px"}},"children":["node_14"],"parentKey":"node_11"},"node_11":{"key":"node_11","type":"Flex","props":{"gap":0,"style":{"width":"100%","alignItems":"center"}},"children":["node_12","node_13"],"parentKey":"node_10"},"node_16":{"key":"node_16","type":"span","props":{"children":"创建组织"},"parentKey":"node_15"},"node_15":{"key":"node_15","type":"Button","props":{"type":"default","style":{"height":"32px","lineHeight":"32px","padding":"0 15px"},"interactions":[{"trigger":"click","action":"SET_VISIBLE","target":"modal_create_org","payload":true}]},"children":["node_16"],"parentKey":"node_10"},"node_17":{"key":"node_17","type":"Tree","props":{"treeData":[{"title":"XX科技集团","key":"0","children":[{"title":"研发中心","key":"0-0","children":[{"title":"前端部","key":"0-0-0"},{"title":"后端部","key":"0-0-1"},{"title":"测试部","key":"0-0-2"}]},{"title":"产品中心","key":"0-1","children":[{"title":"产品一部","key":"0-1-0"},{"title":"产品二部","key":"0-1-1"},{"title":"设计部","key":"0-1-2"}]},{"title":"运营中心","key":"0-2","children":[{"title":"运营部","key":"0-2-0"},{"title":"市场部","key":"0-2-1"},{"title":"客服部","key":"0-2-2"}]},{"title":"职能部门","key":"0-3","children":[{"title":"人力资源部","key":"0-3-0"},{"title":"财务部","key":"0-3-1"},{"title":"行政部","key":"0-3-2"}]},{"title":"销售中心","key":"0-4","children":[{"title":"销售一部","key":"0-4-0"},{"title":"销售二部","key":"0-4-1"},{"title":"渠道部","key":"0-4-2"}]},{"title":"客户成功中心","key":"0-5","children":[{"title":"实施部","key":"0-5-0"},{"title":"交付部","key":"0-5-1"},{"title":"续约部","key":"0-5-2"}]},{"title":"质量管理中心","key":"0-6","children":[{"title":"流程质量部","key":"0-6-0"},{"title":"数据质量部","key":"0-6-1"},{"title":"内控部","key":"0-6-2"}]},{"title":"战略发展中心","key":"0-7","children":[{"title":"战略规划部","key":"0-7-0"},{"title":"投资并购部","key":"0-7-1"},{"title":"经营分析部","key":"0-7-2"}]},{"title":"行政服务中心","key":"0-8","children":[{"title":"行政支持部","key":"0-8-0"},{"title":"资产管理部","key":"0-8-1"},{"title":"后勤保障部","key":"0-8-2"}]}]}],"defaultExpandAll":true,"style":{"flex":1,"minHeight":0,"overflowY":"auto","overflowX":"hidden"}},"parentKey":"node_10"},"node_10":{"key":"node_10","type":"Flex","props":{"vertical":true,"gap":16,"style":{"width":"380px","height":"100%","minHeight":0,"overflow":"hidden"}},"children":["node_11","node_15","node_17"],"parentKey":"node_9"},"node_18":{"key":"node_18","type":"Divider","props":{"type":"vertical","style":{"height":"100%","alignSelf":"stretch"}},"parentKey":"node_9"},"node_25":{"key":"node_25","type":"span","props":{"children":"正大信息安全上海办事处"},"parentKey":"node_24"},"node_24":{"key":"node_24","type":"Typography.Title","props":{"level":4,"style":{"margin":0}},"children":["node_25"],"parentKey":"node_23"},"node_27":{"key":"node_27","type":"span","props":{"children":"组织类型"},"parentKey":"node_26"},"node_26":{"key":"node_26","type":"Typography.Text","props":{"style":{"fontSize":"12px","lineHeight":"20px","color":"#1966FF","backgroundColor":"rgba(25,102,255,0.12)","padding":"0 8px","borderRadius":"4px"}},"children":["node_27"],"parentKey":"node_23"},"node_29":{"key":"node_29","type":"span","props":{"children":"二级组织"},"parentKey":"node_28"},"node_28":{"key":"node_28","type":"Typography.Text","props":{"style":{"fontSize":"12px","lineHeight":"20px","color":"#1966FF","backgroundColor":"rgba(25,102,255,0.12)","padding":"0 8px","borderRadius":"4px"}},"children":["node_29"],"parentKey":"node_23"},"node_23":{"key":"node_23","type":"Flex","props":{"align":"center","gap":8,"style":{"flexWrap":"wrap"}},"children":["node_24","node_26","node_28"],"parentKey":"node_22"},"node_31":{"key":"node_31","type":"span","props":{"children":"组织详情"},"parentKey":"node_30"},"node_30":{"key":"node_30","type":"Typography.Text","props":{"style":{"color":"#1966FF","cursor":"pointer"},"interactions":[{"trigger":"click","action":"SET_VISIBLE","target":"modal_org_detail","payload":true}]},"children":["node_31"],"parentKey":"node_22"},"node_22":{"key":"node_22","type":"Flex","props":{"justify":"space-between","align":"center"},"children":["node_23","node_30"],"parentKey":"node_21"},"node_35":{"key":"node_35","type":"span","props":{"children":"成员总数"},"parentKey":"node_34"},"node_34":{"key":"node_34","type":"Typography.Text","props":{"style":{"color":"rgba(0,0,0,0.65)"}},"children":["node_35"],"parentKey":"node_33"},"node_37":{"key":"node_37","type":"span","props":{"children":"80"},"parentKey":"node_36"},"node_36":{"key":"node_36","type":"Typography.Text","props":{"style":{"color":"rgba(0,0,0,0.88)"}},"children":["node_37"],"parentKey":"node_33"},"node_33":{"key":"node_33","type":"Flex","props":{"align":"center","gap":4},"children":["node_34","node_36"],"parentKey":"node_32"},"node_39":{"key":"node_39","type":"span","props":{"children":"|"},"parentKey":"node_38"},"node_38":{"key":"node_38","type":"Typography.Text","props":{"style":{"color":"rgba(0,0,0,0.2)"}},"children":["node_39"],"parentKey":"node_32"},"node_42":{"key":"node_42","type":"span","props":{"children":"直属成员"},"parentKey":"node_41"},"node_41":{"key":"node_41","type":"Typography.Text","props":{"style":{"color":"rgba(0,0,0,0.65)"}},"children":["node_42"],"parentKey":"node_40"},"node_44":{"key":"node_44","type":"span","props":{"children":"23"},"parentKey":"node_43"},"node_43":{"key":"node_43","type":"Typography.Text","props":{"style":{"color":"rgba(0,0,0,0.88)"}},"children":["node_44"],"parentKey":"node_40"},"node_40":{"key":"node_40","type":"Flex","props":{"align":"center","gap":4},"children":["node_41","node_43"],"parentKey":"node_32"},"node_46":{"key":"node_46","type":"span","props":{"children":"|"},"parentKey":"node_45"},"node_45":{"key":"node_45","type":"Typography.Text","props":{"style":{"color":"rgba(0,0,0,0.2)"}},"children":["node_46"],"parentKey":"node_32"},"node_49":{"key":"node_49","type":"span","props":{"children":"组织负责人"},"parentKey":"node_48"},"node_48":{"key":"node_48","type":"Typography.Text","props":{"style":{"color":"rgba(0,0,0,0.65)"}},"children":["node_49"],"parentKey":"node_47"},"node_51":{"key":"node_51","type":"span","props":{"children":"邱云云"},"parentKey":"node_50"},"node_50":{"key":"node_50","type":"Typography.Text","props":{"style":{"color":"rgba(0,0,0,0.88)"}},"children":["node_51"],"parentKey":"node_47"},"node_47":{"key":"node_47","type":"Flex","props":{"align":"center","gap":4},"children":["node_48","node_50"],"parentKey":"node_32"},"node_53":{"key":"node_53","type":"span","props":{"children":"|"},"parentKey":"node_52"},"node_52":{"key":"node_52","type":"Typography.Text","props":{"style":{"color":"rgba(0,0,0,0.2)"}},"children":["node_53"],"parentKey":"node_32"},"node_56":{"key":"node_56","type":"span","props":{"children":"审批主管"},"parentKey":"node_55"},"node_55":{"key":"node_55","type":"Typography.Text","props":{"style":{"color":"rgba(0,0,0,0.65)"}},"children":["node_56"],"parentKey":"node_54"},"node_58":{"key":"node_58","type":"span","props":{"children":"邱云"},"parentKey":"node_57"},"node_57":{"key":"node_57","type":"Typography.Text","props":{"style":{"color":"rgba(0,0,0,0.88)"}},"children":["node_58"],"parentKey":"node_54"},"node_54":{"key":"node_54","type":"Flex","props":{"align":"center","gap":4},"children":["node_55","node_57"],"parentKey":"node_32"},"node_60":{"key":"node_60","type":"span","props":{"children":"|"},"parentKey":"node_59"},"node_59":{"key":"node_59","type":"Typography.Text","props":{"style":{"color":"rgba(0,0,0,0.2)"}},"children":["node_60"],"parentKey":"node_32"},"node_63":{"key":"node_63","type":"span","props":{"children":"下级组织数"},"parentKey":"node_62"},"node_62":{"key":"node_62","type":"Typography.Text","props":{"style":{"color":"rgba(0,0,0,0.65)"}},"children":["node_63"],"parentKey":"node_61"},"node_65":{"key":"node_65","type":"span","props":{"children":"80"},"parentKey":"node_64"},"node_64":{"key":"node_64","type":"Typography.Text","props":{"style":{"color":"rgba(0,0,0,0.88)"}},"children":["node_65"],"parentKey":"node_61"},"node_61":{"key":"node_61","type":"Flex","props":{"align":"center","gap":4},"children":["node_62","node_64"],"parentKey":"node_32"},"node_32":{"key":"node_32","type":"Flex","props":{"align":"center","gap":12,"style":{"flexWrap":"wrap"}},"children":["node_33","node_38","node_40","node_45","node_47","node_52","node_54","node_59","node_61"],"parentKey":"node_21"},"node_21":{"key":"node_21","type":"Flex","props":{"vertical":true,"gap":12},"children":["node_22","node_32"],"parentKey":"node_20"},"node_20":{"key":"node_20","type":"Card","props":{"variant":"borderless","style":{"backgroundColor":"rgba(25, 102, 255, 0.04)","borderRadius":"8px"}},"children":["node_21"],"parentKey":"node_19"},"node_66":{"key":"node_66","type":"Segmented","props":{"options":["直属成员","全部成员"],"defaultValue":"直属成员","style":{"width":"fit-content"}},"parentKey":"node_19"},"node_71":{"key":"node_71","type":"span","props":{"children":"邀请成员"},"parentKey":"node_70"},"node_70":{"key":"node_70","type":"Button","props":{"type":"primary","icon":"DownOutlined","iconPosition":"right"},"children":["node_71"],"parentKey":"node_69"},"node_69":{"key":"node_69","type":"Dropdown","props":{"menu":{"items":[{"key":"1","label":"手机号邀请成员","interactions":[{"trigger":"click","action":"SET_VISIBLE","target":"modal_invite_by_phone","payload":true}]},{"key":"2","label":"二维码邀请成员"},{"key":"3","label":"邀请记录"}]},"trigger":["click"]},"children":["node_70"],"parentKey":"node_68"},"node_74":{"key":"node_74","type":"span","props":{"children":"导入/导出"},"parentKey":"node_73"},"node_73":{"key":"node_73","type":"Button","props":{"type":"default","icon":"DownOutlined","iconPosition":"right"},"children":["node_74"],"parentKey":"node_72"},"node_72":{"key":"node_72","type":"Dropdown","props":{"menu":{"items":[{"key":"1","label":"导入成员","interactions":[{"trigger":"click","action":"SET_VISIBLE","target":"modal_import_member","payload":true}]},{"key":"2","label":"导出成员","interactions":[{"trigger":"click","action":"SET_VISIBLE","target":"modal_export_member","payload":true}]}]},"trigger":["click"]},"children":["node_73"],"parentKey":"node_68"},"node_76":{"key":"node_76","type":"span","props":{"children":"调整组织"},"parentKey":"node_75"},"node_75":{"key":"node_75","type":"Button","props":{"type":"default"},"children":["node_76"],"parentKey":"node_68"},"node_78":{"key":"node_78","type":"span","props":{"children":"成员排序"},"parentKey":"node_77"},"node_77":{"key":"node_77","type":"Button","props":{"type":"default"},"children":["node_78"],"parentKey":"node_68"},"node_81":{"key":"node_81","type":"span","props":{"children":"批量操作"},"parentKey":"node_80"},"node_80":{"key":"node_80","type":"Button","props":{"type":"default","icon":"DownOutlined","iconPosition":"right"},"children":["node_81"],"parentKey":"node_79"},"node_79":{"key":"node_79","type":"Dropdown","props":{"menu":{"items":[{"key":"1","label":"批量删除"},{"key":"2","label":"批量撤销"}]},"trigger":["click"]},"children":["node_80"],"parentKey":"node_68"},"node_68":{"key":"node_68","type":"Flex","props":{"gap":8},"children":["node_69","node_72","node_75","node_77","node_79"],"parentKey":"node_67"},"node_83":{"key":"node_83","type":"span","props":{"children":"设置"},"parentKey":"node_82"},"node_82":{"key":"node_82","type":"Button","props":{"type":"default","icon":"SettingOutlined"},"children":["node_83"],"parentKey":"node_67"},"node_67":{"key":"node_67","type":"Flex","props":{"justify":"space-between","align":"center","gap":8},"children":["node_68","node_82"],"parentKey":"node_19"},"node_85":{"key":"node_85","type":"Table","props":{"size":"small","bordered":true,"scroll":{"x":"max-content","y":460},"dataSource":[{"id":1,"name":"张三","dept":"研发中心/前端部","position":"前端工程师","phone":"13800138001","email":"zhangsan@example.com","status":"在职","joinDate":"2021-03-15","employeeId":"EMP1001","supervisor":"部门负责人","rank":"P5"},{"id":2,"name":"李四","dept":"产品中心/产品一部","position":"产品经理","phone":"13800138002","email":"lisi@example.com","status":"在职","joinDate":"2020-07-22","employeeId":"EMP1002","supervisor":"部门负责人","rank":"P5"},{"id":3,"name":"王五","dept":"运营中心/市场部","position":"市场专员","phone":"13800138003","email":"wangwu@example.com","status":"在职","joinDate":"2022-01-10","employeeId":"EMP1003","supervisor":"部门负责人","rank":"P5"},{"id":4,"name":"赵六","dept":"职能部门/人力资源部","position":"招聘专员","phone":"13800138004","email":"zhaoliu@example.com","status":"在职","joinDate":"2019-11-05","employeeId":"EMP1004","supervisor":"部门负责人","rank":"P5"},{"id":5,"name":"钱七","dept":"销售中心/销售一部","position":"销售经理","phone":"13800138005","email":"qianqi@example.com","status":"在职","joinDate":"2020-05-30","employeeId":"EMP1005","supervisor":"部门负责人","rank":"P5"},{"id":6,"name":"孙八","dept":"研发中心/后端部","position":"后端工程师","phone":"13800138006","email":"sunba@example.com","status":"在职","joinDate":"2021-08-14","employeeId":"EMP1006","supervisor":"部门负责人","rank":"P5"},{"id":7,"name":"周九","dept":"产品中心/设计部","position":"UI设计师","phone":"13800138007","email":"zhoujiu@example.com","status":"在职","joinDate":"2022-03-01","employeeId":"EMP1007","supervisor":"部门负责人","rank":"P5"},{"id":8,"name":"吴十","dept":"运营中心/运营部","position":"运营主管","phone":"13800138008","email":"wushi@example.com","status":"在职","joinDate":"2020-09-18","employeeId":"EMP1008","supervisor":"部门负责人","rank":"P5"},{"id":9,"name":"郑十一","dept":"职能部门/财务部","position":"会计","phone":"13800138009","email":"zhengshiyi@example.com","status":"在职","joinDate":"2021-12-03","employeeId":"EMP1009","supervisor":"部门负责人","rank":"P5"},{"id":10,"name":"王十二","dept":"销售中心/渠道部","position":"渠道专员","phone":"13800138010","email":"wangshier@example.com","status":"在职","joinDate":"2022-06-20","employeeId":"EMP1010","supervisor":"部门负责人","rank":"P5"},{"id":11,"name":"刘十三","dept":"研发中心/测试部","position":"测试工程师","phone":"13800138011","email":"liushisan@example.com","status":"在职","joinDate":"2021-05-11","employeeId":"EMP1011","supervisor":"部门负责人","rank":"P5"},{"id":12,"name":"陈十四","dept":"产品中心/产品二部","position":"产品助理","phone":"13800138012","email":"chenshisi@example.com","status":"在职","joinDate":"2022-07-25","employeeId":"EMP1012","supervisor":"部门负责人","rank":"P5"},{"id":13,"name":"杨十五","dept":"运营中心/客服部","position":"客服专员","phone":"13800138013","email":"yangshiwu@example.com","status":"在职","joinDate":"2021-10-09","employeeId":"EMP1013","supervisor":"部门负责人","rank":"P5"},{"id":14,"name":"黄十六","dept":"职能部门/行政部","position":"行政专员","phone":"13800138014","email":"huangshiliu@example.com","status":"在职","joinDate":"2020-12-12","employeeId":"EMP1014","supervisor":"部门负责人","rank":"P5"},{"id":15,"name":"林十七","dept":"销售中心/销售二部","position":"销售代表","phone":"13800138015","email":"linshiqi@example.com","status":"在职","joinDate":"2022-04-05","employeeId":"EMP1015","supervisor":"部门负责人","rank":"P5"},{"id":16,"name":"许十六","dept":"客户成功中心/实施部","position":"实施顾问","phone":"13800130016","email":"user0016@example.com","status":"在职","joinDate":"2022-05-15","employeeId":"EMP1016","supervisor":"部门负责人","rank":"P5"},{"id":17,"name":"何十七","dept":"客户成功中心/交付部","position":"交付经理","phone":"13800130017","email":"user0017@example.com","status":"在职","joinDate":"2022-06-15","employeeId":"EMP1017","supervisor":"部门负责人","rank":"P6"},{"id":18,"name":"高十八","dept":"质量管理中心/流程质量部","position":"质量专员","phone":"13800130018","email":"user0018@example.com","status":"在职","joinDate":"2022-07-15","employeeId":"EMP1018","supervisor":"部门负责人","rank":"P5"},{"id":19,"name":"邓十九","dept":"质量管理中心/内控部","position":"内控专员","phone":"13800130019","email":"user0019@example.com","status":"在职","joinDate":"2022-08-15","employeeId":"EMP1019","supervisor":"部门负责人","rank":"P6"},{"id":20,"name":"潘二十","dept":"战略发展中心/战略规划部","position":"战略分析师","phone":"13800130020","email":"user0020@example.com","status":"在职","joinDate":"2022-09-15","employeeId":"EMP1020","supervisor":"部门负责人","rank":"P5"},{"id":21,"name":"蔡二十一","dept":"战略发展中心/经营分析部","position":"经营分析师","phone":"13800130021","email":"user0021@example.com","status":"在职","joinDate":"2022-10-15","employeeId":"EMP1021","supervisor":"部门负责人","rank":"P6"},{"id":22,"name":"蒙二十二","dept":"行政服务中心/行政支持部","position":"行政主管","phone":"13800130022","email":"user0022@example.com","status":"在职","joinDate":"2022-11-15","employeeId":"EMP1022","supervisor":"部门负责人","rank":"P5"},{"id":23,"name":"尤二十三","dept":"行政服务中心/资产管理部","position":"资产管理专员","phone":"13800130023","email":"user0023@example.com","status":"在职","joinDate":"2022-12-15","employeeId":"EMP1023","supervisor":"部门负责人","rank":"P6"},{"id":24,"name":"费二十四","dept":"考勤管理/打卡记录","position":"人事专员","phone":"13800130024","email":"user0024@example.com","status":"在职","joinDate":"2022-01-15","employeeId":"EMP1024","supervisor":"部门负责人","rank":"P5"},{"id":25,"name":"郎二十五","dept":"员工关系/合同管理","position":"员工关系专员","phone":"13800130025","email":"user0025@example.com","status":"在职","joinDate":"2022-02-15","employeeId":"EMP1025","supervisor":"部门负责人","rank":"P6"}],"columns":[{"title":"ID","dataIndex":"id","key":"id"},{"title":"姓名","dataIndex":"name","key":"name"},{"title":"部门","dataIndex":"dept","key":"dept"},{"title":"职位","dataIndex":"position","key":"position"},{"title":"手机号","dataIndex":"phone","key":"phone"},{"title":"邮箱","dataIndex":"email","key":"email"},{"title":"员工状态","dataIndex":"status","key":"status","renderType":"status","valueEnum":{"在职":"green"}},{"title":"入职日期","dataIndex":"joinDate","key":"joinDate"},{"title":"员工编号","dataIndex":"employeeId","key":"employeeId"},{"title":"直属上级","dataIndex":"supervisor","key":"supervisor"},{"title":"职级","dataIndex":"rank","key":"rank"},{"title":"操作","key":"action","renderType":"action","actions":[{"label":"详情","type":"link","interactions":[{"trigger":"click","action":"SET_VISIBLE","target":"modal_member_detail","payload":true}]}]}],"style":{"height":"100%"}},"parentKey":"node_84"},"node_84":{"key":"node_84","type":"div","props":{"style":{"position":"relative","flex":1,"minHeight":0}},"children":["node_85"],"parentKey":"node_19"},"node_19":{"key":"node_19","type":"Flex","props":{"vertical":true,"gap":16,"style":{"flex":1,"minHeight":0,"overflow":"hidden"}},"children":["node_20","node_66","node_67","node_84"],"parentKey":"node_9"},"node_9":{"key":"node_9","type":"Flex","props":{"gap":16,"style":{"height":"100%","minHeight":0,"overflow":"hidden"}},"children":["node_10","node_18","node_19"],"parentKey":"node_8"},"node_8":{"key":"node_8","type":"div","props":{"style":{"backgroundColor":"#fff","padding":"16px","borderRadius":"8px","height":"100%","boxSizing":"border-box","minHeight":0,"overflow":"hidden"}},"children":["node_9"],"parentKey":"node_7"},"node_7":{"key":"node_7","type":"Content","props":{"style":{"padding":"16px","backgroundColor":"#F2F4F6","minHeight":0,"overflow":"hidden"}},"children":["node_8"],"parentKey":"node_4"},"node_4":{"key":"node_4","type":"Layout","props":{"style":{"flexDirection":"row","flex":1,"minHeight":0,"overflow":"hidden"}},"children":["node_5","node_7"],"parentKey":"node_1"},"node_1":{"key":"node_1","type":"Layout","props":{"style":{"height":"100%","minHeight":0,"overflow":"hidden"}},"children":["node_2","node_4"],"parentKey":"node_0"},"node_90":{"key":"node_90","type":"span","props":{"children":"姓名"},"parentKey":"node_89"},"node_89":{"key":"node_89","type":"Typography.Text","props":{"style":{"width":"68px","textAlign":"right","marginRight":"8px"}},"children":["node_90"],"parentKey":"node_88"},"node_91":{"key":"node_91","type":"Input","props":{"placeholder":"请输入姓名","style":{"flex":1}},"parentKey":"node_88"},"node_88":{"key":"node_88","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_89","node_91"],"parentKey":"node_87"},"node_94":{"key":"node_94","type":"span","props":{"children":"手机号"},"parentKey":"node_93"},"node_93":{"key":"node_93","type":"Typography.Text","props":{"style":{"width":"68px","textAlign":"right","marginRight":"8px"}},"children":["node_94"],"parentKey":"node_92"},"node_95":{"key":"node_95","type":"Input","props":{"placeholder":"请输入手机号","style":{"flex":1}},"parentKey":"node_92"},"node_92":{"key":"node_92","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_93","node_95"],"parentKey":"node_87"},"node_98":{"key":"node_98","type":"span","props":{"children":"部门"},"parentKey":"node_97"},"node_97":{"key":"node_97","type":"Typography.Text","props":{"style":{"width":"68px","textAlign":"right","marginRight":"8px"}},"children":["node_98"],"parentKey":"node_96"},"node_99":{"key":"node_99","type":"Select","props":{"placeholder":"请选择部门","style":{"flex":1},"options":[{"label":"研发中心","value":"rd"},{"label":"产品中心","value":"pd"},{"label":"运营中心","value":"op"}]},"parentKey":"node_96"},"node_96":{"key":"node_96","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_97","node_99"],"parentKey":"node_87"},"node_102":{"key":"node_102","type":"span","props":{"children":"职位"},"parentKey":"node_101"},"node_101":{"key":"node_101","type":"Typography.Text","props":{"style":{"width":"68px","textAlign":"right","marginRight":"8px"}},"children":["node_102"],"parentKey":"node_100"},"node_103":{"key":"node_103","type":"Input","props":{"placeholder":"请输入职位","style":{"flex":1}},"parentKey":"node_100"},"node_100":{"key":"node_100","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_101","node_103"],"parentKey":"node_87"},"node_106":{"key":"node_106","type":"span","props":{"children":"备注"},"parentKey":"node_105"},"node_105":{"key":"node_105","type":"Typography.Text","props":{"style":{"width":"68px","textAlign":"right","marginRight":"8px","lineHeight":"32px"}},"children":["node_106"],"parentKey":"node_104"},"node_107":{"key":"node_107","type":"TextArea","props":{"placeholder":"请输入备注信息","rows":4,"style":{"flex":1}},"parentKey":"node_104"},"node_104":{"key":"node_104","type":"div","props":{"style":{"display":"flex","alignItems":"flex-start"}},"children":["node_105","node_107"],"parentKey":"node_87"},"node_87":{"key":"node_87","type":"Flex","props":{"vertical":true,"gap":16},"children":["node_88","node_92","node_96","node_100","node_104"],"parentKey":"node_86"},"node_86":{"key":"node_86","type":"Modal","props":{"id":"modal_invite_by_phone","title":"新增人员","open":false,"footer":[{"type":"Flex","props":{"justify":"flex-end","gap":8},"children":[{"type":"Button","props":{"type":"default","children":"取消","interactions":[{"trigger":"click","action":"SET_VISIBLE","target":"modal_invite_by_phone","payload":false}]},"children":[]},{"type":"Button","props":{"type":"primary","children":"保存","interactions":[{"trigger":"click","action":"SET_VISIBLE","target":"modal_invite_by_phone","payload":false}]},"children":[]}]}],"dividers":false,"style":{},"width":480},"children":["node_87"],"parentKey":"node_0"},"node_111":{"key":"node_111","type":"span","props":{"children":"将文件拖到此处，或点击上传"},"parentKey":"node_110"},"node_110":{"key":"node_110","type":"Typography.Text","props":{},"children":["node_111"],"parentKey":"node_109"},"node_114":{"key":"node_114","type":"span","props":{"children":"支持扩展名：.xls .xlsx"},"parentKey":"node_113"},"node_113":{"key":"node_113","type":"Typography.Text","props":{"type":"secondary"},"children":["node_114"],"parentKey":"node_112"},"node_112":{"key":"node_112","type":"div","props":{"style":{"marginTop":"8px"}},"children":["node_113"],"parentKey":"node_109"},"node_109":{"key":"node_109","type":"div","props":{"style":{"border":"2px dashed #d9d9d9","borderRadius":"8px","padding":"40px 20px","textAlign":"center","backgroundColor":"#fafafa"}},"children":["node_110","node_112"],"parentKey":"node_108"},"node_108":{"key":"node_108","type":"Modal","props":{"id":"modal_import_member","title":"导入成员","open":false,"footer":[{"type":"Flex","props":{"justify":"flex-end","gap":8},"children":[{"type":"Button","props":{"type":"default","children":"取消","interactions":[{"trigger":"click","action":"SET_VISIBLE","target":"modal_import_member","payload":false}]},"children":[]},{"type":"Button","props":{"type":"primary","children":"保存","interactions":[{"trigger":"click","action":"SET_VISIBLE","target":"modal_import_member","payload":false}]},"children":[]}]}],"dividers":false},"children":["node_109"],"parentKey":"node_0"},"node_116":{"key":"node_116","type":"Tree","props":{"treeData":[{"title":"XX科技集团","key":"root","children":[{"title":"研发中心","key":"rd","children":[{"title":"前端部","key":"rd-fe"},{"title":"后端部","key":"rd-be"},{"title":"测试部","key":"rd-qa"}]},{"title":"产品中心","key":"pd"}]}],"checkable":true,"defaultExpandAll":true,"style":{"maxHeight":"300px","overflowY":"auto"}},"parentKey":"node_115"},"node_115":{"key":"node_115","type":"Modal","props":{"id":"modal_export_member","title":"导出成员","open":false,"footer":[{"type":"Flex","props":{"justify":"flex-end","gap":8},"children":[{"type":"Button","props":{"type":"default","children":"取消","interactions":[{"trigger":"click","action":"SET_VISIBLE","target":"modal_export_member","payload":false}]},"children":[]},{"type":"Button","props":{"type":"primary","children":"保存","interactions":[{"trigger":"click","action":"SET_VISIBLE","target":"modal_export_member","payload":false}]},"children":[]}]}],"dividers":false},"children":["node_116"],"parentKey":"node_0"},"node_122":{"key":"node_122","type":"span","props":{"children":"姓名"},"parentKey":"node_121"},"node_121":{"key":"node_121","type":"Typography.Text","props":{"style":{"width":"80px","color":"rgba(0,0,0,0.45)"}},"children":["node_122"],"parentKey":"node_120"},"node_124":{"key":"node_124","type":"span","props":{"children":"张三"},"parentKey":"node_123"},"node_123":{"key":"node_123","type":"Typography.Text","props":{},"children":["node_124"],"parentKey":"node_120"},"node_120":{"key":"node_120","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_121","node_123"],"parentKey":"node_119"},"node_127":{"key":"node_127","type":"span","props":{"children":"性别"},"parentKey":"node_126"},"node_126":{"key":"node_126","type":"Typography.Text","props":{"style":{"width":"80px","color":"rgba(0,0,0,0.45)"}},"children":["node_127"],"parentKey":"node_125"},"node_129":{"key":"node_129","type":"span","props":{"children":"男"},"parentKey":"node_128"},"node_128":{"key":"node_128","type":"Typography.Text","props":{},"children":["node_129"],"parentKey":"node_125"},"node_125":{"key":"node_125","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_126","node_128"],"parentKey":"node_119"},"node_132":{"key":"node_132","type":"span","props":{"children":"年龄"},"parentKey":"node_131"},"node_131":{"key":"node_131","type":"Typography.Text","props":{"style":{"width":"80px","color":"rgba(0,0,0,0.45)"}},"children":["node_132"],"parentKey":"node_130"},"node_134":{"key":"node_134","type":"span","props":{"children":"28"},"parentKey":"node_133"},"node_133":{"key":"node_133","type":"Typography.Text","props":{},"children":["node_134"],"parentKey":"node_130"},"node_130":{"key":"node_130","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_131","node_133"],"parentKey":"node_119"},"node_137":{"key":"node_137","type":"span","props":{"children":"手机号"},"parentKey":"node_136"},"node_136":{"key":"node_136","type":"Typography.Text","props":{"style":{"width":"80px","color":"rgba(0,0,0,0.45)"}},"children":["node_137"],"parentKey":"node_135"},"node_139":{"key":"node_139","type":"span","props":{"children":"13800138001"},"parentKey":"node_138"},"node_138":{"key":"node_138","type":"Typography.Text","props":{},"children":["node_139"],"parentKey":"node_135"},"node_135":{"key":"node_135","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_136","node_138"],"parentKey":"node_119"},"node_119":{"key":"node_119","type":"Flex","props":{"vertical":true,"gap":16,"style":{"flex":1}},"children":["node_120","node_125","node_130","node_135"],"parentKey":"node_118"},"node_143":{"key":"node_143","type":"span","props":{"children":"部门"},"parentKey":"node_142"},"node_142":{"key":"node_142","type":"Typography.Text","props":{"style":{"width":"80px","color":"rgba(0,0,0,0.45)"}},"children":["node_143"],"parentKey":"node_141"},"node_145":{"key":"node_145","type":"span","props":{"children":"研发中心/前端部"},"parentKey":"node_144"},"node_144":{"key":"node_144","type":"Typography.Text","props":{},"children":["node_145"],"parentKey":"node_141"},"node_141":{"key":"node_141","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_142","node_144"],"parentKey":"node_140"},"node_148":{"key":"node_148","type":"span","props":{"children":"职位"},"parentKey":"node_147"},"node_147":{"key":"node_147","type":"Typography.Text","props":{"style":{"width":"80px","color":"rgba(0,0,0,0.45)"}},"children":["node_148"],"parentKey":"node_146"},"node_150":{"key":"node_150","type":"span","props":{"children":"前端工程师"},"parentKey":"node_149"},"node_149":{"key":"node_149","type":"Typography.Text","props":{},"children":["node_150"],"parentKey":"node_146"},"node_146":{"key":"node_146","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_147","node_149"],"parentKey":"node_140"},"node_153":{"key":"node_153","type":"span","props":{"children":"员工编号"},"parentKey":"node_152"},"node_152":{"key":"node_152","type":"Typography.Text","props":{"style":{"width":"80px","color":"rgba(0,0,0,0.45)"}},"children":["node_153"],"parentKey":"node_151"},"node_155":{"key":"node_155","type":"span","props":{"children":"EMP1001"},"parentKey":"node_154"},"node_154":{"key":"node_154","type":"Typography.Text","props":{},"children":["node_155"],"parentKey":"node_151"},"node_151":{"key":"node_151","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_152","node_154"],"parentKey":"node_140"},"node_158":{"key":"node_158","type":"span","props":{"children":"入职日期"},"parentKey":"node_157"},"node_157":{"key":"node_157","type":"Typography.Text","props":{"style":{"width":"80px","color":"rgba(0,0,0,0.45)"}},"children":["node_158"],"parentKey":"node_156"},"node_160":{"key":"node_160","type":"span","props":{"children":"2021-03-15"},"parentKey":"node_159"},"node_159":{"key":"node_159","type":"Typography.Text","props":{},"children":["node_160"],"parentKey":"node_156"},"node_156":{"key":"node_156","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_157","node_159"],"parentKey":"node_140"},"node_140":{"key":"node_140","type":"Flex","props":{"vertical":true,"gap":16,"style":{"flex":1}},"children":["node_141","node_146","node_151","node_156"],"parentKey":"node_118"},"node_118":{"key":"node_118","type":"Flex","props":{"gap":24},"children":["node_119","node_140"],"parentKey":"node_117"},"node_117":{"key":"node_117","type":"Modal","props":{"id":"modal_member_detail","title":"人员详情","open":false,"footer":[{"type":"Flex","props":{"justify":"flex-end","gap":8},"children":[{"type":"Button","props":{"type":"default","children":"取消","interactions":[{"trigger":"click","action":"SET_VISIBLE","target":"modal_member_detail","payload":false}]},"children":[]},{"type":"Button","props":{"type":"primary","children":"保存","interactions":[{"trigger":"click","action":"SET_VISIBLE","target":"modal_member_detail","payload":false}]},"children":[]}]}],"dividers":false,"style":{},"width":640},"children":["node_118"],"parentKey":"node_0"},"node_165":{"key":"node_165","type":"span","props":{"children":"组织名称"},"parentKey":"node_164"},"node_164":{"key":"node_164","type":"Typography.Text","props":{"style":{"width":"68px","textAlign":"right","marginRight":"8px"}},"children":["node_165"],"parentKey":"node_163"},"node_166":{"key":"node_166","type":"Input","props":{"placeholder":"请输入组织名称","style":{"flex":1}},"parentKey":"node_163"},"node_163":{"key":"node_163","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_164","node_166"],"parentKey":"node_162"},"node_169":{"key":"node_169","type":"span","props":{"children":"组织编码"},"parentKey":"node_168"},"node_168":{"key":"node_168","type":"Typography.Text","props":{"style":{"width":"68px","textAlign":"right","marginRight":"8px"}},"children":["node_169"],"parentKey":"node_167"},"node_170":{"key":"node_170","type":"Input","props":{"placeholder":"请输入组织编码","style":{"flex":1}},"parentKey":"node_167"},"node_167":{"key":"node_167","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_168","node_170"],"parentKey":"node_162"},"node_173":{"key":"node_173","type":"span","props":{"children":"上级组织"},"parentKey":"node_172"},"node_172":{"key":"node_172","type":"Typography.Text","props":{"style":{"width":"68px","textAlign":"right","marginRight":"8px"}},"children":["node_173"],"parentKey":"node_171"},"node_174":{"key":"node_174","type":"Select","props":{"placeholder":"请选择上级组织","style":{"flex":1},"options":[{"label":"XX科技集团","value":"root"},{"label":"研发中心","value":"rd"},{"label":"产品中心","value":"pd"}]},"parentKey":"node_171"},"node_171":{"key":"node_171","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_172","node_174"],"parentKey":"node_162"},"node_177":{"key":"node_177","type":"span","props":{"children":"负责人"},"parentKey":"node_176"},"node_176":{"key":"node_176","type":"Typography.Text","props":{"style":{"width":"68px","textAlign":"right","marginRight":"8px"}},"children":["node_177"],"parentKey":"node_175"},"node_178":{"key":"node_178","type":"Input","props":{"placeholder":"请输入负责人","style":{"flex":1}},"parentKey":"node_175"},"node_175":{"key":"node_175","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_176","node_178"],"parentKey":"node_162"},"node_181":{"key":"node_181","type":"span","props":{"children":"描述"},"parentKey":"node_180"},"node_180":{"key":"node_180","type":"Typography.Text","props":{"style":{"width":"68px","textAlign":"right","marginRight":"8px","lineHeight":"32px"}},"children":["node_181"],"parentKey":"node_179"},"node_182":{"key":"node_182","type":"TextArea","props":{"placeholder":"请输入组织描述","rows":4,"style":{"flex":1}},"parentKey":"node_179"},"node_179":{"key":"node_179","type":"div","props":{"style":{"display":"flex","alignItems":"flex-start"}},"children":["node_180","node_182"],"parentKey":"node_162"},"node_162":{"key":"node_162","type":"Flex","props":{"vertical":true,"gap":16},"children":["node_163","node_167","node_171","node_175","node_179"],"parentKey":"node_161"},"node_161":{"key":"node_161","type":"Modal","props":{"id":"modal_create_org","title":"创建组织","open":false,"footer":[{"type":"Flex","props":{"justify":"flex-end","gap":8},"children":[{"type":"Button","props":{"type":"default","children":"取消","interactions":[{"trigger":"click","action":"SET_VISIBLE","target":"modal_create_org","payload":false}]},"children":[]},{"type":"Button","props":{"type":"primary","children":"保存","interactions":[{"trigger":"click","action":"SET_VISIBLE","target":"modal_create_org","payload":false}]},"children":[]}]}],"dividers":false,"style":{},"width":480},"children":["node_162"],"parentKey":"node_0"},"node_187":{"key":"node_187","type":"span","props":{"children":"组织名称"},"parentKey":"node_186"},"node_186":{"key":"node_186","type":"Typography.Text","props":{"style":{"width":"96px","color":"rgba(0,0,0,0.45)"}},"children":["node_187"],"parentKey":"node_185"},"node_189":{"key":"node_189","type":"span","props":{"children":"正大信息安全上海办事处"},"parentKey":"node_188"},"node_188":{"key":"node_188","type":"Typography.Text","props":{},"children":["node_189"],"parentKey":"node_185"},"node_185":{"key":"node_185","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_186","node_188"],"parentKey":"node_184"},"node_192":{"key":"node_192","type":"span","props":{"children":"组织编码"},"parentKey":"node_191"},"node_191":{"key":"node_191","type":"Typography.Text","props":{"style":{"width":"96px","color":"rgba(0,0,0,0.45)"}},"children":["node_192"],"parentKey":"node_190"},"node_194":{"key":"node_194","type":"span","props":{"children":"SH-ZD-002"},"parentKey":"node_193"},"node_193":{"key":"node_193","type":"Typography.Text","props":{},"children":["node_194"],"parentKey":"node_190"},"node_190":{"key":"node_190","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_191","node_193"],"parentKey":"node_184"},"node_197":{"key":"node_197","type":"span","props":{"children":"组织类型"},"parentKey":"node_196"},"node_196":{"key":"node_196","type":"Typography.Text","props":{"style":{"width":"96px","color":"rgba(0,0,0,0.45)"}},"children":["node_197"],"parentKey":"node_195"},"node_199":{"key":"node_199","type":"span","props":{"children":"二级组织"},"parentKey":"node_198"},"node_198":{"key":"node_198","type":"Typography.Text","props":{},"children":["node_199"],"parentKey":"node_195"},"node_195":{"key":"node_195","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_196","node_198"],"parentKey":"node_184"},"node_202":{"key":"node_202","type":"span","props":{"children":"组织负责人"},"parentKey":"node_201"},"node_201":{"key":"node_201","type":"Typography.Text","props":{"style":{"width":"96px","color":"rgba(0,0,0,0.45)"}},"children":["node_202"],"parentKey":"node_200"},"node_204":{"key":"node_204","type":"span","props":{"children":"邱云云"},"parentKey":"node_203"},"node_203":{"key":"node_203","type":"Typography.Text","props":{},"children":["node_204"],"parentKey":"node_200"},"node_200":{"key":"node_200","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_201","node_203"],"parentKey":"node_184"},"node_207":{"key":"node_207","type":"span","props":{"children":"审批主管"},"parentKey":"node_206"},"node_206":{"key":"node_206","type":"Typography.Text","props":{"style":{"width":"96px","color":"rgba(0,0,0,0.45)"}},"children":["node_207"],"parentKey":"node_205"},"node_209":{"key":"node_209","type":"span","props":{"children":"邱云"},"parentKey":"node_208"},"node_208":{"key":"node_208","type":"Typography.Text","props":{},"children":["node_209"],"parentKey":"node_205"},"node_205":{"key":"node_205","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_206","node_208"],"parentKey":"node_184"},"node_212":{"key":"node_212","type":"span","props":{"children":"成立时间"},"parentKey":"node_211"},"node_211":{"key":"node_211","type":"Typography.Text","props":{"style":{"width":"96px","color":"rgba(0,0,0,0.45)"}},"children":["node_212"],"parentKey":"node_210"},"node_214":{"key":"node_214","type":"span","props":{"children":"2021-04-18"},"parentKey":"node_213"},"node_213":{"key":"node_213","type":"Typography.Text","props":{},"children":["node_214"],"parentKey":"node_210"},"node_210":{"key":"node_210","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_211","node_213"],"parentKey":"node_184"},"node_217":{"key":"node_217","type":"span","props":{"children":"办公地点"},"parentKey":"node_216"},"node_216":{"key":"node_216","type":"Typography.Text","props":{"style":{"width":"96px","color":"rgba(0,0,0,0.45)"}},"children":["node_217"],"parentKey":"node_215"},"node_219":{"key":"node_219","type":"span","props":{"children":"上海市浦东新区"},"parentKey":"node_218"},"node_218":{"key":"node_218","type":"Typography.Text","props":{},"children":["node_219"],"parentKey":"node_215"},"node_215":{"key":"node_215","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_216","node_218"],"parentKey":"node_184"},"node_222":{"key":"node_222","type":"span","props":{"children":"编制人数"},"parentKey":"node_221"},"node_221":{"key":"node_221","type":"Typography.Text","props":{"style":{"width":"96px","color":"rgba(0,0,0,0.45)"}},"children":["node_222"],"parentKey":"node_220"},"node_224":{"key":"node_224","type":"span","props":{"children":"100"},"parentKey":"node_223"},"node_223":{"key":"node_223","type":"Typography.Text","props":{},"children":["node_224"],"parentKey":"node_220"},"node_220":{"key":"node_220","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_221","node_223"],"parentKey":"node_184"},"node_227":{"key":"node_227","type":"span","props":{"children":"在编人数"},"parentKey":"node_226"},"node_226":{"key":"node_226","type":"Typography.Text","props":{"style":{"width":"96px","color":"rgba(0,0,0,0.45)"}},"children":["node_227"],"parentKey":"node_225"},"node_229":{"key":"node_229","type":"span","props":{"children":"80"},"parentKey":"node_228"},"node_228":{"key":"node_228","type":"Typography.Text","props":{},"children":["node_229"],"parentKey":"node_225"},"node_225":{"key":"node_225","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_226","node_228"],"parentKey":"node_184"},"node_232":{"key":"node_232","type":"span","props":{"children":"下级组织数"},"parentKey":"node_231"},"node_231":{"key":"node_231","type":"Typography.Text","props":{"style":{"width":"96px","color":"rgba(0,0,0,0.45)"}},"children":["node_232"],"parentKey":"node_230"},"node_234":{"key":"node_234","type":"span","props":{"children":"8"},"parentKey":"node_233"},"node_233":{"key":"node_233","type":"Typography.Text","props":{},"children":["node_234"],"parentKey":"node_230"},"node_230":{"key":"node_230","type":"div","props":{"style":{"display":"flex","alignItems":"center"}},"children":["node_231","node_233"],"parentKey":"node_184"},"node_184":{"key":"node_184","type":"Flex","props":{"vertical":true,"gap":12},"children":["node_185","node_190","node_195","node_200","node_205","node_210","node_215","node_220","node_225","node_230"],"parentKey":"node_183"},"node_183":{"key":"node_183","type":"Modal","props":{"id":"modal_org_detail","title":"组织详情","open":false,"footer":[{"type":"Flex","props":{"justify":"flex-end","gap":8},"children":[{"type":"Button","props":{"type":"primary","children":"关闭","interactions":[{"trigger":"click","action":"SET_VISIBLE","target":"modal_org_detail","payload":false}]},"children":[]}]}],"dividers":false,"style":{},"width":640},"children":["node_184"],"parentKey":"node_0"},"node_0":{"key":"node_0","type":"div","props":{"style":{"width":"1920px","height":"1080px","minHeight":0,"overflow":"hidden"}},"children":["node_1","node_86","node_108","node_115","node_117","node_161","node_183"],"parentKey":null}}},"mode":"interactive","savedAt":1773279188824,"registry":{"XFTTopBar":{"html":"\u003cdiv style=\"height: 48px; width: 100%; background: #1966ff; display: flex; align-items: center; justify-content: space-between; padding-inline: 16px;\">\u003cdiv style=\"display: flex; align-items: center;\">\u003cdiv style=\"position: relative; width: 24px; height: 24px; border-radius: 4px; overflow: hidden;\">\u003cdiv style=\"position: absolute; inset: 0; background: #ffffff; opacity: 0.9; border-radius: 4px;\">\u003c/div>\u003cimg src=\"./branding/logo.png\" alt=\"\" style=\"position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; border-radius: 4px;\" onerror=\"this.style.display='none'\"/>\u003c/div>\u003cdiv style=\"color: #ffffff; font-size: 14px; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Microsoft YaHei', 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif; margin-left: 8px;\">某某企业\u003c/div>\u003cdiv style=\"color: #ffffff; font-size: 14px; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Microsoft YaHei', 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif; margin-left: 24px;\">工作台\u003c/div>\u003cdiv style=\"color: #ffffff; font-size: 14px; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Microsoft YaHei', 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif; margin-left: 24px;\">全部应用\u003c/div>\u003c/div>\u003cdiv style=\"display: flex; align-items: center; flex-direction: row-reverse; gap: 24px;\">\u003cdiv style=\"position: relative; width: 24px; height: 24px; border-radius: 4px; overflow: hidden;\">\u003cdiv style=\"position: absolute; inset: 0; background: #ffffff; opacity: 0.9; border-radius: 4px;\">\u003c/div>\u003cimg src=\"./branding/avatar.png\" alt=\"\" style=\"position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; border-radius: 4px;\" onerror=\"this.style.display='none'\"/>\u003c/div>\u003cdiv style=\"color: #ffffff; font-size: 14px; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Microsoft YaHei', 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif;\">某某员工\u003c/div>\u003cdiv style=\"color: #ffffff; font-size: 14px; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Microsoft YaHei', 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif;\">管理后台\u003c/div>\u003cdiv style=\"color: #ffffff; font-size: 14px; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Microsoft YaHei', 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif;\">工具箱\u003c/div>\u003cdiv style=\"color: #ffffff; font-size: 14px; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Microsoft YaHei', 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif;\">服务中心\u003c/div>\u003cinput placeholder=\"赶快使用 AI 体验搜索吧！\" style=\"width: 200px; height: 32px; border-radius: 6px; background: rgba(255,255,255,0.2); color: #ffffff; border: none; padding-left: 8px;\" />\u003c/div>\u003c/div>"}},"actionState":{"visibility":{"modal_invite_by_phone":false,"modal_import_member":false,"modal_export_member":false,"modal_member_detail":false,"modal_create_org":false,"modal_org_detail":false},"activeKeys":{}}};
  try {
    window[globalKey] = payload;
  } catch (error) {
  }

  try {
    if (!self.__next_r) {
      self.__next_r = "offline-export";
    }
  } catch (error) {
  }

  var normalizeUrl = function (input) {
    if (!input) return "";
    if (typeof input === "string") return input;
    if (typeof Request !== "undefined" && input instanceof Request) return input.url || "";
    if (typeof URL !== "undefined" && input instanceof URL) return input.toString();
    return "";
  };

  var isFileScheme = function (input) {
    try {
      var raw = normalizeUrl(input).trim();
      if (!raw) return false;
      if (/^file:/i.test(raw)) return true;
      var parsed = new URL(raw, window.location.href);
      return parsed.protocol === "file:";
    } catch (error) {
      return false;
    }
  };

  var patchWebSocketForFileScheme = function () {
    if (typeof window.WebSocket !== "function") return;
    var NativeWebSocket = window.WebSocket;
    var buildStubSocket = function (url) {
      var listeners = { open: [], message: [], error: [], close: [] };
      var socket = {
        url: normalizeUrl(url),
        readyState: 1,
        bufferedAmount: 0,
        binaryType: "blob",
        protocol: "",
        extensions: "",
        CONNECTING: 0,
        OPEN: 1,
        CLOSING: 2,
        CLOSED: 3,
        onopen: null,
        onmessage: null,
        onerror: null,
        onclose: null,
        addEventListener: function (type, listener) {
          if (!type || typeof listener !== "function") return;
          if (!listeners[type]) listeners[type] = [];
          listeners[type].push(listener);
        },
        removeEventListener: function (type, listener) {
          var list = listeners[type];
          if (!list || !list.length) return;
          listeners[type] = list.filter(function (item) {
            return item !== listener;
          });
        },
        dispatchEvent: function (event) {
          var eventType = event && event.type ? event.type : "";
          if (!eventType) return false;
          var list = listeners[eventType] || [];
          list.forEach(function (listener) {
            try {
              listener.call(socket, event);
            } catch (error) {
            }
          });
          return list.length > 0;
        },
        send: function () {},
        close: function () {
          socket.readyState = socket.CLOSED;
          var closeEvent = { type: "close", code: 1000, reason: "offline" };
          if (typeof socket.onclose === "function") {
            try {
              socket.onclose(closeEvent);
            } catch (error) {
            }
          }
          socket.dispatchEvent(closeEvent);
        },
      };
      setTimeout(function () {
        var openEvent = { type: "open" };
        if (typeof socket.onopen === "function") {
          try {
            socket.onopen(openEvent);
          } catch (error) {
          }
        }
        socket.dispatchEvent(openEvent);
      }, 0);
      return socket;
    };

    var OfflineWebSocket = function (url, protocols) {
      if (isFileScheme(url)) {
        return buildStubSocket(url);
      }
      if (arguments.length > 1) return new NativeWebSocket(url, protocols);
      return new NativeWebSocket(url);
    };

    try {
      OfflineWebSocket.prototype = NativeWebSocket.prototype;
      OfflineWebSocket.CONNECTING = NativeWebSocket.CONNECTING ?? 0;
      OfflineWebSocket.OPEN = NativeWebSocket.OPEN ?? 1;
      OfflineWebSocket.CLOSING = NativeWebSocket.CLOSING ?? 2;
      OfflineWebSocket.CLOSED = NativeWebSocket.CLOSED ?? 3;
    } catch (error) {
    }

    window.WebSocket = OfflineWebSocket;
  };

  patchWebSocketForFileScheme();

  var isApiUrl = function (input) {
    try {
      var raw = normalizeUrl(input).trim();
      if (!raw) return false;
      if (/^https?:\/\//i.test(raw)) {
        var parsed = new URL(raw, window.location.href);
        return parsed.pathname.indexOf("/api/") === 0;
      }
      return raw.indexOf("/api/") === 0 || raw.indexOf("./api/") === 0 || raw.indexOf("api/") === 0;
    } catch (error) {
      return false;
    }
  };

  var isStackFrameUrl = function (input) {
    try {
      var raw = normalizeUrl(input).trim();
      if (!raw) return false;
      if (/^https?:\/\//i.test(raw) || /^file:/i.test(raw) || raw.indexOf("/") === 0 || raw.indexOf(".") === 0) {
        var parsed = new URL(raw, window.location.href);
        return parsed.pathname.indexOf("__nextjs_original-stack-frames") >= 0;
      }
      return raw.indexOf("__nextjs_original-stack-frames") >= 0;
    } catch (error) {
      return false;
    }
  };

  var mockBody = JSON.stringify({
    offline: true,
    mocked: true,
    message: "offline-export-mock",
  });
  var mockStackFrameBody = JSON.stringify({
    originalStackFrame: null,
    originalCodeFrame: null,
  });

  if (typeof window.fetch === "function") {
    var nativeFetch = window.fetch.bind(window);
    window.fetch = function (input, init) {
      if (isStackFrameUrl(input)) {
        return Promise.resolve(
          new Response(mockStackFrameBody, {
            status: 200,
            headers: {
              "Content-Type": "application/json",
              "X-Offline-Mock": "1",
            },
          }),
        );
      }
      if (isApiUrl(input)) {
        return Promise.resolve(
          new Response(mockBody, {
            status: 200,
            headers: {
              "Content-Type": "application/json",
              "X-Offline-Mock": "1",
            },
          }),
        );
      }
      return nativeFetch(input, init).catch(function (error) {
        if (isStackFrameUrl(input)) {
          return new Response(mockStackFrameBody, {
            status: 200,
            headers: {
              "Content-Type": "application/json",
              "X-Offline-Mock": "1",
            },
          });
        }
        if (isApiUrl(input)) {
          return new Response(mockBody, {
            status: 200,
            headers: {
              "Content-Type": "application/json",
              "X-Offline-Mock": "1",
            },
          });
        }
        throw error;
      });
    };
  }

  if (window.XMLHttpRequest && window.XMLHttpRequest.prototype) {
    var nativeOpen = window.XMLHttpRequest.prototype.open;
    var nativeSend = window.XMLHttpRequest.prototype.send;
    window.XMLHttpRequest.prototype.open = function (method, url) {
      try {
        this.__offlineApiMock = isApiUrl(url);
        this.__offlineStackFrameMock = isStackFrameUrl(url);
      } catch (error) {
        this.__offlineApiMock = false;
        this.__offlineStackFrameMock = false;
      }
      return nativeOpen.apply(this, arguments);
    };
    window.XMLHttpRequest.prototype.send = function () {
      if (this.__offlineStackFrameMock) {
        try {
          Object.defineProperty(this, "readyState", { configurable: true, value: 4 });
          Object.defineProperty(this, "status", { configurable: true, value: 200 });
          Object.defineProperty(this, "responseText", { configurable: true, value: mockStackFrameBody });
          Object.defineProperty(this, "response", { configurable: true, value: mockStackFrameBody });
        } catch (error) {
        }
        if (typeof this.onreadystatechange === "function") this.onreadystatechange();
        if (typeof this.onload === "function") this.onload();
        return;
      }
      if (this.__offlineApiMock) {
        try {
          Object.defineProperty(this, "readyState", { configurable: true, value: 4 });
          Object.defineProperty(this, "status", { configurable: true, value: 200 });
          Object.defineProperty(this, "responseText", { configurable: true, value: mockBody });
          Object.defineProperty(this, "response", { configurable: true, value: mockBody });
        } catch (error) {
        }
        if (typeof this.onreadystatechange === "function") this.onreadystatechange();
        if (typeof this.onload === "function") this.onload();
        return;
      }
      return nativeSend.apply(this, arguments);
    };
  }

  var isRoutableHref = function (href) {
    if (!href) return false;
    if (/^(?:https?:|mailto:|tel:|javascript:|data:|blob:|#)/i.test(href)) return false;
    return true;
  };

  var toHashHref = function (href) {
    var normalized = href.trim();
    if (normalized.indexOf("./") === 0) {
      normalized = normalized.slice(1);
    }
    if (normalized.charAt(0) !== "/") {
      normalized = "/" + normalized.replace(/^\/+/, "");
    }
    return "#" + normalized;
  };

  var rewriteAnchors = function () {
    var anchors = document.querySelectorAll("a[href]");
    anchors.forEach(function (anchor) {
      var href = anchor.getAttribute("href") || "";
      if (!isRoutableHref(href)) return;
      anchor.setAttribute("href", toHashHref(href));
    });
  };

  document.addEventListener(
    "click",
    function (event) {
      var target = event.target;
      if (!target || !target.closest) return;
      var anchor = target.closest("a[href]");
      if (!anchor) return;
      var href = anchor.getAttribute("href") || "";
      if (!isRoutableHref(href)) return;
      event.preventDefault();
      window.location.hash = toHashHref(href);
    },
    true,
  );

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", rewriteAnchors);
  } else {
    rewriteAnchors();
  }
})();