# XFT Content Action Bar

Use `XftContentActionBar` when page-level actions must remain available while the workspace canvas scrolls. Import it from `components/product-specific/XftContentActionBar`, then place it inside a page-private host supplied through the Application Frame's `workspaceBottomDock`.

The page-private host owns width and horizontal position. The page also owns button alignment, order, emphasis, business meaning, handlers, loading, and disabled state. Compose those choices inside `children` with existing layout primitives.

`XftContentActionBar` only fills its owning container, supplies its bright background, full-width top boundary, compact padding, `role="toolbar"`, and the required accessible name. It does not use fixed, sticky, or absolute positioning and does not accept alignment, action, business-state, `className`, or `style` props.
