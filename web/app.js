const COLOR_FIELDS = [
  ["mainBackground", "메인 배경"],
  ["chatBackground", "채팅방 배경"],
  ["tabBarBackground", "탭바 배경"],
  ["headerText", "상단 타이틀"],
  ["tabText", "탭 기본 텍스트"],
  ["tabHighlightedText", "탭 선택 텍스트"],
  ["mainText", "목록 이름"],
  ["descriptionText", "상태메시지"],
  ["paragraphText", "마지막 메시지"],
  ["sectionText", "섹션 타이틀"],
  ["inputBarBackground", "입력창 배경"],
  ["sendButtonBackground", "보내기 버튼"],
  ["sendButtonText", "보내기 텍스트"],
  ["messageSendText", "내 말풍선 텍스트"],
  ["messageReceiveText", "상대 말풍선 텍스트"],
  ["bubbleSendBackground", "내 말풍선"],
  ["bubbleReceiveBackground", "상대 말풍선"],
  ["unreadText", "안 읽음 숫자"],
  ["passcodeBackground", "암호화면 배경"],
  ["passcodeTitle", "암호화면 타이틀"],
  ["profileBackground", "기본 프로필"],
  ["iconNormal", "아이콘 기본"],
  ["iconSelected", "아이콘 선택"],
  ["notificationBackground", "알림바 배경"],
];

const ASSET_SLOTS = [
  {
    inputId: "mainBgInput",
    bases: ["mainBgImage"],
    sizes: { 2: [750, 1500], 3: [1125, 2250] },
    fit: "cover",
  },
  {
    inputId: "chatBgInput",
    bases: ["chatroomBgImage"],
    sizes: { 2: [750, 1500], 3: [1125, 2250] },
    fit: "cover",
  },
  {
    inputId: "passcodeBgInput",
    bases: ["passcodeBgImage"],
    sizes: { 2: [750, 1500], 3: [1125, 2250] },
    fit: "cover",
  },
  {
    inputId: "tabBgInput",
    bases: ["maintabBgImage"],
    sizes: { 2: [940, 98], 3: [1410, 147] },
    fit: "cover",
  },
];

let theme = null;

const $ = (id) => document.getElementById(id);
const status = (message) => { $("status").textContent = message; };

async function init() {
  const response = await fetch("/api/default-theme");
  theme = await response.json();
  bindMeta();
  renderColorFields();
  updateFormFromTheme();
  updatePreview();
  $("downloadIosBtn").addEventListener("click", () => exportBinary("/api/export/ios", "ktheme"));
  $("downloadAndroidBtn").addEventListener("click", () => exportBinary("/api/export/android-res", "zip"));
  $("exportJsonBtn").addEventListener("click", exportJson);
  $("importJsonInput").addEventListener("change", importJson);
}

function bindMeta() {
  const bindings = [
    ["nameInput", "name"],
    ["authorInput", "authorName"],
    ["iosIdInput", "iosThemeId"],
    ["androidIdInput", "androidPackageId"],
  ];
  for (const [inputId, key] of bindings) {
    $(inputId).addEventListener("input", () => {
      theme.meta[key] = $(inputId).value;
      updatePreview();
    });
  }
}

function renderColorFields() {
  const container = $("colorFields");
  container.innerHTML = "";
  for (const [key, label] of COLOR_FIELDS) {
    const row = document.createElement("label");
    row.className = "color-field";
    row.innerHTML = `
      <input type="color" id="color-${key}" />
      <span>${label}<code id="value-${key}"></code></span>
    `;
    container.append(row);
    row.querySelector("input").addEventListener("input", (event) => {
      theme.colors[key] = event.target.value.toUpperCase();
      $("value-" + key).textContent = theme.colors[key];
      syncDerivedColors(key);
      updatePreview();
    });
  }
}

function syncDerivedColors(key) {
  if (key === "bubbleSendBackground") {
    theme.colors.sendButtonBackground = theme.colors.bubbleSendBackground;
    theme.colors.unreadText = theme.colors.bubbleSendBackground;
    theme.colors.bubbleSendSelectedBackground = darken(theme.colors.bubbleSendBackground, 0.08);
    setColorInput("sendButtonBackground");
    setColorInput("unreadText");
  }
  if (key === "mainBackground") {
    theme.colors.passcodeBackground = theme.colors.mainBackground;
    setColorInput("passcodeBackground");
  }
}

function darken(hex, amount) {
  const n = parseInt(hex.slice(1), 16);
  const r = Math.max(0, Math.round(((n >> 16) & 255) * (1 - amount)));
  const g = Math.max(0, Math.round(((n >> 8) & 255) * (1 - amount)));
  const b = Math.max(0, Math.round((n & 255) * (1 - amount)));
  return "#" + [r, g, b].map((v) => v.toString(16).padStart(2, "0")).join("").toUpperCase();
}

function updateFormFromTheme() {
  $("nameInput").value = theme.meta.name;
  $("authorInput").value = theme.meta.authorName;
  $("iosIdInput").value = theme.meta.iosThemeId;
  $("androidIdInput").value = theme.meta.androidPackageId;
  for (const [key] of COLOR_FIELDS) setColorInput(key);
}

function setColorInput(key) {
  const input = $("color-" + key);
  const code = $("value-" + key);
  if (input) input.value = theme.colors[key]?.slice(0, 7) || "#000000";
  if (code) code.textContent = theme.colors[key] || "";
}

function updatePreview() {
  const root = $("phonePreview");
  root.style.setProperty("--preview-main-bg", theme.colors.mainBackground);
  root.style.setProperty("--preview-chat-bg", theme.colors.chatBackground);
  root.style.setProperty("--preview-header", theme.colors.headerText);
  root.style.setProperty("--preview-tab", theme.colors.tabText);
  root.style.setProperty("--preview-title", theme.colors.mainText);
  root.style.setProperty("--preview-desc", theme.colors.descriptionText);
  root.style.setProperty("--preview-section", theme.colors.sectionText);
  root.style.setProperty("--preview-input-bg", theme.colors.inputBarBackground);
  root.style.setProperty("--preview-send-button", theme.colors.sendButtonBackground);
  root.style.setProperty("--preview-send-button-text", theme.colors.sendButtonText);
  root.style.setProperty("--preview-input-icon", theme.colors.inputIcon);
  root.style.setProperty("--preview-send-bubble", theme.colors.bubbleSendBackground);
  root.style.setProperty("--preview-send-text", theme.colors.messageSendText);
  root.style.setProperty("--preview-receive-bubble", theme.colors.bubbleReceiveBackground);
  root.style.setProperty("--preview-receive-text", theme.colors.messageReceiveText);
  root.style.setProperty("--preview-profile", theme.colors.profileBackground);
}

function collectTheme() {
  const cloned = structuredClone(theme);
  cloned.meta.name = $("nameInput").value.trim() || "MAKEETHEME Theme";
  cloned.meta.authorName = $("authorInput").value.trim() || "MAKEETHEME";
  cloned.meta.iosThemeId = $("iosIdInput").value.trim() || "com.example.talk.theme.makeetheme.ios";
  cloned.meta.androidPackageId = $("androidIdInput").value.trim() || "com.example.talk.theme.makeetheme";
  return cloned;
}

async function exportBinary(endpoint, fallbackExt) {
  status("이미지 처리 중...");
  try {
    const payload = { theme: collectTheme(), assetData: await prepareAssetData() };
    status("테마 파일 생성 중...");
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: "Export failed" }));
      throw new Error(error.error || "Export failed");
    }
    const blob = await response.blob();
    const disposition = response.headers.get("Content-Disposition") || "";
    const filename = disposition.match(/filename="?([^";]+)"?/)?.[1] || `user-theme.${fallbackExt}`;
    downloadBlob(blob, filename);
    status("다운로드 준비 완료");
  } catch (error) {
    status(error.message);
  }
}

async function prepareAssetData() {
  const assetData = {};
  for (const slot of ASSET_SLOTS) {
    const file = $(slot.inputId).files?.[0];
    if (!file) continue;
    const image = await loadImage(file);
    for (const base of slot.bases) {
      for (const [scale, size] of Object.entries(slot.sizes)) {
        const [width, height] = size;
        assetData[`${base}@${scale}x.png`] = renderImageToPngDataUrl(image, width, height, slot.fit);
      }
    }
  }
  return assetData;
}

function loadImage(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(url);
      resolve(img);
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error("이미지를 읽을 수 없습니다."));
    };
    img.src = url;
  });
}

function renderImageToPngDataUrl(img, width, height, fit = "cover") {
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, width, height);
  const scale = fit === "contain" ? Math.min(width / img.width, height / img.height) : Math.max(width / img.width, height / img.height);
  const drawW = img.width * scale;
  const drawH = img.height * scale;
  const dx = (width - drawW) / 2;
  const dy = (height - drawH) / 2;
  ctx.drawImage(img, dx, dy, drawW, drawH);
  return canvas.toDataURL("image/png");
}

function exportJson() {
  const blob = new Blob([JSON.stringify(collectTheme(), null, 2)], { type: "application/json" });
  downloadBlob(blob, "theme.json");
}

async function importJson(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  try {
    const imported = JSON.parse(await file.text());
    theme = mergeThemeClient(theme, imported);
    updateFormFromTheme();
    updatePreview();
    status("theme.json을 불러왔습니다.");
  } catch (error) {
    status("theme.json 형식이 올바르지 않습니다.");
  } finally {
    event.target.value = "";
  }
}

function mergeThemeClient(base, override) {
  const out = structuredClone(base);
  if (override.meta) Object.assign(out.meta, override.meta);
  if (override.colors) Object.assign(out.colors, override.colors);
  if (override.options) Object.assign(out.options, override.options);
  return out;
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 3000);
}

init().catch((error) => status(error.message));
