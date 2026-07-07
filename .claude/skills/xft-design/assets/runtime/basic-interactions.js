(function () {
  function setHidden(el, hidden) {
    if (!el) {
      return;
    }
    el.hidden = hidden;
    el.setAttribute("aria-hidden", hidden ? "true" : "false");
  }

  function activateTabs(root, trigger) {
    var triggers = Array.from(root.querySelectorAll("[data-tab-trigger]"));
    triggers.forEach(function (item) {
      var active = item === trigger;
      item.classList.toggle("active", active);
      item.classList.toggle("is-active", active);
      item.setAttribute("aria-selected", active ? "true" : "false");
    });
  }

  function bindTabs(root) {
    root.addEventListener("click", function (event) {
      var close = event.target.closest("[data-tab-close]");
      if (close) {
        event.stopPropagation();
        return;
      }
      var trigger = event.target.closest("[data-tab-trigger]");
      if (!trigger || !root.contains(trigger)) {
        return;
      }
      activateTabs(root, trigger);
    });
  }

  function setExpanded(toggle, panel, expanded) {
    toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
    toggle.classList.toggle("is-selected", expanded);
    var arrow = toggle.querySelector(".nav-arrow");
    if (arrow) {
      arrow.classList.toggle("contract", !expanded);
    }
    if (panel) {
      panel.hidden = !expanded;
    }
  }

  function bindMenu(root) {
    root.addEventListener("click", function (event) {
      var item = event.target.closest("[data-menu-item]");
      if (item && root.contains(item)) {
        root.querySelectorAll("[data-menu-item]").forEach(function (candidate) {
          var active = candidate === item;
          candidate.classList.toggle("is-active", active);
          candidate.setAttribute("aria-current", active ? "page" : "false");
        });
      }

      var toggle = event.target.closest("[data-menu-toggle]");
      if (!toggle || !root.contains(toggle)) {
        return;
      }
      var group = toggle.closest("[data-menu-group]");
      var panel = group ? group.querySelector("[data-menu-panel]") : null;
      var expanded = toggle.getAttribute("aria-expanded") === "true";
      setExpanded(toggle, panel, !expanded);
    });
  }

  function bindCollapse(root) {
    root.addEventListener("click", function (event) {
      var toggle = event.target.closest("[data-collapse-toggle]");
      if (!toggle || !root.contains(toggle)) {
        return;
      }
      var panelId = toggle.getAttribute("data-collapse-toggle");
      var panel = document.getElementById(panelId);
      if (!panel) {
        return;
      }
      var expanded = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", expanded ? "false" : "true");
      panel.hidden = expanded;
    });
  }

  function bindSwitches(root) {
    root.addEventListener("click", function (event) {
      var toggle = event.target.closest("[data-switch]");
      if (!toggle || !root.contains(toggle)) {
        return;
      }
      var checked = toggle.getAttribute("aria-checked") === "true";
      toggle.setAttribute("aria-checked", checked ? "false" : "true");
      toggle.classList.toggle("is-active", !checked);
    });
  }

  function bindOverlayDismiss() {
    document.addEventListener("click", function (event) {
      var close = event.target.closest("[data-overlay-close]");
      if (!close) {
        return;
      }
      var overlay = close.closest("[data-overlay]");
      if (overlay) {
        setHidden(overlay, true);
      }
    });
  }

  function bindOverlayOpen() {
    document.addEventListener("click", function (event) {
      var trigger = event.target.closest("[data-overlay-open]");
      if (!trigger) {
        return;
      }
      var targetId = trigger.getAttribute("data-overlay-open");
      if (!targetId) {
        return;
      }
      var overlay = document.getElementById(targetId);
      if (overlay) {
        setHidden(overlay, false);
      }
    });
  }

  function bindAnchors(root) {
    root.addEventListener("click", function (event) {
      var trigger = event.target.closest("[data-anchor-target]");
      if (!trigger || !root.contains(trigger)) {
        return;
      }
      var targetId = trigger.getAttribute("data-anchor-target");
      if (!targetId) {
        return;
      }
      root.querySelectorAll("[data-anchor-target]").forEach(function (candidate) {
        var active = candidate === trigger;
        candidate.classList.toggle("is-active", active);
        candidate.setAttribute("aria-current", active ? "true" : "false");
      });
      var panel = document.getElementById(targetId);
      if (panel && typeof panel.scrollIntoView === "function") {
        panel.scrollIntoView({ block: "start", behavior: "smooth" });
      }
    });
  }

  function closeDisclosures(exceptionTrigger, exceptionPanel) {
    document.querySelectorAll("[data-disclosure-panel]").forEach(function (panel) {
      if (panel === exceptionPanel) {
        return;
      }
      setHidden(panel, true);
      var triggerId = panel.getAttribute("data-disclosure-owned-by");
      if (!triggerId) {
        return;
      }
      var trigger = document.querySelector('[data-disclosure-id="' + triggerId + '"]');
      if (trigger && trigger !== exceptionTrigger) {
        trigger.setAttribute("aria-expanded", "false");
        trigger.classList.remove("is-active");
      }
    });
  }

  function bindDisclosures() {
    document.addEventListener("click", function (event) {
      var trigger = event.target.closest("[data-disclosure-trigger]");
      if (trigger) {
        var disclosureId = trigger.getAttribute("data-disclosure-id");
        var panel = disclosureId
          ? document.querySelector('[data-disclosure-panel="' + disclosureId + '"]')
          : null;
        if (!panel) {
          return;
        }
        var expanded = trigger.getAttribute("aria-expanded") === "true";
        closeDisclosures(trigger, expanded ? null : panel);
        trigger.setAttribute("aria-expanded", expanded ? "false" : "true");
        trigger.classList.toggle("is-active", !expanded);
        setHidden(panel, expanded);
        panel.setAttribute("data-disclosure-owned-by", disclosureId);
        return;
      }

      if (
        event.target.closest("[data-disclosure-panel]") ||
        event.target.closest("[data-disclosure-trigger]")
      ) {
        return;
      }
      closeDisclosures(null, null);
    });
  }

  document.querySelectorAll("[data-tabs-root]").forEach(bindTabs);
  document.querySelectorAll("[data-menu-root]").forEach(bindMenu);
  document.querySelectorAll("[data-collapse-root]").forEach(bindCollapse);
  document.querySelectorAll("[data-switch-root]").forEach(bindSwitches);
  document.querySelectorAll("[data-anchor-root]").forEach(bindAnchors);
  bindOverlayDismiss();
  bindOverlayOpen();
  bindDisclosures();
})();
