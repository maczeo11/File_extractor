const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const extractBtn = document.getElementById('extractBtn');
const resultsArea = document.getElementById('resultsArea');
const resultsList = document.getElementById('resultsList');
const btnSpinner = document.getElementById('btnSpinner');
const btnContent = document.querySelector('.btn-content');
const apiUrlInput = document.getElementById('apiUrl');
const toggleConfig = document.getElementById('toggleConfig');
const configPanel = document.getElementById('configPanel');

let currentFiles = [];

toggleConfig.addEventListener('click', () => {
    configPanel.classList.toggle('collapsed');
});

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(e => {
    dropZone.addEventListener(e, ev => ev.preventDefault());
    document.body.addEventListener(e, ev => ev.preventDefault());
});

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('drop', e => {
    handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', e => {
    handleFiles(e.target.files);
});

function handleFiles(files) {
    if (files.length > 5) {
        alert("Maximum 5 files allowed!");
        return;
    }

    currentFiles = Array.from(files);

    fileName.textContent = currentFiles.map(f => f.name).join(", ");
    dropZone.style.display = 'none';
    fileInfo.style.display = 'flex';
    extractBtn.style.display = 'block';
    resultsArea.style.display = 'none';
}

window.clearFiles = function () {
    currentFiles = [];
    fileInput.value = "";
    dropZone.style.display = 'block';
    fileInfo.style.display = 'none';
    extractBtn.style.display = 'none';
    resultsArea.style.display = 'none';
};

extractBtn.addEventListener('click', async () => {
    if (currentFiles.length === 0) return;

    const baseUrl = (apiUrlInput.value || "http://localhost:8000").replace(/\/$/, "");
    const endpoint = `${baseUrl}/api/extract`;

    const formData = new FormData();
    currentFiles.forEach(file => {
        formData.append("files", file);
    });

    setLoading(true);
    resultsList.innerHTML = "";

    try {
        const res = await fetch(endpoint, {
            method: "POST",
            body: formData
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Extraction failed");
        }

        const data = await res.json();
        renderResults(data.results);

    } catch (err) {
        alert(err.message);
    } finally {
        setLoading(false);
    }
});

function setLoading(state) {
    extractBtn.disabled = state;
    btnSpinner.style.display = state ? 'block' : 'none';
    btnContent.style.opacity = state ? 0 : 1;
}

function renderResults(results) {
    results.forEach(file => {
        const text = file.content.map(c => c.text).join("\n\n");
        createCard(file.filename, text);
    });
    resultsArea.style.display = 'block';
}

function createCard(title, text) {
    const card = document.createElement("div");
    card.className = "page-card";
    card.innerHTML = `
        <div class="page-header">
            <span class="page-title">${title}</span>
            <span class="page-badge">${text.length} chars</span>
        </div>
        <div class="page-content">${text}</div>
    `;
    resultsList.appendChild(card);
}
