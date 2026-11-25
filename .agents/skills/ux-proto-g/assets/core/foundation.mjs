import { createHash } from "node:crypto";
import { foundationRuntime } from "./foundation-runtime.mjs";

const CONTRACT_VERSION = 4;
const GENERIC_CONTRACT_VERSION = 3;
const SEED_CONTRACT_VERSION = 2;
const LEGACY_CONTRACT_VERSION = 1;

const aliasNames = Object.freeze([
  "border.accent", "border.error", "border.error.tint", "border.neutral",
  "border.none", "divider.neutral", "divider.none", "font_size.body",
  "font_size.body_large", "font_size.caption", "font_size.heading.1", "font_size.heading.2",
  "font_size.heading.3", "font_size.heading.4", "font_size.heading.5", "font_size.heading.6",
  "font_weight.regular", "font_weight.semibold", "font_weight.thin", "line_height.loose",
  "line_height.regular", "line_height.tight", "radius.large", "radius.none",
  "radius.regular", "radius.small", "shadow.large.bottom", "shadow.none",
  "shadow.regular.bottom", "shadow.small.bottom", "space.0", "space.1",
  "space.10", "space.11", "space.12", "space.2",
  "space.3", "space.4", "space.5", "space.6",
  "space.7", "space.8", "space.9", "surface.accent.solid",
  "surface.accent.tint", "surface.container.bright", "surface.container.inverse", "surface.container.muted",
  "surface.error.solid", "surface.error.tint", "surface.info.solid", "surface.info.tint",
  "surface.region.bright", "surface.region.inverse", "surface.region.muted", "surface.success.solid",
  "surface.success.tint", "surface.warning.solid", "surface.warning.tint", "text.accent",
  "text.default", "text.disabled", "text.error", "text.info",
  "text.inverse", "text.inverse_secondary", "text.muted", "text.secondary",
  "text.success", "text.value", "text.warning"
]);
const extendedAliasNames = Object.freeze([...aliasNames, "border.width", "font_weight.strong"].sort());
const stateRoles = Object.freeze(["accent", "info", "success", "warning", "error"]);
const stateAliasNames = Object.freeze(stateRoles.flatMap((role) => [
  `surface.${role}.solid.hover`, `surface.${role}.solid.active`,
  `surface.${role}.tint.hover`, `surface.${role}.tint.active`,
  `text.${role}.hover`, `text.${role}.active`,
  `border.${role}.hover`, `border.${role}.active`, `border.${role}.tint`
]).concat([
  "surface.container.bright.hover", "surface.container.bright.active",
  "surface.container.muted.hover", "surface.container.muted.active"
]).sort());
const statefulAliasNames = Object.freeze([...extendedAliasNames, ...stateAliasNames].sort());
const aliasesForVersion = (version) => version === CONTRACT_VERSION ? statefulAliasNames
  : version === GENERIC_CONTRACT_VERSION ? extendedAliasNames : aliasNames;
const requiredAliasesForVersion = (version) => version >= GENERIC_CONTRACT_VERSION ? extendedAliasNames : aliasNames;

const legacyAntdEntries = Object.freeze([
  ["colorPrimary", "surface.accent.solid"],
  ["colorInfo", "surface.info.solid"],
  ["colorSuccess", "surface.success.solid"],
  ["colorWarning", "surface.warning.solid"],
  ["colorError", "surface.error.solid"],
  ["colorLink", "text.accent"],
  ["colorTextBase", "text.default"],
  ["colorBgBase", "surface.region.bright"],
  ["fontSize", "font_size.body"],
  ["borderRadius", "radius.regular"],
  ["colorText", "text.default"],
  ["colorPrimaryBg", "surface.accent.tint"],
  ["colorInfoBg", "surface.info.tint"],
  ["colorSuccessBg", "surface.success.tint"],
  ["colorWarningBg", "surface.warning.tint"],
  ["colorErrorBg", "surface.error.tint"]
]);
const seedAntdEntries = Object.freeze(legacyAntdEntries.filter(([name]) => ![
  "colorLink", "colorText", "colorPrimaryBg", "colorInfoBg", "colorSuccessBg", "colorWarningBg", "colorErrorBg"
].includes(name)).concat([
  ["blue", "surface.accent.solid"], ["purple", "surface.accent.solid"],
  ["cyan", "surface.info.solid"], ["green", "surface.success.solid"],
  ["magenta", "surface.error.solid"], ["pink", "surface.error.solid"],
  ["red", "surface.error.solid"], ["orange", "surface.warning.solid"],
  ["yellow", "surface.warning.solid"], ["volcano", "surface.error.solid"],
  ["geekblue", "surface.accent.solid"], ["gold", "surface.warning.solid"],
  ["lime", "surface.success.solid"]
]));
const extendedAntdEntries = Object.freeze(seedAntdEntries.concat([
  ["colorTextSecondary", "text.secondary"],
  ["colorTextTertiary", "text.muted"],
  ["colorTextDisabled", "text.disabled"],
  ["colorBgContainer", "surface.container.bright"],
  ["colorBgLayout", "surface.region.muted"],
  ["colorBorder", "border.neutral"],
  ["colorSplit", "divider.neutral"],
  ["fontWeightStrong", "font_weight.strong"],
  ["lineHeight", "line_height.regular"],
  ["lineHeightLG", "line_height.loose"],
  ["lineHeightSM", "line_height.tight"],
  ["fontSizeSM", "font_size.caption"],
  ["fontSizeLG", "font_size.body_large"],
  ["fontSizeHeading1", "font_size.heading.1"],
  ["fontSizeHeading2", "font_size.heading.2"],
  ["fontSizeHeading3", "font_size.heading.3"],
  ["fontSizeHeading4", "font_size.heading.4"],
  ["fontSizeHeading5", "font_size.heading.5"],
  ["borderRadiusSM", "radius.small"],
  ["borderRadiusLG", "radius.large"],
  ["lineWidth", "border.width"],
  ["boxShadow", "shadow.regular.bottom"],
  ["boxShadowSecondary", "shadow.large.bottom"],
  ["boxShadowTertiary", "shadow.small.bottom"],
  ["sizeUnit", "space.1"],
  ["paddingXXS", "space.1"], ["paddingXS", "space.2"],
  ["paddingSM", "space.3"], ["padding", "space.4"],
  ["paddingMD", "space.5"], ["paddingLG", "space.6"],
  ["paddingXL", "space.7"],
  ["marginXXS", "space.1"], ["marginXS", "space.2"],
  ["marginSM", "space.3"], ["margin", "space.4"],
  ["marginMD", "space.5"], ["marginLG", "space.6"],
  ["marginXL", "space.7"], ["marginXXL", "space.9"]
]));
const stateAntdEntries = Object.freeze(stateRoles.flatMap((role) => {
  const prefix = role === "accent" ? "Primary" : role[0].toUpperCase() + role.slice(1);
  return [
    [`color${prefix}Hover`, `surface.${role}.solid.hover`],
    [`color${prefix}Active`, `surface.${role}.solid.active`],
    [`color${prefix}Bg`, `surface.${role}.tint`],
    [`color${prefix}BgHover`, `surface.${role}.tint.hover`],
    [`color${prefix}Border`, role === "accent" ? "border.accent" : role === "error" ? "border.error.tint" : `border.${role}.tint`],
    [`color${prefix}BorderHover`, `border.${role}.hover`],
    [`color${prefix}Text`, `text.${role}`],
    [`color${prefix}TextHover`, `text.${role}.hover`],
    [`color${prefix}TextActive`, `text.${role}.active`]
  ];
}).concat([
  ["colorErrorBgActive", "surface.error.tint.active"],
  ["colorLink", "text.accent"],
  ["colorLinkHover", "text.accent.hover"],
  ["colorLinkActive", "text.accent.active"]
]));
const defaultAntdMapping = Object.freeze(Object.fromEntries(legacyAntdEntries));
const staticStyleIncludes = Object.freeze([
  "Alert", "Badge", "Breadcrumb", "Button", "Card", "Checkbox", "DatePicker",
  "Descriptions", "Divider", "Drawer", "Dropdown", "Empty", "Flex", "Form",
  "Input", "InputNumber", "Layout", "Menu", "Modal", "Pagination", "Popconfirm",
  "Progress", "Radio", "Result", "Select", "Space", "Statistic", "Steps", "Switch",
  "Table", "Tabs", "Tag", "Timeline", "Tree", "TreeSelect", "Typography", "Upload"
]);

const allowedAntdOverrides = Object.freeze([...new Set([...Object.keys(defaultAntdMapping), ...seedAntdEntries.map(([name]) => name)])].sort());
const extendedAntdOverrides = Object.freeze([...new Set([...allowedAntdOverrides, ...extendedAntdEntries.map(([name]) => name)])].sort());
const statefulAntdOverrides = Object.freeze([...new Set([...extendedAntdOverrides, ...stateAntdEntries.map(([name]) => name)])].sort());
const numericPrefixes = ["border.width", "font_size.", "font_weight.", "line_height.", "space."];

function aliasType(name) {
  if (numericPrefixes.some((prefix) => name.startsWith(prefix))) return "number";
  if (name.startsWith("radius.") && name !== "radius.none") return "number";
  return "string";
}

function clone(value) {
  return structuredClone(value);
}

function fail(message) {
  throw new Error(`Foundation contract error: ${message}`);
}

function assertPlainObject(value, label) {
  if (!value || typeof value !== "object" || Array.isArray(value)) fail(`${label} must be an object.`);
}

function assertExactKeys(value, allowed, label) {
  assertPlainObject(value, label);
  const unknown = Object.keys(value).filter((key) => !allowed.includes(key)).sort();
  if (unknown.length) fail(`${label} contains unknown field(s): ${unknown.join(", ")}.`);
}

function validateVersionAndOuterShape(config) {
  assertExactKeys(config, ["contractVersion", "aliasValues", "antdOverrides"], "foundation");
  if (![LEGACY_CONTRACT_VERSION, SEED_CONTRACT_VERSION, GENERIC_CONTRACT_VERSION, CONTRACT_VERSION].includes(config.contractVersion)) {
    fail(`contractVersion must be integer ${LEGACY_CONTRACT_VERSION}, ${SEED_CONTRACT_VERSION}, ${GENERIC_CONTRACT_VERSION} or ${CONTRACT_VERSION}.`);
  }
  assertPlainObject(config.aliasValues, "foundation.aliasValues");
  if ("antdOverrides" in config) assertPlainObject(config.antdOverrides, "foundation.antdOverrides");
}

function validateAliasValues(aliasValues, { contractVersion, requireComplete }) {
  const names = aliasesForVersion(contractVersion);
  const unknown = Object.keys(aliasValues).filter((name) => !names.includes(name)).sort();
  if (unknown.length) fail(`aliasValues contains unknown alias(es): ${unknown.join(", ")}.`);
  if (requireComplete) {
    const missing = requiredAliasesForVersion(contractVersion).filter((name) => !(name in aliasValues));
    if (missing.length) fail(`aliasValues is missing required alias(es): ${missing.join(", ")}.`);
  }
  for (const [name, value] of Object.entries(aliasValues)) {
    const expected = aliasType(name);
    if (typeof value !== expected || (expected === "number" && !Number.isFinite(value))) {
      fail(`aliasValues.${name} must have JSON scalar type ${expected}.`);
    }
  }
}

function validateOverrides(overrides = {}, contractVersion = SEED_CONTRACT_VERSION) {
  const allowed = contractVersion === CONTRACT_VERSION ? statefulAntdOverrides
    : contractVersion === GENERIC_CONTRACT_VERSION ? extendedAntdOverrides : allowedAntdOverrides;
  const names = aliasesForVersion(contractVersion);
  const unknown = Object.keys(overrides).filter((name) => !allowed.includes(name)).sort();
  if (unknown.length) fail(`antdOverrides contains unknown AntD token(s): ${unknown.join(", ")}.`);
  const normalized = {};
  for (const name of Object.keys(overrides).sort()) {
    const value = overrides[name];
    if (["string", "number", "boolean"].includes(typeof value)) {
      if (typeof value === "number" && !Number.isFinite(value)) fail(`antdOverrides.${name} must be a finite JSON scalar.`);
      normalized[name] = value;
      continue;
    }
    assertExactKeys(value, ["alias"], `antdOverrides.${name}`);
    if (typeof value.alias !== "string" || !names.includes(value.alias)) {
      fail(`antdOverrides.${name}.alias must reference a known alias.`);
    }
    normalized[name] = { alias: value.alias };
  }
  return normalized;
}

function cssAliasName(name) {
  return name.replaceAll(".", "-").replaceAll("_", "-");
}

function cssValue(name, value) {
  if (typeof value !== "number") return String(value);
  if (name === "border.width" || name.startsWith("space.") || name.startsWith("radius.") || name.startsWith("font_size.")) return `${value}px`;
  return String(value);
}

function stableObject(value) {
  if (Array.isArray(value)) return value.map(stableObject);
  if (!value || typeof value !== "object") return value;
  return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stableObject(value[key])]));
}

function stableJson(value) {
  return `${JSON.stringify(stableObject(value), null, 2)}\n`;
}

function sha256(value) {
  return createHash("sha256").update(value).digest("hex");
}

function resolvedAntd(config) {
  const overrides = validateOverrides(config.antdOverrides, config.contractVersion);
  const entries = (config.contractVersion === LEGACY_CONTRACT_VERSION ? legacyAntdEntries
    : config.contractVersion === SEED_CONTRACT_VERSION ? seedAntdEntries : extendedAntdEntries).concat(
    config.contractVersion === CONTRACT_VERSION ? stateAntdEntries.filter(([, alias]) => alias in config.aliasValues) : []
  );
  const resolved = Object.fromEntries(entries.map(([token, defaultAlias]) => {
    const override = overrides[token];
    if (override !== undefined) {
      return [token, typeof override === "object"
        ? { source: "alias", alias: override.alias, value: config.aliasValues[override.alias] }
        : { source: "literal", value: override }];
    }
    const alias = defaultAlias;
    return [token, { source: "alias", alias, value: config.aliasValues[alias] }];
  }));
  for (const [token, override] of Object.entries(overrides)) {
    if (token in resolved) continue;
    resolved[token] = typeof override === "object"
      ? { source: "alias", alias: override.alias, value: config.aliasValues[override.alias] }
      : { source: "literal", value: override };
  }
  return resolved;
}

function aliasCss(aliasValues, contractVersion) {
  const rows = aliasesForVersion(contractVersion).filter((name) => name in aliasValues)
    .map((name) => `  --alias-${cssAliasName(name)}: ${cssValue(name, aliasValues[name])};`);
  return `/* Generated by UX Proto Foundation Core contract v${contractVersion}. Do not edit. */\n:root {\n${rows.join("\n")}\n}\n`;
}

function staticAntdCss(antdTokens, contractVersion) {
  try {
    const runtimeRequire = foundationRuntime().require;
    const previous = process.env.NODE_ENV;
    process.env.NODE_ENV = "production";
    try {
      const React = runtimeRequire("react");
      const antd = runtimeRequire("antd");
      const { extractStyle } = runtimeRequire("@ant-design/static-style-extract");
      const token = Object.fromEntries(Object.entries(antdTokens).map(([name, resolved]) => [name, resolved.value]));
      return extractStyle({
        ...(contractVersion === LEGACY_CONTRACT_VERSION ? { includes: [...staticStyleIncludes] } : {}),
        antdInstance: antd,
        customTheme: (node) => React.createElement(antd.ConfigProvider, { theme: { cssVar: true, token } }, node)
      });
    } finally {
      if (previous === undefined) delete process.env.NODE_ENV;
      else process.env.NODE_ENV = previous;
    }
  } catch (cause) {
    throw new Error("Foundation compiler requires the co-packaged locked React/AntD static-style runtime.", { cause });
  }
}

function themeModule(aliasValues, antdTokens, contractVersion) {
  const aliasRows = aliasesForVersion(contractVersion).filter((name) => name in aliasValues)
    .map((name) => `  ${JSON.stringify(name)}: ${JSON.stringify(aliasValues[name])}`);
  const tokenRows = Object.entries(antdTokens).map(([token, resolved]) => {
    const expression = resolved.source === "alias"
      ? `aliasTokens[${JSON.stringify(resolved.alias)}]`
      : JSON.stringify(resolved.value);
    return `    ${JSON.stringify(token)}: ${expression}`;
  });
  return [
    `// Generated by UX Proto Foundation Core contract v${contractVersion}. Do not edit.`,
    "export const aliasTokens = {",
    `${aliasRows.join(",\n")}`,
    "};",
    "",
    "export const themeConfig = {",
    '  "cssVar": true,',
    '  "token": {',
    `${tokenRows.join(",\n")}`,
    "  }",
    "};",
    ""
  ].join("\n");
}

export function getFoundationContract() {
  return {
    contractVersion: CONTRACT_VERSION,
    aliases: statefulAliasNames.map((name) => ({ name, type: aliasType(name), required: !stateAliasNames.includes(name) })),
    allowedAntdOverrides: [...statefulAntdOverrides]
  };
}

export function compileFoundation({ config } = {}) {
  validateVersionAndOuterShape(config);
  validateAliasValues(config.aliasValues, { contractVersion: config.contractVersion, requireComplete: true });
  const normalized = {
    contractVersion: config.contractVersion,
    aliasValues: Object.fromEntries(aliasesForVersion(config.contractVersion)
      .filter((name) => name in config.aliasValues).map((name) => [name, config.aliasValues[name]])),
    ...("antdOverrides" in config ? { antdOverrides: validateOverrides(config.antdOverrides, config.contractVersion) } : {})
  };
  const antdTokens = resolvedAntd(normalized);
  const artifacts = [
    { path: "alias-vars.generated.css", content: aliasCss(normalized.aliasValues, config.contractVersion) },
    { path: "antd.generated.css", content: staticAntdCss(antdTokens, config.contractVersion) },
    { path: "theme-config.generated.mjs", content: themeModule(normalized.aliasValues, antdTokens, config.contractVersion) }
  ];
  const contentDigest = `sha256:${sha256(stableJson(artifacts.map(({ path, content }) => ({ path, sha256: sha256(content) }))))}`;
  return { contractVersion: config.contractVersion, artifacts, contentDigest };
}

export function upgradeFoundation({ config, targetContractVersion } = {}) {
  validateVersionAndOuterShape(config);
  if (![SEED_CONTRACT_VERSION, GENERIC_CONTRACT_VERSION, CONTRACT_VERSION].includes(targetContractVersion)) fail(`targetContractVersion must be ${SEED_CONTRACT_VERSION}, ${GENERIC_CONTRACT_VERSION} or ${CONTRACT_VERSION}.`);
  if (config.contractVersion > targetContractVersion) fail("targetContractVersion must not downgrade the Foundation contract.");
  validateAliasValues(config.aliasValues, { contractVersion: targetContractVersion, requireComplete: true });
  const overrides = "antdOverrides" in config ? validateOverrides(config.antdOverrides, targetContractVersion) : undefined;
  const changes = config.contractVersion === targetContractVersion ? [] : [{ path: "contractVersion", kind: "updated", value: targetContractVersion }];
  return {
    config: {
      contractVersion: targetContractVersion,
      aliasValues: Object.fromEntries(aliasesForVersion(targetContractVersion)
        .filter((name) => name in config.aliasValues).map((name) => [name, config.aliasValues[name]])),
      ...(overrides ? { antdOverrides: overrides } : {})
    },
    changes
  };
}
