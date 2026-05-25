"""Setup Case 005: 刁钻版自助申请权限 - source files + route_decision.json"""
import sys
sys.path.insert(0, '.')
from packages.common import get_project_source_dir, get_project_runtime_dir, get_knowledge_root_dir
import os, json

project_id = 'uxb-qc-005-self-service-permission-tricky'
repo_root = os.path.dirname(str(get_knowledge_root_dir()))
kroot = str(get_knowledge_root_dir())

# Write source files
src_dir = str(get_project_source_dir(project_id))
inp = os.path.join(repo_root, 'uxb_mainline_quality_test_pack', 'inputs', '需求文档_005_自助申请权限.md')
open(os.path.join(src_dir, 'requirement.md'), 'w', encoding='utf-8').write(open(inp, encoding='utf-8').read())
open(os.path.join(src_dir, 'background.md'), 'w', encoding='utf-8').write('# Background\n\n本测试仅使用 requirement.md 中的信息，不额外补充背景。\n')

def find_files(subpath):
    d = os.path.join(kroot, subpath)
    if not os.path.exists(d): return []
    result = []
    for root, dirs, files in os.walk(d):
        for f in files:
            if f.endswith('.md') and f != 'README.md':
                full = os.path.join(root, f)
                rel = os.path.relpath(full, repo_root).replace('\\', '/')
                result.append(rel)
    return sorted(result)

def select_by_prefix(files, prefixes):
    selected = []
    for f in files:
        basename = os.path.basename(f)
        for prefix in prefixes:
            if basename.startswith(prefix):
                selected.append(f)
                break
    return selected

perm_files = find_files('raw/业务/权限管理')
approval_files = find_files('raw/业务/审批管理')
guide_files = find_files('raw/设计准则')

# === Case 005: 刁钻版自助申请权限 ===
# This is a tricky version: explicit conflicts, misleading suggestions ("先授权后审批"),
# ambiguous role definitions. The knowledge selection needs to support:
# 1. Identifying conflicts against existing rules
# 2. Resisting misleading suggestions
# 3. Distinguishing what must be confirmed vs what can be recommended

biz_refs = select_by_prefix(perm_files, [
    '00_',  # Domain overview - where does self-service fit?
    '01_',  # Scope/boundary - what can employees actually apply for?
    '02_',  # Glossary - unified terminology for conflict resolution
    '03_',  # Business rules - compare with existing rules to identify conflicts
    '04_',  # Object relationships - employee-permission-approval entities
    '14_',  # Role boundaries - who can do what? (critical for conflicting role claims)
    '21_',  # Source model - critical: can "temporary pre-approval" be a valid source?
    '24_',  # Governance state model - critical: pre-approval state doesn't exist in current model
    '30_',  # Experience risk patterns - critical: identify security risks in misleading suggestions
])
biz_refs.extend(approval_files)

guide_refs = []
for f in guide_files:
    basename = os.path.basename(f)
    if basename.startswith('可用性') or basename.startswith('流程模式') or basename.startswith('信息架构') or basename.startswith('认知'):
        guide_refs.append(f)
for f in guide_files:
    if '反馈与报错' in f and '00_' in os.path.basename(f):
        guide_refs.append(f)

# Build selection_reasons - FRESH, based on this specific tricky requirement
reasons = []
for ref in biz_refs:
    basename = os.path.basename(ref)
    prefix = basename[:3] if basename[0].isdigit() else ''
    if prefix == '00_':
        r = '理解权限管理整体定位——确认自助申请在权限体系中的位置。本次需求存在"临时授权+审批拒绝后回收"的争议方案，需要先理解正常权限来源模型才能判断这个方案是否合理'
    elif prefix == '01_':
        r = '判断自助申请的能力边界——需求中"默认全部可申请"和"只能申请白名单内权限"是两个冲突的说法。需要用范围与边界知识来判断哪种更合理'
    elif prefix == '02_':
        r = '统一术语定义——需求中出现了"临时授权""先授权后审批""自动通过"等多个非标准表述，需要用术语表来校准'
    elif prefix == '03_':
        r = '比对现有业务规则——需求中"提交后先临时获得权限"的说法与现有权限规则存在冲突。需要先理解现有规则才能判断冲突的严重性'
    elif prefix == '04_':
        r = '理解员工-权限-角色-审批的实体关系——需求中"管理员也可能处理申请"模糊了管理员和审批人的边界，需要对象关系来澄清'
    elif prefix == '14_':
        r = '定义角色边界——需求中权限管理员的角色不明确（能否开启能力未确认），审批人的身份不明确（默认是谁未定），需要角色边界知识来定义'
    elif prefix == '21_':
        r = '关键知识：判断"临时授权"能否作为有效的权限状态——现有来源模型中没有"先授权后审批"的先例。"临时授权+审批拒绝后回收"是一个高风险方案，需要来源模型知识来评估其合理性'
    elif prefix == '24_':
        r = '关键知识：现有状态模型中只有draft/pending/approved/rejected/effective/revoked，没有"临时生效(temporary_effective)"状态。"先授权后审批"要求新增一个状态——这需要治理状态模型来判断是否可行'
    elif prefix == '30_':
        r = '关键知识：识别需求中的安全风险——"先授权后审批"(RISK-007)、"默认全部可申请"(RISK-001)、"审批人缺失时自动通过"(RISK-006)。这些诱导性建议对应多类已知风险'
    else:
        r = '理解审批流程设计规则——需求中审批人默认谁、审批人缺失时转交还是自动通过、是否多级审批，都需要审批管理知识来判断'
    reasons.append({'ref': ref, 'reason': r})

for ref in guide_refs:
    basename = os.path.basename(ref)
    if '可用性' in basename:
        r = '指导员工端申请流程的可用性设计——需求提到"无权限页展示申请按钮"，需要可用性知识来设计合理的申请入口'
    elif '流程模式' in basename:
        r = '指导管理端配置流程和审批流程的模式选择——需求有多方冲突说法，体验方案需要在不确定中保持可用'
    elif '信息架构' in basename:
        r = '指导员工端权限查看和申请记录的信息组织——需求中员工是否能看到权限来源未确认'
    elif '认知' in basename:
        r = '指导员工对"权限申请"和"权限生效"的认知——需求中"先授权后审批"可能让员工以为提交即生效'
    elif '反馈' in ref:
        r = '指导审批结果、冲突提示、异常状态等场景的反馈文案——需求中多个冲突点需要在体验层面给用户明确反馈'
    else:
        r = '支撑体验设计'
    reasons.append({'ref': ref, 'reason': r})

decision = {
    'schema_version': 'uxb_route_decision@3.0',
    'created_by': 'uxb_ai',
    'confirmed_by_user': True,
    'can_execute_mainline': True,
    'judgment': {
        'demand_type': 'complex_business_capability',
        'business_depth': 'full',
        'experience_output': 'full_blueprint',
        'reason': '本需求是新增"员工自助申请权限"业务通道。需求文档包含6对显式冲突（生效时机/可申请范围/敏感权限/关闭影响/服务人员/审批人缺失）和多个诱导性建议（"先授权后审批""默认全部可申请""自动通过"）。核心工作不仅是做业务方案设计，更重要的是识别冲突、拒绝不合理的诱导性建议、对无法确认的冲突标记GAP。不能顺水推舟地接受所有业务方想法。'
    },
    'complexity_judgment': {
        'business_change': 'deep',
        'business_change_reason': '引入新的权限来源路径。需求中"先授权后审批"的方案如果实施，将需要在权限状态模型中新增"临时生效(temporary_effective)"状态——这是对现有状态模型的重大变更。此外还与已有治理模式存在互斥可能。',
        'experience_pressure': 'high',
        'experience_pressure_reason': '涉及管理端/员工端/审批端三侧。需求中6对冲突需要在方案中明确立场，不能模棱两可。诱导性建议需要被识别和拒绝。',
        'uncertainties': [
            {'item': '生效时机：先临时授权后审批 vs 审批通过后才授权（冲突1）', 'type': 'blocking', 'reason': '这是安全红线——"先授权后审批"在现有权限模型中无先例，且存在越权访问风险。必须拒绝"先授权"，采用"审批通过后授权"。这是不可妥协的安全原则'},
            {'item': '可申请范围：默认全部可申请 vs 仅白名单内权限（冲突2）', 'type': 'blocking', 'reason': '安全团队vs业务方的立场冲突。默认全部可申请存在严重安全风险——必须采用白名单模式'},
            {'item': '敏感权限：可申请（审批同意即放）vs 不允许自助申请（冲突3）', 'type': 'blocking', 'reason': '敏感权限如果允许自助申请，即使有审批也可能被社会工程攻击绕过。建议默认排除敏感权限'},
            {'item': '关闭能力后：回收已授权权限 vs 仅关闭入口（冲突4）', 'type': 'blocking', 'reason': '影响关闭能力的设计和员工体验。建议关闭时不回收已授权权限，但需产品确认'},
            {'item': '审批人缺失时：转交超管 vs 自动通过 vs 禁止提交（冲突6）', 'type': 'blocking', 'reason': '"自动通过"是完全不可接受的安全风险——等于审批形同虚设'},
            {'item': '服务人员是否开放（冲突5）', 'type': 'non_blocking', 'reason': '可在方案中建议不开放，不阻断整体设计'},
            {'item': '审批人默认是谁', 'type': 'non_blocking', 'reason': '可在方案中建议默认组织负责人'},
            {'item': '是否支持多级审批', 'type': 'non_blocking', 'reason': '可在方案中建议支持'},
            {'item': '员工能否申请管理员权限', 'type': 'blocking', 'reason': '涉及权限体系的角色边界安全'},
            {'item': '员工能否替别人申请权限', 'type': 'non_blocking', 'reason': '可在方案中建议不支持'}
        ]
    },
    'knowledge_selection': {
        'business_refs': biz_refs,
        'guideline_refs': guide_refs,
        'complexity_refs': [],
        'selection_reasons': reasons
    },
    'execution': {
        'required_outputs': ['facts.md', 'business_blueprint.md', 'experience_blueprint.md', 'gap_list.md', 'check_report.md'],
        'notes': [
            '需求包含6对冲突和多个诱导性建议——不能在方案中"顺水推舟"接受所有业务方想法',
            '"先授权后审批"是安全红线——必须在business中明确拒绝，不是标记GAP待确认',
            '"默认全部可申请"存在严重安全风险——必须采用白名单模式',
            '"审批人缺失时自动通过"不可接受——审批形同虚设',
            '冲突1/2/3/6涉及安全原则，不能妥协——需要在business中给出明确立场',
            '冲突4/5可在方案中给出推荐策略并标记GAP'
        ]
    }
}

runtime = str(get_project_runtime_dir(project_id))
os.makedirs(runtime, exist_ok=True)
path = os.path.join(runtime, 'uxb_route_decision.json')
with open(path, 'w', encoding='utf-8') as f:
    json.dump(decision, f, ensure_ascii=False, indent=2)

print(f'Done: {len(biz_refs)} biz + {len(guide_refs)} guide + {len(reasons)} reasons')
for r in biz_refs:
    print(f'  BIZ: {os.path.basename(r)}')
