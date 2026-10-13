const $ = (id) => document.getElementById(id);

let recordedBlob = null;
const recorder = new LectureRecorder({
  onTick: (s) => ($("rec-time").textContent = formatDuration(s)),
  onLevel: (v) => ($("rec-level").style.width = `${Math.round(v * 100)}%`),
});

$("date").valueAsDate = new Date();

function setRecordingUi(state) {
  $("rec-start").hidden = state !== "idle";
  $("rec-pause").hidden = state === "idle";
  $("rec-stop").hidden = state === "idle";
  $("rec-dot").hidden = state !== "recording";
  $("rec-pause").textContent = state === "paused" ? "▶ Fortsetzen" : "❚❚ Pause";
  $("submit").disabled = state !== "idle";
}

function useRecording(blob) {
  recordedBlob = blob;
  const preview = $("rec-preview");
  preview.src = URL.createObjectURL(blob);
  preview.hidden = false;
  $("rec-start").textContent = "● Neue Aufnahme";
  $("status").textContent = `Aufnahme bereit (${(blob.size / 1024 / 1024).toFixed(1)} MB).`;
}

$("rec-start").onclick = async () => {
  if (recordedBlob && !confirm("Die vorhandene Aufnahme wird verworfen. Fortfahren?")) return;
  try {
    await recorder.start();
  } catch (e) {
    alert(`Mikrofon konnte nicht gestartet werden: ${e.message}`);
    return;
  }
  recordedBlob = null;
  $("rec-preview").hidden = true;
  $("recovery").hidden = true;
  setRecordingUi("recording");
};

$("rec-pause").onclick = () => {
  if (recorder.state === "recording") {
    recorder.pause();
    setRecordingUi("paused");
  } else {
    recorder.resume();
    setRecordingUi("recording");
  }
};

$("rec-stop").onclick = async () => {
  const blob = await recorder.stop();
  setRecordingUi("idle");
  if (blob && blob.size) useRecording(blob);
};

window.addEventListener("beforeunload", (e) => {
  if (recorder.state !== "inactive") {
    e.preventDefault();
    e.returnValue = "";
  }
});

// Unterbrochene Aufnahme aus IndexedDB anbieten
(async () => {
  try {
    const chunks = await RecorderStore.all();
    if (!chunks.length) return;
    $("recovery-length").textContent = `ca. ${formatDuration(chunks[chunks.length - 1].elapsed)}`;
    $("recovery").hidden = false;
    $("recovery-use").onclick = () => {
      useRecording(LectureRecorder.toBlob(chunks));
      $("recovery").hidden = true;
    };
    $("recovery-discard").onclick = async () => {
      await RecorderStore.clear();
      $("recovery").hidden = true;
    };
  } catch (e) {
    console.warn(e);
  }
})();

function extensionFor(mime) {
  if (mime.includes("mp4")) return "m4a";
  if (mime.includes("ogg")) return "ogg";
  return "webm";
}

$("form").onsubmit = async (e) => {
  e.preventDefault();
  const data = new FormData();
  const audioFile = $("audio-file").files[0];
  const transcriptFile = $("transcript-file").files[0];
  if (recordedBlob) {
    data.append("audio", recordedBlob, `aufnahme.${extensionFor(recordedBlob.type)}`);
  } else if (audioFile) {
    data.append("audio", audioFile);
  } else if (transcriptFile) {
    data.append("transcript", transcriptFile);
  } else {
    $("status").textContent = "Bitte zuerst aufnehmen oder eine Datei auswählen.";
    return;
  }
  if ($("slides").files[0]) data.append("slides", $("slides").files[0]);
  const date = $("date").value ? $("date").valueAsDate.toLocaleDateString("de-DE") : "";
  data.append("title", $("title").value);
  data.append("course", $("course").value);
  data.append("date", date);
  data.append("language", $("language").value);
  data.append("extra", $("extra").value);

  $("submit").disabled = true;
  $("status").textContent = "Wird hochgeladen …";
  try {
    const res = await fetch("/api/mitschriebe", { method: "POST", body: data });
    const body = await res.json();
    if (!res.ok) throw new Error(body.error || res.statusText);
    if (recordedBlob) await RecorderStore.clear();
    location.href = `/mitschrieb/${body.id}`;
  } catch (err) {
    $("status").innerHTML = "";
    const span = document.createElement("span");
    span.className = "error";
    span.textContent = `Fehler: ${err.message}`;
    $("status").appendChild(span);
    $("submit").disabled = false;
  }
};

const STATUS_LABELS = {
  wartet: "in Warteschlange",
  transkribiert: "transkribiert …",
  schreibt: "schreibt …",
  fertig: "fertig",
  fehler: "Fehler",
};

async function loadList() {
  const res = await fetch("/api/mitschriebe");
  const notes = await res.json();
  const list = $("notes-list");
  if (!notes.length) return;
  list.innerHTML = "";
  for (const n of notes) {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = `/mitschrieb/${n.id}`;
    a.textContent = n.title;
    const left = document.createElement("div");
    const meta = document.createElement("div");
    meta.className = "muted";
    meta.textContent = [n.course, n.date].filter(Boolean).join(" · ");
    left.append(a, meta);
    const badge = document.createElement("span");
    badge.className = `badge ${n.status}`;
    badge.textContent = STATUS_LABELS[n.status] || n.status;
    li.append(left, badge);
    list.appendChild(li);
  }
}
loadList();

async function checkApiKey() {
  const res = await fetch("/api/einstellungen");
  const { has_api_key } = await res.json();
  $("key-card").hidden = has_api_key;
}

$("api-key-save").onclick = async () => {
  const res = await fetch("/api/einstellungen", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: $("api-key").value }),
  });
  if (res.ok) {
    $("api-key").value = "";
    checkApiKey();
  } else {
    $("api-key-status").textContent = (await res.json()).error;
  }
};
checkApiKey();
