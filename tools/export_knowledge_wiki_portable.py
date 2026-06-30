from __future__ import annotations

import re
import shutil
import tempfile
import zipfile
from pathlib import Path


SOURCE_SKILL = Path(".claude/skills/knowledge-wiki")
ZIP_FILE = Path("knowledge-wiki.zip")
TEXT_SUFFIXES = {".md", ".txt", ".py", ".json", ".yaml", ".yml"}
CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")
KNOWLEDGE_PATH_RE = re.compile(
    r"knowledge/(?:raw|wiki/summaries|candidates|templates)/[^`)\]\s，。：；、“”‘’！？,]*[\u4e00-\u9fff][^`)\]\s，。：；、“”‘’！？,]*"
)


SEGMENT_MAP = {
    "业务": "yewu",
    "设计准则": "design-guidelines",
    "反馈与报错": "feedback-and-errors",
    "业务知识入库": "business-knowledge-ingestion",
    "已入库": "archived",
    "未入库": "pending",
    "新需求文档": "new-requirements",
    "知识问答": "knowledge-qa",
    "诊断咨询": "diagnosis-consulting",
    "<领域>": "<domain-pinyin>",
    "人事服务": "renshi-fuwu",
    "企业支付": "qiye-zhifu",
    "企业设置": "qiye-shezhi",
    "信息架构.md": "information-architecture.md",
    "协同办公": "xietong-bangong",
    "协同工具": "xietong-gongju",
    "可用性.md": "usability.md",
    "可读性.md": "readability.md",
    "员工管理": "yuangong-guanli",
    "安全管理": "anquan-guanli",
    "审批管理": "shenpi-guanli",
    "客户管理": "kehu-guanli",
    "工作台与全局入口": "gongzuotai-yu-quanju-rukou",
    "差旅服务": "chalv-fuwu",
    "应用管理": "yingyong-guanli",
    "成员管理": "chengyuan-guanli",
    "招聘管理": "zhaopin-guanli",
    "无障碍.md": "accessibility.md",
    "日常报销": "richang-baoxiao",
    "智能报表": "zhineng-baobiao",
    "服务管理": "fuwu-guanli",
    "权限管理": "quanxian-guanli",
    "治理.md": "governance.md",
    "流程模式.md": "flow-patterns.md",
    "组织架构": "zuzhi-jiagou",
    "组织管理": "zuzhi-guanli",
    "考勤管理": "kaoqin-guanli",
    "视觉.md": "visual.md",
    "认知.md": "cognition.md",
    "账户与企业生命周期": "zhanghu-yu-qiye-shengming-zhouqi",
    "质量.md": "quality.md",
    "费用管理": "feiyong-guanli",
    "通用配置": "tongyong-peizhi",
    "项目背景": "xiangmu-beijing",
    "00_反馈与报错体验设计指南.md": "00_feedback-and-error-ux-guidelines.md",
    "00_领域概述.md": "00_lingyu-gaishu.md",
    "00_领域概述.template.md": "00_lingyu-gaishu.template.md",
    "01_产品定位.md": "01_chanpin-dingwei.md",
    "01_反馈形式选择原则.md": "01_feedback-pattern-selection-principles.md",
    "01_范围与边界.md": "01_fanwei-yu-bianjie.md",
    "02_平台角色与终端.md": "02_pingtai-juese-yu-zhongduan.md",
    "02_报错与状态文案模板.md": "02_error-and-state-copy-template.md",
    "02_术语表.md": "02_shuyubiao.md",
    "03_业务对象.md": "03_yewu-duixiang.md",
    "03_产品能力版图.md": "03_chanpin-nengli-bantu.md",
    "03_通用报错场景案例.md": "03_general-error-scenario-examples.md",
    "04_产品优势与服务模式.md": "04_chanpin-youshi-yu-fuwu-moshi.md",
    "04_人事与薪酬场景案例.md": "04_hr-and-payroll-scenario-examples.md",
    "04_对象关系.md": "04_duixiang-guanxi.md",
    "05_管理控制台能力概览.md": "05_guanli-kongzhitai-nengli-gailan.md",
    "05_财税场景案例.md": "05_finance-and-tax-scenario-examples.md",
    "10_企业信息展示.md": "10_qiye-xinxi-zhanshi.md",
    "10_企业支付.md": "10_qiye-zhifu.md",
    "10_协同工具.md": "10_xietong-gongju.md",
    "10_安全水印.md": "10_anquan-shuiyin.md",
    "10_审批管理.md": "10_shenpi-guanli.md",
    "10_客户管理.md": "10_kehu-guanli.md",
    "10_工作台.md": "10_gongzuotai.md",
    "10_差旅服务.md": "10_chalv-fuwu.md",
    "10_应用管理.md": "10_yingyong-guanli.md",
    "10_开通路径.md": "10_kaitong-lujing.md",
    "10_成员加入与邀请.md": "10_chengyuan-jiaru-yu-yaoqing.md",
    "10_招聘管理.md": "10_zhaopin-guanli.md",
    "10_日常报销.md": "10_richang-baoxiao.md",
    "10_智能报表.md": "10_zhineng-baobiao.md",
    "10_服务人员授权.md": "10_fuwu-renyuan-shouquan.md",
    "10_组织架构.md": "10_zuzhi-jiagou.md",
    "10_组织架构设计.md": "10_zuzhi-jiagou-sheji.md",
    "10_考勤管理.md": "10_kaoqin-guanli.md",
    "10_能力地图.md": "10_nengli-ditu.md",
    "10_能力地图.template.md": "10_nengli-ditu.template.md",
    "10_通用配置.md": "10_tongyong-peizhi.md",
    "11_任务场景.md": "11_renwu-changjing.md",
    "11_任务场景.template.md": "11_renwu-changjing.template.md",
    "11_企业创建与认证.md": "11_qiye-chuangjian-yu-renzheng.md",
    "11_企业登录页自定义.md": "11_qiye-dengluyemian-zidingyi.md",
    "11_全局导航与服务入口.md": "11_quanju-daohang-yu-fuwu-rukou.md",
    "11_应用组装.md": "11_yingyong-zuzhuang.md",
    "11_成员退出与离职交接.md": "11_chengyuan-tuichu-yu-lizhi-jiaojie.md",
    "11_操作记录.md": "11_caozuo-jilu.md",
    "11_法律实体.md": "11_falv-shiti.md",
    "12_企业文化.md": "12_qiye-wenhua.md",
    "12_企业状态与变更.md": "12_qiye-zhuangtai-yu-biangeng.md",
    "12_入口与路径.md": "12_rukou-yu-lujing.md",
    "12_入口与路径.template.md": "12_rukou-yu-lujing.template.md",
    "12_安全设置.md": "12_anquan-shezhi.md",
    "12_成员分组.md": "12_chengyuan-fenzu.md",
    "12_成本中心.md": "12_chengben-zhongxin.md",
    "12_查询与配置路径.md": "12_chaxun-yu-peizhi-lujing.md",
    "13_外部人员.md": "13_waibu-renyuan.md",
    "13_状态与流程.md": "13_zhuangtai-yu-liucheng.md",
    "13_状态与流程.template.md": "13_zhuangtai-yu-liucheng.template.md",
    "13_编制管理.md": "13_bianzhi-guanli.md",
    "13_职能与视图模型.md": "13_zhineng-yu-shitu-moxing.md",
    "13_超级管理员变更.md": "13_chaoji-guanliyuan-biangeng.md",
    "13_路由地图.md": "13_luyou-ditu.md",
    "14_岗位与职级管理.md": "14_gangwei-yu-zhiji-guanli.md",
    "14_成员绑定与范围生成.md": "14_chengyuan-bangding-yu-fanwei-shengcheng.md",
    "14_角色边界.md": "14_juese-bianjie.md",
    "14_账号常见问题.md": "14_zhanghao-changjian-wenti.md",
    "14_页面与字段.md": "14_yemian-yu-ziduan.md",
    "14_页面与字段.template.md": "14_yemian-yu-ziduan.template.md",
    "15_个人账号安全.md": "15_geren-zhanghao-anquan.md",
    "15_边界与限制.md": "15_bianjie-yu-xianzhi.md",
    "15_边界与限制.template.md": "15_bianjie-yu-xianzhi.template.md",
    "15_运行时流程与遗留映射.md": "15_yunxingshi-liucheng-yu-yiliu-yingshe.md",
    "15_页面载体语义.md": "15_yemian-zaiti-yuyi.md",
    "20_决策规则.template.md": "20_juece-guize.template.md",
    "20_决策链契约.md": "20_juece-lian-qiyue.md",
    "21_来源模型.md": "21_laiyuan-moxing.md",
    "22_冲突原因码.md": "22_chongtu-yuanyinma.md",
    "23_规则契约.md": "23_guize-qiyue.md",
    "24_治理状态模型.md": "24_zhili-zhuangtai-moxing.md",
    "25_审计契约.md": "25_shenji-qiyue.md",
    "30_体验风险与解释.template.md": "30_tiyan-fengxian-yu-jieshi.template.md",
    "30_体验风险模式.md": "30_tiyan-fengxian-moshi.md",
    "31_体验翻译需求.md": "31_tiyan-fanyi-xuqiu.md",
    "32_文案与解释策略.md": "32_wenan-yu-jieshi-celue.md",
    "50_帮助文档权限差异.md": "50_bangzhu-wendang-quanxian-chayi.md",
    "50_常见问题.md": "50_changjian-wenti.md",
    "50_常见问题与外部口径.template.md": "50_changjian-wenti-yu-waibu-koujing.template.md",
}

EXTRA_PATH_REPLACEMENTS = {
    "knowledge/raw/业务/**": "knowledge/raw/yewu/**",
    "knowledge/raw/业务/<领域>/README.md": "knowledge/raw/yewu/<domain-pinyin>/README.md",
    "knowledge/raw/设计准则/**": "knowledge/raw/design-guidelines/**",
    "knowledge/wiki/summaries/业务/**": "knowledge/wiki/summaries/yewu/**",
    "knowledge/wiki/summaries/设计准则/**": "knowledge/wiki/summaries/design-guidelines/**",
    "knowledge/candidates/已入库/**": "knowledge/candidates/archived/**",
    "knowledge/candidates/未入库/**": "knowledge/candidates/pending/**",
    "knowledge/templates/业务知识入库/**": "knowledge/templates/business-knowledge-ingestion/**",
    "knowledge/raw/业务/<领域>/": "knowledge/raw/yewu/<domain-pinyin>/",
    "knowledge/wiki/summaries/业务/<领域>/": "knowledge/wiki/summaries/yewu/<domain-pinyin>/",
}


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def rename_segment(segment: str) -> str:
    return SEGMENT_MAP.get(segment, segment)


def rename_rel_path(rel_path: str) -> str:
    return "/".join(rename_segment(part) for part in rel_path.split("/"))


def build_segment_inventory(skill_root: Path) -> set[str]:
    segments: set[str] = set()
    for path in skill_root.rglob("*"):
        rel = path.relative_to(skill_root).as_posix()
        for part in rel.split("/"):
            if CHINESE_RE.search(part):
                segments.add(part)
    return segments


def assert_mapping_complete(skill_root: Path) -> None:
    actual = build_segment_inventory(skill_root)
    missing = sorted(item for item in actual if item not in SEGMENT_MAP)
    if missing:
        raise RuntimeError("映射表缺失这些中文片段: " + ", ".join(missing))


def collect_path_replacements(skill_root: Path) -> dict[str, str]:
    replacements: dict[str, str] = {}
    for path in sorted(skill_root.rglob("*")):
        rel = path.relative_to(skill_root).as_posix()
        if not CHINESE_RE.search(rel):
            continue
        renamed = rename_rel_path(rel)
        replacements[rel] = renamed
        if path.is_dir():
            replacements[f"{rel}/"] = f"{renamed}/"
    replacements.update(EXTRA_PATH_REPLACEMENTS)
    return dict(sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True))


def copy_source_tree(source_skill: Path, temp_root: Path) -> Path:
    temp_skill = temp_root / "knowledge-wiki"
    shutil.copytree(source_skill, temp_skill)
    return temp_skill


def rename_tree(export_root: Path) -> None:
    for path in sorted(export_root.rglob("*"), key=lambda item: len(item.relative_to(export_root).parts), reverse=True):
        new_name = rename_segment(path.name)
        if new_name == path.name:
            continue
        target = path.with_name(new_name)
        if target.exists():
            raise RuntimeError(f"重命名冲突: {path} -> {target}")
        path.rename(target)


def rewrite_text_files(export_root: Path, replacements: dict[str, str]) -> list[Path]:
    changed: list[Path] = []
    for path in export_root.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        updated = text
        for source, target in replacements.items():
            updated = updated.replace(source, target)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed.append(path)
    return changed


def ensure_ascii_paths(export_root: Path) -> None:
    bad = []
    for path in export_root.rglob("*"):
        rel = path.relative_to(export_root).as_posix()
        if any(ord(ch) > 127 for ch in rel):
            bad.append(rel)
    if bad:
        preview = ", ".join(bad[:10])
        raise RuntimeError(f"导出目录仍包含非 ASCII 路径: {preview}")


def ensure_no_chinese_knowledge_paths(export_root: Path) -> None:
    offenders: list[str] = []
    for path in export_root.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        if CHINESE_RE.search(text):
            for match in KNOWLEDGE_PATH_RE.finditer(text):
                rel = path.relative_to(export_root).as_posix()
                offenders.append(f"{rel}: {match.group(0)}")
    if offenders:
        preview = "; ".join(offenders[:10])
        raise RuntimeError(f"仍残留中文知识路径: {preview}")


def ensure_reference_paths_exist(export_root: Path) -> None:
    broken: list[str] = []
    for path in export_root.rglob("*.md"):
        rel = path.relative_to(export_root).as_posix()
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("- source_path:") or stripped.startswith("- summary_path:"):
                target_rel = stripped.split(":", 1)[1].strip()
                if not target_rel:
                    continue
                target = export_root / Path(target_rel)
                if not target.exists():
                    broken.append(f"{rel} -> {target_rel}")
    if broken:
        preview = "; ".join(broken[:10])
        raise RuntimeError(f"存在失效的 source_path/summary_path: {preview}")


def ensure_counts_match(source_skill: Path, export_root: Path) -> None:
    source_files = sum(1 for path in source_skill.rglob("*") if path.is_file())
    export_files = sum(1 for path in export_root.rglob("*") if path.is_file())
    source_dirs = sum(1 for path in source_skill.rglob("*") if path.is_dir())
    export_dirs = sum(1 for path in export_root.rglob("*") if path.is_dir())
    if (source_files, source_dirs) != (export_files, export_dirs):
        raise RuntimeError(
            "导出结构数量不一致: "
            f"source(files={source_files}, dirs={source_dirs}) "
            f"export(files={export_files}, dirs={export_dirs})"
        )


def write_zip(export_root: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(export_root.rglob("*")):
            if not path.is_file():
                continue
            arcname = path.relative_to(export_root).as_posix()
            archive.write(path, arcname)


def replace_output(repo_root: Path, temp_export_root: Path) -> Path:
    final_zip = repo_root / ZIP_FILE

    write_zip(temp_export_root, final_zip)
    return final_zip


def main() -> int:
    repo_root = repo_root_from_script()
    source_skill = repo_root / SOURCE_SKILL
    if not source_skill.exists():
        raise RuntimeError(f"未找到源 skill: {source_skill}")

    assert_mapping_complete(source_skill)
    replacements = collect_path_replacements(source_skill)

    with tempfile.TemporaryDirectory(prefix="knowledge-wiki-export-", dir=repo_root) as temp_dir:
        temp_root = Path(temp_dir)
        temp_skill = copy_source_tree(source_skill, temp_root)
        rename_tree(temp_skill)
        rewrite_text_files(temp_skill, replacements)
        ensure_counts_match(source_skill, temp_skill)
        ensure_ascii_paths(temp_skill)
        ensure_no_chinese_knowledge_paths(temp_skill)
        ensure_reference_paths_exist(temp_skill)
        final_zip = replace_output(repo_root, temp_skill)

    print(f"source_skill={source_skill}")
    print(f"zip_file={final_zip}")
    print("status=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
