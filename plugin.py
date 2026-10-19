# Copyright (c) 2025-2026 DeepBeepMeep - part of WanGP, WanGP Community License 2.0 (see LICENSE.txt)
"""MiniMax H3 prompt syntax highlighter for the main WanGP prompt textarea."""
import gradio as gr

from shared.utils.plugins import WAN2GPPlugin

PlugIn_Name = "MiniMax H3 Prompt Highlighter"
PlugIn_Id = "MiniMaxH3PromptHighlighter"


def is_h3_model(model_type) -> bool:
    text = str(model_type or "").split("|", 1)[0]
    normalized = text.lower().replace(" ", "_").replace("-", "_")
    return "minimax_h3" in normalized or "minimaxh3" in normalized.replace("_", "")


JS_CODE = r"""
(function () {
  "use strict";

  var COLORS_KEY = "wangp_h3_prompt_highlighter_colors";
  var STYLE_ID = "wangp-h3hl-style";
  var enabled = true;
  var modelIsH3 = true;
  var modelSeen = false;

  var DEFAULT_COLORS = {
    section: "#5c9dd1",
    task: "#7f8ec9",
    ref: "#bd9a62",
    subject1: "#6f8db5",
    subject2: "#58a0a8",
    subject3: "#86ac86",
    subject4: "#c78a66",
    subjectMore: "#4a6b8a",
    shot: "#66a575",
    time: "#8d84c4",
    anchor: "#98a2b3",
    dialog: "#bf6a4c",
    tag: "#a54f4a",
    mode: "#98a06b"
  };

  var COLOR_FIELDS = [
    { key: "section", label: "Section titles" },
    { key: "task", label: "Task tags" },
    { key: "ref", label: "Picture/Video/Audio" },
    { key: "subject1", label: "Subject 1" },
    { key: "subject2", label: "Subject 2" },
    { key: "subject3", label: "Subject 3" },
    { key: "subject4", label: "Subject 4" },
    { key: "subjectMore", label: "Subject 5+" },
    { key: "shot", label: "Shot markers" },
    { key: "time", label: "Timestamps" },
    { key: "anchor", label: "Picture anchors" },
    { key: "dialog", label: "Dialogues" },
    { key: "tag", label: "scenetrans / cutoff" },
    { key: "mode", label: "Retention modes" }
  ];

  var colors = {};

  try {
    var rawColors = localStorage.getItem(COLORS_KEY);
    if (rawColors) {
      var parsed = JSON.parse(rawColors);
      for (var k in DEFAULT_COLORS) {
        if (Object.prototype.hasOwnProperty.call(parsed, k) && typeof parsed[k] === "string") {
          colors[k] = parsed[k];
        }
      }
    }
  } catch (e) {}

  function colorFor(key) {
    if (typeof colors[key] === "string" && colors[key]) return colors[key];
    return DEFAULT_COLORS[key] || "#e5e7eb";
  }

  function wash(key) {
    var c = colorFor(key) || "";
    if (c.charAt(0) === "#") c = c.slice(1);
    if (c.length === 3 || c.length === 4) {
      var e = "";
      for (var i = 0; i < 3; i++) {
        e += c.charAt(i) + c.charAt(i);
      }
      c = e;
    }
    if (c.length === 8) c = c.slice(0, 6);
    if (c.length !== 6) return "transparent";
    return "#" + c + "24";
  }

  function pluginRoot() {
    if (window.gradioApp) {
      try {
        return window.gradioApp();
      } catch (e) {}
    }
    var app = document.querySelector("gradio-app");
    return app ? app.shadowRoot || app : document;
  }

  function buildCss() {
    return (
      ".wangp-h3hl-controls-row .h3hl-bar{" +
      "display:flex;flex-direction:row;flex-wrap:nowrap;align-items:center;" +
      "gap:14px;width:100%;box-sizing:border-box;" +
      "background:var(--block-background-fill,#fff);" +
      "border:1px solid var(--border-color-primary,#d1d5db);border-radius:var(--block-radius,8px);" +
      "padding:10px 14px;box-shadow:var(--block-shadow);color:var(--body-text-color,#1f2937);" +
      "}" +
      ".wangp-h3hl-controls-row .h3hl-check{" +
      "display:flex;align-items:center;gap:8px;cursor:pointer;flex:0 0 auto;" +
      "font-size:var(--text-sm,14px);font-weight:var(--checkbox-label-text-weight,400);" +
      "color:var(--checkbox-label-text-color,var(--body-text-color,#1f2937));user-select:none;" +
      "}" +
      ".wangp-h3hl-controls-row .h3hl-check input[type=checkbox]{" +
      "position:absolute;opacity:0;width:0;height:0;margin:0;pointer-events:none;" +
      "}" +
      ".wangp-h3hl-controls-row .h3hl-check .h3hl-box{" +
      "position:relative;display:inline-block;width:16px;height:16px;flex:0 0 auto;box-sizing:border-box;" +
      "border:2px solid var(--checkbox-border-color,var(--border-color-accent,#9ca3af));" +
      "border-radius:4px;background:var(--background-fill-primary,#ffffff);" +
      "}" +
      ".wangp-h3hl-controls-row .h3hl-check input:checked + .h3hl-box{" +
      "background:var(--color-accent,#22c55e);border-color:var(--color-accent,#22c55e);" +
      "}" +
      ".wangp-h3hl-controls-row .h3hl-check input:checked + .h3hl-box::after{" +
      "content:'';position:absolute;left:3px;top:0;width:4px;height:9px;" +
      "border:solid #ffffff;border-width:0 2px 2px 0;transform:rotate(45deg);" +
      "}" +
      ".wangp-h3hl-controls-row .h3hl-check input:focus-visible + .h3hl-box{" +
      "outline:2px solid var(--color-accent,#22c55e);outline-offset:2px;" +
      "}" +
      ".wangp-h3hl-controls-row .h3hl-check span:last-child{white-space:nowrap;}" +
      ".wangp-h3hl-controls-row .h3hl-bar button{" +
      "margin-left:auto;flex:0 0 auto;" +
      "font-size:var(--button-small-text-size,13px);font-weight:var(--button-small-text-weight,600);" +
      "padding:var(--button-small-padding,5px 10px);cursor:pointer;" +
      "border:1px solid var(--button-secondary-border-color,rgba(0,0,0,0.12));" +
      "border-radius:var(--button-radius,calc(var(--radius-md,8px) - 2px));" +
      "background:var(--button-secondary-background-fill,#e5e7eb);" +
      "color:var(--button-secondary-text-color,#1f2937);" +
      "transition:var(--button-transition,0.2s);" +
      "}" +
      ".wangp-h3hl-controls-row .h3hl-bar button:hover{" +
      "background:var(--button-secondary-background-fill-hover,#d1d5db);" +
      "border-color:var(--button-secondary-border-color-hover,rgba(0,0,0,0.2));" +
      "}" +
      ".wangp-h3hl-controls-row[hidden],.h3hl-hidden{display:none!important;}" +
      ".h3hl-layer{" +
      "position:absolute;inset:0;pointer-events:none;overflow:hidden;z-index:0;" +
      "white-space:pre-wrap;word-wrap:break-word;overflow-wrap:break-word;" +
      "}" +
      ".h3hl-ta{" +
      "position:relative;z-index:1;" +
      "background:transparent!important;color:rgba(0,0,0,0)!important;" +
      "caret-color:#000000!important;" +
      "}" +
      ".h3hl-ta::placeholder{color:transparent!important;}" +
      ".h3hl-ta::selection{background:transparent!important;color:rgba(0,0,0,0)!important;}" +
      ".h3hl-layer .h3hl-sel{background:rgba(59,130,246,0.32);border-radius:2px;}" +
      ".h3-section{color:" + colorFor("section") + ";background:" + wash("section") + ";border-radius:3px;}" +
      ".h3-navtitle{color:#7fa3c9;background:#7fa3c924;border-radius:3px;}" +
      ".h3-cmd{color:#4f8f8a;background:#4f8f8a24;border-radius:3px;}" +
      ".h3-task{color:" + colorFor("task") + ";background:" + wash("task") + ";border-radius:3px;}" +
      ".h3-ref{color:" + colorFor("ref") + ";background:" + wash("ref") + ";border-radius:3px;}" +
      ".h3-subject-1{color:" + colorFor("subject1") + ";background:" + wash("subject1") + ";border-radius:3px;}" +
      ".h3-subject-2{color:" + colorFor("subject2") + ";background:" + wash("subject2") + ";border-radius:3px;}" +
      ".h3-subject-3{color:" + colorFor("subject3") + ";background:" + wash("subject3") + ";border-radius:3px;}" +
      ".h3-subject-4{color:" + colorFor("subject4") + ";background:" + wash("subject4") + ";border-radius:3px;}" +
      ".h3-subject-more{color:" + colorFor("subjectMore") + ";background:" + wash("subjectMore") + ";border-radius:3px;}" +
      ".h3-shot{color:" + colorFor("shot") + ";background:" + wash("shot") + ";border-radius:3px;}" +
      ".h3-time{color:" + colorFor("time") + ";background:" + wash("time") + ";border-radius:3px;}" +
      ".h3-anchor{color:" + colorFor("anchor") + ";background:" + wash("anchor") + ";border-radius:3px;}" +
      ".h3-dialog{color:" + colorFor("dialog") + ";background:" + wash("dialog") + ";border-radius:3px;}" +
      ".h3-tag{color:" + colorFor("tag") + ";background:" + wash("tag") + ";border-radius:3px;}" +
      ".h3-speaker{color:#d4b06a;background:#d4b06a24;border-radius:3px;}" +
      ".h3-mode{color:" + colorFor("mode") + ";background:" + wash("mode") + ";border-radius:3px;}" +
      ".h3hl-layer[hidden]{display:none!important;}"
    );
  }

  var masterRe = new RegExp(
    [
      "(?<section>^(?:subject_definitions|summary|retention_analysis|detailed_description|integrated_multimodal_description|overall_soundscape|non_diegetic_music):)",
      "(?<navtitle>^# .*)",
      "(?<cmd>\\[/[^\\]]+\\])",
      "(?<task>\\[(?:reference generation|video editing|video continuation|audio reuse|audio reference|keyframe completion)[^\\]]*\\])",
      "(?<subject><Subject \\d+>)",
      "(?<ref><(?:Picture|Video|Audio) \\d+>)",
      "(?<shot>\\[Shot \\d+\\])",
      "(?<time>\\bAt \\d{2}:\\d{2}\\.\\d{3}\\b)",
      "(?<anchor>For the target video, at [\\d.]+ seconds into the target video)",
      "(?<dialog><d>(?:\\[[^\\]]*\\])?[\\s\\S]*?<\\/d>)",
      "(?<dialogtag><d>|<\\/d>)",
      "(?<tag><scenetrans>|<cutoff>)",
      "(?<speaker>\\(S\\d+\\))",
      "(?<mode>\\b(?:fully_preserved|partially_preserved|attribute_transfer|weak_reference|fully_copy|partially_copy)\\b)"
    ].join("|"),
    "gim"
  );

  function ensureStyle() {
    var root = pluginRoot();
    var style = null;
    if (root && root !== document && root.getElementById) {
      style = root.getElementById(STYLE_ID);
    }
    if (!style) style = document.getElementById(STYLE_ID);
    if (!style) {
      style = document.createElement("style");
      style.id = STYLE_ID;
    }
    var host = root === document || !root ? document.head : root;
    if (style.parentElement !== host && style.getRootNode() !== host) {
      host.appendChild(style);
    }
    style.textContent = buildCss();
  }

  function refreshStyle() {
    ensureStyle();
    var root = pluginRoot();
    var tas = root.querySelectorAll("textarea.h3hl-ta");
    for (var i = 0; i < tas.length; i++) {
      render(tas[i]);
    }
  }

  function esc(s) {
    return s
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function classify(groups) {
    if (groups.section) return "h3-section";
    if (groups.navtitle) return "h3-navtitle";
    if (groups.cmd) return "h3-cmd";
    if (groups.task) return "h3-task";
    if (groups.subject) {
      var sm = String(groups.subject).match(/(\d+)/);
      var n = sm ? parseInt(sm[1], 10) : 1;
      if (n >= 5) return "h3-subject-more";
      return "h3-subject-" + n;
    }
    if (groups.ref) return "h3-ref";
    if (groups.shot) return "h3-shot";
    if (groups.time) return "h3-time";
    if (groups.anchor) return "h3-anchor";
    if (groups.dialog) return "h3-dialog";
    if (groups.dialogtag) return "h3-dialog";
    if (groups.tag) return "h3-tag";
    if (groups.speaker) return "h3-speaker";
    if (groups.mode) return "h3-mode";
    return "h3-plain";
  }

  function tokenize(text) {
    var segs = [];
    if (!text) return segs;
    var last = 0;
    var re = new RegExp(masterRe.source, masterRe.flags);
    var m;
    while ((m = re.exec(text)) !== null) {
      if (m[0].length === 0) {
        re.lastIndex += 1;
        continue;
      }
      if (m.index > last) {
        segs.push({ s: last, e: m.index, cls: null });
      }
      segs.push({
        s: m.index,
        e: m.index + m[0].length,
        cls: classify(m.groups || {})
      });
      last = m.index + m[0].length;
    }
    if (last < text.length) {
      segs.push({ s: last, e: text.length, cls: null });
    }
    return segs;
  }

  function buildHtml(text, selStart, selEnd) {
    if (!text) return "&#8203;";
    var hasSel =
      typeof selStart === "number" &&
      typeof selEnd === "number" &&
      selStart >= 0 &&
      selEnd >= 0 &&
      selStart !== selEnd;
    if (hasSel && selStart > selEnd) {
      var t = selStart;
      selStart = selEnd;
      selEnd = t;
    }
    var segs = tokenize(text);
    var html = "";
    var openSel = false;
    for (var i = 0; i < segs.length; i++) {
      var s = segs[i].s;
      var e = segs[i].e;
      var cls = segs[i].cls;
      var cl = hasSel ? Math.max(s, Math.min(selStart, e)) : s;
      var cr = hasSel ? Math.min(e, Math.max(selEnd, s)) : s;
      var pieces = [
        { s: s, e: cl, sel: false },
        { s: cl, e: cr, sel: true },
        { s: cr, e: e, sel: false }
      ];
      for (var j = 0; j < pieces.length; j++) {
        var p = pieces[j];
        if (p.e <= p.s) continue;
        if (p.sel !== openSel) {
          html += openSel ? "</span>" : '<span class="h3hl-sel">';
          openSel = p.sel;
        }
        var frag = esc(text.slice(p.s, p.e));
        if (cls) {
          frag = '<span class="' + cls + '">' + frag + "</span>";
        }
        html += frag;
      }
    }
    if (openSel) html += "</span>";
    if (text.charAt(text.length - 1) === "\n") html += "\n";
    return html || "&#8203;";
  }

  function syncLayerStyles(ta, layer) {
    var cs = window.getComputedStyle(ta);
    layer.style.fontFamily = cs.fontFamily;
    layer.style.fontSize = cs.fontSize;
    layer.style.fontWeight = cs.fontWeight;
    layer.style.fontStyle = cs.fontStyle;
    layer.style.lineHeight = cs.lineHeight;
    layer.style.letterSpacing = cs.letterSpacing;
    layer.style.textTransform = cs.textTransform;
    layer.style.textIndent = cs.textIndent;
    layer.style.paddingTop = cs.paddingTop;
    layer.style.paddingRight = cs.paddingRight;
    layer.style.paddingBottom = cs.paddingBottom;
    layer.style.paddingLeft = cs.paddingLeft;
    layer.style.tabSize = cs.tabSize || "4";
    layer.style.boxSizing = cs.boxSizing;
  }

  function isActive() {
    return enabled && modelIsH3;
  }

  function render(ta) {
    var layer = ta._h3hlLayer;
    if (!layer) return;
    if (!layer.isConnected) {
      rebind(ta);
      return;
    }
    syncLayerStyles(ta, layer);
    var html;
    try {
      var selA = ta.selectionStart;
      var selB = ta.selectionEnd;
      if (
        typeof selA === "number" &&
        typeof selB === "number" &&
        selA >= 0 &&
        selB >= 0 &&
        selA !== selB
      ) {
        html = buildHtml(ta.value, selA, selB);
      } else {
        html = buildHtml(ta.value, -1, -1);
      }
    } catch (err) {
      html = buildHtml(ta.value, -1, -1);
    }
    if (layer._h3hlLast !== html) {
      layer.innerHTML = html;
      layer._h3hlLast = html;
    }
    layer.scrollTop = ta.scrollTop;
    layer.scrollLeft = ta.scrollLeft;
    ta._h3hlValSeen = ta.value;
  }

  function setTaEnabled(ta, on) {
    var layer = ta._h3hlLayer;
    if (on) {
      ta.classList.add("h3hl-ta");
      if (layer) layer.hidden = false;
      render(ta);
    } else {
      ta.classList.remove("h3hl-ta");
      if (layer) layer.hidden = true;
    }
  }

  function startValueWatch(ta) {
    if (ta._h3hlValTimer) return;
    ta._h3hlValSeen = ta.value;
    ta._h3hlValTimer = setInterval(function () {
      if (ta._h3hlBound !== "1") {
        clearInterval(ta._h3hlValTimer);
        ta._h3hlValTimer = null;
        return;
      }
      if (ta.value !== ta._h3hlValSeen) {
        render(ta);
      }
    }, 250);
  }

  function rebind(ta) {
    if (ta._h3hlValTimer) {
      clearInterval(ta._h3hlValTimer);
      ta._h3hlValTimer = null;
    }
    if (ta._h3hlRO) {
      try { ta._h3hlRO.disconnect(); } catch (e) {}
      ta._h3hlRO = null;
    }
    if (ta._h3hlLayer && ta._h3hlLayer.parentNode) {
      ta._h3hlLayer.parentNode.removeChild(ta._h3hlLayer);
    }
    ta._h3hlLayer = null;
    ta._h3hlBound = "0";
    attach(ta);
  }

  function attach(ta) {
    if (!ta || ta._h3hlBound === "1") return false;
    var parent = ta.parentElement;
    if (!parent) return false;

    var cs = window.getComputedStyle(parent);
    if (cs.position === "static") parent.style.position = "relative";

    var layer = document.createElement("div");
    layer.className = "h3hl-layer";
    layer.setAttribute("aria-hidden", "true");
    parent.insertBefore(layer, ta);
    ta._h3hlLayer = layer;
    ta._h3hlBound = "1";

    var onValueEvent = function () {
      render(ta);
    };
    ta.addEventListener("input", onValueEvent);
    ta.addEventListener("change", onValueEvent);
    ta.addEventListener("keyup", onValueEvent);
    ta.addEventListener("select", onValueEvent);
    ta.addEventListener("mouseup", onValueEvent);
    ta.addEventListener("scroll", function () {
      if (!ta._h3hlLayer) return;
      ta._h3hlLayer.scrollTop = ta.scrollTop;
      ta._h3hlLayer.scrollLeft = ta.scrollLeft;
    });

    if (window.ResizeObserver) {
      var ro = new ResizeObserver(function () {
        render(ta);
      });
      ro.observe(ta);
      ta._h3hlRO = ro;
    }

    startValueWatch(ta);
    setTaEnabled(ta, isActive());
    return true;
  }

  function eachPromptTa(fn) {
    var root = pluginRoot();
    var ids = ["wangp-prompt-advanced", "wangp-prompt-wizard"];
    for (var i = 0; i < ids.length; i++) {
      var el = root.querySelector("#" + ids[i]);
      if (!el) continue;
      var ta = el.querySelector("textarea");
      if (ta) fn(ta);
    }
  }

  function detachGone() {
    eachPromptTa(function (ta) {
      if (ta._h3hlBound !== "1" || !ta._h3hlLayer || !ta._h3hlLayer.isConnected) {
        rebind(ta);
      }
    });
  }

  function eachControlsRow(fn) {
    var root = pluginRoot();
    var nodes = root.querySelectorAll(
      "#h3hl-controls-row, .wangp-h3hl-controls-row"
    );
    for (var i = 0; i < nodes.length; i++) fn(nodes[i]);
  }

  function applyActive() {
    var active = isActive();
    eachPromptTa(function (ta) {
      if (ta._h3hlBound === "1") setTaEnabled(ta, active);
      else attach(ta);
    });
    syncControlsRow();
  }

  function wireControls() {
    var root = pluginRoot();
    if (!root) return;
    var cb = root.querySelector("#h3hl-enable");
    if (cb && cb._h3hlWired !== "1") {
      cb._h3hlWired = "1";
      cb.checked = enabled;
      cb.addEventListener("change", function () {
        setEnabled(cb.checked);
      });
    }
    var btn = root.querySelector("#h3hl-colors-btn");
    if (btn && btn._h3hlWired !== "1") {
      btn._h3hlWired = "1";
      btn.addEventListener("click", function (ev) {
        ev.preventDefault();
        openColorModal();
      });
    }
  }

  function syncControlsRow() {
    if (!modelSeen) return;
    eachControlsRow(function (row) {
      if (modelIsH3) {
        row.classList.remove("h3hl-hidden");
        row.style.removeProperty("display");
        row.hidden = false;
      } else {
        row.classList.add("h3hl-hidden");
        row.style.setProperty("display", "none", "important");
      }
    });
  }

  function readModelFromDom() {
    var root = pluginRoot();
    var el =
      root.querySelector("#wangp_model_choice_target textarea") ||
      root.querySelector("#wangp_model_choice_target input");
    if (el && typeof el.value === "string" && el.value.trim()) {
      setModel(el.value);
      return true;
    }
    return false;
  }

  function setModel(modelType) {
    var mt = String(modelType || "").trim();
    if (!mt) return;
    var base = mt.split("|")[0].trim().toLowerCase();
    if (!base) return;
    var norm = base.replace(/[\s-]+/g, "_");
    modelIsH3 = norm.indexOf("minimax_h3") !== -1 || norm.replace(/_/g, "").indexOf("minimaxh3") !== -1;
    modelSeen = true;
    applyActive();
  }

  function attachAll() {
    ensureStyle();
    readModelFromDom();
    wireControls();
    var found = 0;
    eachPromptTa(function (ta) {
      if (attach(ta)) found += 1;
      else {
        setTaEnabled(ta, isActive());
        render(ta);
      }
    });
    syncControlsRow();
    return found;
  }

  function setEnabled(value) {
    enabled = !!value;
    applyActive();
  }

  function normalizeHex(value, fallback) {
    if (!value) return fallback || "";
    var v = String(value).trim();
    if (!v) return fallback || "";
    if (v.charAt(0) !== "#") v = "#" + v;
    if (/^#([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/.test(v)) {
      return v.toLowerCase();
    }
    return fallback;
  }

  function pickerValue(hex) {
    if (!hex) return "#000000";
    var h = hex.replace("#", "");
    if (h.length === 3 || h.length === 4) {
      h = h.charAt(0) + h.charAt(0) + h.charAt(1) + h.charAt(1) + h.charAt(2) + h.charAt(2);
    }
    return "#" + h.slice(0, 6);
  }

  function openColorModal() {
    var root = pluginRoot();
    var existing = root.querySelector("#h3hl-color-modal");
    if (existing) {
      existing.style.display = "flex";
      fillModalFields(existing);
      return;
    }

    var modal = document.createElement("div");
    modal.id = "h3hl-color-modal";
    modal.style.cssText =
      "position:fixed;inset:0;z-index:10000;display:flex;align-items:center;justify-content:center;" +
      "background:rgba(0,0,0,0.55);font-family:inherit;";

    var panel = document.createElement("div");
    panel.style.cssText =
      "background:var(--background-fill-primary,#1e293b);color:var(--body-text-color,#e5e7eb);" +
      "border:1px solid var(--border-color-primary,#475569);border-radius:12px;" +
      "width:min(440px,92vw);max-height:86vh;overflow:auto;padding:16px 18px;" +
      "box-shadow:0 20px 50px rgba(0,0,0,0.45);";

    var title = document.createElement("div");
    title.textContent = "H3 Highlight Colors";
    title.style.cssText = "font-weight:700;font-size:1.05em;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;gap:8px;";

    var closeX = document.createElement("button");
    closeX.type = "button";
    closeX.textContent = "×";
    closeX.title = "Close";
    closeX.style.cssText =
      "border:none;background:transparent;color:inherit;font-size:1.4em;line-height:1;cursor:pointer;padding:0 4px;";
    closeX.addEventListener("click", function () {
      modal.style.display = "none";
    });
    title.appendChild(closeX);

    var list = document.createElement("div");
    list.id = "h3hl-color-list";
    list.style.cssText = "display:flex;flex-direction:column;gap:8px;";

    for (var i = 0; i < COLOR_FIELDS.length; i++) {
      var field = COLOR_FIELDS[i];
      var row = document.createElement("label");
      row.style.cssText =
        "display:grid;grid-template-columns:1fr auto 9.5em;gap:8px;align-items:center;font-size:0.92em;";

      var name = document.createElement("span");
      name.textContent = field.label;

      var picker = document.createElement("input");
      picker.type = "color";
      picker.className = "h3hl-color-picker";
      picker.dataset.key = field.key;
      picker.style.cssText = "width:2.2em;height:1.8em;padding:0;border:none;background:transparent;cursor:pointer;";

      var hexInput = document.createElement("input");
      hexInput.type = "text";
      hexInput.className = "h3hl-color-hex";
      hexInput.dataset.key = field.key;
      hexInput.spellcheck = false;
      hexInput.style.cssText =
        "width:100%;box-sizing:border-box;border:1px solid var(--border-color-primary,#64748b);" +
        "border-radius:6px;background:var(--background-fill-secondary,#0f172a);color:inherit;" +
        "padding:4px 6px;font-family:ui-monospace,monospace;font-size:0.9em;";

      picker.addEventListener("input", (function (p, h) {
        return function () {
          h.value = p.value.toLowerCase();
          applyColorLive(p.dataset.key, h.value);
        };
      })(picker, hexInput));

      hexInput.addEventListener("change", (function (p, h) {
        return function () {
          var norm = normalizeHex(h.value, colorFor(p.dataset.key));
          h.value = norm || "";
          if (norm) {
            p.value = pickerValue(norm);
            applyColorLive(p.dataset.key, norm);
          }
        };
      })(picker, hexInput));

      row.appendChild(name);
      row.appendChild(picker);
      row.appendChild(hexInput);
      list.appendChild(row);
    }

    var actions = document.createElement("div");
    actions.style.cssText = "display:flex;gap:8px;justify-content:flex-end;margin-top:14px;flex-wrap:wrap;";

    function makeBtn(text, primary) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = text;
      b.style.cssText =
        "border:1px solid var(--border-color-primary,#64748b);border-radius:8px;cursor:pointer;" +
        "padding:6px 12px;font-weight:600;" +
        (primary
          ? "background:var(--color-accent,#2563eb);color:#fff;"
          : "background:var(--button-secondary-background-fill,#334155);color:var(--body-text-color,#e5e7eb);");
      return b;
    }

    var resetBtn = makeBtn("Reset defaults", false);
    resetBtn.addEventListener("click", function () {
      colors = {};
      try {
        localStorage.removeItem(COLORS_KEY);
      } catch (e) {}
      refreshStyle();
      fillModalFields(modal);
    });

    var cancelBtn = makeBtn("Cancel", false);
    cancelBtn.addEventListener("click", function () {
      colors = savedColorsSnapshot ? JSON.parse(JSON.stringify(savedColorsSnapshot)) : {};
      refreshStyle();
      modal.style.display = "none";
    });

    var saveBtn = makeBtn("Save", true);
    saveBtn.addEventListener("click", function () {
      commitModalFields(modal);
      try {
        localStorage.setItem(COLORS_KEY, JSON.stringify(colors));
      } catch (e) {}
      refreshStyle();
      modal.style.display = "none";
    });

    actions.appendChild(resetBtn);
    actions.appendChild(cancelBtn);
    actions.appendChild(saveBtn);

    modal.addEventListener("click", function (ev) {
      if (ev.target === modal) modal.style.display = "none";
    });
    modal.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") modal.style.display = "none";
    });

    panel.appendChild(title);
    panel.appendChild(list);
    panel.appendChild(actions);
    modal.appendChild(panel);
    root.appendChild(modal);
    fillModalFields(modal);
  }

  var savedColorsSnapshot = null;

  function applyColorLive(key, value) {
    colors[key] = value;
    refreshStyle();
  }

  function fillModalFields(modal) {
    savedColorsSnapshot = JSON.parse(JSON.stringify(colors));
    var pickers = modal.querySelectorAll(".h3hl-color-picker");
    var hexes = modal.querySelectorAll(".h3hl-color-hex");
    var i;
    for (i = 0; i < pickers.length; i++) {
      pickers[i].value = pickerValue(colorFor(pickers[i].dataset.key));
    }
    for (i = 0; i < hexes.length; i++) {
      hexes[i].value = colorFor(hexes[i].dataset.key) || "";
    }
  }

  function commitModalFields(modal) {
    var hexes = modal.querySelectorAll(".h3hl-color-hex");
    for (var i = 0; i < hexes.length; i++) {
      var key = hexes[i].dataset.key;
      var norm = normalizeHex(hexes[i].value, DEFAULT_COLORS[key] || "");
      if (norm) colors[key] = norm;
      else delete colors[key];
    }
  }

  window.wgpH3HL = {
    setEnabled: setEnabled,
    setModel: setModel,
    isEnabled: function () {
      return enabled;
    },
    isH3: function () {
      return modelIsH3;
    },
    update: attachAll,
    openColors: openColorModal
  };

  function boot() {
    attachAll();
    var root = pluginRoot();
    if (!root || root._h3hlObserver === "1") return;
    root._h3hlObserver = "1";
    if (window.MutationObserver) {
      var observer = new MutationObserver(function () {
        detachGone();
        readModelFromDom();
        wireControls();
      });
      observer.observe(root, { childList: true, subtree: true });
    }
  }

  var tries = 0;
  function tryBoot() {
    attachAll();
    tries += 1;
    if (tries < 120) setTimeout(tryBoot, 250);
  }

  setInterval(function () {
    readModelFromDom();
  }, 500);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      boot();
      tryBoot();
    });
  } else {
    boot();
    tryBoot();
  }
})();
"""

CONTROLS_HTML = """
<div class="h3hl-bar">
  <label class="h3hl-check">
    <input type="checkbox" id="h3hl-enable" checked />
    <span class="h3hl-box"></span>
    <span>Highlight MiniMax H3 prompt syntax</span>
  </label>
  <button type="button" id="h3hl-colors-btn">Customize colors</button>
</div>
"""


class MiniMaxH3PromptHighlighterPlugin(WAN2GPPlugin):
    def setup_ui(self) -> None:
        self.request_component("prompt")
        self.request_component("wizard_prompt")
        self.insert_after("prompt", self._create_toggle_ui)
        self.add_custom_js(JS_CODE)

    def _create_toggle_ui(self):
        return gr.HTML(
            value=CONTROLS_HTML,
            elem_id="h3hl-controls-row",
            elem_classes=["wangp-h3hl-controls-row"],
            container=False,
            padding=False,
            visible=True,
        )
