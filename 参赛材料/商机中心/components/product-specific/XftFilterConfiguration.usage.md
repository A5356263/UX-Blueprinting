# XFT Filter Configuration

Use this Product-specific component when an XFT prototype needs a recognizable filter-configuration editor. Import it from `components/product-specific/XftFilterConfiguration` and keep the implementation unchanged.

The page supplies field definitions, current values, defaults, and an `onChange` handler. The component presents available fields separately from enabled-field settings, then emits in-memory changes for field enablement, operators, default values, and reset.

The bundled `XftFilterConfiguration.mock.ts` data is illustrative; it is not a backend contract. Saved templates, remote field schemas, complex grouping, drag ordering, query execution, persistence, permissions, and production compatibility remain outside this component.
