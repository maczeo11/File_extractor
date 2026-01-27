// =====================================================
// CONFIGURATION
// =====================================================
const HARDCODED_API_URL = window.location.origin;

// =====================================================
// ELEMENT REFERENCES
// =====================================================
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

// 🔥 CHANGED: store MULTIPLE files
let currentFiles = [];

// =====================================================
// SETTINGS PANEL TOGGLE
// =====================================================
toggleConfig.addEventListener('click', () => {
    configPanel.classList.toggle('collapsed');
});

// =====================================================
// DRAG & DROP HANDLING
// =====================================================
dropZone.addEventListener('click', (e) => {
    if (e.target !== dropZone && !e.target.classList.contains('browse-btn')) return;
    fileInput.click();
});

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(event => {
    dropZone.addEventListener(event, preventDefaults, false);
    document.body.addEventListener(event, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(event => {
    dropZone.addEventListener(event, () => dropZone.classList.add('drag-over'), false);
});

['dragleave', 'drop'].forEach(event => {
    dropZone.addEventListener(event, () => dropZone.classList.remove('drag-over'), false);
});

// 🔥 CHANGED: handle ALL dropped files
dropZone.addEventListener('drop', (e) => {
    if (e.dataTransfer.files.length) handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) handleFiles(e.target.files);
});

// =====================================================
// FILE HANDLING (MULTIPLE)
// =====================================================
function handleFiles(files) {
    if (files.length > 5) {
        alert("Maximum 5 files allowed.");
        return;
    }

    currentFiles = Array.from(files);
    fileName.textContent = currentFiles.map(f => f.name).join(', ');

    dropZone.style.display = 'none';
    fileInfo.style.display = 'flex';
    extractBtn.style.display = 'block';
    resultsArea.style.display = 'none';
}

// same function name kept for HTML compatibility
window.clearFile = function () {
    currentFiles = [];
    fileInput.value = '';

    dropZone.style.display = 'block';
    fileInfo.style.display = 'none';
    extractBtn.style.display = 'none';
    resultsArea.style.display = 'none';
};

// =====================================================
// EXTRACTION REQUEST (MULTIPLE FILES)
// =====================================================
extractBtn.addEventListener('click', async () => {
    if (currentFiles.length === 0) return;

    const baseUrl =
        apiUrlInput.value.trim() ||
        HARDCODED_API_URL;

    const endpoint = `${baseUrl.replace(/\/$/, '')}/api/extract`;

    setLoading(true);
    resultsArea.style.display = 'none';
    resultsList.innerHTML = '';

    const formData = new FormData();

    // 🔥 CHANGED: append multiple files
    currentFiles.forEach(file => {
        formData.append('files', file);
    });

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || 'Extraction failed');
        }

        const data = await response.json();

        // 🔥 CHANGED: backend now returns results[]
        renderMultipleResults(data.results);

    } catch (error) {
        alert(`Error: ${error.message}\nServer: ${baseUrl}`);
        console.error(error);
    } finally {
        setLoading(false);
    }
});

// =====================================================
// UI HELPERS
// =====================================================
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

// =====================================================
// RENDER RESULTS (MULTIPLE FILES)
// =====================================================
function renderMultipleResults(results) {
    results.forEach(file => {
        const grouped = {};
        const content = (file.content || []).sort(
            (a, b) => (a.location?.number || 0) - (b.location?.number || 0)
        );

        content.forEach(unit => {
            let key = 'Extracted Text';

            if (unit.location?.type === 'page') {
                key = `Page ${unit.location.number}`;
            } else if (unit.location?.type === 'row' && unit.location.sheet) {
                key = `Sheet: ${unit.location.sheet}`;
            }

            if (!grouped[key]) grouped[key] = [];
            grouped[key].push(unit.text);
        });

        Object.entries(grouped).forEach(([title, texts]) => {
            createPageCard(`${file.filename} – ${title}`, texts.join('\n\n'));
        });
    });

    resultsArea.style.display = 'block';
}

// =====================================================
// PAGE CARD
// =====================================================
function createPageCard(title, text) {
    const card = document.createElement('div');
    card.className = 'page-card';
    card.innerHTML = `
        <div class="page-header">
            <span class="page-title">
                <i class="fa-regular fa-file-lines"></i>&nbsp; ${title}
            </span>
            <span class="page-badge">${text.length} chars</span>
        </div>
        <div class="page-content">${escapeHtml(text)}</div>
    `;
    resultsList.appendChild(card);
}

// =====================================================
// SECURITY: HTML ESCAPE
// =====================================================
function escapeHtml(text) {
    const div = document.createElement('div');
    div.innerText = text;
    return div.innerHTML;
}
