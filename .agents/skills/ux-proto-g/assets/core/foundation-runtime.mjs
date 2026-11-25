let authority = null;

export function installFoundationRuntime({ root, require: runtimeRequire, versions }) {
  if (!root || typeof runtimeRequire !== "function" || !versions || typeof versions !== "object") {
    throw new Error("Foundation runtime authority is invalid.");
  }
  authority = Object.freeze({
    root,
    require: runtimeRequire,
    versions: Object.freeze({ ...versions })
  });
  return authority;
}

export function foundationRuntime() {
  if (!authority) {
    throw new Error("Foundation compiler requires the Builder-validated locked runtime authority.");
  }
  return authority;
}
