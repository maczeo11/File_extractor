
const CANDIDATE_URLS = [
    "https://fileextractor-production.up.railway.app",  
    "https://file-extractor.onrender.com/"               
];

let dropZone, fileInput, fileInfo, fileName, extractBtn, resultsArea, resultsList, btnSpinner, btnContent, apiUrlInput, toggleConfig, configPanel;
let currentFiles = []; 
let activeApiUrl = ""; 

document.addEventListener('DOMContentLoaded', () => {
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

    setupEventListeners();
    findActiveBackend();
});

async function findActiveBackend() {
    const statusIcon = document.querySelector('.fa-server'); 
    const statusText = document.querySelector('#configPanel small'); 
    
    apiUrlInput.placeholder = "Waking up server (wait 60s)...";
    statusIcon.style.color = "orange";
    statusIcon.className = "fa-solid fa-server fa-beat"; 
    
    const pollServer = async (url) => {
        const maxRetries = 30; 
        for (let i = 0; i < maxRetries; i++) {
            try {
                if (statusText) statusText.textContent = `Attempt ${i+1}/${maxRetries}: Pinging server...`;
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 3000); 
                const response = await fetch(`${url}/`, { method: 'GET', signal: controller.signal });
                clearTimeout(timeoutId);

                if (response.ok) return url; 
            } catch (err) {
                await new Promise(r => setTimeout(r, 2000));
            }
        }
        throw new Error(`Server at ${url} did not wake up.`);
    };

    try {
        const winner = await Promise.any(CANDIDATE_URLS.map(pollServer));
        activeApiUrl = winner;
        apiUrlInput.value = winner; 
        statusIcon.style.color = "#10b981"; 
        statusIcon.className = "fa-solid fa-server"; 
        if (statusText) statusText.textContent = "Server Active & Connected";
        console.log(`✅ Server woke up: ${winner}`);
    } catch (error) {
        console.error("❌ No active backend found.");
        statusIcon.style.color = "#ef4444"; 
        statusIcon.className = "fa-solid fa-server";
        apiUrlInput.value = ""; 
        apiUrlInput.placeholder = "Server failed to wake up.";
        if (statusText) statusText.textContent = "Connection failed. Check logs.";
    }
}

// --- EVENT LISTENERS ---
function setupEventListeners() {
    toggleConfig.addEventListener('click', () => configPanel.classList.toggle('collapsed'));

    dropZone.addEventListener('click', (e) => {
        if (e.target !== fileInput && !e.target.classList.contains('browse-btn')) {
            fileInput.value = ''; 
            fileInput.click();
        }
    });
    
    const browseBtn = dropZone.querySelector('.browse-btn');
    if(browseBtn) {
        browseBtn.addEventListener('click', (e) => { e.stopPropagation(); fileInput.value = ''; fileInput.click(); });
    }

    fileInput.addEventListener('change', (e) => { if (e.target.files.length) handleFiles(e.target.files); });

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

    extractBtn.addEventListener('click', async () => {
        if (currentFiles.length === 0) return;

        let rawUrl = apiUrlInput.value.trim() || activeApiUrl;
        if (!rawUrl) {
            alert("No server connected! Please wait for wake-up.");
            return;
        }

        let baseUrl = rawUrl.replace(/\/$/, "");
        const endpoint = `${baseUrl}/api/extract`;

        setLoading(true);
        resultsArea.style.display = 'block'; 
        resultsList.innerHTML = ''; 

        for (let i = 0; i < currentFiles.length; i++) {
            const file = currentFiles[i];
            btnContent.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Processing ${i + 1}/${currentFiles.length}...`;
            
            const formData = new FormData();
            formData.append('file', file);

            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 60000); 

                const response = await fetch(endpoint, { 
                    method: 'POST', body: formData, signal: controller.signal
                });
                clearTimeout(timeoutId);

                if (!response.ok) {
                    const err = await response.json().catch(() => ({}));
                    throw new Error(JSON.stringify({ status: response.status, msg: err.detail || 'Server Error' }));
                }
                const data = await response.json();
                renderResultCard(data, file.name);
            } catch (error) {
                renderErrorCard(file.name, error);
            }
        }

        btnContent.innerHTML = `<i class="fa-solid fa-check"></i> Done`;
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

// ✅ NEW: Result Card with Show More + Copy
function renderResultCard(data, originalName) {
    const fullText = data.content.map(u => u.text).join('\n\n');
    const isLong = fullText.length > 600;
    
    const shortText = isLong ? fullText.substring(0, 600) + "..." : fullText;

    const card = document.createElement('div');
    card.className = 'page-card';
    card.style.borderLeft = "4px solid #10b981"; 

    const escapedText = fullText.replace(/"/g, '&quot;');

    card.innerHTML = `
        <div class="page-header">
            <span class="page-title"><i class="fa-regular fa-file-lines"></i> ${originalName}</span>
            <div style="display:flex; gap:10px; align-items:center;">
                <span class="page-badge">${data.processing_time_ms}ms</span>
                <button class="copy-btn" title="Copy to Clipboard" data-text="${escapedText}">
                    <i class="fa-regular fa-copy"></i>
                </button>
            </div>
        </div>
        <div class="page-content">
            <span class="text-content">${shortText.replace(/\n/g, '<br>')}</span>
            ${isLong ? `
                <button class="read-more-btn">
                    <i class="fa-solid fa-expand"></i> Show Full Text
                </button>
            ` : ''}
        </div>
        <div class="full-text-storage" style="display:none;">${fullText.replace(/\n/g, '<br>')}</div>
    `;

    // Copy Logic
    const copyBtn = card.querySelector('.copy-btn');
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(fullText);
        copyBtn.innerHTML = '<i class="fa-solid fa-check"></i>';
        setTimeout(() => copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i>', 2000);
    });

    // Show More Logic
    if (isLong) {
        const btn = card.querySelector('.read-more-btn');
        const contentSpan = card.querySelector('.text-content');
        const fullContent = card.querySelector('.full-text-storage').innerHTML;
        
        btn.addEventListener('click', () => {
            if (btn.innerText.includes("Show Full")) {
                contentSpan.innerHTML = fullContent;
                btn.innerHTML = '<i class="fa-solid fa-compress"></i> Collapse Text';
                btn.style.background = 'transparent';
                btn.style.border = '1px dashed var(--text-secondary)';
                btn.style.color = 'var(--text-secondary)';
            } else {
                contentSpan.innerHTML = shortText.replace(/\n/g, '<br>');
                btn.innerHTML = '<i class="fa-solid fa-expand"></i> Show Full Text';
                btn.removeAttribute('style');
            }
        });
    }

    resultsList.appendChild(card);
}

// ✅ NEW: Error Card with Supported Types
function renderErrorCard(filename, errorObj) {
    let title = "Extraction Failed";
    let detail = "An unexpected error occurred.";
    let icon = "fa-triangle-exclamation";
    
    let errorMsg = errorObj.message;
    let status = 0;

    try {
        const parsed = JSON.parse(errorMsg);
        if(parsed.status) {
            status = parsed.status;
            errorMsg = parsed.msg;
        }
    } catch(e) {}

    if (errorObj.name === 'AbortError') {
        title = "Request Timeout";
        detail = "The file took too long (>60s). Try a smaller file.";
        icon = "fa-hourglass-end";
    } else if (status === 413) {
        title = "File Too Large";
        detail = "The file exceeds the server's size limit.";
        icon = "fa-weight-hanging";
    } else if (status === 422 || status === 400) {
        title = "Unsupported Format";
        detail = errorMsg; 
        icon = "fa-file-circle-xmark";
    } else if (status === 500) {
        title = "Server Error";
        detail = "The extraction engine crashed. The file might be corrupt.";
        icon = "fa-bomb";
    } else if (errorMsg.includes("Failed to fetch")) {
        title = "Network Error";
        detail = "Could not reach the server. Is it awake?";
        icon = "fa-wifi";
    }

    const card = document.createElement('div');
    card.className = 'page-card';
    card.style.borderLeft = "4px solid #ef4444"; 
    
    card.innerHTML = `
        <div class="page-header">
            <span class="page-title" style="color: #ef4444">
                <i class="fa-solid ${icon}"></i> ${filename}
            </span>
            <span class="page-badge" style="background: #fee2e2; color: #ef4444;">${title}</span>
        </div>
        <div class="page-content" style="color: #cbd5e1;">
            <p style="margin-bottom: 0.5rem;"><strong>Reason:</strong> ${detail}</p>
        </div>
    `;
    resultsList.appendChild(card);
}