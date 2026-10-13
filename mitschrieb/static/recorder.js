// Mikrofonaufnahme mit Pause, Pegelanzeige, Bildschirm-Wachhalten und
// laufender Sicherung in IndexedDB (übersteht Tab-Abstürze und Neuladen).

const RecorderStore = {
  db: null,
  async open() {
    if (this.db) return this.db;
    this.db = await new Promise((resolve, reject) => {
      const req = indexedDB.open("mitschrieb-aufnahme", 1);
      req.onupgradeneeded = () => req.result.createObjectStore("chunks", { autoIncrement: true });
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
    return this.db;
  },
  async tx(mode, fn) {
    const db = await this.open();
    return new Promise((resolve, reject) => {
      const t = db.transaction("chunks", mode);
      const result = fn(t.objectStore("chunks"));
      t.oncomplete = () => resolve(result && "result" in result ? result.result : undefined);
      t.onerror = () => reject(t.error);
    });
  },
  add(chunk) { return this.tx("readwrite", (s) => s.add(chunk)); },
  all() { return this.tx("readonly", (s) => s.getAll()); },
  clear() { return this.tx("readwrite", (s) => s.clear()); },
};

class LectureRecorder {
  constructor({ onTick, onLevel }) {
    this.onTick = onTick;
    this.onLevel = onLevel;
    this.mediaRecorder = null;
    this.chunks = [];
    this.elapsedBefore = 0;
    this.startedAt = null;
    this.timer = null;
    this.wakeLock = null;
  }

  static pickMime() {
    const candidates = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4", "audio/ogg;codecs=opus"];
    return candidates.find((m) => window.MediaRecorder && MediaRecorder.isTypeSupported(m)) || "";
  }

  get elapsed() {
    return this.elapsedBefore + (this.startedAt ? (Date.now() - this.startedAt) / 1000 : 0);
  }

  get state() {
    return this.mediaRecorder ? this.mediaRecorder.state : "inactive";
  }

  async start() {
    await RecorderStore.clear();
    this.stream = await navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: false, noiseSuppression: true, autoGainControl: true },
    });
    this.mime = LectureRecorder.pickMime();
    this.mediaRecorder = new MediaRecorder(this.stream, {
      mimeType: this.mime || undefined,
      audioBitsPerSecond: 48000,
    });
    this.mime = this.mediaRecorder.mimeType || this.mime || "audio/webm";
    this.chunks = [];
    this.elapsedBefore = 0;

    this.mediaRecorder.ondataavailable = (e) => {
      if (!e.data || !e.data.size) return;
      const chunk = { blob: e.data, mime: this.mime, elapsed: this.elapsed };
      this.chunks.push(chunk);
      RecorderStore.add(chunk).catch((err) => console.warn("Sicherung fehlgeschlagen", err));
    };
    this.mediaRecorder.start(10000); // alle 10 s ein Stück sichern
    this.startedAt = Date.now();
    this.timer = setInterval(() => this.onTick(this.elapsed), 500);
    this.startLevelMeter();
    this.keepAwake();
  }

  pause() {
    if (this.state !== "recording") return;
    this.mediaRecorder.pause();
    this.elapsedBefore = this.elapsed;
    this.startedAt = null;
  }

  resume() {
    if (this.state !== "paused") return;
    this.mediaRecorder.resume();
    this.startedAt = Date.now();
  }

  stop() {
    return new Promise((resolve) => {
      if (!this.mediaRecorder || this.state === "inactive") return resolve(null);
      this.mediaRecorder.onstop = () => {
        this.elapsedBefore = this.elapsed;
        this.startedAt = null;
        clearInterval(this.timer);
        this.stream.getTracks().forEach((t) => t.stop());
        if (this.audioCtx) this.audioCtx.close();
        if (this.wakeLock) this.wakeLock.release().catch(() => {});
        this.wakeLock = null;
        resolve(LectureRecorder.toBlob(this.chunks));
      };
      this.mediaRecorder.stop();
    });
  }

  static toBlob(chunks) {
    const mime = chunks.length ? chunks[0].mime : "audio/webm";
    return new Blob(chunks.map((c) => c.blob), { type: mime.split(";")[0] });
  }

  startLevelMeter() {
    try {
      this.audioCtx = new AudioContext();
      const source = this.audioCtx.createMediaStreamSource(this.stream);
      const analyser = this.audioCtx.createAnalyser();
      analyser.fftSize = 512;
      source.connect(analyser);
      const data = new Uint8Array(analyser.fftSize);
      const loop = () => {
        if (this.state === "inactive") return this.onLevel(0);
        analyser.getByteTimeDomainData(data);
        let peak = 0;
        for (const v of data) peak = Math.max(peak, Math.abs(v - 128));
        this.onLevel(this.state === "paused" ? 0 : Math.min(1, peak / 64));
        requestAnimationFrame(loop);
      };
      loop();
    } catch (e) {
      console.warn("Pegelanzeige nicht verfügbar", e);
    }
  }

  async keepAwake() {
    if (!("wakeLock" in navigator)) return;
    const acquire = async () => {
      try {
        this.wakeLock = await navigator.wakeLock.request("screen");
      } catch (e) { /* z. B. Energiesparmodus */ }
    };
    await acquire();
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible" && this.state !== "inactive") acquire();
    });
  }
}

function formatDuration(seconds) {
  seconds = Math.floor(seconds);
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}
