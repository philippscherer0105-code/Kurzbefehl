const $ = (id) => document.getElementById(id);
const api = `/api/mitschriebe/${window.NOTE_ID}`;
const notesEl = $("notes");
let lastStatus = null;
let lastMarkdown = null;

const HINTS = {
  wartet: "Wartet auf Verarbeitung …",
  transkribiert: "Spracherkennung läuft lokal – bei langen Vorlesungen kann das eine Weile dauern.",
  schreibt: "Claude schreibt den Mitschrieb – du kannst live mitlesen. Diagramme erscheinen am Ende.",
};

async function poll() {
  let meta;
  try {
    const res = await fetch(api);
    if (res.status === 404) {
      notesEl.innerHTML = '<p class="error">Mitschrieb nicht gefunden.</p>';
      return;
    }
    meta = await res.json();
  } catch (e) {
    return setTimeout(poll, 3000);
  }

  document.title = `${meta.title} – Mitschrieb`;
  const busy = ["wartet", "transkribiert", "schreibt"].includes(meta.status);

  $("progress-card").hidden = !busy;
  if (busy) {
    $("progress-label").textContent =
      meta.status === "transkribiert" ? `Transkription: ${Math.round(meta.progress * 100)} %`
      : meta.status === "schreibt" ? "Mitschrieb wird geschrieben …" : "In Warteschlange …";
    const bar = $("progress");
    if (meta.status === "transkribiert") bar.value = meta.progress;
    else bar.removeAttribute("value");
    $("progress-hint").textContent = HINTS[meta.status];
  }

  $("error-card").hidden = meta.status !== "fehler";
  if (meta.status === "fehler") $("error-card").textContent = `Fehler: ${meta.error}`;

  $("toolbar").hidden = meta.status !== "fertig";
  $("transcript-link").hidden = !meta.has_transcript;
  $("regenerate-box").hidden = busy || !meta.has_transcript;

  const audio = $("audio");
  if (meta.audio_file && audio.hidden) {
    audio.src = `${api}/dateien/${encodeURIComponent(meta.audio_file)}`;
    audio.hidden = false;
  }

  if (meta.markdown !== lastMarkdown || meta.status !== lastStatus) {
    if (meta.markdown) {
      const done = meta.status === "fertig";
      await MitschriebRender.renderNotes(notesEl, meta.markdown, { diagrams: done });
      notesEl.classList.toggle("cursor", meta.status === "schreibt");
      MitschriebRender.buildToc(notesEl, $("toc"));
    } else if (busy) {
      notesEl.innerHTML = '<p class="muted">Der Mitschrieb erscheint hier, sobald er geschrieben wird.</p>';
    } else if (meta.status === "fehler") {
      notesEl.innerHTML = "";
    }
    lastMarkdown = meta.markdown;
  }
  lastStatus = meta.status;

  if (busy) setTimeout(poll, 1500);
}

$("delete").onclick = async () => {
  if (!confirm("Mitschrieb, Aufnahme und Transkript endgültig löschen?")) return;
  const res = await fetch(api, { method: "DELETE" });
  if (res.ok) location.href = "/";
  else alert((await res.json()).error);
};

$("regenerate").onclick = async () => {
  const res = await fetch(`${api}/neu`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ extra: $("regenerate-extra").value }),
  });
  if (!res.ok) return alert((await res.json()).error);
  $("regenerate-box").open = false;
  lastMarkdown = null;
  poll();
};

poll();
