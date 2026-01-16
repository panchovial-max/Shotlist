// ui.ts
document.querySelectorAll(".tab-button").forEach((button) => {
  button.addEventListener("click", () => {
    const tabName = button.getAttribute("data-tab");
    document.querySelectorAll(".tab-button").forEach((b) => b.classList.remove("active"));
    button.classList.add("active");
    document.querySelectorAll(".tab-content").forEach((content) => content.classList.remove("active"));
    document.getElementById(`${tabName}-tab`)?.classList.add("active");
  });
});
document.getElementById("exportButton")?.addEventListener("click", () => {
  const targetFile = document.getElementById("targetFile").value;
  const targetCss = document.getElementById("targetCss").value;
  const overwrite = document.getElementById("overwriteExport").checked;
  if (!targetFile.trim()) {
    showMessage("export-message", "Please enter a target file name", "error");
    return;
  }
  const payload = { targetFile, targetCss, overwrite };
  parent.postMessage({ pluginMessage: { type: "export-to-localhost", payload } }, "*");
  updateStatus("export-status", "Exporting... please wait");
});
document.getElementById("importButton")?.addEventListener("click", () => {
  const importPage = document.getElementById("importPage").value;
  const localhostUrl = document.getElementById("localhostUrl").value || "http://localhost:8000";
  if (!localhostUrl.trim()) {
    showMessage("import-message", "Please enter a localhost URL", "error");
    return;
  }
  const payload = { page: importPage, localhostUrl };
  parent.postMessage({ pluginMessage: { type: "import-from-localhost", payload } }, "*");
  updateStatus("import-status", "Importing... please wait");
});
document.getElementById("saveSettingsButton")?.addEventListener("click", () => {
  const settingsUrl = document.getElementById("settingsUrl").value || "http://localhost:8000";
  const settings = {
    localhostUrl: settingsUrl,
    apiUrl: settingsUrl,
    autoSync: document.getElementById("autoSync").checked,
    watchMode: document.getElementById("watchMode").checked,
    syncColors: document.getElementById("syncColors").checked,
    syncTypography: document.getElementById("syncTypography").checked
  };
  parent.postMessage({ pluginMessage: { type: "save-config", payload: settings } }, "*");
  showMessage("settings-message", "Settings saved successfully", "success");
});
function showMessage(elementId, message, type) {
  const element = document.getElementById(elementId);
  if (element) {
    element.textContent = message;
    element.className = `message ${type}`;
    element.style.display = "block";
    if (type === "success" || type === "info") {
      setTimeout(() => {
        element.style.display = "none";
      }, 3000);
    }
  }
}
function updateStatus(elementId, message) {
  const element = document.getElementById(elementId);
  if (element) {
    element.textContent = message;
  }
}
window.onmessage = async (event) => {
  const pluginMessage = event.data.pluginMessage;
  if (pluginMessage && pluginMessage.type === "notify") {
    const { tab, message, type } = pluginMessage.payload;
    showMessage(`${tab}-message`, message, type);
    updateStatus(`${tab}-status`, "");
  } else if (pluginMessage && pluginMessage.type === "config") {
    const config = pluginMessage.payload;
    if (config.localhostUrl) {
      document.getElementById("localhostUrl").value = config.localhostUrl;
      document.getElementById("settingsUrl").value = config.localhostUrl;
    }
    if (config.autoSync) document.getElementById("autoSync").checked = true;
    if (config.watchMode) document.getElementById("watchMode").checked = true;
    if (config.syncColors) document.getElementById("syncColors").checked = true;
    if (config.syncTypography) document.getElementById("syncTypography").checked = true;
  }
};
window.addEventListener("load", () => {
  parent.postMessage({ pluginMessage: { type: "get-config" } }, "*");
});
