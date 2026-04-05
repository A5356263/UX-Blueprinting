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
                        "label": "人员管理",
                        "icon": "UserOutlined",
                        "children": [
                          {
                            "key": "1-1",
                            "label": "成员管理"
                          },
                          {
                            "key": "1-2",
                            "label": "组织管理"
                          },
                          {
                            "key": "1-3",
                            "label": "岗位管理"
                          }
                        ]
                      },
                      {
                        "key": "2",
                        "label": "在职管理",
                        "icon": "TeamOutlined",
                        "children": [
                          {
                            "key": "2-1",
                            "label": "在职信息"
                          },
                          {
                            "key": "2-2",
                            "label": "薪酬社保"
                          }
                        ]
                      },
                      {
                        "key": "3",
                        "label": "发展管理",
                        "icon": "AppstoreOutlined",
                        "children": [
                          {
                            "key": "3-1",
                            "label": "培训记录"
                          },
                          {
                            "key": "3-2",
                            "label": "绩效考核"
                          }
                        ]
                      },
                      {
                        "key": "4",
                        "label": "扩展菜单1",
                        "children": [
                          {
                            "key": "4-1",
                            "label": "二级菜单1-1"
                          },
                          {
                            "key": "4-2",
                            "label": "二级菜单1-2"
                          }
                        ],
                        "icon": "FileOutlined"
                      },
                      {
                        "key": "5",
                        "label": "扩展菜单2",
                        "children": [
                          {
                            "key": "5-1",
                            "label": "二级菜单2-1"
                          },
                          {
                            "key": "5-2",
                            "label": "二级菜单2-2"
                          }
                        ],
                        "icon": "SafetyCertificateOutlined"
                      },
                      {
                        "key": "6",
                        "label": "扩展菜单3",
                        "children": [
                          {
                            "key": "6-1",
                            "label": "二级菜单3-1"
                          },
                          {
                            "key": "6-2",
                            "label": "二级菜单3-2"
                          }
                        ],
                        "icon": "BarChartOutlined"
                      },
                      {
                        "key": "7",
                        "label": "扩展菜单4",
                        "children": [
                          {
                            "key": "7-1",
                            "label": "二级菜单4-1"
                          },
                          {
                            "key": "7-2",
                            "label": "二级菜单4-2"
                          }
                        ],
                        "icon": "PieChartOutlined"
                      },
                      {
                        "key": "8",
                        "label": "扩展菜单5",
                        "children": [
                          {
                            "key": "8-1",
                            "label": "二级菜单5-1"
                          },
                          {
                            "key": "8-2",
                            "label": "二级菜单5-2"
                          }
                        ],
                        "icon": "MailOutlined"
                      },
                      {
                        "key": "9",
                        "label": "扩展菜单6",
                        "children": [
                          {
                            "key": "9-1",
                            "label": "二级菜单6-1"
                          },
                          {
                            "key": "9-2",
                            "label": "二级菜单6-2"
                          }
                        ],
                        "icon": "BellOutlined"
                      }
                    ]
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
                          "type": "div",
                          "props": {
                            "style": {
                              "width": "220px",
                              "minWidth": "220px",
                              "maxWidth": "220px",
                              "height": "100%",
                              "overflow": "hidden",
                              "borderRight": "1px solid #f0f0f0",
                              "paddingRight": "12px"
                            }
                          },
                          "children": [
                            {
                              "type": "Anchor",
                              "props": {
                                "affix": false,
                                "containerId": "employee-form-scroll",
                                "targetOffset": 12,
                                "items": [
                                  {
                                    "key": "section_basic",
                                    "href": "#section_basic",
                                    "title": "基本信息"
                                  },
                                  {
                                    "key": "section_job",
                                    "href": "#section_job",
                                    "title": "在职信息"
                                  },
                                  {
                                    "key": "section_salary",
                                    "href": "#section_salary",
                                    "title": "工资社保"
                                  },
                                  {
                                    "key": "section_personal",
                                    "href": "#section_personal",
                                    "title": "个人信息"
                                  },
                                  {
                                    "key": "section_emergency",
                                    "href": "#section_emergency",
                                    "title": "紧急联系人"
                                  },
                                  {
                                    "key": "section_education",
                                    "href": "#section_education",
                                    "title": "教育经历"
                                  },
                                  {
                                    "key": "section_work",
                                    "href": "#section_work",
                                    "title": "工作经历"
                                  },
                                  {
                                    "key": "section_family",
                                    "href": "#section_family",
                                    "title": "家庭成员"
                                  },
                                  {
                                    "key": "section_cert",
                                    "href": "#section_cert",
                                    "title": "专业证书"
                                  },
                                  {
                                    "key": "section_reward",
                                    "href": "#section_reward",
                                    "title": "奖惩记录"
                                  },
                                  {
                                    "key": "section_title",
                                    "href": "#section_title",
                                    "title": "职称"
                                  },
                                  {
                                    "key": "section_training",
                                    "href": "#section_training",
                                    "title": "培训记录"
                                  },
                                  {
                                    "key": "section_perf",
                                    "href": "#section_perf",
                                    "title": "绩效考核"
                                  },
                                  {
                                    "key": "section_material",
                                    "href": "#section_material",
                                    "title": "个人材料"
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
                            "id": "employee-form-scroll",
                            "style": {
                              "flex": 1,
                              "minWidth": 0,
                              "height": "100%",
                              "overflowY": "auto",
                              "overflowX": "hidden",
                              "paddingRight": "8px",
                              "boxSizing": "border-box"
                            }
                          },
                          "children": [
                            {
                              "type": "Form",
                              "props": {
                                "layout": "horizontal",
                                "labelCol": {
                                  "span": 7
                                },
                                "wrapperCol": {
                                  "span": 17
                                },
                                "style": {
                                  "width": "100%"
                                }
                              },
                              "children": [
                                {
                                  "type": "div",
                                  "props": {
                                    "id": "section_basic",
                                    "style": {
                                      "marginBottom": "28px",
                                      "paddingTop": "2px"
                                    }
                                  },
                                  "children": [
                                    {
                                      "type": "Typography.Title",
                                      "props": {
                                        "level": 4,
                                        "style": {
                                          "marginBottom": "12px",
                                          "borderLeft": "3px solid #1677ff",
                                          "paddingLeft": "8px"
                                        }
                                      },
                                      "children": [
                                        {
                                          "type": "span",
                                          "props": {
                                            "children": "基本信息"
                                          },
                                          "children": []
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "员工号",
                                                "name": "employeeNo",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "系统自动生成"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "* 手机号",
                                                "name": "mobile",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "* 姓名",
                                                "name": "name",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "别名",
                                                "name": "nickname",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "曾用名",
                                                "name": "oldName",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "* 部门",
                                                "name": "secondDept",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请选择"
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "职位",
                                                "name": "jobTitle",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请选择"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "工作邮箱",
                                                "name": "workEmail",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "兼职",
                                                "name": "partTimeRole",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请选择"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "汇报上级",
                                                "name": "landline",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
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
                                  "type": "div",
                                  "props": {
                                    "id": "section_job",
                                    "style": {
                                      "marginBottom": "28px",
                                      "paddingTop": "2px"
                                    }
                                  },
                                  "children": [
                                    {
                                      "type": "Typography.Title",
                                      "props": {
                                        "level": 4,
                                        "style": {
                                          "marginBottom": "12px",
                                          "borderLeft": "3px solid #1677ff",
                                          "paddingLeft": "8px"
                                        }
                                      },
                                      "children": [
                                        {
                                          "type": "span",
                                          "props": {
                                            "children": "在职信息"
                                          },
                                          "children": []
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "在职信息字段1",
                                                "name": "department",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Select",
                                                  "props": {
                                                    "placeholder": "请选择",
                                                    "options": [
                                                      {
                                                        "label": "选项1",
                                                        "value": "rd"
                                                      },
                                                      {
                                                        "label": "选项2",
                                                        "value": "pd"
                                                      },
                                                      {
                                                        "label": "选项3",
                                                        "value": "op"
                                                      }
                                                    ]
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "在职信息字段2",
                                                "name": "position",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Select",
                                                  "props": {
                                                    "placeholder": "请选择",
                                                    "options": [
                                                      {
                                                        "label": "选项4",
                                                        "value": "fe"
                                                      },
                                                      {
                                                        "label": "选项5",
                                                        "value": "be"
                                                      },
                                                      {
                                                        "label": "选项6",
                                                        "value": "pm"
                                                      }
                                                    ]
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "在职信息字段3",
                                                "name": "rank",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Select",
                                                  "props": {
                                                    "placeholder": "请选择",
                                                    "options": [
                                                      {
                                                        "label": "P5",
                                                        "value": "P5"
                                                      },
                                                      {
                                                        "label": "P6",
                                                        "value": "P6"
                                                      },
                                                      {
                                                        "label": "P7",
                                                        "value": "P7"
                                                      }
                                                    ]
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "在职信息字段4",
                                                "name": "bizGroup",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Select",
                                                  "props": {
                                                    "placeholder": "请选择",
                                                    "options": [
                                                      {
                                                        "label": "选项7",
                                                        "value": "platform"
                                                      },
                                                      {
                                                        "label": "选项8",
                                                        "value": "business"
                                                      }
                                                    ]
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "在职信息字段5",
                                                "name": "leader",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "在职信息字段6",
                                                "name": "workLocation",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Select",
                                                  "props": {
                                                    "placeholder": "请选择",
                                                    "options": [
                                                      {
                                                        "label": "选项9",
                                                        "value": "sh"
                                                      },
                                                      {
                                                        "label": "选项10",
                                                        "value": "bj"
                                                      },
                                                      {
                                                        "label": "选项11",
                                                        "value": "sz"
                                                      }
                                                    ]
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "在职信息字段7",
                                                "name": "entryDate",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "DatePicker",
                                                  "props": {
                                                    "style": {
                                                      "width": "100%"
                                                    }
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "在职信息字段8",
                                                "name": "regularDate",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "DatePicker",
                                                  "props": {
                                                    "style": {
                                                      "width": "100%"
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "在职信息字段9",
                                                "name": "contractEndDate",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "DatePicker",
                                                  "props": {
                                                    "style": {
                                                      "width": "100%"
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
                                },
                                {
                                  "type": "div",
                                  "props": {
                                    "id": "section_salary",
                                    "style": {
                                      "marginBottom": "28px",
                                      "paddingTop": "2px"
                                    }
                                  },
                                  "children": [
                                    {
                                      "type": "Typography.Title",
                                      "props": {
                                        "level": 4,
                                        "style": {
                                          "marginBottom": "12px",
                                          "borderLeft": "3px solid #1677ff",
                                          "paddingLeft": "8px"
                                        }
                                      },
                                      "children": [
                                        {
                                          "type": "span",
                                          "props": {
                                            "children": "工资社保"
                                          },
                                          "children": []
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "工资社保字段1",
                                                "name": "baseSalary",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "InputNumber",
                                                  "props": {
                                                    "placeholder": "请输入",
                                                    "style": {
                                                      "width": "100%"
                                                    }
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "工资社保字段2",
                                                "name": "performanceSalary",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "InputNumber",
                                                  "props": {
                                                    "placeholder": "请输入",
                                                    "style": {
                                                      "width": "100%"
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "工资社保字段3",
                                                "name": "socialCity",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Select",
                                                  "props": {
                                                    "placeholder": "请选择",
                                                    "options": [
                                                      {
                                                        "label": "选项12",
                                                        "value": "sh"
                                                      },
                                                      {
                                                        "label": "选项13",
                                                        "value": "bj"
                                                      },
                                                      {
                                                        "label": "选项14",
                                                        "value": "sz"
                                                      }
                                                    ]
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "工资社保字段4",
                                                "name": "socialBase",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "InputNumber",
                                                  "props": {
                                                    "placeholder": "请输入",
                                                    "style": {
                                                      "width": "100%"
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "工资社保字段5",
                                                "name": "fundRate",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "InputNumber",
                                                  "props": {
                                                    "placeholder": "请输入",
                                                    "style": {
                                                      "width": "100%"
                                                    }
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "工资社保字段6",
                                                "name": "taxDeduction",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "InputNumber",
                                                  "props": {
                                                    "placeholder": "请输入",
                                                    "style": {
                                                      "width": "100%"
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
                                },
                                {
                                  "type": "div",
                                  "props": {
                                    "id": "section_personal",
                                    "style": {
                                      "marginBottom": "28px",
                                      "paddingTop": "2px"
                                    }
                                  },
                                  "children": [
                                    {
                                      "type": "Typography.Title",
                                      "props": {
                                        "level": 4,
                                        "style": {
                                          "marginBottom": "12px",
                                          "borderLeft": "3px solid #1677ff",
                                          "paddingLeft": "8px"
                                        }
                                      },
                                      "children": [
                                        {
                                          "type": "span",
                                          "props": {
                                            "children": "个人信息"
                                          },
                                          "children": []
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "个人信息字段1",
                                                "name": "idNo",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "个人信息字段2",
                                                "name": "email",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "个人信息字段3",
                                                "name": "nation",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "个人信息字段4",
                                                "name": "hukouAddress",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
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
                                  "type": "div",
                                  "props": {
                                    "id": "section_emergency",
                                    "style": {
                                      "marginBottom": "28px",
                                      "paddingTop": "2px"
                                    }
                                  },
                                  "children": [
                                    {
                                      "type": "Typography.Title",
                                      "props": {
                                        "level": 4,
                                        "style": {
                                          "marginBottom": "12px",
                                          "borderLeft": "3px solid #1677ff",
                                          "paddingLeft": "8px"
                                        }
                                      },
                                      "children": [
                                        {
                                          "type": "span",
                                          "props": {
                                            "children": "紧急联系人"
                                          },
                                          "children": []
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "紧急联系人字段1",
                                                "name": "emergencyName",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "紧急联系人字段2",
                                                "name": "emergencyPhone",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "紧急联系人字段3",
                                                "name": "emergencyRelation",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "紧急联系人字段4",
                                                "name": "emergencyAddress",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
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
                                  "type": "div",
                                  "props": {
                                    "id": "section_education",
                                    "style": {
                                      "marginBottom": "28px",
                                      "paddingTop": "2px"
                                    }
                                  },
                                  "children": [
                                    {
                                      "type": "Typography.Title",
                                      "props": {
                                        "level": 4,
                                        "style": {
                                          "marginBottom": "12px",
                                          "borderLeft": "3px solid #1677ff",
                                          "paddingLeft": "8px"
                                        }
                                      },
                                      "children": [
                                        {
                                          "type": "span",
                                          "props": {
                                            "children": "教育经历"
                                          },
                                          "children": []
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "教育经历字段1",
                                                "name": "degree",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Select",
                                                  "props": {
                                                    "placeholder": "请选择",
                                                    "options": [
                                                      {
                                                        "label": "选项15",
                                                        "value": "bachelor"
                                                      },
                                                      {
                                                        "label": "选项16",
                                                        "value": "master"
                                                      },
                                                      {
                                                        "label": "选项17",
                                                        "value": "doctor"
                                                      }
                                                    ]
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "教育经历字段2",
                                                "name": "school",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "教育经历字段3",
                                                "name": "major",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "教育经历字段4",
                                                "name": "graduationDate",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "DatePicker",
                                                  "props": {
                                                    "style": {
                                                      "width": "100%"
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
                                },
                                {
                                  "type": "div",
                                  "props": {
                                    "id": "section_work",
                                    "style": {
                                      "marginBottom": "28px",
                                      "paddingTop": "2px"
                                    }
                                  },
                                  "children": [
                                    {
                                      "type": "Typography.Title",
                                      "props": {
                                        "level": 4,
                                        "style": {
                                          "marginBottom": "12px",
                                          "borderLeft": "3px solid #1677ff",
                                          "paddingLeft": "8px"
                                        }
                                      },
                                      "children": [
                                        {
                                          "type": "span",
                                          "props": {
                                            "children": "工作经历"
                                          },
                                          "children": []
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "工作经历字段1",
                                                "name": "lastCompany",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "工作经历字段2",
                                                "name": "lastPosition",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "工作经历字段3",
                                                "name": "lastEntryDate",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "DatePicker",
                                                  "props": {
                                                    "style": {
                                                      "width": "100%"
                                                    }
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "工作经历字段4",
                                                "name": "lastLeaveDate",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "DatePicker",
                                                  "props": {
                                                    "style": {
                                                      "width": "100%"
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
                                },
                                {
                                  "type": "div",
                                  "props": {
                                    "id": "section_family",
                                    "style": {
                                      "marginBottom": "28px",
                                      "paddingTop": "2px"
                                    }
                                  },
                                  "children": [
                                    {
                                      "type": "Typography.Title",
                                      "props": {
                                        "level": 4,
                                        "style": {
                                          "marginBottom": "12px",
                                          "borderLeft": "3px solid #1677ff",
                                          "paddingLeft": "8px"
                                        }
                                      },
                                      "children": [
                                        {
                                          "type": "span",
                                          "props": {
                                            "children": "家庭成员"
                                          },
                                          "children": []
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "家庭成员字段1",
                                                "name": "familyName",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "家庭成员字段2",
                                                "name": "familyRelation",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "家庭成员字段3",
                                                "name": "familyPhone",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "家庭成员字段4",
                                                "name": "familyCompany",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
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
                                  "type": "div",
                                  "props": {
                                    "id": "section_cert",
                                    "style": {
                                      "marginBottom": "28px",
                                      "paddingTop": "2px"
                                    }
                                  },
                                  "children": [
                                    {
                                      "type": "Typography.Title",
                                      "props": {
                                        "level": 4,
                                        "style": {
                                          "marginBottom": "12px",
                                          "borderLeft": "3px solid #1677ff",
                                          "paddingLeft": "8px"
                                        }
                                      },
                                      "children": [
                                        {
                                          "type": "span",
                                          "props": {
                                            "children": "专业证书"
                                          },
                                          "children": []
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "专业证书字段1",
                                                "name": "certName",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "专业证书字段2",
                                                "name": "certNo",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "专业证书字段3",
                                                "name": "certDate",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "DatePicker",
                                                  "props": {
                                                    "style": {
                                                      "width": "100%"
                                                    }
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "专业证书字段4",
                                                "name": "certExpireDate",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "DatePicker",
                                                  "props": {
                                                    "style": {
                                                      "width": "100%"
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
                                },
                                {
                                  "type": "div",
                                  "props": {
                                    "id": "section_reward",
                                    "style": {
                                      "marginBottom": "28px",
                                      "paddingTop": "2px"
                                    }
                                  },
                                  "children": [
                                    {
                                      "type": "Typography.Title",
                                      "props": {
                                        "level": 4,
                                        "style": {
                                          "marginBottom": "12px",
                                          "borderLeft": "3px solid #1677ff",
                                          "paddingLeft": "8px"
                                        }
                                      },
                                      "children": [
                                        {
                                          "type": "span",
                                          "props": {
                                            "children": "奖惩记录"
                                          },
                                          "children": []
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "奖惩记录字段1",
                                                "name": "rewardType",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "奖惩记录字段2",
                                                "name": "rewardDate",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "DatePicker",
                                                  "props": {
                                                    "style": {
                                                      "width": "100%"
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "奖惩记录字段3",
                                                "name": "rewardOrg",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
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
                                  "type": "div",
                                  "props": {
                                    "id": "section_title",
                                    "style": {
                                      "marginBottom": "28px",
                                      "paddingTop": "2px"
                                    }
                                  },
                                  "children": [
                                    {
                                      "type": "Typography.Title",
                                      "props": {
                                        "level": 4,
                                        "style": {
                                          "marginBottom": "12px",
                                          "borderLeft": "3px solid #1677ff",
                                          "paddingLeft": "8px"
                                        }
                                      },
                                      "children": [
                                        {
                                          "type": "span",
                                          "props": {
                                            "children": "职称"
                                          },
                                          "children": []
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "职称字段1",
                                                "name": "titleName",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "职称字段2",
                                                "name": "titleDate",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "DatePicker",
                                                  "props": {
                                                    "style": {
                                                      "width": "100%"
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "职称字段3",
                                                "name": "titleOrg",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "职称字段4",
                                                "name": "titleCertNo",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
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
                                  "type": "div",
                                  "props": {
                                    "id": "section_training",
                                    "style": {
                                      "marginBottom": "28px",
                                      "paddingTop": "2px"
                                    }
                                  },
                                  "children": [
                                    {
                                      "type": "Typography.Title",
                                      "props": {
                                        "level": 4,
                                        "style": {
                                          "marginBottom": "12px",
                                          "borderLeft": "3px solid #1677ff",
                                          "paddingLeft": "8px"
                                        }
                                      },
                                      "children": [
                                        {
                                          "type": "span",
                                          "props": {
                                            "children": "培训记录"
                                          },
                                          "children": []
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "培训记录字段1",
                                                "name": "trainTopic",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "培训记录字段2",
                                                "name": "trainDate",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "DatePicker",
                                                  "props": {
                                                    "style": {
                                                      "width": "100%"
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "培训记录字段3",
                                                "name": "trainOrg",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "培训记录字段4",
                                                "name": "trainHours",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
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
                                  "type": "div",
                                  "props": {
                                    "id": "section_perf",
                                    "style": {
                                      "marginBottom": "28px",
                                      "paddingTop": "2px"
                                    }
                                  },
                                  "children": [
                                    {
                                      "type": "Typography.Title",
                                      "props": {
                                        "level": 4,
                                        "style": {
                                          "marginBottom": "12px",
                                          "borderLeft": "3px solid #1677ff",
                                          "paddingLeft": "8px"
                                        }
                                      },
                                      "children": [
                                        {
                                          "type": "span",
                                          "props": {
                                            "children": "绩效考核"
                                          },
                                          "children": []
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "绩效考核字段1",
                                                "name": "perfCycle",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "绩效考核字段2",
                                                "name": "perfLevel",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Select",
                                                  "props": {
                                                    "placeholder": "请选择",
                                                    "options": [
                                                      {
                                                        "label": "A",
                                                        "value": "A"
                                                      },
                                                      {
                                                        "label": "B",
                                                        "value": "B"
                                                      },
                                                      {
                                                        "label": "C",
                                                        "value": "C"
                                                      }
                                                    ]
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "绩效考核字段3",
                                                "name": "perfReviewer",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "绩效考核字段4",
                                                "name": "perfDate",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "DatePicker",
                                                  "props": {
                                                    "style": {
                                                      "width": "100%"
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
                                },
                                {
                                  "type": "div",
                                  "props": {
                                    "id": "section_material",
                                    "style": {
                                      "marginBottom": "28px",
                                      "paddingTop": "2px"
                                    }
                                  },
                                  "children": [
                                    {
                                      "type": "Typography.Title",
                                      "props": {
                                        "level": 4,
                                        "style": {
                                          "marginBottom": "12px",
                                          "borderLeft": "3px solid #1677ff",
                                          "paddingLeft": "8px"
                                        }
                                      },
                                      "children": [
                                        {
                                          "type": "span",
                                          "props": {
                                            "children": "个人材料"
                                          },
                                          "children": []
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "个人材料字段1",
                                                "name": "materialName",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "个人材料字段2",
                                                "name": "materialNo",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "个人材料字段3",
                                                "name": "materialLocation",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "个人材料字段4",
                                                "name": "materialKeeper",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
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
                                  "type": "div",
                                  "props": {
                                    "id": "section_union",
                                    "style": {
                                      "marginBottom": "28px",
                                      "paddingTop": "2px"
                                    }
                                  },
                                  "children": [
                                    {
                                      "type": "Typography.Title",
                                      "props": {
                                        "level": 4,
                                        "style": {
                                          "marginBottom": "12px",
                                          "borderLeft": "3px solid #1677ff",
                                          "paddingLeft": "8px"
                                        }
                                      },
                                      "children": [
                                        {
                                          "type": "span",
                                          "props": {
                                            "children": "工会信息"
                                          },
                                          "children": []
                                        }
                                      ]
                                    },
                                    {
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "工会信息字段1",
                                                "name": "unionNo",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
                                                  },
                                                  "children": []
                                                }
                                              ]
                                            }
                                          ]
                                        },
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "工会信息字段2",
                                                "name": "unionStatus",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "Input",
                                                  "props": {
                                                    "placeholder": "请输入"
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
                                      "type": "Row",
                                      "props": {
                                        "gutter": [
                                          16,
                                          0
                                        ]
                                      },
                                      "children": [
                                        {
                                          "type": "Col",
                                          "props": {
                                            "span": 12
                                          },
                                          "children": [
                                            {
                                              "type": "Form.Item",
                                              "props": {
                                                "label": "工会信息字段3",
                                                "name": "unionJoinDate",
                                                "style": {
                                                  "marginBottom": "12px"
                                                }
                                              },
                                              "children": [
                                                {
                                                  "type": "DatePicker",
                                                  "props": {
                                                    "style": {
                                                      "width": "100%"
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
                                },
                                {
                                  "type": "Flex",
                                  "props": {
                                    "justify": "flex-start",
                                    "gap": 12,
                                    "style": {
                                      "position": "sticky",
                                      "bottom": 0,
                                      "zIndex": 5,
                                      "backgroundColor": "#fff",
                                      "borderTop": "1px solid #f0f0f0",
                                      "padding": "12px 0 12px",
                                      "marginTop": "8px"
                                    }
                                  },
                                  "children": [
                                    {
                                      "type": "Button",
                                      "props": {
                                        "type": "default",
                                        "children": "取消"
                                      },
                                      "children": []
                                    },
                                    {
                                      "type": "Button",
                                      "props": {
                                        "type": "primary",
                                        "children": "保存"
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
        }
      ]
    }
  ]
}
