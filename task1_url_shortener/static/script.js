const form = document.getElementById("shorten-form");
const urlInput = document.getElementById("url");
const customInput = document.getElementById("custom");
const errorBox = document.getElementById("error");
const resultBox = document.getElementById("result");
const shortLink = document.getElementById("short-link");
const copyBtn = document.getElementById("copy-btn");
const linksList = document.getElementById("links");
const emptyMsg = document.getElementById("empty");

function showError(msg) {
  errorBox.textContent = msg;
  errorBox.hidden = !msg;
}

async function loadLinks() {
  const res = await fetch("/api/links");
  const links = await res.json();
  linksList.innerHTML = "";
  emptyMsg.hidden = links.length > 0;
  links.forEach((l) => {
    const li = document.createElement("li");

    const a = document.createElement("a");
    a.href = l.short_url;
    a.target = "_blank";
    a.rel = "noopener";
    a.textContent = l.short_url;

    const orig = document.createElement("span");
    orig.className = "orig";
    orig.textContent = l.original_url;

    const clicks = document.createElement("span");
    clicks.className = "clicks";
    clicks.textContent = l.clicks + (l.clicks === 1 ? " click" : " clicks");

    li.append(a, orig, clicks);
    linksList.appendChild(li);
  });
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  showError("");
  try {
    const res = await fetch("/api/shorten", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: urlInput.value, custom_code: customInput.value }),
    });
    const data = await res.json();
    if (!res.ok) {
      resultBox.hidden = true;
      showError(data.error || "Something went wrong. Try again.");
      return;
    }
    shortLink.textContent = data.short_url;
    shortLink.href = data.short_url;
    resultBox.hidden = false;
    copyBtn.textContent = "Copy";
    loadLinks();
  } catch (err) {
    showError("Could not reach the server. Is it running?");
  }
});

copyBtn.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(shortLink.textContent);
    copyBtn.textContent = "Copied";
  } catch (err) {
    copyBtn.textContent = "Copy failed";
  }
});

loadLinks();
