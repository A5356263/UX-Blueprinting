import React from "react";
import { subapplicationTopBarAssets } from "./XftSubapplicationTopBar.assets";
import "./XftSubapplicationTopBar.css";

export type XftSubapplicationTopBarVariant = "smart-accounting" | "sub-application";

export type XftSubapplicationTopBarAction = {
  key: string;
  label: string;
  icon: string;
  size?: 24 | 28;
  containerWidth?: 24 | 28 | 32;
};

export type XftSubapplicationTopBarNavItem = {
  key: string;
  label: string;
};

export type XftSubapplicationTopBarProps = {
  variant?: XftSubapplicationTopBarVariant;
  brandName?: string;
  organizationName?: string;
  accountSetName?: string;
  accountingPeriod?: string;
  userName?: string;
  avatarUrl?: string;
  showPrimaryNav?: boolean;
  primaryNavItems?: XftSubapplicationTopBarNavItem[];
  activePrimaryNavKey?: string;
  utilityActions?: XftSubapplicationTopBarAction[];
  searchPlaceholder?: string;
  onSwitchOrganization?: () => void;
  onSwitchAccountSet?: () => void;
  onAccountingMonthAction?: (action: "previous" | "current" | "next") => void;
  onPrimaryNavChange?: (key: string) => void;
  onAllAppsClick?: () => void;
  onSearchChange?: (value: string) => void;
  onUtilityAction?: (key: string) => void;
  onGuideClick?: () => void;
  onNoticeClick?: () => void;
  onUserClick?: () => void;
};

const defaultNavItems: XftSubapplicationTopBarNavItem[] = [
  { key: "accounting-engine", label: "会计引擎" },
  { key: "data-connection", label: "数据互联" },
];

const defaultUtilityActions: XftSubapplicationTopBarAction[] = [
  { key: "help", label: "帮助说明", icon: subapplicationTopBarAssets.helpNav24, size: 24, containerWidth: 32 },
  { key: "customer-service", label: "客服", icon: subapplicationTopBarAssets.customerServiceNav24, size: 24, containerWidth: 32 },
  { key: "upload-download-center", label: "上传下载中心", icon: subapplicationTopBarAssets.uploadDownload24, size: 24, containerWidth: 32 },
];

const Divider = () => <span className="xft-subapp-top-bar__divider" aria-hidden="true" />;

const UtilityActions = ({
  actions,
  onAction,
  dense = false,
}: {
  actions: XftSubapplicationTopBarAction[];
  onAction?: (key: string) => void;
  dense?: boolean;
}) => <div className={`xft-subapp-top-bar__utility-actions${dense ? " xft-subapp-top-bar__utility-actions--dense" : ""}`}>
    {actions.map((action) => <button
      key={action.key}
    className="xft-subapp-top-bar__icon-button"
      type="button"
      style={{ width: action.containerWidth ?? action.size ?? 24, flexBasis: action.containerWidth ?? action.size ?? 24 }}
      aria-label={action.label}
      title={action.label}
      onClick={() => onAction?.(action.key)}
    >
      <img
        src={action.icon}
        alt=""
        aria-hidden="true"
        style={{ width: action.size ?? 24, height: action.size ?? 24 }}
      />
    </button>)}
  </div>;

const SearchBox = ({ placeholder, icon, onChange }: { placeholder: string; icon: string; onChange?: (value: string) => void }) => <label className="xft-subapp-top-bar__search">
    <img src={icon} alt="" aria-hidden="true" />
    <input
      type="search"
      aria-label={placeholder}
      placeholder={placeholder}
      onChange={(event) => onChange?.(event.currentTarget.value)}
    />
  </label>;

const OrganizationButton = ({
  name,
  onClick,
  withArrow,
  mode,
}: {
  name: string;
  onClick?: () => void;
  withArrow: boolean;
  mode: "smart-accounting" | "sub-application";
}) => <button className="xft-subapp-top-bar__organization" type="button" aria-label={`切换企业，当前企业：${name}`} onClick={onClick}>
    <img src={mode === "smart-accounting" ? subapplicationTopBarAssets.companySmart16 : subapplicationTopBarAssets.companyNoPrimary16} alt="" aria-hidden="true" />
    <span className="xft-subapp-top-bar__organization-name">{name}</span>
    {withArrow ? <img
      className="xft-subapp-top-bar__organization-arrow"
      src={subapplicationTopBarAssets.companyNoPrimaryArrow16}
      alt=""
      aria-hidden="true"
    /> : null}
  </button>;

const UserButton = ({ name, avatarUrl, onClick, arrowType = "small" }: {
  name: string;
  avatarUrl?: string;
  onClick?: () => void;
  arrowType?: "solid" | "small" | "smart-accounting";
}) => <button className="xft-subapp-top-bar__user" type="button" aria-label={`用户 ${name}`} onClick={onClick}>
    <img className="xft-subapp-top-bar__avatar" src={avatarUrl || subapplicationTopBarAssets.avatar} alt="" aria-hidden="true" />
    <span className="xft-subapp-top-bar__user-info">
      <span className="xft-subapp-top-bar__user-name">{name}</span>
      <img
        className={`xft-subapp-top-bar__user-arrow xft-subapp-top-bar__user-arrow--${arrowType}`}
        src={arrowType === "solid" ? subapplicationTopBarAssets.profileArrow16 : arrowType === "smart-accounting" ? subapplicationTopBarAssets.profileCaret8 : subapplicationTopBarAssets.noPrimaryCaret8}
        alt=""
        aria-hidden="true"
      />
    </span>
  </button>;

export function XftSubapplicationTopBar({
  variant = "sub-application",
  showPrimaryNav = false,
  brandName = "应用名称",
  organizationName = "招商银行薪福通",
  accountSetName = "招银网络科技",
  accountingPeriod = "2024年6月",
  userName = "邱云",
  avatarUrl,
  primaryNavItems,
  activePrimaryNavKey,
  utilityActions,
  searchPlaceholder,
  onSwitchOrganization,
  onSwitchAccountSet,
  onAccountingMonthAction,
  onPrimaryNavChange,
  onAllAppsClick,
  onSearchChange,
  onUtilityAction,
  onGuideClick,
  onNoticeClick,
  onUserClick,
}: XftSubapplicationTopBarProps) {
  const navItems = primaryNavItems ?? defaultNavItems;
  const companyName = organizationName;
  const hasPrimaryNav = variant === "sub-application" && showPrimaryNav;
  const defaultActiveKey = navItems[0]?.key ?? "";
  const [internalActiveKey, setInternalActiveKey] = React.useState(activePrimaryNavKey ?? defaultActiveKey);
  const activeKey = activePrimaryNavKey ?? internalActiveKey;
  const brand = brandName;
  const actions = utilityActions ?? defaultUtilityActions;
  const placeholder = searchPlaceholder ?? "输入关键词，问题";

  const choosePrimaryNav = (key: string) => {
    if (activePrimaryNavKey === undefined) setInternalActiveKey(key);
    onPrimaryNavChange?.(key);
  };

  return <header className={`xft-subapp-top-bar xft-subapp-top-bar--${variant}`}>
    <div className="xft-subapp-top-bar__left">
      <div className="xft-subapp-top-bar__brand">{brand}</div>

      {variant === "smart-accounting" ? <>
        <button className="xft-subapp-top-bar__account-set" type="button" aria-label={`切换账套，当前账套：${accountSetName}`} onClick={onSwitchAccountSet}>
          <span>{accountSetName}</span>
          <img src={subapplicationTopBarAssets.caretDown8} alt="" aria-hidden="true" />
        </button>
        <div className="xft-subapp-top-bar__accounting-tools">
          <span className="xft-subapp-top-bar__period">{accountingPeriod}</span>
          <Divider />
          <div className="xft-subapp-top-bar__month-actions">
            {["previous", "current", "next"].map((key, index) => <button
              className="xft-subapp-top-bar__month-action"
              type="button"
              key={key}
              aria-label={["上一月", "当前月", "下一月"][index]}
              onClick={() => onAccountingMonthAction?.(key as "previous" | "current" | "next")}
            ><img src={[subapplicationTopBarAssets.monthPrevious, subapplicationTopBarAssets.monthCurrent, subapplicationTopBarAssets.monthNext][index]} alt="" aria-hidden="true" /></button>)}
          </div>
          <Divider />
          <button className="xft-subapp-top-bar__all-apps" type="button" onClick={onAllAppsClick}>
            <img src={subapplicationTopBarAssets.allApps24} alt="" aria-hidden="true" />
            <span>全部应用</span>
          </button>
        </div>
      </> : <>
        <OrganizationButton name={companyName} onClick={onSwitchOrganization} withArrow mode="sub-application" />
        {hasPrimaryNav ? <>
          <Divider />
          <nav className="xft-subapp-top-bar__primary-nav" aria-label="一级菜单">
            {navItems.map((item) => <button
              className={`xft-subapp-top-bar__primary-nav-item${activeKey === item.key ? " is-active" : ""}`}
              key={item.key}
              type="button"
              aria-current={activeKey === item.key ? "page" : undefined}
              onClick={() => choosePrimaryNav(item.key)}
            >
              <span>{item.label}</span>
              {activeKey === item.key ? <img src={subapplicationTopBarAssets.activeBar} alt="" aria-hidden="true" /> : null}
            </button>)}
          </nav>
          <Divider />
        </> : <Divider />}
        <button className="xft-subapp-top-bar__all-apps" type="button" onClick={onAllAppsClick}>
          <img src={subapplicationTopBarAssets.allAppsSettings24} alt="" aria-hidden="true" />
          <span>全部应用</span>
        </button>
      </>}
    </div>

    <div className="xft-subapp-top-bar__right">
      {variant === "smart-accounting" ? <>
        <div className="xft-subapp-top-bar__smart-links">
          <button className="xft-subapp-top-bar__text-action" type="button" onClick={onGuideClick}>初始化指引</button>
          <button className="xft-subapp-top-bar__text-action" type="button" onClick={onNoticeClick}>公告</button>
          <Divider />
          <UtilityActions actions={actions} onAction={onUtilityAction} dense />
        </div>
        <Divider />
        <OrganizationButton name={companyName} onClick={onSwitchOrganization} withArrow mode="smart-accounting" />
        <UserButton name={userName} avatarUrl={avatarUrl || subapplicationTopBarAssets.avatar} onClick={onUserClick} arrowType="smart-accounting" />
      </> : <>
        <SearchBox placeholder={placeholder} icon={subapplicationTopBarAssets.searchNoPrimary} onChange={onSearchChange} />
        <div className="xft-subapp-top-bar__utilities-with-divider">
          <UtilityActions actions={actions} onAction={onUtilityAction} dense />
          <Divider />
        </div>
        <UserButton
          name={userName}
          avatarUrl={avatarUrl || subapplicationTopBarAssets.avatar}
          onClick={onUserClick}
          arrowType="small"
        />
      </>}
    </div>
  </header>;
}
