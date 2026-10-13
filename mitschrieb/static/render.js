// Rendert einen Markdown-Mitschrieb mit Tabellen, Mermaid-Diagrammen und KaTeX-Formeln.
// Benötigt global: marked, DOMPurify, katex, mermaid.

(function () {
  let mermaidReady = false;
  let diagramCounter = 0;

  function initMermaid() {
    if (mermaidReady || !window.mermaid) return;
    const dark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    mermaid.initialize({ startOnLoad: false, theme: dark ? "dark" : "default", securityLevel: "strict" });
    mermaidReady = true;
  }

  // Formeln vor dem Markdown-Parser schützen, damit z. B. "_" nicht als Kursiv gilt.
  function extractMath(markdown) {
    const math = [];
    const parts = markdown.split(/(```[\s\S]*?(?:```|$)|`[^`\n]*`)/g);
    const out = parts.map((part, i) => {
      if (i % 2 === 1) return part; // Code bleibt unverändert
      return part
        .replace(/\$\$([\s\S]+?)\$\$/g, (_, tex) => {
          math.push({ tex, display: true });
          return `\n\nMATHPLACEHOLDER${math.length - 1}X\n\n`;
        })
        .replace(/(^|[^\\$])\$([^\s$](?:[^$\n]*?[^\s$])?)\$(?!\d)/g, (_, pre, tex) => {
          math.push({ tex, display: false });
          return `${pre}MATHPLACEHOLDER${math.length - 1}X`;
        });
    });
    return { text: out.join(""), math };
  }

  function insertMath(html, math) {
    return html.replace(/MATHPLACEHOLDER(\d+)X/g, (_, idx) => {
      const { tex, display } = math[Number(idx)];
      try {
        return katex.renderToString(tex, { displayMode: display, throwOnError: false });
      } catch (e) {
        return `<code>${tex.replace(/</g, "&lt;")}</code>`;
      }
    });
  }

  function slugify(text) {
    return text.toLowerCase().trim()
      .replace(/[^\p{L}\p{N}]+/gu, "-")
      .replace(/^-|-$/g, "") || "abschnitt";
  }

  async function renderDiagrams(container) {
    initMermaid();
    const blocks = container.querySelectorAll("pre > code.language-mermaid");
    for (const code of blocks) {
      const source = code.textContent;
      const wrapper = document.createElement("div");
      wrapper.className = "diagram";
      code.parentElement.replaceWith(wrapper);
      try {
        const { svg } = await mermaid.render(`diagramm-${++diagramCounter}`, source);
        wrapper.innerHTML = svg;
      } catch (e) {
        wrapper.innerHTML = "";
        const note = document.createElement("div");
        note.className = "diagram-error";
        note.textContent = "Diagramm konnte nicht dargestellt werden:";
        const pre = document.createElement("pre");
        pre.textContent = source;
        wrapper.append(note, pre);
        document.querySelectorAll(`#ddiagramm-${diagramCounter}`).forEach((n) => n.remove());
      }
    }
  }

  // options.diagrams=false zeigt Mermaid-Code als Text (z. B. während des Streamens).
  async function renderNotes(container, markdown, options = {}) {
    const { text, math } = extractMath(markdown || "");
    let html = marked.parse(text, { gfm: true, breaks: false });
    html = DOMPurify.sanitize(html);
    html = insertMath(html, math);
    container.innerHTML = html;

    const used = new Set();
    container.querySelectorAll("h1, h2, h3").forEach((h) => {
      let id = slugify(h.textContent);
      while (used.has(id)) id += "-1";
      used.add(id);
      h.id = id;
    });

    if (options.diagrams !== false) await renderDiagrams(container);
  }

  function buildToc(container, tocElement) {
    tocElement.innerHTML = "";
    container.querySelectorAll("h2").forEach((h) => {
      const a = document.createElement("a");
      a.href = `#${h.id}`;
      a.textContent = h.textContent;
      tocElement.appendChild(a);
    });
  }

  window.MitschriebRender = { renderNotes, buildToc };
})();
