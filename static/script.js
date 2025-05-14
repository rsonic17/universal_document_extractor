// static/script.js

document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("fileInput");
  const extractBtn = document.getElementById("extractBtn");
  const resetBtn = document.getElementById("resetBtn");
  const downloadBtn = document.getElementById("downloadBtn");
  const customPromptBtn = document.getElementById("customPromptBtn");

  const preview = document.getElementById("preview");
  const ocrText = document.getElementById("ocrText");
  const jsonOutput = document.getElementById("jsonOutput");
  const ocrTimer = document.getElementById("ocrTimer");
  const llmTimer = document.getElementById("llmTimer");

  extractBtn.onclick = async () => {
    const file = fileInput.files[0];
    if (!file) return alert("Please select a file.");

    const formData = new FormData();
    formData.append("file", file);

    preview.innerHTML = "";
    if (file.type.startsWith("image/")) {
      const img = document.createElement("img");
      img.src = URL.createObjectURL(file);
      img.style.maxWidth = "100%";
      img.onload = () => URL.revokeObjectURL(img.src);
      preview.appendChild(img);
    } else if (file.name.endsWith(".pdf")) {
      const embed = document.createElement("embed");
      embed.src = URL.createObjectURL(file);
      embed.type = "application/pdf";
      embed.width = "100%";
      embed.height = "500px";
      embed.onload = () => URL.revokeObjectURL(embed.src);
      preview.appendChild(embed);
    } else {
      preview.textContent = "Unsupported preview format.";
    }

    ocrText.textContent = "Extracting text...";
    jsonOutput.textContent = "Extracting fields...";

    const res = await fetch("/extract", { method: "POST", body: formData });
    const data = await res.json();

    if (data.error) {
      ocrText.textContent = "OCR Failed: " + data.error;
      jsonOutput.textContent = "LLM Error: " + (data.llm_output?.error || "Unknown");
    } else {
      ocrText.textContent = data.ocr_text || "(No OCR text)";
      jsonOutput.textContent = prettyPrintJSON(data.llm_output);
      ocrTimer.textContent = data.timing?.ocr_seconds || "--";
      llmTimer.textContent = data.timing?.llm_seconds || "--";
    }
  };

  customPromptBtn.onclick = async () => {
    const prompt = document.getElementById("customPrompt").value.trim();
    if (!prompt) return alert("Please enter a prompt.");

    jsonOutput.textContent = "Sending prompt to LLM...";
    const res = await fetch("/extract_prompt", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt })
    });
    const data = await res.json();

    if (data.error) {
      jsonOutput.textContent = "LLM Error: " + data.error;
    } else {
      jsonOutput.textContent = prettyPrintJSON(data.llm_output);
      llmTimer.textContent = data.llm_seconds || "--";
    }
  };

  resetBtn.onclick = async () => {
    ocrText.textContent = "";
    jsonOutput.textContent = "{}";
    ocrTimer.textContent = "--";
    llmTimer.textContent = "--";
    preview.innerHTML = "No file selected.";
    fileInput.value = "";

    await fetch("/reset", { method: "POST" });
  };

  downloadBtn.onclick = () => {
    const blob = new Blob([jsonOutput.textContent], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "extracted_data.json";
    link.click();
  };

  function prettyPrintJSON(raw) {
    try {
      if (typeof raw === "string") {
        raw = JSON.parse(raw);
      }
      return JSON.stringify(raw, null, 2);
    } catch (e) {
      return typeof raw === "string" ? raw : JSON.stringify(raw);
    }
  }
});
