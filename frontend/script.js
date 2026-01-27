const DEFAULTS = {
    API_URL: "https://file-extractor.onrender.com",
    MAX_FILES: 5
};

const els = {
    dropZone: document.getElementById('dropZone'),
    fileInput: document.getElementById('fileInput'),
    queue: document.getElementById('queueContainer'),
    extractBtn: document.getElementById('extractBtn'),
    resultsList: document.getElementById('resultsList'), 
    resultsArea: document.getElementById('resultsArea'),
    spinner: document.getElementById('btnSpinner'),
    apiUrl: document.getElementById('apiUrl'),
    batchStatus: document.getElementById('batchStatus'),
    configPanel: document.getElementById('configPanel')
};

let fileQueue = []; 

window.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem('utext_api_url');
    if (saved) els.apiUrl.value = saved;
});

document.getElementById('toggleConfig').onclick = () => 
    els.configPanel.classList.toggle('collapsed');

const highlight = (active) => els.dropZone.classList.toggle('drag-over', active);

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => {
    els.dropZone.addEventListener(evt, (e) => {
        e.preventDefault();
        e.stopPropagation();
    });
});

els.dropZone.addEventListener('dragenter', () => highlight(true));
els.dropZone.addEventListener('dragleave', () => highlight(false));
els.dropZone.addEventListener('drop', (e) => {
    highlight(false);
    if (e.dataTransfer.files.length) handleFiles(e.dataTransfer.files);
});

els.dropZone.addEventListener('click', (e) => {
    if (e.target !== els.dropZone && !e.target.classList.contains('browse-btn')) return;
    els.fileInput.click();
});

els.fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) handleFiles(e.target.files);
});

function handleFiles(files) {
    if (files.length > DEFAULTS.MAX_FILES) return alert(`Max ${DEFAULTS.MAX_FILES} files allowed.`);
    
    fileQueue = Array.from(files);
    resetUI();

    els.queue.innerHTML = fileQueue.map((f, i) => `
        <div class="queue-item" id="q-item-${i}">
            <div class="q-name"><i class="fa-regular fa-file"></i> &nbsp; ${f.name}</div>
            <div class="q-status status-pending" id="q-status-${i}">PENDING</div>
        </div>
    `).join('');

    toggleView(true);
}

els.extractBtn.addEventListener('click', async () => {
    if (!fileQueue.length) return;

    const endpoint = getSafeEndpoint();
    setLoading(true);
    els.batchStatus.textContent = "PROCESSING...";

    for (const [i, file] of fileQueue.entries()) {
        const ui = {
            card: document.getElementById(`q-item-${i}`),
            status: document.getElementById(`q-status-${i}`)
        };

        updateItemStatus(ui, 'processing', 'PROCESSING...');
        
        try {
            const formData = new FormData();
            formData.append('file', file);

            const res = await fetch(endpoint, { method: 'POST', body: formData });
            if (!res.ok) throw new Error((await res.json()).detail || 'Failed');
            
            const data = await res.json();
            updateItemStatus(ui, 'done', 'DONE');
            renderFileResult(data);

        } catch (err) {
            console.error(err);
            updateItemStatus(ui, 'error', 'ERROR');
            renderError(file.name, err.message);
            if (i === 0) alert(`Connection Failed to: ${endpoint}\n\n${err.message}`);
        }
    }

    els.batchStatus.textContent = "COMPLETED";
    setLoading(false);
});

function getSafeEndpoint() {
    let url = els.apiUrl.value.trim();
    if (url) localStorage.setItem('utext_api_url', url);
    
    url = url || DEFAULTS.API_URL;
    url = url.replace(/(\/docs|\/api\/extract|\/)+$/, "");
    
    if (!/^https?:\/\//i.test(url)) {
        url = (url.includes('localhost') || url.includes('127.0.0.1')) 
            ? `http://${url}` 
            : `https://${url}`;
    }
    return `${url}/api/extract`;
}

function updateItemStatus({ card, status }, type, text) {
    status.className = `q-status status-${type}`;
    status.textContent = text;
    card.classList.remove('processing', 'done', 'error');
    card.classList.add(type);
}

function resetUI() {
    els.queue.innerHTML = '';
    els.resultsList.innerHTML = ''; 
    els.resultsArea.style.display = 'none';
    els.batchStatus.textContent = "READY";
}

function toggleView(hasFiles) {
    els.queue.style.display = hasFiles ? 'flex' : 'none';
    els.extractBtn.style.display = hasFiles ? 'block' : 'none';
}

function setLoading(active) {
    els.extractBtn.disabled = active;
    els.spinner.style.display = active ? 'block' : 'none';
    document.querySelector('.btn-content').style.opacity = active ? '0' : '1';
    if (active) els.resultsArea.style.display = 'block';
}

function renderFileResult(data) {
    const safeType = (data.file_type || 'UNK').toUpperCase();
    
    const groups = {};
    (data.content || []).sort((a,b) => (a.location?.number||0) - (b.location?.number||0))
        .forEach(u => {
            const k = u.location.type === 'page' ? `PAGE ${u.location.number}` : 
                      u.location.sheet ? `SHEET: ${u.location.sheet}` : "EXTRACTED TEXT";
            if (!groups[k]) groups[k] = [];
            groups[k].push(u.text);
        });

    const html = `
        <div class="file-result-block">
            <div class="file-result-header">
                <div class="fr-title"><i class="fa-solid fa-file-circle-check" style="color:var(--accent)"></i> ${data.filename}</div>
                <div class="fr-meta">
                    <span class="fr-badge fr-type">${safeType}</span>
                    <span class="fr-badge fr-time">${data.processing_time_ms || 0}ms</span>
                </div>
            </div>
            ${Object.keys(groups).length ? '' : '<div class="empty-msg">No text found.</div>'}
            ${Object.entries(groups).map(([title, texts]) => `
                <div class="page-card">
                    <div class="page-header">
                        <span class="page-title"><i class="fa-regular fa-file-lines"></i> ${title}</span>
                        <span class="page-badge">${texts.join('').length} chars</span>
                    </div>
                    <div class="page-content">${texts.join('\n\n')}</div>
                </div>
            `).join('')}
        </div>
    `;
    els.resultsList.insertAdjacentHTML('beforeend', html);
}

function renderError(name, msg) {
    els.resultsList.insertAdjacentHTML('beforeend', `
        <div class="file-result-block" style="border-color:#ef4444">
            <div class="file-result-header" style="border-color:rgba(239,68,68,0.3)">
                <div class="fr-title" style="color:#ef4444"><i class="fa-solid fa-circle-exclamation"></i> ${name}</div>
                <span class="fr-badge" style="background:rgba(239,68,68,0.1);color:#ef4444">FAILED</span>
            </div>
            <div style="color:#ef4444;padding:0.5rem">${msg}</div>
        </div>
    `);
}