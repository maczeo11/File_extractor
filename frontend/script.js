// --- CONFIGURATION ---
const HARDCODED_API_URL = ""; 

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

let currentFile = null;

// Settings Toggle
toggleConfig.addEventListener('click', () => {
    configPanel.classList.toggle('collapsed');
});

// Drag & Drop Handlers
dropZone.addEventListener('click', (e) => {
    if (e.target !== dropZone && !e.target.classList.contains('browse-btn')) return;
    fileInput.click();
});

// Prevent defaults for all drag events to ensure drop works
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.add('drag-over'), false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.remove('drag-over'), false);
});

dropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length) handleFile(files[0]);
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) handleFile(e.target.files[0]);
});

function handleFile(file) {
    currentFile = file;
    fileName.textContent = file.name;
    dropZone.style.display = 'none';
    fileInfo.style.display = 'flex';
    extractBtn.style.display = 'block';
    resultsArea.style.display = 'none';
}

window.clearFile = function() {
    currentFile = null;
    fileInput.value = '';
    dropZone.style.display = 'block';
    fileInfo.style.display = 'none';
    extractBtn.style.display = 'none';
    resultsArea.style.display = 'none';
}

extractBtn.addEventListener('click', async () => {
    if (!currentFile) return;

    let rawUrl = apiUrlInput.value.trim() || HARDCODED_API_URL || "http://localhost:8000";
    let baseUrl = rawUrl.replace(/\/$/, "");
    const endpoint = `${baseUrl}/api/extract`;

    setLoading(true);
    resultsArea.style.display = 'none';
    resultsList.innerHTML = '';

    const formData = new FormData();
    formData.append('file', currentFile);

    try {
        const response = await fetch(endpoint, { method: 'POST', body: formData });
        
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || 'Extraction failed');
        }

        const data = await response.json();
        renderResults(data);

    } catch (error) {
        alert(`Error: ${error.message}\n\nServer: ${baseUrl}`);
        console.error(error);
    } finally {
        setLoading(false);
    }
});

function setLoading(isLoading) {
    extractBtn.disabled = isLoading;
    if (isLoading) {
        btnSpinner.style.display = 'block';
        btnContent.style.opacity = '0';
    } else {
        btnSpinner.style.display = 'none';
        btnContent.style.opacity = '1';
    }
}

function renderResults(data) {
    document.getElementById('resType').textContent = (data.file_type || 'UNKNOWN').toUpperCase();
    document.getElementById('resTime').textContent = `${data.processing_time_ms}ms`;

    const grouped = {};
    const sortedContent = data.content.sort((a, b) => (a.location?.number || 0) - (b.location?.number || 0));

    sortedContent.forEach(unit => {
        let key = "Extracted Text";
        if (unit.location.type === 'page') key = `Page ${unit.location.number}`;
        else if (unit.location.type === 'row' && unit.location.sheet) key = `Sheet: ${unit.location.sheet}`;
        
        if (!grouped[key]) grouped[key] = [];
        grouped[key].push(unit.text);
    });

    const keys = Object.keys(grouped);
    if (keys.length === 0) {
        resultsList.innerHTML = `<div style="text-align:center; color: #64748b;">No text found in this file.</div>`;
    } else {
        keys.forEach(groupName => {
            const textContent = grouped[groupName].join('\n\n');
            createPageCard(groupName, textContent);
        });
    }
    resultsArea.style.display = 'block';
}

function createPageCard(title, text) {
    const card = document.createElement('div');
    card.className = 'page-card';
    card.innerHTML = `
        <div class="page-header">
            <span class="page-title"><i class="fa-regular fa-file-lines"></i> &nbsp; ${title}</span>
            <span class="page-badge">${text.length} chars</span>
        </div>
        <div class="page-content">${text}</div>
    `;
    resultsList.appendChild(card);
}