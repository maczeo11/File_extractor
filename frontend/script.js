// --- CONFIGURATION ---
// Priority: 1. Railway, 2. Render
// Note: Localhost is excluded from auto-check to prevent CORS errors in production.
const CANDIDATE_URLS = [
    "https://fileextractor-production.up.railway.app", // 🏆 Primary
    "https://text-extractor.onrender.com"               // 🛡️ Backup
];

let dropZone, fileInput, fileInfo, fileName, extractBtn, resultsArea, resultsList, btnSpinner, btnContent, apiUrlInput, toggleConfig, configPanel;
let currentFiles = []; // 🟢 Supports Multiple Files
let activeApiUrl = ""; 

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', () => {
    // 1. Get DOM Elements
    dropZone = document.getElementById('dropZone');
    fileInput = document.getElementById('fileInput');
    fileInfo = document.getElementById('fileInfo');
    fileName = document.getElementById('fileName');
    extractBtn = document.getElementById('extractBtn');
    resultsArea = document.getElementById('resultsArea');
    resultsList = document.getElementById('resultsList');
    btnSpinner = document.getElementById('btnSpinner');
    btnContent = document.querySelector('.btn-content');
    apiUrlInput = document.getElementById('apiUrl');
    toggleConfig = document.getElementById('toggleConfig');
    configPanel = document.getElementById('configPanel');

    // 2. Attach Listeners
    setupEventListeners();

    // 3. Start Server Hunt
    findActiveBackend();
});

// --- 🚀 SMART SERVER DETECTION ---
async function findActiveBackend() {
    const statusIcon = document.querySelector('.fa-server'); 
    apiUrlInput.placeholder = "Connecting to server...";
    statusIcon.style.color = "orange";

    const checks = CANDIDATE_URLS.map(async (url) => {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); // 5s timeout
            
            // Check Root "/" endpoint (Backend must have @app.get("/"))
            const response = await fetch(`${url}/`, { method: 'GET', signal: controller.signal });
            clearTimeout(timeoutId);

            if (response.ok) return url;
            throw new Error(`Status: ${response.status}`);
        } catch (err) {
            throw err; 
        }
    });

    try {
        const winner = await Promise.any(checks);
        activeApiUrl = winner;
        apiUrlInput.value = winner; 
        statusIcon.style.color = "#10b981"; // Green
        console.log(`✅ Connected to: ${winner}`);
    } catch (error) {
        console.error("❌ No active backend found.");
        statusIcon.style.color = "#ef4444"; // Red
        apiUrlInput.value = ""; 
        apiUrlInput.placeholder = "Enter URL manually";
    }
}

// --- EVENT LISTENERS ---
function setupEventListeners() {
    toggleConfig.addEventListener('click', () => configPanel.classList.toggle('collapsed'));

    // Drag & Drop / Browse Logic
    dropZone.addEventListener('click', (e) => {
        if (e.target !== fileInput && !e.target.classList.contains('browse-btn')) {
            fileInput.value = ''; // 🟢 Clear input to allow re-selecting same file
            fileInput.click();
        }
    });
    
    // Explicit browse button support
    const browseBtn = dropZone.querySelector('.browse-btn');
    if(browseBtn) {
        browseBtn.addEventListener('click', (e) => {
             e.stopPropagation();
             fileInput.value = '';
             fileInput.click();
        });
    }

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFiles(e.target.files);
    });

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => { e.preventDefault(); e.stopPropagation(); }, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('drag-over'), false);
    });

    dropZone.addEventListener('dragleave', (e) => {
        if (dropZone.contains(e.relatedTarget)) return;
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) handleFiles(e.dataTransfer.files);
    });

    // --- BATCH EXTRACTION QUEUE ---
    extractBtn.addEventListener('click', async () => {
        if (currentFiles.length === 0) return;

        let rawUrl = apiUrlInput.value.trim() || activeApiUrl;
        if (!rawUrl) {
            alert("No server connected! Please enter a URL in settings.");
            return;
        }

        let baseUrl = rawUrl.replace(/\/$/, "");
        const endpoint = `${baseUrl}/api/extract`;

        setLoading(true);
        resultsArea.style.display = 'block'; 
        resultsList.innerHTML = ''; // Clear old results

        // 🔄 Process Loop: File by File
        for (let i = 0; i < currentFiles.length; i++) {
            const file = currentFiles[i];
            
            // Update UI
            btnContent.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Processing ${i + 1}/${currentFiles.length}...`;
            
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch(endpoint, { method: 'POST', body: formData });
                if (!response.ok) {
                    const err = await response.json().catch(() => ({}));
                    throw new Error(err.detail || 'Server Error');
                }
                const data = await response.json();
                renderResultCard(data, file.name);
            } catch (error) {
                renderErrorCard(file.name, error.message);
            }
        }

        // Finish State
        btnContent.innerHTML = `<i class="fa-solid fa-check"></i> Done`;
        
        // 🟢 Reset Logic: After 2s, user can upload again
        setTimeout(() => {
            setLoading(false);
            btnContent.innerHTML = `<i class="fa-solid fa-bolt"></i> Extract Text`;
        }, 2000);
    });
}

// --- HELPER FUNCTIONS ---
function handleFiles(files) {
    currentFiles = Array.from(files);
    fileName.textContent = `${currentFiles.length} file(s) selected`;
    dropZone.style.display = 'none';
    fileInfo.style.display = 'flex';
    extractBtn.style.display = 'block';
    resultsArea.style.display = 'none';
}

window.clearFile = function() {
    currentFiles = [];
    if (fileInput) fileInput.value = '';
    dropZone.style.display = 'block';
    fileInfo.style.display = 'none';
    extractBtn.style.display = 'none';
    resultsArea.style.display = 'none';
}

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

function renderResultCard(data, originalName) {
    // Combine text chunks
    const fullText = data.content.map(u => u.text).join('\n\n');
    
    const card = document.createElement('div');
    card.className = 'page-card';
    card.style.borderLeft = "4px solid #10b981"; // Green success border
    
    // Truncate logic for UI (Full text is in the HTML though)
    const displayText = fullText.length > 2000 
        ? fullText.substring(0, 2000) + "\n\n... [Text truncated for display]" 
        : fullText;

    card.innerHTML = `
        <div class="page-header">
            <span class="page-title"><i class="fa-regular fa-file-lines"></i> ${originalName}</span>
            <span class="page-badge">${data.processing_time_ms}ms</span>
        </div>
        <div class="page-content">${displayText}</div>
    `;
    resultsList.appendChild(card);
}

function renderErrorCard(filename, errorMsg) {
    const card = document.createElement('div');
    card.className = 'page-card';
    card.style.borderLeft = "4px solid #ef4444"; // Red error border
    card.innerHTML = `
        <div class="page-header">
            <span class="page-title" style="color: #ef4444">${filename}</span>
            <span class="page-badge">FAILED</span>
        </div>
        <div class="page-content">Error: ${errorMsg}. Please check file format or server logs.</div>
    `;
    resultsList.appendChild(card);
}