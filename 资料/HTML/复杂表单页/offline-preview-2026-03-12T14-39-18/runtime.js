(function () {
  var globalKey = "__SAAS_OFFLINE_PAYLOAD__";
  var payload = {"tree":{"root":"node_0","elements":{"node_3":{"key":"node_3","type":"XFTTopBar","props":{},"parentKey":"node_2"},"node_2":{"key":"node_2","type":"Header","props":{"style":{"height":"48px"}},"children":["node_3"],"parentKey":"node_1"},"node_6":{"key":"node_6","type":"Menu","props":{"mode":"inline","theme":"light","defaultSelectedKeys":["1-1"],"items":[{"key":"1","label":"人员管理","icon":"UserOutlined","children":[{"key":"1-1","label":"成员管理"},{"key":"1-2","label":"组织管理"},{"key":"1-3","label":"岗位管理"}]},{"key":"2","label":"在职管理","icon":"TeamOutlined","children":[{"key":"2-1","label":"在职信息"},{"key":"2-2","label":"薪酬社保"}]},{"key":"3","label":"发展管理","icon":"AppstoreOutlined","children":[{"key":"3-1","label":"培训记录"},{"key":"3-2","label":"绩效考核"}]},{"key":"4","label":"扩展菜单1","children":[{"key":"4-1","label":"二级菜单1-1"},{"key":"4-2","label":"二级菜单1-2"}],"icon":"FileOutlined"},{"key":"5","label":"扩展菜单2","children":[{"key":"5-1","label":"二级菜单2-1"},{"key":"5-2","label":"二级菜单2-2"}],"icon":"SafetyCertificateOutlined"},{"key":"6","label":"扩展菜单3","children":[{"key":"6-1","label":"二级菜单3-1"},{"key":"6-2","label":"二级菜单3-2"}],"icon":"BarChartOutlined"},{"key":"7","label":"扩展菜单4","children":[{"key":"7-1","label":"二级菜单4-1"},{"key":"7-2","label":"二级菜单4-2"}],"icon":"PieChartOutlined"},{"key":"8","label":"扩展菜单5","children":[{"key":"8-1","label":"二级菜单5-1"},{"key":"8-2","label":"二级菜单5-2"}],"icon":"MailOutlined"},{"key":"9","label":"扩展菜单6","children":[{"key":"9-1","label":"二级菜单6-1"},{"key":"9-2","label":"二级菜单6-2"}],"icon":"BellOutlined"}]},"parentKey":"node_5"},"node_5":{"key":"node_5","type":"Sider","props":{"theme":"light","style":{"backgroundColor":"#ffffff","height":"100%","minHeight":0,"overflowY":"auto","overflowX":"hidden","width":"188px"}},"children":["node_6"],"parentKey":"node_4"},"node_11":{"key":"node_11","type":"Anchor","props":{"affix":false,"containerId":"employee-form-scroll","targetOffset":12,"items":[{"key":"section_basic","href":"#section_basic","title":"基本信息"},{"key":"section_job","href":"#section_job","title":"在职信息"},{"key":"section_salary","href":"#section_salary","title":"工资社保"},{"key":"section_personal","href":"#section_personal","title":"个人信息"},{"key":"section_emergency","href":"#section_emergency","title":"紧急联系人"},{"key":"section_education","href":"#section_education","title":"教育经历"},{"key":"section_work","href":"#section_work","title":"工作经历"},{"key":"section_family","href":"#section_family","title":"家庭成员"},{"key":"section_cert","href":"#section_cert","title":"专业证书"},{"key":"section_reward","href":"#section_reward","title":"奖惩记录"},{"key":"section_title","href":"#section_title","title":"职称"},{"key":"section_training","href":"#section_training","title":"培训记录"},{"key":"section_perf","href":"#section_perf","title":"绩效考核"},{"key":"section_material","href":"#section_material","title":"个人材料"}]},"parentKey":"node_10"},"node_10":{"key":"node_10","type":"div","props":{"style":{"width":"220px","minWidth":"220px","maxWidth":"220px","height":"100%","overflow":"hidden","borderRight":"1px solid #f0f0f0","paddingRight":"12px"}},"children":["node_11"],"parentKey":"node_9"},"node_16":{"key":"node_16","type":"span","props":{"children":"基本信息"},"parentKey":"node_15"},"node_15":{"key":"node_15","type":"Typography.Title","props":{"level":4,"style":{"marginBottom":"12px","borderLeft":"3px solid #1677ff","paddingLeft":"8px"}},"children":["node_16"],"parentKey":"node_14"},"node_20":{"key":"node_20","type":"Input","props":{"placeholder":"系统自动生成"},"parentKey":"node_19"},"node_19":{"key":"node_19","type":"Form.Item","props":{"label":"员工号","name":"employeeNo","style":{"marginBottom":"12px"}},"children":["node_20"],"parentKey":"node_18"},"node_18":{"key":"node_18","type":"Col","props":{"span":12},"children":["node_19"],"parentKey":"node_17"},"node_23":{"key":"node_23","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_22"},"node_22":{"key":"node_22","type":"Form.Item","props":{"label":"* 手机号","name":"mobile","style":{"marginBottom":"12px"}},"children":["node_23"],"parentKey":"node_21"},"node_21":{"key":"node_21","type":"Col","props":{"span":12},"children":["node_22"],"parentKey":"node_17"},"node_17":{"key":"node_17","type":"Row","props":{"gutter":[16,0]},"children":["node_18","node_21"],"parentKey":"node_14"},"node_27":{"key":"node_27","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_26"},"node_26":{"key":"node_26","type":"Form.Item","props":{"label":"* 姓名","name":"name","style":{"marginBottom":"12px"}},"children":["node_27"],"parentKey":"node_25"},"node_25":{"key":"node_25","type":"Col","props":{"span":12},"children":["node_26"],"parentKey":"node_24"},"node_30":{"key":"node_30","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_29"},"node_29":{"key":"node_29","type":"Form.Item","props":{"label":"别名","name":"nickname","style":{"marginBottom":"12px"}},"children":["node_30"],"parentKey":"node_28"},"node_28":{"key":"node_28","type":"Col","props":{"span":12},"children":["node_29"],"parentKey":"node_24"},"node_24":{"key":"node_24","type":"Row","props":{"gutter":[16,0]},"children":["node_25","node_28"],"parentKey":"node_14"},"node_34":{"key":"node_34","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_33"},"node_33":{"key":"node_33","type":"Form.Item","props":{"label":"曾用名","name":"oldName","style":{"marginBottom":"12px"}},"children":["node_34"],"parentKey":"node_32"},"node_32":{"key":"node_32","type":"Col","props":{"span":12},"children":["node_33"],"parentKey":"node_31"},"node_37":{"key":"node_37","type":"Input","props":{"placeholder":"请选择"},"parentKey":"node_36"},"node_36":{"key":"node_36","type":"Form.Item","props":{"label":"* 部门","name":"secondDept","style":{"marginBottom":"12px"}},"children":["node_37"],"parentKey":"node_35"},"node_35":{"key":"node_35","type":"Col","props":{"span":12},"children":["node_36"],"parentKey":"node_31"},"node_31":{"key":"node_31","type":"Row","props":{"gutter":[16,0]},"children":["node_32","node_35"],"parentKey":"node_14"},"node_41":{"key":"node_41","type":"Input","props":{"placeholder":"请选择"},"parentKey":"node_40"},"node_40":{"key":"node_40","type":"Form.Item","props":{"label":"职位","name":"jobTitle","style":{"marginBottom":"12px"}},"children":["node_41"],"parentKey":"node_39"},"node_39":{"key":"node_39","type":"Col","props":{"span":12},"children":["node_40"],"parentKey":"node_38"},"node_44":{"key":"node_44","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_43"},"node_43":{"key":"node_43","type":"Form.Item","props":{"label":"工作邮箱","name":"workEmail","style":{"marginBottom":"12px"}},"children":["node_44"],"parentKey":"node_42"},"node_42":{"key":"node_42","type":"Col","props":{"span":12},"children":["node_43"],"parentKey":"node_38"},"node_38":{"key":"node_38","type":"Row","props":{"gutter":[16,0]},"children":["node_39","node_42"],"parentKey":"node_14"},"node_48":{"key":"node_48","type":"Input","props":{"placeholder":"请选择"},"parentKey":"node_47"},"node_47":{"key":"node_47","type":"Form.Item","props":{"label":"兼职","name":"partTimeRole","style":{"marginBottom":"12px"}},"children":["node_48"],"parentKey":"node_46"},"node_46":{"key":"node_46","type":"Col","props":{"span":12},"children":["node_47"],"parentKey":"node_45"},"node_51":{"key":"node_51","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_50"},"node_50":{"key":"node_50","type":"Form.Item","props":{"label":"汇报上级","name":"landline","style":{"marginBottom":"12px"}},"children":["node_51"],"parentKey":"node_49"},"node_49":{"key":"node_49","type":"Col","props":{"span":12},"children":["node_50"],"parentKey":"node_45"},"node_45":{"key":"node_45","type":"Row","props":{"gutter":[16,0]},"children":["node_46","node_49"],"parentKey":"node_14"},"node_14":{"key":"node_14","type":"div","props":{"id":"section_basic","style":{"marginBottom":"28px","paddingTop":"2px"}},"children":["node_15","node_17","node_24","node_31","node_38","node_45"],"parentKey":"node_13"},"node_54":{"key":"node_54","type":"span","props":{"children":"在职信息"},"parentKey":"node_53"},"node_53":{"key":"node_53","type":"Typography.Title","props":{"level":4,"style":{"marginBottom":"12px","borderLeft":"3px solid #1677ff","paddingLeft":"8px"}},"children":["node_54"],"parentKey":"node_52"},"node_58":{"key":"node_58","type":"Select","props":{"placeholder":"请选择","options":[{"label":"选项1","value":"rd"},{"label":"选项2","value":"pd"},{"label":"选项3","value":"op"}]},"parentKey":"node_57"},"node_57":{"key":"node_57","type":"Form.Item","props":{"label":"在职信息字段1","name":"department","style":{"marginBottom":"12px"}},"children":["node_58"],"parentKey":"node_56"},"node_56":{"key":"node_56","type":"Col","props":{"span":12},"children":["node_57"],"parentKey":"node_55"},"node_61":{"key":"node_61","type":"Select","props":{"placeholder":"请选择","options":[{"label":"选项4","value":"fe"},{"label":"选项5","value":"be"},{"label":"选项6","value":"pm"}]},"parentKey":"node_60"},"node_60":{"key":"node_60","type":"Form.Item","props":{"label":"在职信息字段2","name":"position","style":{"marginBottom":"12px"}},"children":["node_61"],"parentKey":"node_59"},"node_59":{"key":"node_59","type":"Col","props":{"span":12},"children":["node_60"],"parentKey":"node_55"},"node_55":{"key":"node_55","type":"Row","props":{"gutter":[16,0]},"children":["node_56","node_59"],"parentKey":"node_52"},"node_65":{"key":"node_65","type":"Select","props":{"placeholder":"请选择","options":[{"label":"P5","value":"P5"},{"label":"P6","value":"P6"},{"label":"P7","value":"P7"}]},"parentKey":"node_64"},"node_64":{"key":"node_64","type":"Form.Item","props":{"label":"在职信息字段3","name":"rank","style":{"marginBottom":"12px"}},"children":["node_65"],"parentKey":"node_63"},"node_63":{"key":"node_63","type":"Col","props":{"span":12},"children":["node_64"],"parentKey":"node_62"},"node_68":{"key":"node_68","type":"Select","props":{"placeholder":"请选择","options":[{"label":"选项7","value":"platform"},{"label":"选项8","value":"business"}]},"parentKey":"node_67"},"node_67":{"key":"node_67","type":"Form.Item","props":{"label":"在职信息字段4","name":"bizGroup","style":{"marginBottom":"12px"}},"children":["node_68"],"parentKey":"node_66"},"node_66":{"key":"node_66","type":"Col","props":{"span":12},"children":["node_67"],"parentKey":"node_62"},"node_62":{"key":"node_62","type":"Row","props":{"gutter":[16,0]},"children":["node_63","node_66"],"parentKey":"node_52"},"node_72":{"key":"node_72","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_71"},"node_71":{"key":"node_71","type":"Form.Item","props":{"label":"在职信息字段5","name":"leader","style":{"marginBottom":"12px"}},"children":["node_72"],"parentKey":"node_70"},"node_70":{"key":"node_70","type":"Col","props":{"span":12},"children":["node_71"],"parentKey":"node_69"},"node_75":{"key":"node_75","type":"Select","props":{"placeholder":"请选择","options":[{"label":"选项9","value":"sh"},{"label":"选项10","value":"bj"},{"label":"选项11","value":"sz"}]},"parentKey":"node_74"},"node_74":{"key":"node_74","type":"Form.Item","props":{"label":"在职信息字段6","name":"workLocation","style":{"marginBottom":"12px"}},"children":["node_75"],"parentKey":"node_73"},"node_73":{"key":"node_73","type":"Col","props":{"span":12},"children":["node_74"],"parentKey":"node_69"},"node_69":{"key":"node_69","type":"Row","props":{"gutter":[16,0]},"children":["node_70","node_73"],"parentKey":"node_52"},"node_79":{"key":"node_79","type":"DatePicker","props":{"style":{"width":"100%"}},"parentKey":"node_78"},"node_78":{"key":"node_78","type":"Form.Item","props":{"label":"在职信息字段7","name":"entryDate","style":{"marginBottom":"12px"}},"children":["node_79"],"parentKey":"node_77"},"node_77":{"key":"node_77","type":"Col","props":{"span":12},"children":["node_78"],"parentKey":"node_76"},"node_82":{"key":"node_82","type":"DatePicker","props":{"style":{"width":"100%"}},"parentKey":"node_81"},"node_81":{"key":"node_81","type":"Form.Item","props":{"label":"在职信息字段8","name":"regularDate","style":{"marginBottom":"12px"}},"children":["node_82"],"parentKey":"node_80"},"node_80":{"key":"node_80","type":"Col","props":{"span":12},"children":["node_81"],"parentKey":"node_76"},"node_76":{"key":"node_76","type":"Row","props":{"gutter":[16,0]},"children":["node_77","node_80"],"parentKey":"node_52"},"node_86":{"key":"node_86","type":"DatePicker","props":{"style":{"width":"100%"}},"parentKey":"node_85"},"node_85":{"key":"node_85","type":"Form.Item","props":{"label":"在职信息字段9","name":"contractEndDate","style":{"marginBottom":"12px"}},"children":["node_86"],"parentKey":"node_84"},"node_84":{"key":"node_84","type":"Col","props":{"span":12},"children":["node_85"],"parentKey":"node_83"},"node_83":{"key":"node_83","type":"Row","props":{"gutter":[16,0]},"children":["node_84"],"parentKey":"node_52"},"node_52":{"key":"node_52","type":"div","props":{"id":"section_job","style":{"marginBottom":"28px","paddingTop":"2px"}},"children":["node_53","node_55","node_62","node_69","node_76","node_83"],"parentKey":"node_13"},"node_89":{"key":"node_89","type":"span","props":{"children":"工资社保"},"parentKey":"node_88"},"node_88":{"key":"node_88","type":"Typography.Title","props":{"level":4,"style":{"marginBottom":"12px","borderLeft":"3px solid #1677ff","paddingLeft":"8px"}},"children":["node_89"],"parentKey":"node_87"},"node_93":{"key":"node_93","type":"InputNumber","props":{"placeholder":"请输入","style":{"width":"100%"}},"parentKey":"node_92"},"node_92":{"key":"node_92","type":"Form.Item","props":{"label":"工资社保字段1","name":"baseSalary","style":{"marginBottom":"12px"}},"children":["node_93"],"parentKey":"node_91"},"node_91":{"key":"node_91","type":"Col","props":{"span":12},"children":["node_92"],"parentKey":"node_90"},"node_96":{"key":"node_96","type":"InputNumber","props":{"placeholder":"请输入","style":{"width":"100%"}},"parentKey":"node_95"},"node_95":{"key":"node_95","type":"Form.Item","props":{"label":"工资社保字段2","name":"performanceSalary","style":{"marginBottom":"12px"}},"children":["node_96"],"parentKey":"node_94"},"node_94":{"key":"node_94","type":"Col","props":{"span":12},"children":["node_95"],"parentKey":"node_90"},"node_90":{"key":"node_90","type":"Row","props":{"gutter":[16,0]},"children":["node_91","node_94"],"parentKey":"node_87"},"node_100":{"key":"node_100","type":"Select","props":{"placeholder":"请选择","options":[{"label":"选项12","value":"sh"},{"label":"选项13","value":"bj"},{"label":"选项14","value":"sz"}]},"parentKey":"node_99"},"node_99":{"key":"node_99","type":"Form.Item","props":{"label":"工资社保字段3","name":"socialCity","style":{"marginBottom":"12px"}},"children":["node_100"],"parentKey":"node_98"},"node_98":{"key":"node_98","type":"Col","props":{"span":12},"children":["node_99"],"parentKey":"node_97"},"node_103":{"key":"node_103","type":"InputNumber","props":{"placeholder":"请输入","style":{"width":"100%"}},"parentKey":"node_102"},"node_102":{"key":"node_102","type":"Form.Item","props":{"label":"工资社保字段4","name":"socialBase","style":{"marginBottom":"12px"}},"children":["node_103"],"parentKey":"node_101"},"node_101":{"key":"node_101","type":"Col","props":{"span":12},"children":["node_102"],"parentKey":"node_97"},"node_97":{"key":"node_97","type":"Row","props":{"gutter":[16,0]},"children":["node_98","node_101"],"parentKey":"node_87"},"node_107":{"key":"node_107","type":"InputNumber","props":{"placeholder":"请输入","style":{"width":"100%"}},"parentKey":"node_106"},"node_106":{"key":"node_106","type":"Form.Item","props":{"label":"工资社保字段5","name":"fundRate","style":{"marginBottom":"12px"}},"children":["node_107"],"parentKey":"node_105"},"node_105":{"key":"node_105","type":"Col","props":{"span":12},"children":["node_106"],"parentKey":"node_104"},"node_110":{"key":"node_110","type":"InputNumber","props":{"placeholder":"请输入","style":{"width":"100%"}},"parentKey":"node_109"},"node_109":{"key":"node_109","type":"Form.Item","props":{"label":"工资社保字段6","name":"taxDeduction","style":{"marginBottom":"12px"}},"children":["node_110"],"parentKey":"node_108"},"node_108":{"key":"node_108","type":"Col","props":{"span":12},"children":["node_109"],"parentKey":"node_104"},"node_104":{"key":"node_104","type":"Row","props":{"gutter":[16,0]},"children":["node_105","node_108"],"parentKey":"node_87"},"node_87":{"key":"node_87","type":"div","props":{"id":"section_salary","style":{"marginBottom":"28px","paddingTop":"2px"}},"children":["node_88","node_90","node_97","node_104"],"parentKey":"node_13"},"node_113":{"key":"node_113","type":"span","props":{"children":"个人信息"},"parentKey":"node_112"},"node_112":{"key":"node_112","type":"Typography.Title","props":{"level":4,"style":{"marginBottom":"12px","borderLeft":"3px solid #1677ff","paddingLeft":"8px"}},"children":["node_113"],"parentKey":"node_111"},"node_117":{"key":"node_117","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_116"},"node_116":{"key":"node_116","type":"Form.Item","props":{"label":"个人信息字段1","name":"idNo","style":{"marginBottom":"12px"}},"children":["node_117"],"parentKey":"node_115"},"node_115":{"key":"node_115","type":"Col","props":{"span":12},"children":["node_116"],"parentKey":"node_114"},"node_120":{"key":"node_120","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_119"},"node_119":{"key":"node_119","type":"Form.Item","props":{"label":"个人信息字段2","name":"email","style":{"marginBottom":"12px"}},"children":["node_120"],"parentKey":"node_118"},"node_118":{"key":"node_118","type":"Col","props":{"span":12},"children":["node_119"],"parentKey":"node_114"},"node_114":{"key":"node_114","type":"Row","props":{"gutter":[16,0]},"children":["node_115","node_118"],"parentKey":"node_111"},"node_124":{"key":"node_124","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_123"},"node_123":{"key":"node_123","type":"Form.Item","props":{"label":"个人信息字段3","name":"nation","style":{"marginBottom":"12px"}},"children":["node_124"],"parentKey":"node_122"},"node_122":{"key":"node_122","type":"Col","props":{"span":12},"children":["node_123"],"parentKey":"node_121"},"node_127":{"key":"node_127","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_126"},"node_126":{"key":"node_126","type":"Form.Item","props":{"label":"个人信息字段4","name":"hukouAddress","style":{"marginBottom":"12px"}},"children":["node_127"],"parentKey":"node_125"},"node_125":{"key":"node_125","type":"Col","props":{"span":12},"children":["node_126"],"parentKey":"node_121"},"node_121":{"key":"node_121","type":"Row","props":{"gutter":[16,0]},"children":["node_122","node_125"],"parentKey":"node_111"},"node_111":{"key":"node_111","type":"div","props":{"id":"section_personal","style":{"marginBottom":"28px","paddingTop":"2px"}},"children":["node_112","node_114","node_121"],"parentKey":"node_13"},"node_130":{"key":"node_130","type":"span","props":{"children":"紧急联系人"},"parentKey":"node_129"},"node_129":{"key":"node_129","type":"Typography.Title","props":{"level":4,"style":{"marginBottom":"12px","borderLeft":"3px solid #1677ff","paddingLeft":"8px"}},"children":["node_130"],"parentKey":"node_128"},"node_134":{"key":"node_134","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_133"},"node_133":{"key":"node_133","type":"Form.Item","props":{"label":"紧急联系人字段1","name":"emergencyName","style":{"marginBottom":"12px"}},"children":["node_134"],"parentKey":"node_132"},"node_132":{"key":"node_132","type":"Col","props":{"span":12},"children":["node_133"],"parentKey":"node_131"},"node_137":{"key":"node_137","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_136"},"node_136":{"key":"node_136","type":"Form.Item","props":{"label":"紧急联系人字段2","name":"emergencyPhone","style":{"marginBottom":"12px"}},"children":["node_137"],"parentKey":"node_135"},"node_135":{"key":"node_135","type":"Col","props":{"span":12},"children":["node_136"],"parentKey":"node_131"},"node_131":{"key":"node_131","type":"Row","props":{"gutter":[16,0]},"children":["node_132","node_135"],"parentKey":"node_128"},"node_141":{"key":"node_141","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_140"},"node_140":{"key":"node_140","type":"Form.Item","props":{"label":"紧急联系人字段3","name":"emergencyRelation","style":{"marginBottom":"12px"}},"children":["node_141"],"parentKey":"node_139"},"node_139":{"key":"node_139","type":"Col","props":{"span":12},"children":["node_140"],"parentKey":"node_138"},"node_144":{"key":"node_144","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_143"},"node_143":{"key":"node_143","type":"Form.Item","props":{"label":"紧急联系人字段4","name":"emergencyAddress","style":{"marginBottom":"12px"}},"children":["node_144"],"parentKey":"node_142"},"node_142":{"key":"node_142","type":"Col","props":{"span":12},"children":["node_143"],"parentKey":"node_138"},"node_138":{"key":"node_138","type":"Row","props":{"gutter":[16,0]},"children":["node_139","node_142"],"parentKey":"node_128"},"node_128":{"key":"node_128","type":"div","props":{"id":"section_emergency","style":{"marginBottom":"28px","paddingTop":"2px"}},"children":["node_129","node_131","node_138"],"parentKey":"node_13"},"node_147":{"key":"node_147","type":"span","props":{"children":"教育经历"},"parentKey":"node_146"},"node_146":{"key":"node_146","type":"Typography.Title","props":{"level":4,"style":{"marginBottom":"12px","borderLeft":"3px solid #1677ff","paddingLeft":"8px"}},"children":["node_147"],"parentKey":"node_145"},"node_151":{"key":"node_151","type":"Select","props":{"placeholder":"请选择","options":[{"label":"选项15","value":"bachelor"},{"label":"选项16","value":"master"},{"label":"选项17","value":"doctor"}]},"parentKey":"node_150"},"node_150":{"key":"node_150","type":"Form.Item","props":{"label":"教育经历字段1","name":"degree","style":{"marginBottom":"12px"}},"children":["node_151"],"parentKey":"node_149"},"node_149":{"key":"node_149","type":"Col","props":{"span":12},"children":["node_150"],"parentKey":"node_148"},"node_154":{"key":"node_154","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_153"},"node_153":{"key":"node_153","type":"Form.Item","props":{"label":"教育经历字段2","name":"school","style":{"marginBottom":"12px"}},"children":["node_154"],"parentKey":"node_152"},"node_152":{"key":"node_152","type":"Col","props":{"span":12},"children":["node_153"],"parentKey":"node_148"},"node_148":{"key":"node_148","type":"Row","props":{"gutter":[16,0]},"children":["node_149","node_152"],"parentKey":"node_145"},"node_158":{"key":"node_158","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_157"},"node_157":{"key":"node_157","type":"Form.Item","props":{"label":"教育经历字段3","name":"major","style":{"marginBottom":"12px"}},"children":["node_158"],"parentKey":"node_156"},"node_156":{"key":"node_156","type":"Col","props":{"span":12},"children":["node_157"],"parentKey":"node_155"},"node_161":{"key":"node_161","type":"DatePicker","props":{"style":{"width":"100%"}},"parentKey":"node_160"},"node_160":{"key":"node_160","type":"Form.Item","props":{"label":"教育经历字段4","name":"graduationDate","style":{"marginBottom":"12px"}},"children":["node_161"],"parentKey":"node_159"},"node_159":{"key":"node_159","type":"Col","props":{"span":12},"children":["node_160"],"parentKey":"node_155"},"node_155":{"key":"node_155","type":"Row","props":{"gutter":[16,0]},"children":["node_156","node_159"],"parentKey":"node_145"},"node_145":{"key":"node_145","type":"div","props":{"id":"section_education","style":{"marginBottom":"28px","paddingTop":"2px"}},"children":["node_146","node_148","node_155"],"parentKey":"node_13"},"node_164":{"key":"node_164","type":"span","props":{"children":"工作经历"},"parentKey":"node_163"},"node_163":{"key":"node_163","type":"Typography.Title","props":{"level":4,"style":{"marginBottom":"12px","borderLeft":"3px solid #1677ff","paddingLeft":"8px"}},"children":["node_164"],"parentKey":"node_162"},"node_168":{"key":"node_168","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_167"},"node_167":{"key":"node_167","type":"Form.Item","props":{"label":"工作经历字段1","name":"lastCompany","style":{"marginBottom":"12px"}},"children":["node_168"],"parentKey":"node_166"},"node_166":{"key":"node_166","type":"Col","props":{"span":12},"children":["node_167"],"parentKey":"node_165"},"node_171":{"key":"node_171","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_170"},"node_170":{"key":"node_170","type":"Form.Item","props":{"label":"工作经历字段2","name":"lastPosition","style":{"marginBottom":"12px"}},"children":["node_171"],"parentKey":"node_169"},"node_169":{"key":"node_169","type":"Col","props":{"span":12},"children":["node_170"],"parentKey":"node_165"},"node_165":{"key":"node_165","type":"Row","props":{"gutter":[16,0]},"children":["node_166","node_169"],"parentKey":"node_162"},"node_175":{"key":"node_175","type":"DatePicker","props":{"style":{"width":"100%"}},"parentKey":"node_174"},"node_174":{"key":"node_174","type":"Form.Item","props":{"label":"工作经历字段3","name":"lastEntryDate","style":{"marginBottom":"12px"}},"children":["node_175"],"parentKey":"node_173"},"node_173":{"key":"node_173","type":"Col","props":{"span":12},"children":["node_174"],"parentKey":"node_172"},"node_178":{"key":"node_178","type":"DatePicker","props":{"style":{"width":"100%"}},"parentKey":"node_177"},"node_177":{"key":"node_177","type":"Form.Item","props":{"label":"工作经历字段4","name":"lastLeaveDate","style":{"marginBottom":"12px"}},"children":["node_178"],"parentKey":"node_176"},"node_176":{"key":"node_176","type":"Col","props":{"span":12},"children":["node_177"],"parentKey":"node_172"},"node_172":{"key":"node_172","type":"Row","props":{"gutter":[16,0]},"children":["node_173","node_176"],"parentKey":"node_162"},"node_162":{"key":"node_162","type":"div","props":{"id":"section_work","style":{"marginBottom":"28px","paddingTop":"2px"}},"children":["node_163","node_165","node_172"],"parentKey":"node_13"},"node_181":{"key":"node_181","type":"span","props":{"children":"家庭成员"},"parentKey":"node_180"},"node_180":{"key":"node_180","type":"Typography.Title","props":{"level":4,"style":{"marginBottom":"12px","borderLeft":"3px solid #1677ff","paddingLeft":"8px"}},"children":["node_181"],"parentKey":"node_179"},"node_185":{"key":"node_185","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_184"},"node_184":{"key":"node_184","type":"Form.Item","props":{"label":"家庭成员字段1","name":"familyName","style":{"marginBottom":"12px"}},"children":["node_185"],"parentKey":"node_183"},"node_183":{"key":"node_183","type":"Col","props":{"span":12},"children":["node_184"],"parentKey":"node_182"},"node_188":{"key":"node_188","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_187"},"node_187":{"key":"node_187","type":"Form.Item","props":{"label":"家庭成员字段2","name":"familyRelation","style":{"marginBottom":"12px"}},"children":["node_188"],"parentKey":"node_186"},"node_186":{"key":"node_186","type":"Col","props":{"span":12},"children":["node_187"],"parentKey":"node_182"},"node_182":{"key":"node_182","type":"Row","props":{"gutter":[16,0]},"children":["node_183","node_186"],"parentKey":"node_179"},"node_192":{"key":"node_192","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_191"},"node_191":{"key":"node_191","type":"Form.Item","props":{"label":"家庭成员字段3","name":"familyPhone","style":{"marginBottom":"12px"}},"children":["node_192"],"parentKey":"node_190"},"node_190":{"key":"node_190","type":"Col","props":{"span":12},"children":["node_191"],"parentKey":"node_189"},"node_195":{"key":"node_195","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_194"},"node_194":{"key":"node_194","type":"Form.Item","props":{"label":"家庭成员字段4","name":"familyCompany","style":{"marginBottom":"12px"}},"children":["node_195"],"parentKey":"node_193"},"node_193":{"key":"node_193","type":"Col","props":{"span":12},"children":["node_194"],"parentKey":"node_189"},"node_189":{"key":"node_189","type":"Row","props":{"gutter":[16,0]},"children":["node_190","node_193"],"parentKey":"node_179"},"node_179":{"key":"node_179","type":"div","props":{"id":"section_family","style":{"marginBottom":"28px","paddingTop":"2px"}},"children":["node_180","node_182","node_189"],"parentKey":"node_13"},"node_198":{"key":"node_198","type":"span","props":{"children":"专业证书"},"parentKey":"node_197"},"node_197":{"key":"node_197","type":"Typography.Title","props":{"level":4,"style":{"marginBottom":"12px","borderLeft":"3px solid #1677ff","paddingLeft":"8px"}},"children":["node_198"],"parentKey":"node_196"},"node_202":{"key":"node_202","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_201"},"node_201":{"key":"node_201","type":"Form.Item","props":{"label":"专业证书字段1","name":"certName","style":{"marginBottom":"12px"}},"children":["node_202"],"parentKey":"node_200"},"node_200":{"key":"node_200","type":"Col","props":{"span":12},"children":["node_201"],"parentKey":"node_199"},"node_205":{"key":"node_205","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_204"},"node_204":{"key":"node_204","type":"Form.Item","props":{"label":"专业证书字段2","name":"certNo","style":{"marginBottom":"12px"}},"children":["node_205"],"parentKey":"node_203"},"node_203":{"key":"node_203","type":"Col","props":{"span":12},"children":["node_204"],"parentKey":"node_199"},"node_199":{"key":"node_199","type":"Row","props":{"gutter":[16,0]},"children":["node_200","node_203"],"parentKey":"node_196"},"node_209":{"key":"node_209","type":"DatePicker","props":{"style":{"width":"100%"}},"parentKey":"node_208"},"node_208":{"key":"node_208","type":"Form.Item","props":{"label":"专业证书字段3","name":"certDate","style":{"marginBottom":"12px"}},"children":["node_209"],"parentKey":"node_207"},"node_207":{"key":"node_207","type":"Col","props":{"span":12},"children":["node_208"],"parentKey":"node_206"},"node_212":{"key":"node_212","type":"DatePicker","props":{"style":{"width":"100%"}},"parentKey":"node_211"},"node_211":{"key":"node_211","type":"Form.Item","props":{"label":"专业证书字段4","name":"certExpireDate","style":{"marginBottom":"12px"}},"children":["node_212"],"parentKey":"node_210"},"node_210":{"key":"node_210","type":"Col","props":{"span":12},"children":["node_211"],"parentKey":"node_206"},"node_206":{"key":"node_206","type":"Row","props":{"gutter":[16,0]},"children":["node_207","node_210"],"parentKey":"node_196"},"node_196":{"key":"node_196","type":"div","props":{"id":"section_cert","style":{"marginBottom":"28px","paddingTop":"2px"}},"children":["node_197","node_199","node_206"],"parentKey":"node_13"},"node_215":{"key":"node_215","type":"span","props":{"children":"奖惩记录"},"parentKey":"node_214"},"node_214":{"key":"node_214","type":"Typography.Title","props":{"level":4,"style":{"marginBottom":"12px","borderLeft":"3px solid #1677ff","paddingLeft":"8px"}},"children":["node_215"],"parentKey":"node_213"},"node_219":{"key":"node_219","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_218"},"node_218":{"key":"node_218","type":"Form.Item","props":{"label":"奖惩记录字段1","name":"rewardType","style":{"marginBottom":"12px"}},"children":["node_219"],"parentKey":"node_217"},"node_217":{"key":"node_217","type":"Col","props":{"span":12},"children":["node_218"],"parentKey":"node_216"},"node_222":{"key":"node_222","type":"DatePicker","props":{"style":{"width":"100%"}},"parentKey":"node_221"},"node_221":{"key":"node_221","type":"Form.Item","props":{"label":"奖惩记录字段2","name":"rewardDate","style":{"marginBottom":"12px"}},"children":["node_222"],"parentKey":"node_220"},"node_220":{"key":"node_220","type":"Col","props":{"span":12},"children":["node_221"],"parentKey":"node_216"},"node_216":{"key":"node_216","type":"Row","props":{"gutter":[16,0]},"children":["node_217","node_220"],"parentKey":"node_213"},"node_226":{"key":"node_226","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_225"},"node_225":{"key":"node_225","type":"Form.Item","props":{"label":"奖惩记录字段3","name":"rewardOrg","style":{"marginBottom":"12px"}},"children":["node_226"],"parentKey":"node_224"},"node_224":{"key":"node_224","type":"Col","props":{"span":12},"children":["node_225"],"parentKey":"node_223"},"node_223":{"key":"node_223","type":"Row","props":{"gutter":[16,0]},"children":["node_224"],"parentKey":"node_213"},"node_213":{"key":"node_213","type":"div","props":{"id":"section_reward","style":{"marginBottom":"28px","paddingTop":"2px"}},"children":["node_214","node_216","node_223"],"parentKey":"node_13"},"node_229":{"key":"node_229","type":"span","props":{"children":"职称"},"parentKey":"node_228"},"node_228":{"key":"node_228","type":"Typography.Title","props":{"level":4,"style":{"marginBottom":"12px","borderLeft":"3px solid #1677ff","paddingLeft":"8px"}},"children":["node_229"],"parentKey":"node_227"},"node_233":{"key":"node_233","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_232"},"node_232":{"key":"node_232","type":"Form.Item","props":{"label":"职称字段1","name":"titleName","style":{"marginBottom":"12px"}},"children":["node_233"],"parentKey":"node_231"},"node_231":{"key":"node_231","type":"Col","props":{"span":12},"children":["node_232"],"parentKey":"node_230"},"node_236":{"key":"node_236","type":"DatePicker","props":{"style":{"width":"100%"}},"parentKey":"node_235"},"node_235":{"key":"node_235","type":"Form.Item","props":{"label":"职称字段2","name":"titleDate","style":{"marginBottom":"12px"}},"children":["node_236"],"parentKey":"node_234"},"node_234":{"key":"node_234","type":"Col","props":{"span":12},"children":["node_235"],"parentKey":"node_230"},"node_230":{"key":"node_230","type":"Row","props":{"gutter":[16,0]},"children":["node_231","node_234"],"parentKey":"node_227"},"node_240":{"key":"node_240","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_239"},"node_239":{"key":"node_239","type":"Form.Item","props":{"label":"职称字段3","name":"titleOrg","style":{"marginBottom":"12px"}},"children":["node_240"],"parentKey":"node_238"},"node_238":{"key":"node_238","type":"Col","props":{"span":12},"children":["node_239"],"parentKey":"node_237"},"node_243":{"key":"node_243","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_242"},"node_242":{"key":"node_242","type":"Form.Item","props":{"label":"职称字段4","name":"titleCertNo","style":{"marginBottom":"12px"}},"children":["node_243"],"parentKey":"node_241"},"node_241":{"key":"node_241","type":"Col","props":{"span":12},"children":["node_242"],"parentKey":"node_237"},"node_237":{"key":"node_237","type":"Row","props":{"gutter":[16,0]},"children":["node_238","node_241"],"parentKey":"node_227"},"node_227":{"key":"node_227","type":"div","props":{"id":"section_title","style":{"marginBottom":"28px","paddingTop":"2px"}},"children":["node_228","node_230","node_237"],"parentKey":"node_13"},"node_246":{"key":"node_246","type":"span","props":{"children":"培训记录"},"parentKey":"node_245"},"node_245":{"key":"node_245","type":"Typography.Title","props":{"level":4,"style":{"marginBottom":"12px","borderLeft":"3px solid #1677ff","paddingLeft":"8px"}},"children":["node_246"],"parentKey":"node_244"},"node_250":{"key":"node_250","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_249"},"node_249":{"key":"node_249","type":"Form.Item","props":{"label":"培训记录字段1","name":"trainTopic","style":{"marginBottom":"12px"}},"children":["node_250"],"parentKey":"node_248"},"node_248":{"key":"node_248","type":"Col","props":{"span":12},"children":["node_249"],"parentKey":"node_247"},"node_253":{"key":"node_253","type":"DatePicker","props":{"style":{"width":"100%"}},"parentKey":"node_252"},"node_252":{"key":"node_252","type":"Form.Item","props":{"label":"培训记录字段2","name":"trainDate","style":{"marginBottom":"12px"}},"children":["node_253"],"parentKey":"node_251"},"node_251":{"key":"node_251","type":"Col","props":{"span":12},"children":["node_252"],"parentKey":"node_247"},"node_247":{"key":"node_247","type":"Row","props":{"gutter":[16,0]},"children":["node_248","node_251"],"parentKey":"node_244"},"node_257":{"key":"node_257","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_256"},"node_256":{"key":"node_256","type":"Form.Item","props":{"label":"培训记录字段3","name":"trainOrg","style":{"marginBottom":"12px"}},"children":["node_257"],"parentKey":"node_255"},"node_255":{"key":"node_255","type":"Col","props":{"span":12},"children":["node_256"],"parentKey":"node_254"},"node_260":{"key":"node_260","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_259"},"node_259":{"key":"node_259","type":"Form.Item","props":{"label":"培训记录字段4","name":"trainHours","style":{"marginBottom":"12px"}},"children":["node_260"],"parentKey":"node_258"},"node_258":{"key":"node_258","type":"Col","props":{"span":12},"children":["node_259"],"parentKey":"node_254"},"node_254":{"key":"node_254","type":"Row","props":{"gutter":[16,0]},"children":["node_255","node_258"],"parentKey":"node_244"},"node_244":{"key":"node_244","type":"div","props":{"id":"section_training","style":{"marginBottom":"28px","paddingTop":"2px"}},"children":["node_245","node_247","node_254"],"parentKey":"node_13"},"node_263":{"key":"node_263","type":"span","props":{"children":"绩效考核"},"parentKey":"node_262"},"node_262":{"key":"node_262","type":"Typography.Title","props":{"level":4,"style":{"marginBottom":"12px","borderLeft":"3px solid #1677ff","paddingLeft":"8px"}},"children":["node_263"],"parentKey":"node_261"},"node_267":{"key":"node_267","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_266"},"node_266":{"key":"node_266","type":"Form.Item","props":{"label":"绩效考核字段1","name":"perfCycle","style":{"marginBottom":"12px"}},"children":["node_267"],"parentKey":"node_265"},"node_265":{"key":"node_265","type":"Col","props":{"span":12},"children":["node_266"],"parentKey":"node_264"},"node_270":{"key":"node_270","type":"Select","props":{"placeholder":"请选择","options":[{"label":"A","value":"A"},{"label":"B","value":"B"},{"label":"C","value":"C"}]},"parentKey":"node_269"},"node_269":{"key":"node_269","type":"Form.Item","props":{"label":"绩效考核字段2","name":"perfLevel","style":{"marginBottom":"12px"}},"children":["node_270"],"parentKey":"node_268"},"node_268":{"key":"node_268","type":"Col","props":{"span":12},"children":["node_269"],"parentKey":"node_264"},"node_264":{"key":"node_264","type":"Row","props":{"gutter":[16,0]},"children":["node_265","node_268"],"parentKey":"node_261"},"node_274":{"key":"node_274","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_273"},"node_273":{"key":"node_273","type":"Form.Item","props":{"label":"绩效考核字段3","name":"perfReviewer","style":{"marginBottom":"12px"}},"children":["node_274"],"parentKey":"node_272"},"node_272":{"key":"node_272","type":"Col","props":{"span":12},"children":["node_273"],"parentKey":"node_271"},"node_277":{"key":"node_277","type":"DatePicker","props":{"style":{"width":"100%"}},"parentKey":"node_276"},"node_276":{"key":"node_276","type":"Form.Item","props":{"label":"绩效考核字段4","name":"perfDate","style":{"marginBottom":"12px"}},"children":["node_277"],"parentKey":"node_275"},"node_275":{"key":"node_275","type":"Col","props":{"span":12},"children":["node_276"],"parentKey":"node_271"},"node_271":{"key":"node_271","type":"Row","props":{"gutter":[16,0]},"children":["node_272","node_275"],"parentKey":"node_261"},"node_261":{"key":"node_261","type":"div","props":{"id":"section_perf","style":{"marginBottom":"28px","paddingTop":"2px"}},"children":["node_262","node_264","node_271"],"parentKey":"node_13"},"node_280":{"key":"node_280","type":"span","props":{"children":"个人材料"},"parentKey":"node_279"},"node_279":{"key":"node_279","type":"Typography.Title","props":{"level":4,"style":{"marginBottom":"12px","borderLeft":"3px solid #1677ff","paddingLeft":"8px"}},"children":["node_280"],"parentKey":"node_278"},"node_284":{"key":"node_284","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_283"},"node_283":{"key":"node_283","type":"Form.Item","props":{"label":"个人材料字段1","name":"materialName","style":{"marginBottom":"12px"}},"children":["node_284"],"parentKey":"node_282"},"node_282":{"key":"node_282","type":"Col","props":{"span":12},"children":["node_283"],"parentKey":"node_281"},"node_287":{"key":"node_287","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_286"},"node_286":{"key":"node_286","type":"Form.Item","props":{"label":"个人材料字段2","name":"materialNo","style":{"marginBottom":"12px"}},"children":["node_287"],"parentKey":"node_285"},"node_285":{"key":"node_285","type":"Col","props":{"span":12},"children":["node_286"],"parentKey":"node_281"},"node_281":{"key":"node_281","type":"Row","props":{"gutter":[16,0]},"children":["node_282","node_285"],"parentKey":"node_278"},"node_291":{"key":"node_291","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_290"},"node_290":{"key":"node_290","type":"Form.Item","props":{"label":"个人材料字段3","name":"materialLocation","style":{"marginBottom":"12px"}},"children":["node_291"],"parentKey":"node_289"},"node_289":{"key":"node_289","type":"Col","props":{"span":12},"children":["node_290"],"parentKey":"node_288"},"node_294":{"key":"node_294","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_293"},"node_293":{"key":"node_293","type":"Form.Item","props":{"label":"个人材料字段4","name":"materialKeeper","style":{"marginBottom":"12px"}},"children":["node_294"],"parentKey":"node_292"},"node_292":{"key":"node_292","type":"Col","props":{"span":12},"children":["node_293"],"parentKey":"node_288"},"node_288":{"key":"node_288","type":"Row","props":{"gutter":[16,0]},"children":["node_289","node_292"],"parentKey":"node_278"},"node_278":{"key":"node_278","type":"div","props":{"id":"section_material","style":{"marginBottom":"28px","paddingTop":"2px"}},"children":["node_279","node_281","node_288"],"parentKey":"node_13"},"node_297":{"key":"node_297","type":"span","props":{"children":"工会信息"},"parentKey":"node_296"},"node_296":{"key":"node_296","type":"Typography.Title","props":{"level":4,"style":{"marginBottom":"12px","borderLeft":"3px solid #1677ff","paddingLeft":"8px"}},"children":["node_297"],"parentKey":"node_295"},"node_301":{"key":"node_301","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_300"},"node_300":{"key":"node_300","type":"Form.Item","props":{"label":"工会信息字段1","name":"unionNo","style":{"marginBottom":"12px"}},"children":["node_301"],"parentKey":"node_299"},"node_299":{"key":"node_299","type":"Col","props":{"span":12},"children":["node_300"],"parentKey":"node_298"},"node_304":{"key":"node_304","type":"Input","props":{"placeholder":"请输入"},"parentKey":"node_303"},"node_303":{"key":"node_303","type":"Form.Item","props":{"label":"工会信息字段2","name":"unionStatus","style":{"marginBottom":"12px"}},"children":["node_304"],"parentKey":"node_302"},"node_302":{"key":"node_302","type":"Col","props":{"span":12},"children":["node_303"],"parentKey":"node_298"},"node_298":{"key":"node_298","type":"Row","props":{"gutter":[16,0]},"children":["node_299","node_302"],"parentKey":"node_295"},"node_308":{"key":"node_308","type":"DatePicker","props":{"style":{"width":"100%"}},"parentKey":"node_307"},"node_307":{"key":"node_307","type":"Form.Item","props":{"label":"工会信息字段3","name":"unionJoinDate","style":{"marginBottom":"12px"}},"children":["node_308"],"parentKey":"node_306"},"node_306":{"key":"node_306","type":"Col","props":{"span":12},"children":["node_307"],"parentKey":"node_305"},"node_305":{"key":"node_305","type":"Row","props":{"gutter":[16,0]},"children":["node_306"],"parentKey":"node_295"},"node_295":{"key":"node_295","type":"div","props":{"id":"section_union","style":{"marginBottom":"28px","paddingTop":"2px"}},"children":["node_296","node_298","node_305"],"parentKey":"node_13"},"node_310":{"key":"node_310","type":"Button","props":{"type":"default","children":"取消"},"parentKey":"node_309"},"node_311":{"key":"node_311","type":"Button","props":{"type":"primary","children":"保存"},"parentKey":"node_309"},"node_309":{"key":"node_309","type":"Flex","props":{"justify":"flex-start","gap":12,"style":{"position":"sticky","bottom":0,"zIndex":5,"backgroundColor":"#fff","borderTop":"1px solid #f0f0f0","padding":"12px 0 12px","marginTop":"8px"}},"children":["node_310","node_311"],"parentKey":"node_13"},"node_13":{"key":"node_13","type":"Form","props":{"layout":"horizontal","labelCol":{"span":7},"wrapperCol":{"span":17},"style":{"width":"100%"}},"children":["node_14","node_52","node_87","node_111","node_128","node_145","node_162","node_179","node_196","node_213","node_227","node_244","node_261","node_278","node_295","node_309"],"parentKey":"node_12"},"node_12":{"key":"node_12","type":"div","props":{"id":"employee-form-scroll","style":{"flex":1,"minWidth":0,"height":"100%","overflowY":"auto","overflowX":"hidden","paddingRight":"8px","boxSizing":"border-box"}},"children":["node_13"],"parentKey":"node_9"},"node_9":{"key":"node_9","type":"Flex","props":{"gap":16,"style":{"height":"100%","minHeight":0,"overflow":"hidden"}},"children":["node_10","node_12"],"parentKey":"node_8"},"node_8":{"key":"node_8","type":"div","props":{"style":{"backgroundColor":"#fff","padding":"16px","borderRadius":"8px","height":"100%","boxSizing":"border-box","minHeight":0,"overflow":"hidden"}},"children":["node_9"],"parentKey":"node_7"},"node_7":{"key":"node_7","type":"Content","props":{"style":{"padding":"16px","backgroundColor":"#F2F4F6","minHeight":0,"overflow":"hidden"}},"children":["node_8"],"parentKey":"node_4"},"node_4":{"key":"node_4","type":"Layout","props":{"style":{"flexDirection":"row","flex":1,"minHeight":0,"overflow":"hidden"}},"children":["node_5","node_7"],"parentKey":"node_1"},"node_1":{"key":"node_1","type":"Layout","props":{"style":{"height":"100%","minHeight":0,"overflow":"hidden"}},"children":["node_2","node_4"],"parentKey":"node_0"},"node_0":{"key":"node_0","type":"div","props":{"style":{"width":"1920px","height":"1080px","minHeight":0,"overflow":"hidden"}},"children":["node_1"],"parentKey":null}}},"mode":"interactive","savedAt":1773326358008,"registry":{"XFTTopBar":{"html":"\u003cdiv style=\"height: 48px; width: 100%; background: #1966ff; display: flex; align-items: center; justify-content: space-between; padding-inline: 16px;\">\u003cdiv style=\"display: flex; align-items: center;\">\u003cdiv style=\"position: relative; width: 24px; height: 24px; border-radius: 4px; overflow: hidden;\">\u003cdiv style=\"position: absolute; inset: 0; background: #ffffff; opacity: 0.9; border-radius: 4px;\">\u003c/div>\u003cimg src=\"./branding/logo.png\" alt=\"\" style=\"position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; border-radius: 4px;\" onerror=\"this.style.display='none'\"/>\u003c/div>\u003cdiv style=\"color: #ffffff; font-size: 14px; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Microsoft YaHei', 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif; margin-left: 8px;\">某某企业\u003c/div>\u003cdiv style=\"color: #ffffff; font-size: 14px; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Microsoft YaHei', 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif; margin-left: 24px;\">工作台\u003c/div>\u003cdiv style=\"color: #ffffff; font-size: 14px; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Microsoft YaHei', 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif; margin-left: 24px;\">全部应用\u003c/div>\u003c/div>\u003cdiv style=\"display: flex; align-items: center; flex-direction: row-reverse; gap: 24px;\">\u003cdiv style=\"position: relative; width: 24px; height: 24px; border-radius: 4px; overflow: hidden;\">\u003cdiv style=\"position: absolute; inset: 0; background: #ffffff; opacity: 0.9; border-radius: 4px;\">\u003c/div>\u003cimg src=\"./branding/avatar.png\" alt=\"\" style=\"position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; border-radius: 4px;\" onerror=\"this.style.display='none'\"/>\u003c/div>\u003cdiv style=\"color: #ffffff; font-size: 14px; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Microsoft YaHei', 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif;\">某某员工\u003c/div>\u003cdiv style=\"color: #ffffff; font-size: 14px; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Microsoft YaHei', 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif;\">管理后台\u003c/div>\u003cdiv style=\"color: #ffffff; font-size: 14px; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Microsoft YaHei', 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif;\">工具箱\u003c/div>\u003cdiv style=\"color: #ffffff; font-size: 14px; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Microsoft YaHei', 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif;\">服务中心\u003c/div>\u003cinput placeholder=\"赶快使用 AI 体验搜索吧！\" style=\"width: 200px; height: 32px; border-radius: 6px; background: rgba(255,255,255,0.2); color: #ffffff; border: none; padding-left: 8px;\" />\u003c/div>\u003c/div>"}},"actionState":{"visibility":{},"activeKeys":{}}};
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