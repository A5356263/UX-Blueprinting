{
  "type": "div",
  "props": {
    "style": {
      "width": "1920px",
      "height": "1080px",
      "minHeight": 0,
      "overflow": "hidden"
    }
  },
  "children": [
    {
      "type": "Layout",
      "props": {
        "style": {
          "height": "100%",
          "minHeight": 0,
          "overflow": "hidden"
        }
      },
      "children": [
        {
          "type": "Header",
          "props": {
            "height": "48px"
          },
          "children": [
            {
              "type": "XFTTopBar",
              "props": {},
              "children": []
            }
          ]
        },
        {
          "type": "Layout",
          "props": {
            "style": {
              "flexDirection": "row",
              "flex": 1,
              "minHeight": 0,
              "overflow": "hidden"
            }
          },
          "children": [
            {
              "type": "Sider",
              "props": {
                "width": "188px",
                "theme": "light",
                "style": {
                  "backgroundColor": "#ffffff",
                  "height": "100%",
                  "minHeight": 0,
                  "overflowY": "auto",
                  "overflowX": "hidden"
                }
              },
              "children": [
                {
                  "type": "Menu",
                  "props": {
                    "mode": "inline",
                    "theme": "light",
                    "defaultSelectedKeys": [
                      "1-1"
                    ],
                    "items": [
                      {
                        "key": "1",
                        "label": "人力资源管理",
                        "icon": "UserOutlined",
                        "children": [
                          {
                            "key": "1-1",
                            "label": "成员管理"
                          },
                          {
                            "key": "1-2",
                            "label": "组织架构"
                          },
                          {
                            "key": "1-3",
                            "label": "职位管理"
                          }
                        ]
                      },
                      {
                        "key": "2",
                        "label": "招聘管理",
                        "icon": "TeamOutlined",
                        "children": [
                          {
                            "key": "2-1",
                            "label": "职位发布"
                          },
                          {
                            "key": "2-2",
                            "label": "候选人库"
                          },
                          {
                            "key": "2-3",
                            "label": "面试流程"
                          }
                        ]
                      },
                      {
                        "key": "3",
                        "label": "绩效管理",
                        "icon": "AppstoreOutlined",
                        "children": [
                          {
                            "key": "3-1",
                            "label": "考核周期"
                          },
                          {
                            "key": "3-2",
                            "label": "绩效结果"
                          },
                          {
                            "key": "3-3",
                            "label": "绩效申诉"
                          }
                        ]
                      },
                      {
                        "key": "4",
                        "label": "培训发展",
                        "icon": "SettingOutlined",
                        "children": [
                          {
                            "key": "4-1",
                            "label": "培训计划"
                          },
                          {
                            "key": "4-2",
                            "label": "学习地图"
                          },
                          {
                            "key": "4-3",
                            "label": "认证管理"
                          }
                        ]
                      },
                      {
                        "key": "5",
                        "label": "薪酬福利",
                        "icon": "UserOutlined",
                        "children": [
                          {
                            "key": "5-1",
                            "label": "薪资核算"
                          },
                          {
                            "key": "5-2",
                            "label": "福利方案"
                          },
                          {
                            "key": "5-3",
                            "label": "个税申报"
                          }
                        ]
                      },
                      {
                        "key": "6",
                        "label": "考勤管理",
                        "icon": "TeamOutlined",
                        "children": [
                          {
                            "key": "6-1",
                            "label": "排班管理"
                          },
                          {
                            "key": "6-2",
                            "label": "打卡记录"
                          },
                          {
                            "key": "6-3",
                            "label": "请假审批"
                          }
                        ]
                      },
                      {
                        "key": "7",
                        "label": "员工关系",
                        "icon": "AppstoreOutlined",
                        "children": [
                          {
                            "key": "7-1",
                            "label": "合同管理"
                          },
                          {
                            "key": "7-2",
                            "label": "异动管理"
                          },
                          {
                            "key": "7-3",
                            "label": "离职管理"
                          }
                        ]
                      },
                      {
                        "key": "8",
                        "label": "组织人才",
                        "icon": "SettingOutlined",
                        "children": [
                          {
                            "key": "8-1",
                            "label": "人才盘点"
                          },
                          {
                            "key": "8-2",
                            "label": "继任计划"
                          },
                          {
                            "key": "8-3",
                            "label": "关键岗位"
                          }
                        ]
                      },
                      {
                        "key": "9",
                        "label": "合规风控",
                        "icon": "UserOutlined",
                        "children": [
                          {
                            "key": "9-1",
                            "label": "制度中心"
                          },
                          {
                            "key": "9-2",
                            "label": "审计日志"
                          },
                          {
                            "key": "9-3",
                            "label": "权限审批"
                          }
                        ]
                      }
                    ],
                    "style": {
                      "height": "100%",
                      "minHeight": 0,
                      "overflowY": "auto",
                      "overflowX": "hidden"
                    }
                  },
                  "children": []
                }
              ]
            },
            {
              "type": "Content",
              "props": {
                "style": {
                  "padding": "16px",
                  "backgroundColor": "#F2F4F6",
                  "minHeight": 0,
                  "overflow": "hidden"
                }
              },
              "children": [
                {
                  "type": "div",
                  "props": {
                    "style": {
                      "backgroundColor": "#fff",
                      "padding": "16px",
                      "borderRadius": "8px",
                      "height": "100%",
                      "boxSizing": "border-box",
                      "minHeight": 0,
                      "overflow": "hidden"
                    }
                  },
                  "children": [
                    {
                      "type": "Flex",
                      "props": {
                        "gap": 16,
                        "style": {
                          "height": "100%",
                          "minHeight": 0,
                          "overflow": "hidden"
                        }
                      },
                      "children": [
                        {
                          "type": "Flex",
                          "props": {
                            "vertical": true,
                            "gap": 16,
                            "style": {
                              "width": "380px",
                              "height": "100%",
                              "minHeight": 0,
                              "overflow": "hidden"
                            }
                          },
                          "children": [
                            {
                              "type": "Flex",
                              "props": {
                                "gap": 0,
                                "style": {
                                  "width": "100%",
                                  "alignItems": "center"
                                }
                              },
                              "children": [
                                {
                                  "type": "Input",
                                  "props": {
                                    "placeholder": "搜索组织",
                                    "allowClear": true,
                                    "style": {
                                      "flex": 1,
                                      "minWidth": 0,
                                      "borderTopRightRadius": 0,
                                      "borderBottomRightRadius": 0
                                    }
                                  },
                                  "children": []
                                },
                                {
                                  "type": "Button",
                                  "props": {
                                    "type": "default",
                                    "style": {
                                      "borderTopLeftRadius": 0,
                                      "borderBottomLeftRadius": 0,
                                      "marginLeft": "-1px"
                                    }
                                  },
                                  "children": [
                                    {
                                      "type": "span",
                                      "props": {
                                        "children": "搜索"
                                      },
                                      "children": []
                                    }
                                  ]
                                }
                              ]
                            },
                            {
                              "type": "Button",
                              "props": {
                                "type": "default",
                                "style": {
                                  "height": "32px",
                                  "lineHeight": "32px",
                                  "padding": "0 15px"
                                },
                                "interactions": [
                                  {
                                    "trigger": "click",
                                    "action": "SET_VISIBLE",
                                    "target": "modal_create_org",
                                    "payload": true
                                  }
                                ]
                              },
                              "children": [
                                {
                                  "type": "span",
                                  "props": {
                                    "children": "创建组织"
                                  },
                                  "children": []
                                }
                              ]
                            },
                            {
                              "type": "Tree",
                              "props": {
                                "treeData": [
                                  {
                                    "title": "XX科技集团",
                                    "key": "0",
                                    "children": [
                                      {
                                        "title": "研发中心",
                                        "key": "0-0",
                                        "children": [
                                          {
                                            "title": "前端部",
                                            "key": "0-0-0"
                                          },
                                          {
                                            "title": "后端部",
                                            "key": "0-0-1"
                                          },
                                          {
                                            "title": "测试部",
                                            "key": "0-0-2"
                                          }
                                        ]
                                      },
                                      {
                                        "title": "产品中心",
                                        "key": "0-1",
                                        "children": [
                                          {
                                            "title": "产品一部",
                                            "key": "0-1-0"
                                          },
                                          {
                                            "title": "产品二部",
                                            "key": "0-1-1"
                                          },
                                          {
                                            "title": "设计部",
                                            "key": "0-1-2"
                                          }
                                        ]
                                      },
                                      {
                                        "title": "运营中心",
                                        "key": "0-2",
                                        "children": [
                                          {
                                            "title": "运营部",
                                            "key": "0-2-0"
                                          },
                                          {
                                            "title": "市场部",
                                            "key": "0-2-1"
                                          },
                                          {
                                            "title": "客服部",
                                            "key": "0-2-2"
                                          }
                                        ]
                                      },
                                      {
                                        "title": "职能部门",
                                        "key": "0-3",
                                        "children": [
                                          {
                                            "title": "人力资源部",
                                            "key": "0-3-0"
                                          },
                                          {
                                            "title": "财务部",
                                            "key": "0-3-1"
                                          },
                                          {
                                            "title": "行政部",
                                            "key": "0-3-2"
                                          }
                                        ]
                                      },
                                      {
                                        "title": "销售中心",
                                        "key": "0-4",
                                        "children": [
                                          {
                                            "title": "销售一部",
                                            "key": "0-4-0"
                                          },
                                          {
                                            "title": "销售二部",
                                            "key": "0-4-1"
                                          },
                                          {
                                            "title": "渠道部",
                                            "key": "0-4-2"
                                          }
                                        ]
                                      },
                                      {
                                        "title": "客户成功中心",
                                        "key": "0-5",
                                        "children": [
                                          {
                                            "title": "实施部",
                                            "key": "0-5-0"
                                          },
                                          {
                                            "title": "交付部",
                                            "key": "0-5-1"
                                          },
                                          {
                                            "title": "续约部",
                                            "key": "0-5-2"
                                          }
                                        ]
                                      },
                                      {
                                        "title": "质量管理中心",
                                        "key": "0-6",
                                        "children": [
                                          {
                                            "title": "流程质量部",
                                            "key": "0-6-0"
                                          },
                                          {
                                            "title": "数据质量部",
                                            "key": "0-6-1"
                                          },
                                          {
                                            "title": "内控部",
                                            "key": "0-6-2"
                                          }
                                        ]
                                      },
                                      {
                                        "title": "战略发展中心",
                                        "key": "0-7",
                                        "children": [
                                          {
                                            "title": "战略规划部",
                                            "key": "0-7-0"
                                          },
                                          {
                                            "title": "投资并购部",
                                            "key": "0-7-1"
                                          },
                                          {
                                            "title": "经营分析部",
                                            "key": "0-7-2"
                                          }
                                        ]
                                      },
                                      {
                                        "title": "行政服务中心",
                                        "key": "0-8",
                                        "children": [
                                          {
                                            "title": "行政支持部",
                                            "key": "0-8-0"
                                          },
                                          {
                                            "title": "资产管理部",
                                            "key": "0-8-1"
                                          },
                                          {
                                            "title": "后勤保障部",
                                            "key": "0-8-2"
                                          }
                                        ]
                                      }
                                    ]
                                  }
                                ],
                                "defaultExpandAll": true,
                                "style": {
                                  "flex": 1,
                                  "minHeight": 0,
                                  "overflowY": "auto",
                                  "overflowX": "hidden"
                                }
                              },
                              "children": []
                            }
                          ]
                        },
                        {
                          "type": "Divider",
                          "props": {
                            "type": "vertical",
                            "style": {
                              "height": "100%",
                              "alignSelf": "stretch"
                            }
                          },
                          "children": []
                        },
                        {
                          "type": "Flex",
                          "props": {
                            "vertical": true,
                            "gap": 16,
                            "style": {
                              "flex": 1,
                              "minHeight": 0,
                              "overflow": "hidden"
                            }
                          },
                          "children": [
                            {
                              "type": "Card",
                              "props": {
                                "variant": "borderless",
                                "style": {
                                  "backgroundColor": "rgba(25, 102, 255, 0.04)",
                                  "borderRadius": "8px"
                                }
                              },
                              "children": [
                                {
                                  "type": "Flex",
                                  "props": {
                                    "vertical": true,
                                    "gap": 12
                                  },
                                  "children": [
                                    {
                                      "type": "Flex",
                                      "props": {
                                        "justify": "space-between",
                                        "align": "center"
                                      },
                                      "children": [
                                        {
                                          "type": "Flex",
                                          "props": {
                                            "align": "center",
                                            "gap": 8,
                                            "style": {
                                              "flexWrap": "wrap"
                                            }
                                          },
                                          "children": [
                                            {
                                              "type": "Typography.Title",
                                              "props": {
                                                "level": 4,
                                                "style": {
                                                  "margin": 0
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "span",
                                                  "props": {
                                                    "children": "正大信息安全上海办事处"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            },
                                            {
                                              "type": "Typography.Text",
                                              "props": {
                                                "style": {
                                                  "fontSize": "12px",
                                                  "lineHeight": "20px",
                                                  "color": "#1966FF",
                                                  "backgroundColor": "rgba(25,102,255,0.12)",
                                                  "padding": "0 8px",
                                                  "borderRadius": "4px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "span",
                                                  "props": {
                                                    "children": "组织类型"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            },
                                            {
                                              "type": "Typography.Text",
                                              "props": {
                                                "style": {
                                                  "fontSize": "12px",
                                                  "lineHeight": "20px",
                                                  "color": "#1966FF",
                                                  "backgroundColor": "rgba(25,102,255,0.12)",
                                                  "padding": "0 8px",
                                                  "borderRadius": "4px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "span",
                                                  "props": {
                                                    "children": "二级组织"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Typography.Text",
                                          "props": {
                                            "style": {
                                              "color": "#1966FF",
                                              "cursor": "pointer"
                                            },
                                            "interactions": [
                                              {
                                                "trigger": "click",
                                                "action": "SET_VISIBLE",
                                                "target": "modal_org_detail",
                                                "payload": true
                                              }
                                            ]
                                          },
                                          "children": [
                                            {
                                              "type": "span",
                                              "props": {
                                                "children": "组织详情"
                                              },
                                              "children": []
                                            }
                                          ]
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Flex",
                                      "props": {
                                        "align": "center",
                                        "gap": 12,
                                        "style": {
                                          "flexWrap": "wrap"
                                        }
                                      },
                                      "children": [
                                        {
                                          "type": "Flex",
                                          "props": {
                                            "align": "center",
                                            "gap": 4
                                          },
                                          "children": [
                                            {
                                              "type": "Typography.Text",
                                              "props": {
                                                "style": {
                                                  "color": "rgba(0,0,0,0.65)"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "span",
                                                  "props": {
                                                    "children": "成员总数"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            },
                                            {
                                              "type": "Typography.Text",
                                              "props": {
                                                "style": {
                                                  "color": "rgba(0,0,0,0.88)"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "span",
                                                  "props": {
                                                    "children": "80"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Typography.Text",
                                          "props": {
                                            "style": {
                                              "color": "rgba(0,0,0,0.2)"
                                            }
                                          },
                                          "children": [
                                            {
                                              "type": "span",
                                              "props": {
                                                "children": "|"
                                              },
                                              "children": []
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Flex",
                                          "props": {
                                            "align": "center",
                                            "gap": 4
                                          },
                                          "children": [
                                            {
                                              "type": "Typography.Text",
                                              "props": {
                                                "style": {
                                                  "color": "rgba(0,0,0,0.65)"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "span",
                                                  "props": {
                                                    "children": "直属成员"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            },
                                            {
                                              "type": "Typography.Text",
                                              "props": {
                                                "style": {
                                                  "color": "rgba(0,0,0,0.88)"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "span",
                                                  "props": {
                                                    "children": "23"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Typography.Text",
                                          "props": {
                                            "style": {
                                              "color": "rgba(0,0,0,0.2)"
                                            }
                                          },
                                          "children": [
                                            {
                                              "type": "span",
                                              "props": {
                                                "children": "|"
                                              },
                                              "children": []
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Flex",
                                          "props": {
                                            "align": "center",
                                            "gap": 4
                                          },
                                          "children": [
                                            {
                                              "type": "Typography.Text",
                                              "props": {
                                                "style": {
                                                  "color": "rgba(0,0,0,0.65)"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "span",
                                                  "props": {
                                                    "children": "组织负责人"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            },
                                            {
                                              "type": "Typography.Text",
                                              "props": {
                                                "style": {
                                                  "color": "rgba(0,0,0,0.88)"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "span",
                                                  "props": {
                                                    "children": "邱云云"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Typography.Text",
                                          "props": {
                                            "style": {
                                              "color": "rgba(0,0,0,0.2)"
                                            }
                                          },
                                          "children": [
                                            {
                                              "type": "span",
                                              "props": {
                                                "children": "|"
                                              },
                                              "children": []
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Flex",
                                          "props": {
                                            "align": "center",
                                            "gap": 4
                                          },
                                          "children": [
                                            {
                                              "type": "Typography.Text",
                                              "props": {
                                                "style": {
                                                  "color": "rgba(0,0,0,0.65)"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "span",
                                                  "props": {
                                                    "children": "审批主管"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            },
                                            {
                                              "type": "Typography.Text",
                                              "props": {
                                                "style": {
                                                  "color": "rgba(0,0,0,0.88)"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "span",
                                                  "props": {
                                                    "children": "邱云"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Typography.Text",
                                          "props": {
                                            "style": {
                                              "color": "rgba(0,0,0,0.2)"
                                            }
                                          },
                                          "children": [
                                            {
                                              "type": "span",
                                              "props": {
                                                "children": "|"
                                              },
                                              "children": []
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Flex",
                                          "props": {
                                            "align": "center",
                                            "gap": 4
                                          },
                                          "children": [
                                            {
                                              "type": "Typography.Text",
                                              "props": {
                                                "style": {
                                                  "color": "rgba(0,0,0,0.65)"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "span",
                                                  "props": {
                                                    "children": "下级组织数"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            },
                                            {
                                              "type": "Typography.Text",
                                              "props": {
                                                "style": {
                                                  "color": "rgba(0,0,0,0.88)"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "span",
                                                  "props": {
                                                    "children": "80"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        }
                                      ]
                                    }
                                  ]
                                }
                              ]
                            },
                            {
                              "type": "Segmented",
                              "props": {
                                "options": [
                                  "直属成员",
                                  "全部成员"
                                ],
                                "defaultValue": "直属成员",
                                "style": {
                                  "width": "fit-content"
                                }
                              },
                              "children": []
                            },
                            {
                              "type": "Flex",
                              "props": {
                                "justify": "space-between",
                                "align": "center",
                                "gap": 8
                              },
                              "children": [
                                {
                                  "type": "Flex",
                                  "props": {
                                    "gap": 8
                                  },
                                  "children": [
                                    {
                                      "type": "Dropdown",
                                      "props": {
                                        "menu": {
                                          "items": [
                                            {
                                              "key": "1",
                                              "label": "手机号邀请成员",
                                              "interactions": [
                                                {
                                                  "trigger": "click",
                                                  "action": "SET_VISIBLE",
                                                  "target": "modal_invite_by_phone",
                                                  "payload": true
                                                }
                                              ]
                                            },
                                            {
                                              "key": "2",
                                              "label": "二维码邀请成员"
                                            },
                                            {
                                              "key": "3",
                                              "label": "邀请记录"
                                            }
                                          ]
                                        },
                                        "trigger": [
                                          "click"
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Button",
                                          "props": {
                                            "type": "primary",
                                            "icon": "DownOutlined",
                                            "iconPosition": "right"
                                          },
                                          "children": [
                                            {
                                              "type": "span",
                                              "props": {
                                                "children": "邀请成员"
                                              },
                                              "children": []
                                            }
                                          ]
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Dropdown",
                                      "props": {
                                        "menu": {
                                          "items": [
                                            {
                                              "key": "1",
                                              "label": "导入成员",
                                              "interactions": [
                                                {
                                                  "trigger": "click",
                                                  "action": "SET_VISIBLE",
                                                  "target": "modal_import_member",
                                                  "payload": true
                                                }
                                              ]
                                            },
                                            {
                                              "key": "2",
                                              "label": "导出成员",
                                              "interactions": [
                                                {
                                                  "trigger": "click",
                                                  "action": "SET_VISIBLE",
                                                  "target": "modal_export_member",
                                                  "payload": true
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        "trigger": [
                                          "click"
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Button",
                                          "props": {
                                            "type": "default",
                                            "icon": "DownOutlined",
                                            "iconPosition": "right"
                                          },
                                          "children": [
                                            {
                                              "type": "span",
                                              "props": {
                                                "children": "导入/导出"
                                              },
                                              "children": []
                                            }
                                          ]
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Button",
                                      "props": {
                                        "type": "default"
                                      },
                                      "children": [
                                        {
                                          "type": "span",
                                          "props": {
                                            "children": "调整组织"
                                          },
                                          "children": []
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Button",
                                      "props": {
                                        "type": "default"
                                      },
                                      "children": [
                                        {
                                          "type": "span",
                                          "props": {
                                            "children": "成员排序"
                                          },
                                          "children": []
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Dropdown",
                                      "props": {
                                        "menu": {
                                          "items": [
                                            {
                                              "key": "1",
                                              "label": "批量删除"
                                            },
                                            {
                                              "key": "2",
                                              "label": "批量撤销"
                                            }
                                          ]
                                        },
                                        "trigger": [
                                          "click"
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Button",
                                          "props": {
                                            "type": "default",
                                            "icon": "DownOutlined",
                                            "iconPosition": "right"
                                          },
                                          "children": [
                                            {
                                              "type": "span",
                                              "props": {
                                                "children": "批量操作"
                                              },
                                              "children": []
                                            }
                                          ]
                                        }
                                      ]
                                    }
                                  ]
                                },
                                {
                                  "type": "Button",
                                  "props": {
                                    "type": "default",
                                    "icon": "SettingOutlined"
                                  },
                                  "children": [
                                    {
                                      "type": "span",
                                      "props": {
                                        "children": "设置"
                                      },
                                      "children": []
                                    }
                                  ]
                                }
                              ]
                            },
                            {
                              "type": "div",
                              "props": {
                                "style": {
                                  "position": "relative",
                                  "flex": 1,
                                  "minHeight": 0
                                }
                              },
                              "children": [
                                {
                                  "type": "Table",
                                  "props": {
                                    "size": "small",
                                    "bordered": true,
                                    "scroll": {
                                      "x": "max-content",
                                      "y": 460
                                    },
                                    "dataSource": [
                                      {
                                        "id": 1,
                                        "name": "张三",
                                        "dept": "研发中心/前端部",
                                        "position": "前端工程师",
                                        "phone": "13800138001",
                                        "email": "zhangsan@example.com",
                                        "status": "在职",
                                        "joinDate": "2021-03-15",
                                        "employeeId": "EMP1001",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 2,
                                        "name": "李四",
                                        "dept": "产品中心/产品一部",
                                        "position": "产品经理",
                                        "phone": "13800138002",
                                        "email": "lisi@example.com",
                                        "status": "在职",
                                        "joinDate": "2020-07-22",
                                        "employeeId": "EMP1002",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 3,
                                        "name": "王五",
                                        "dept": "运营中心/市场部",
                                        "position": "市场专员",
                                        "phone": "13800138003",
                                        "email": "wangwu@example.com",
                                        "status": "在职",
                                        "joinDate": "2022-01-10",
                                        "employeeId": "EMP1003",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 4,
                                        "name": "赵六",
                                        "dept": "职能部门/人力资源部",
                                        "position": "招聘专员",
                                        "phone": "13800138004",
                                        "email": "zhaoliu@example.com",
                                        "status": "在职",
                                        "joinDate": "2019-11-05",
                                        "employeeId": "EMP1004",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 5,
                                        "name": "钱七",
                                        "dept": "销售中心/销售一部",
                                        "position": "销售经理",
                                        "phone": "13800138005",
                                        "email": "qianqi@example.com",
                                        "status": "在职",
                                        "joinDate": "2020-05-30",
                                        "employeeId": "EMP1005",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 6,
                                        "name": "孙八",
                                        "dept": "研发中心/后端部",
                                        "position": "后端工程师",
                                        "phone": "13800138006",
                                        "email": "sunba@example.com",
                                        "status": "在职",
                                        "joinDate": "2021-08-14",
                                        "employeeId": "EMP1006",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 7,
                                        "name": "周九",
                                        "dept": "产品中心/设计部",
                                        "position": "UI设计师",
                                        "phone": "13800138007",
                                        "email": "zhoujiu@example.com",
                                        "status": "在职",
                                        "joinDate": "2022-03-01",
                                        "employeeId": "EMP1007",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 8,
                                        "name": "吴十",
                                        "dept": "运营中心/运营部",
                                        "position": "运营主管",
                                        "phone": "13800138008",
                                        "email": "wushi@example.com",
                                        "status": "在职",
                                        "joinDate": "2020-09-18",
                                        "employeeId": "EMP1008",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 9,
                                        "name": "郑十一",
                                        "dept": "职能部门/财务部",
                                        "position": "会计",
                                        "phone": "13800138009",
                                        "email": "zhengshiyi@example.com",
                                        "status": "在职",
                                        "joinDate": "2021-12-03",
                                        "employeeId": "EMP1009",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 10,
                                        "name": "王十二",
                                        "dept": "销售中心/渠道部",
                                        "position": "渠道专员",
                                        "phone": "13800138010",
                                        "email": "wangshier@example.com",
                                        "status": "在职",
                                        "joinDate": "2022-06-20",
                                        "employeeId": "EMP1010",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 11,
                                        "name": "刘十三",
                                        "dept": "研发中心/测试部",
                                        "position": "测试工程师",
                                        "phone": "13800138011",
                                        "email": "liushisan@example.com",
                                        "status": "在职",
                                        "joinDate": "2021-05-11",
                                        "employeeId": "EMP1011",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 12,
                                        "name": "陈十四",
                                        "dept": "产品中心/产品二部",
                                        "position": "产品助理",
                                        "phone": "13800138012",
                                        "email": "chenshisi@example.com",
                                        "status": "在职",
                                        "joinDate": "2022-07-25",
                                        "employeeId": "EMP1012",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 13,
                                        "name": "杨十五",
                                        "dept": "运营中心/客服部",
                                        "position": "客服专员",
                                        "phone": "13800138013",
                                        "email": "yangshiwu@example.com",
                                        "status": "在职",
                                        "joinDate": "2021-10-09",
                                        "employeeId": "EMP1013",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 14,
                                        "name": "黄十六",
                                        "dept": "职能部门/行政部",
                                        "position": "行政专员",
                                        "phone": "13800138014",
                                        "email": "huangshiliu@example.com",
                                        "status": "在职",
                                        "joinDate": "2020-12-12",
                                        "employeeId": "EMP1014",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 15,
                                        "name": "林十七",
                                        "dept": "销售中心/销售二部",
                                        "position": "销售代表",
                                        "phone": "13800138015",
                                        "email": "linshiqi@example.com",
                                        "status": "在职",
                                        "joinDate": "2022-04-05",
                                        "employeeId": "EMP1015",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 16,
                                        "name": "许十六",
                                        "dept": "客户成功中心/实施部",
                                        "position": "实施顾问",
                                        "phone": "13800130016",
                                        "email": "user0016@example.com",
                                        "status": "在职",
                                        "joinDate": "2022-05-15",
                                        "employeeId": "EMP1016",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 17,
                                        "name": "何十七",
                                        "dept": "客户成功中心/交付部",
                                        "position": "交付经理",
                                        "phone": "13800130017",
                                        "email": "user0017@example.com",
                                        "status": "在职",
                                        "joinDate": "2022-06-15",
                                        "employeeId": "EMP1017",
                                        "supervisor": "部门负责人",
                                        "rank": "P6"
                                      },
                                      {
                                        "id": 18,
                                        "name": "高十八",
                                        "dept": "质量管理中心/流程质量部",
                                        "position": "质量专员",
                                        "phone": "13800130018",
                                        "email": "user0018@example.com",
                                        "status": "在职",
                                        "joinDate": "2022-07-15",
                                        "employeeId": "EMP1018",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 19,
                                        "name": "邓十九",
                                        "dept": "质量管理中心/内控部",
                                        "position": "内控专员",
                                        "phone": "13800130019",
                                        "email": "user0019@example.com",
                                        "status": "在职",
                                        "joinDate": "2022-08-15",
                                        "employeeId": "EMP1019",
                                        "supervisor": "部门负责人",
                                        "rank": "P6"
                                      },
                                      {
                                        "id": 20,
                                        "name": "潘二十",
                                        "dept": "战略发展中心/战略规划部",
                                        "position": "战略分析师",
                                        "phone": "13800130020",
                                        "email": "user0020@example.com",
                                        "status": "在职",
                                        "joinDate": "2022-09-15",
                                        "employeeId": "EMP1020",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 21,
                                        "name": "蔡二十一",
                                        "dept": "战略发展中心/经营分析部",
                                        "position": "经营分析师",
                                        "phone": "13800130021",
                                        "email": "user0021@example.com",
                                        "status": "在职",
                                        "joinDate": "2022-10-15",
                                        "employeeId": "EMP1021",
                                        "supervisor": "部门负责人",
                                        "rank": "P6"
                                      },
                                      {
                                        "id": 22,
                                        "name": "蒙二十二",
                                        "dept": "行政服务中心/行政支持部",
                                        "position": "行政主管",
                                        "phone": "13800130022",
                                        "email": "user0022@example.com",
                                        "status": "在职",
                                        "joinDate": "2022-11-15",
                                        "employeeId": "EMP1022",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 23,
                                        "name": "尤二十三",
                                        "dept": "行政服务中心/资产管理部",
                                        "position": "资产管理专员",
                                        "phone": "13800130023",
                                        "email": "user0023@example.com",
                                        "status": "在职",
                                        "joinDate": "2022-12-15",
                                        "employeeId": "EMP1023",
                                        "supervisor": "部门负责人",
                                        "rank": "P6"
                                      },
                                      {
                                        "id": 24,
                                        "name": "费二十四",
                                        "dept": "考勤管理/打卡记录",
                                        "position": "人事专员",
                                        "phone": "13800130024",
                                        "email": "user0024@example.com",
                                        "status": "在职",
                                        "joinDate": "2022-01-15",
                                        "employeeId": "EMP1024",
                                        "supervisor": "部门负责人",
                                        "rank": "P5"
                                      },
                                      {
                                        "id": 25,
                                        "name": "郎二十五",
                                        "dept": "员工关系/合同管理",
                                        "position": "员工关系专员",
                                        "phone": "13800130025",
                                        "email": "user0025@example.com",
                                        "status": "在职",
                                        "joinDate": "2022-02-15",
                                        "employeeId": "EMP1025",
                                        "supervisor": "部门负责人",
                                        "rank": "P6"
                                      }
                                    ],
                                    "columns": [
                                      {
                                        "title": "ID",
                                        "dataIndex": "id",
                                        "key": "id"
                                      },
                                      {
                                        "title": "姓名",
                                        "dataIndex": "name",
                                        "key": "name"
                                      },
                                      {
                                        "title": "部门",
                                        "dataIndex": "dept",
                                        "key": "dept"
                                      },
                                      {
                                        "title": "职位",
                                        "dataIndex": "position",
                                        "key": "position"
                                      },
                                      {
                                        "title": "手机号",
                                        "dataIndex": "phone",
                                        "key": "phone"
                                      },
                                      {
                                        "title": "邮箱",
                                        "dataIndex": "email",
                                        "key": "email"
                                      },
                                      {
                                        "title": "员工状态",
                                        "dataIndex": "status",
                                        "key": "status",
                                        "renderType": "status",
                                        "valueEnum": {
                                          "在职": "green"
                                        }
                                      },
                                      {
                                        "title": "入职日期",
                                        "dataIndex": "joinDate",
                                        "key": "joinDate"
                                      },
                                      {
                                        "title": "员工编号",
                                        "dataIndex": "employeeId",
                                        "key": "employeeId"
                                      },
                                      {
                                        "title": "直属上级",
                                        "dataIndex": "supervisor",
                                        "key": "supervisor"
                                      },
                                      {
                                        "title": "职级",
                                        "dataIndex": "rank",
                                        "key": "rank"
                                      },
                                      {
                                        "title": "操作",
                                        "key": "action",
                                        "renderType": "action",
                                        "actions": [
                                          {
                                            "label": "详情",
                                            "type": "link",
                                            "interactions": [
                                              {
                                                "trigger": "click",
                                                "action": "SET_VISIBLE",
                                                "target": "modal_member_detail",
                                                "payload": true
                                              }
                                            ]
                                          }
                                        ]
                                      }
                                    ],
                                    "pagination": {
                                      "pageSize": 20,
                                      "current": 1,
                                      "total": 25,
                                      "showSizeChanger": false,
                                      "position": [
                                        "bottomRight"
                                      ]
                                    },
                                    "style": {
                                      "height": "100%"
                                    }
                                  },
                                  "children": []
                                }
                              ]
                            }
                          ]
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "Modal",
      "props": {
        "id": "modal_invite_by_phone",
        "title": "新增人员",
        "width": 480,
        "open": false,
        "footer": {
          "type": "Flex",
          "props": {
            "justify": "flex-end",
            "gap": 8
          },
          "children": [
            {
              "type": "Button",
              "props": {
                "type": "default",
                "children": "取消",
                "interactions": [
                  {
                    "trigger": "click",
                    "action": "SET_VISIBLE",
                    "target": "modal_invite_by_phone",
                    "payload": false
                  }
                ]
              },
              "children": []
            },
            {
              "type": "Button",
              "props": {
                "type": "primary",
                "children": "保存",
                "interactions": [
                  {
                    "trigger": "click",
                    "action": "SET_VISIBLE",
                    "target": "modal_invite_by_phone",
                    "payload": false
                  }
                ]
              },
              "children": []
            }
          ]
        },
        "dividers": false
      },
      "children": [
        {
          "type": "Flex",
          "props": {
            "vertical": true,
            "gap": 16
          },
          "children": [
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "center"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "68px",
                      "textAlign": "right",
                      "marginRight": "8px"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "姓名"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "Input",
                  "props": {
                    "placeholder": "请输入姓名",
                    "style": {
                      "flex": 1
                    }
                  },
                  "children": []
                }
              ]
            },
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "center"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "68px",
                      "textAlign": "right",
                      "marginRight": "8px"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "手机号"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "Input",
                  "props": {
                    "placeholder": "请输入手机号",
                    "style": {
                      "flex": 1
                    }
                  },
                  "children": []
                }
              ]
            },
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "center"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "68px",
                      "textAlign": "right",
                      "marginRight": "8px"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "部门"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "Select",
                  "props": {
                    "placeholder": "请选择部门",
                    "style": {
                      "flex": 1
                    },
                    "options": [
                      {
                        "label": "研发中心",
                        "value": "rd"
                      },
                      {
                        "label": "产品中心",
                        "value": "pd"
                      },
                      {
                        "label": "运营中心",
                        "value": "op"
                      }
                    ]
                  },
                  "children": []
                }
              ]
            },
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "center"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "68px",
                      "textAlign": "right",
                      "marginRight": "8px"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "职位"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "Input",
                  "props": {
                    "placeholder": "请输入职位",
                    "style": {
                      "flex": 1
                    }
                  },
                  "children": []
                }
              ]
            },
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "flex-start"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "68px",
                      "textAlign": "right",
                      "marginRight": "8px",
                      "lineHeight": "32px"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "备注"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "TextArea",
                  "props": {
                    "placeholder": "请输入备注信息",
                    "rows": 4,
                    "style": {
                      "flex": 1
                    }
                  },
                  "children": []
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "Modal",
      "props": {
        "id": "modal_import_member",
        "title": "导入成员",
        "open": false,
        "footer": {
          "type": "Flex",
          "props": {
            "justify": "flex-end",
            "gap": 8
          },
          "children": [
            {
              "type": "Button",
              "props": {
                "type": "default",
                "children": "取消",
                "interactions": [
                  {
                    "trigger": "click",
                    "action": "SET_VISIBLE",
                    "target": "modal_import_member",
                    "payload": false
                  }
                ]
              },
              "children": []
            },
            {
              "type": "Button",
              "props": {
                "type": "primary",
                "children": "保存",
                "interactions": [
                  {
                    "trigger": "click",
                    "action": "SET_VISIBLE",
                    "target": "modal_import_member",
                    "payload": false
                  }
                ]
              },
              "children": []
            }
          ]
        },
        "dividers": false
      },
      "children": [
        {
          "type": "div",
          "props": {
            "style": {
              "border": "2px dashed #d9d9d9",
              "borderRadius": "8px",
              "padding": "40px 20px",
              "textAlign": "center",
              "backgroundColor": "#fafafa"
            }
          },
          "children": [
            {
              "type": "Typography.Text",
              "props": {},
              "children": [
                {
                  "type": "span",
                  "props": {
                    "children": "将文件拖到此处，或点击上传"
                  },
                  "children": []
                }
              ]
            },
            {
              "type": "div",
              "props": {
                "style": {
                  "marginTop": "8px"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "type": "secondary"
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "支持扩展名：.xls .xlsx"
                      },
                      "children": []
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "Modal",
      "props": {
        "id": "modal_export_member",
        "title": "导出成员",
        "open": false,
        "footer": {
          "type": "Flex",
          "props": {
            "justify": "flex-end",
            "gap": 8
          },
          "children": [
            {
              "type": "Button",
              "props": {
                "type": "default",
                "children": "取消",
                "interactions": [
                  {
                    "trigger": "click",
                    "action": "SET_VISIBLE",
                    "target": "modal_export_member",
                    "payload": false
                  }
                ]
              },
              "children": []
            },
            {
              "type": "Button",
              "props": {
                "type": "primary",
                "children": "保存",
                "interactions": [
                  {
                    "trigger": "click",
                    "action": "SET_VISIBLE",
                    "target": "modal_export_member",
                    "payload": false
                  }
                ]
              },
              "children": []
            }
          ]
        },
        "dividers": false
      },
      "children": [
        {
          "type": "Tree",
          "props": {
            "treeData": [
              {
                "title": "XX科技集团",
                "key": "root",
                "children": [
                  {
                    "title": "研发中心",
                    "key": "rd",
                    "children": [
                      {
                        "title": "前端部",
                        "key": "rd-fe"
                      },
                      {
                        "title": "后端部",
                        "key": "rd-be"
                      },
                      {
                        "title": "测试部",
                        "key": "rd-qa"
                      }
                    ]
                  },
                  {
                    "title": "产品中心",
                    "key": "pd"
                  }
                ]
              }
            ],
            "checkable": true,
            "defaultExpandAll": true,
            "style": {
              "maxHeight": "300px",
              "overflowY": "auto"
            }
          },
          "children": []
        }
      ]
    },
    {
      "type": "Modal",
      "props": {
        "id": "modal_member_detail",
        "title": "人员详情",
        "width": 640,
        "open": false,
        "footer": {
          "type": "Flex",
          "props": {
            "justify": "flex-end",
            "gap": 8
          },
          "children": [
            {
              "type": "Button",
              "props": {
                "type": "default",
                "children": "取消",
                "interactions": [
                  {
                    "trigger": "click",
                    "action": "SET_VISIBLE",
                    "target": "modal_member_detail",
                    "payload": false
                  }
                ]
              },
              "children": []
            },
            {
              "type": "Button",
              "props": {
                "type": "primary",
                "children": "保存",
                "interactions": [
                  {
                    "trigger": "click",
                    "action": "SET_VISIBLE",
                    "target": "modal_member_detail",
                    "payload": false
                  }
                ]
              },
              "children": []
            }
          ]
        },
        "dividers": false
      },
      "children": [
        {
          "type": "Flex",
          "props": {
            "gap": 24
          },
          "children": [
            {
              "type": "Flex",
              "props": {
                "vertical": true,
                "gap": 16,
                "style": {
                  "flex": 1
                }
              },
              "children": [
                {
                  "type": "div",
                  "props": {
                    "style": {
                      "display": "flex",
                      "alignItems": "center"
                    }
                  },
                  "children": [
                    {
                      "type": "Typography.Text",
                      "props": {
                        "style": {
                          "width": "80px",
                          "color": "rgba(0,0,0,0.45)"
                        }
                      },
                      "children": [
                        {
                          "type": "span",
                          "props": {
                            "children": "姓名"
                          },
                          "children": []
                        }
                      ]
                    },
                    {
                      "type": "Typography.Text",
                      "props": {},
                      "children": [
                        {
                          "type": "span",
                          "props": {
                            "children": "张三"
                          },
                          "children": []
                        }
                      ]
                    }
                  ]
                },
                {
                  "type": "div",
                  "props": {
                    "style": {
                      "display": "flex",
                      "alignItems": "center"
                    }
                  },
                  "children": [
                    {
                      "type": "Typography.Text",
                      "props": {
                        "style": {
                          "width": "80px",
                          "color": "rgba(0,0,0,0.45)"
                        }
                      },
                      "children": [
                        {
                          "type": "span",
                          "props": {
                            "children": "性别"
                          },
                          "children": []
                        }
                      ]
                    },
                    {
                      "type": "Typography.Text",
                      "props": {},
                      "children": [
                        {
                          "type": "span",
                          "props": {
                            "children": "男"
                          },
                          "children": []
                        }
                      ]
                    }
                  ]
                },
                {
                  "type": "div",
                  "props": {
                    "style": {
                      "display": "flex",
                      "alignItems": "center"
                    }
                  },
                  "children": [
                    {
                      "type": "Typography.Text",
                      "props": {
                        "style": {
                          "width": "80px",
                          "color": "rgba(0,0,0,0.45)"
                        }
                      },
                      "children": [
                        {
                          "type": "span",
                          "props": {
                            "children": "年龄"
                          },
                          "children": []
                        }
                      ]
                    },
                    {
                      "type": "Typography.Text",
                      "props": {},
                      "children": [
                        {
                          "type": "span",
                          "props": {
                            "children": "28"
                          },
                          "children": []
                        }
                      ]
                    }
                  ]
                },
                {
                  "type": "div",
                  "props": {
                    "style": {
                      "display": "flex",
                      "alignItems": "center"
                    }
                  },
                  "children": [
                    {
                      "type": "Typography.Text",
                      "props": {
                        "style": {
                          "width": "80px",
                          "color": "rgba(0,0,0,0.45)"
                        }
                      },
                      "children": [
                        {
                          "type": "span",
                          "props": {
                            "children": "手机号"
                          },
                          "children": []
                        }
                      ]
                    },
                    {
                      "type": "Typography.Text",
                      "props": {},
                      "children": [
                        {
                          "type": "span",
                          "props": {
                            "children": "13800138001"
                          },
                          "children": []
                        }
                      ]
                    }
                  ]
                }
              ]
            },
            {
              "type": "Flex",
              "props": {
                "vertical": true,
                "gap": 16,
                "style": {
                  "flex": 1
                }
              },
              "children": [
                {
                  "type": "div",
                  "props": {
                    "style": {
                      "display": "flex",
                      "alignItems": "center"
                    }
                  },
                  "children": [
                    {
                      "type": "Typography.Text",
                      "props": {
                        "style": {
                          "width": "80px",
                          "color": "rgba(0,0,0,0.45)"
                        }
                      },
                      "children": [
                        {
                          "type": "span",
                          "props": {
                            "children": "部门"
                          },
                          "children": []
                        }
                      ]
                    },
                    {
                      "type": "Typography.Text",
                      "props": {},
                      "children": [
                        {
                          "type": "span",
                          "props": {
                            "children": "研发中心/前端部"
                          },
                          "children": []
                        }
                      ]
                    }
                  ]
                },
                {
                  "type": "div",
                  "props": {
                    "style": {
                      "display": "flex",
                      "alignItems": "center"
                    }
                  },
                  "children": [
                    {
                      "type": "Typography.Text",
                      "props": {
                        "style": {
                          "width": "80px",
                          "color": "rgba(0,0,0,0.45)"
                        }
                      },
                      "children": [
                        {
                          "type": "span",
                          "props": {
                            "children": "职位"
                          },
                          "children": []
                        }
                      ]
                    },
                    {
                      "type": "Typography.Text",
                      "props": {},
                      "children": [
                        {
                          "type": "span",
                          "props": {
                            "children": "前端工程师"
                          },
                          "children": []
                        }
                      ]
                    }
                  ]
                },
                {
                  "type": "div",
                  "props": {
                    "style": {
                      "display": "flex",
                      "alignItems": "center"
                    }
                  },
                  "children": [
                    {
                      "type": "Typography.Text",
                      "props": {
                        "style": {
                          "width": "80px",
                          "color": "rgba(0,0,0,0.45)"
                        }
                      },
                      "children": [
                        {
                          "type": "span",
                          "props": {
                            "children": "员工编号"
                          },
                          "children": []
                        }
                      ]
                    },
                    {
                      "type": "Typography.Text",
                      "props": {},
                      "children": [
                        {
                          "type": "span",
                          "props": {
                            "children": "EMP1001"
                          },
                          "children": []
                        }
                      ]
                    }
                  ]
                },
                {
                  "type": "div",
                  "props": {
                    "style": {
                      "display": "flex",
                      "alignItems": "center"
                    }
                  },
                  "children": [
                    {
                      "type": "Typography.Text",
                      "props": {
                        "style": {
                          "width": "80px",
                          "color": "rgba(0,0,0,0.45)"
                        }
                      },
                      "children": [
                        {
                          "type": "span",
                          "props": {
                            "children": "入职日期"
                          },
                          "children": []
                        }
                      ]
                    },
                    {
                      "type": "Typography.Text",
                      "props": {},
                      "children": [
                        {
                          "type": "span",
                          "props": {
                            "children": "2021-03-15"
                          },
                          "children": []
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "Modal",
      "props": {
        "id": "modal_create_org",
        "title": "创建组织",
        "width": 480,
        "open": false,
        "footer": {
          "type": "Flex",
          "props": {
            "justify": "flex-end",
            "gap": 8
          },
          "children": [
            {
              "type": "Button",
              "props": {
                "type": "default",
                "children": "取消",
                "interactions": [
                  {
                    "trigger": "click",
                    "action": "SET_VISIBLE",
                    "target": "modal_create_org",
                    "payload": false
                  }
                ]
              },
              "children": []
            },
            {
              "type": "Button",
              "props": {
                "type": "primary",
                "children": "保存",
                "interactions": [
                  {
                    "trigger": "click",
                    "action": "SET_VISIBLE",
                    "target": "modal_create_org",
                    "payload": false
                  }
                ]
              },
              "children": []
            }
          ]
        },
        "dividers": false
      },
      "children": [
        {
          "type": "Flex",
          "props": {
            "vertical": true,
            "gap": 16
          },
          "children": [
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "center"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "68px",
                      "textAlign": "right",
                      "marginRight": "8px"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "组织名称"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "Input",
                  "props": {
                    "placeholder": "请输入组织名称",
                    "style": {
                      "flex": 1
                    }
                  },
                  "children": []
                }
              ]
            },
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "center"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "68px",
                      "textAlign": "right",
                      "marginRight": "8px"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "组织编码"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "Input",
                  "props": {
                    "placeholder": "请输入组织编码",
                    "style": {
                      "flex": 1
                    }
                  },
                  "children": []
                }
              ]
            },
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "center"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "68px",
                      "textAlign": "right",
                      "marginRight": "8px"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "上级组织"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "Select",
                  "props": {
                    "placeholder": "请选择上级组织",
                    "style": {
                      "flex": 1
                    },
                    "options": [
                      {
                        "label": "XX科技集团",
                        "value": "root"
                      },
                      {
                        "label": "研发中心",
                        "value": "rd"
                      },
                      {
                        "label": "产品中心",
                        "value": "pd"
                      }
                    ]
                  },
                  "children": []
                }
              ]
            },
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "center"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "68px",
                      "textAlign": "right",
                      "marginRight": "8px"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "负责人"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "Input",
                  "props": {
                    "placeholder": "请输入负责人",
                    "style": {
                      "flex": 1
                    }
                  },
                  "children": []
                }
              ]
            },
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "flex-start"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "68px",
                      "textAlign": "right",
                      "marginRight": "8px",
                      "lineHeight": "32px"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "描述"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "TextArea",
                  "props": {
                    "placeholder": "请输入组织描述",
                    "rows": 4,
                    "style": {
                      "flex": 1
                    }
                  },
                  "children": []
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "Modal",
      "props": {
        "id": "modal_org_detail",
        "title": "组织详情",
        "width": 640,
        "open": false,
        "footer": {
          "type": "Flex",
          "props": {
            "justify": "flex-end",
            "gap": 8
          },
          "children": [
            {
              "type": "Button",
              "props": {
                "type": "primary",
                "children": "关闭",
                "interactions": [
                  {
                    "trigger": "click",
                    "action": "SET_VISIBLE",
                    "target": "modal_org_detail",
                    "payload": false
                  }
                ]
              },
              "children": []
            }
          ]
        },
        "dividers": false
      },
      "children": [
        {
          "type": "Flex",
          "props": {
            "vertical": true,
            "gap": 12
          },
          "children": [
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "center"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "96px",
                      "color": "rgba(0,0,0,0.45)"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "组织名称"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "Typography.Text",
                  "props": {},
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "正大信息安全上海办事处"
                      },
                      "children": []
                    }
                  ]
                }
              ]
            },
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "center"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "96px",
                      "color": "rgba(0,0,0,0.45)"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "组织编码"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "Typography.Text",
                  "props": {},
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "SH-ZD-002"
                      },
                      "children": []
                    }
                  ]
                }
              ]
            },
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "center"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "96px",
                      "color": "rgba(0,0,0,0.45)"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "组织类型"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "Typography.Text",
                  "props": {},
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "二级组织"
                      },
                      "children": []
                    }
                  ]
                }
              ]
            },
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "center"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "96px",
                      "color": "rgba(0,0,0,0.45)"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "组织负责人"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "Typography.Text",
                  "props": {},
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "邱云云"
                      },
                      "children": []
                    }
                  ]
                }
              ]
            },
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "center"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "96px",
                      "color": "rgba(0,0,0,0.45)"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "审批主管"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "Typography.Text",
                  "props": {},
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "邱云"
                      },
                      "children": []
                    }
                  ]
                }
              ]
            },
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "center"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "96px",
                      "color": "rgba(0,0,0,0.45)"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "成立时间"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "Typography.Text",
                  "props": {},
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "2021-04-18"
                      },
                      "children": []
                    }
                  ]
                }
              ]
            },
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "center"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "96px",
                      "color": "rgba(0,0,0,0.45)"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "办公地点"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "Typography.Text",
                  "props": {},
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "上海市浦东新区"
                      },
                      "children": []
                    }
                  ]
                }
              ]
            },
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "center"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "96px",
                      "color": "rgba(0,0,0,0.45)"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "编制人数"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "Typography.Text",
                  "props": {},
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "100"
                      },
                      "children": []
                    }
                  ]
                }
              ]
            },
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "center"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "96px",
                      "color": "rgba(0,0,0,0.45)"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "在编人数"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "Typography.Text",
                  "props": {},
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "80"
                      },
                      "children": []
                    }
                  ]
                }
              ]
            },
            {
              "type": "div",
              "props": {
                "style": {
                  "display": "flex",
                  "alignItems": "center"
                }
              },
              "children": [
                {
                  "type": "Typography.Text",
                  "props": {
                    "style": {
                      "width": "96px",
                      "color": "rgba(0,0,0,0.45)"
                    }
                  },
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "下级组织数"
                      },
                      "children": []
                    }
                  ]
                },
                {
                  "type": "Typography.Text",
                  "props": {},
                  "children": [
                    {
                      "type": "span",
                      "props": {
                        "children": "8"
                      },
                      "children": []
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
