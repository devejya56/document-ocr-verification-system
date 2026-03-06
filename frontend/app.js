/**
 * DocVerify — Frontend Application
 * Handles Extract, Tamper Check, Face Match, and Verify
 */

const API = '';
let authToken = localStorage.getItem('authToken') || null;
let currentExtractionId = null;
let currentFields = {};
let selectedFiles = {};

// ==================== INIT ====================

document.addEventListener('DOMContentLoaded', () => {
    setupDropZone('extract');
    setupDropZone('tamper');
    setupDropZone('face-doc');
    setupDropZone('face-selfie');
    updateAuthUI();
    setActiveNav('extract');
});

function setupDropZone(id) {
    const dropZone = document.getElementById(`drop-zone-${id}`);
    const fileInput = document.getElementById(`file-input-${id}`);
    if (!dropZone || !fileInput) return;

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('drag-over'); });
    ['dragleave', 'dragend'].forEach(evt => dropZone.addEventListener(evt, () => dropZone.classList.remove('drag-over')));
    dropZone.addEventListener('drop', (e) => { e.preventDefault(); dropZone.classList.remove('drag-over'); if (e.dataTransfer.files.length) handleFileSelect(e.dataTransfer.files[0], id); });
    fileInput.addEventListener('change', (e) => { if (e.target.files.length) handleFileSelect(e.target.files[0], id); });
}

function handleFileSelect(file, id) {
    selectedFiles[id] = file;
    const dropZone = document.getElementById(`drop-zone-${id}`);
    dropZone.classList.add('has-file');

    const content = document.getElementById(`upload-content-${id}`);
    const selected = document.getElementById(`upload-selected-${id}`);
    if (content) content.classList.add('hidden');
    if (selected) selected.classList.remove('hidden');

    const fnEl = document.getElementById(`selected-filename-${id}`);
    const szEl = document.getElementById(`selected-size-${id}`);
    if (fnEl) fnEl.textContent = file.name;
    if (szEl) szEl.textContent = `(${(file.size / 1024 / 1024).toFixed(2)} MB)`;

    // Enable corresponding button
    if (id === 'extract') document.getElementById('extract-btn').disabled = false;
    if (id === 'tamper') document.getElementById('tamper-btn').disabled = false;
    if (id === 'face-doc' || id === 'face-selfie') {
        document.getElementById('face-btn').disabled = !(selectedFiles['face-doc'] && selectedFiles['face-selfie']);
    }
}

function removeFile(e, id) {
    e.stopPropagation();
    delete selectedFiles[id];
    const dropZone = document.getElementById(`drop-zone-${id}`);
    dropZone.classList.remove('has-file');
    const content = document.getElementById(`upload-content-${id}`);
    const selected = document.getElementById(`upload-selected-${id}`);
    if (content) content.classList.remove('hidden');
    if (selected) selected.classList.add('hidden');
    document.getElementById(`file-input-${id}`).value = '';

    if (id === 'extract') document.getElementById('extract-btn').disabled = true;
    if (id === 'tamper') document.getElementById('tamper-btn').disabled = true;
    if (id === 'face-doc' || id === 'face-selfie') document.getElementById('face-btn').disabled = true;
}

// ==================== SECTIONS ====================

function showSection(name) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById(`section-${name}`).classList.add('active');
    setActiveNav(name);
}

function setActiveNav(name) {
    document.querySelectorAll('.nav-link').forEach(btn => btn.classList.toggle('active', btn.dataset.section === name));
}

// ==================== AUTH ====================

function openAuthModal() {
    if (authToken) { authToken = null; localStorage.removeItem('authToken'); updateAuthUI(); showToast('Logged out', 'info'); return; }
    document.getElementById('auth-modal').classList.remove('hidden');
}
function closeAuthModal() { document.getElementById('auth-modal').classList.add('hidden'); }

let isRegisterMode = false;
function toggleAuthMode(e) {
    e.preventDefault();
    isRegisterMode = !isRegisterMode;
    document.getElementById('auth-title').textContent = isRegisterMode ? 'Sign up' : 'Log in';
    document.getElementById('auth-submit-btn').textContent = isRegisterMode ? 'Create account' : 'Log in';
    document.getElementById('auth-toggle-text').textContent = isRegisterMode ? 'Already have an account?' : "Don't have an account?";
    document.getElementById('auth-toggle-link').textContent = isRegisterMode ? 'Log in' : 'Sign up';
    document.getElementById('fullname-group').style.display = isRegisterMode ? 'block' : 'none';
}

async function handleAuth(e) {
    e.preventDefault();
    const username = document.getElementById('auth-username').value;
    const password = document.getElementById('auth-password').value;
    try {
        if (isRegisterMode) {
            const fullName = document.getElementById('auth-fullname').value;
            const res = await fetch(`${API}/api/auth/register`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username, password, full_name: fullName || null }) });
            if (!res.ok) throw new Error((await res.json()).detail || 'Registration failed');
            showToast('Account created!', 'success');
        }
        const formData = new URLSearchParams(); formData.append('username', username); formData.append('password', password);
        const res = await fetch(`${API}/api/auth/login`, { method: 'POST', body: formData });
        if (!res.ok) throw new Error((await res.json()).detail || 'Login failed');
        const data = await res.json();
        authToken = data.access_token; localStorage.setItem('authToken', authToken);
        updateAuthUI(); closeAuthModal(); showToast('Welcome back!', 'success');
    } catch (err) { showToast(err.message, 'error'); }
}

function updateAuthUI() { document.getElementById('auth-btn').textContent = authToken ? 'Log out' : 'Log in'; }
function getAuthHeaders() { const h = {}; if (authToken) h['Authorization'] = `Bearer ${authToken}`; return h; }

// ==================== EXTRACT (with auto-classify) ====================

async function extractDocument() {
    const file = selectedFiles['extract'];
    if (!file) return;

    let docType = document.getElementById('doc-type').value;
    showLoading('Processing document…');

    try {
        // Auto-classify if selected
        if (docType === 'auto') {
            showLoading('Auto-detecting document type…');
            const classifyForm = new FormData();
            classifyForm.append('file', file);
            const classRes = await fetch(`${API}/api/classify`, { method: 'POST', headers: getAuthHeaders(), body: classifyForm });
            if (classRes.ok) {
                const classData = await classRes.json();
                docType = classData.predicted_type;
                showClassificationResult(classData);
                document.getElementById('doc-type').value = docType;
            }
        }

        showLoading('Extracting fields…');
        const formData = new FormData();
        formData.append('file', file);
        const res = await fetch(`${API}/api/extract?document_type=${docType}`, { method: 'POST', headers: getAuthHeaders(), body: formData });
        if (!res.ok) throw new Error((await res.json()).detail || 'Extraction failed');
        const data = await res.json();
        displayExtractionResults(data);
        showToast('Fields extracted successfully', 'success');
    } catch (err) { showToast(err.message, 'error'); }
    finally { hideLoading(); }
}

function showClassificationResult(data) {
    const banner = document.getElementById('classification-result');
    const conf = Math.round(data.confidence * 100);
    const chipClass = conf >= 70 ? 'high' : conf >= 40 ? 'medium' : 'low';
    banner.innerHTML = `<span class="chip ${chipClass}">${conf}% confidence</span> Auto-detected as <strong>${formatFieldName(data.predicted_type)}</strong> — ${data.detail}`;
    banner.classList.remove('hidden');
}

function displayExtractionResults(data) {
    currentExtractionId = data.extraction_id;
    currentFields = data.fields;
    const container = document.getElementById('extraction-results');
    container.classList.remove('hidden');

    const confidence = Math.round(data.overall_confidence * 100);
    const chip = document.getElementById('confidence-chip');
    chip.textContent = `${confidence}% confidence`;
    chip.className = `chip ${confidence >= 70 ? 'high' : confidence >= 40 ? 'medium' : 'low'}`;
    document.getElementById('result-time').textContent = `${data.processing_time.toFixed(2)}s`;

    const fieldsList = document.getElementById('fields-container');
    fieldsList.innerHTML = '';
    for (const [name, field] of Object.entries(data.fields)) {
        const item = document.createElement('div');
        item.className = 'field-item';
        item.innerHTML = `<div class="field-label">${formatFieldName(name)}</div><div class="field-body"><div class="field-value">${escapeHtml(field.value) || '—'}</div><div class="field-conf">${Math.round(field.confidence * 100)}% confidence</div></div>`;
        fieldsList.appendChild(item);
    }
}

function copyExtractionId() {
    if (currentExtractionId) { navigator.clipboard.writeText(currentExtractionId); showToast('Extraction ID copied', 'info'); }
}

// ==================== TAMPER CHECK ====================

async function checkTamper() {
    const file = selectedFiles['tamper'];
    if (!file) return;
    showLoading('Analyzing document for tampering…');
    try {
        const formData = new FormData();
        formData.append('file', file);
        const res = await fetch(`${API}/api/tamper-check`, { method: 'POST', headers: getAuthHeaders(), body: formData });
        if (!res.ok) throw new Error((await res.json()).detail || 'Analysis failed');
        const data = await res.json();
        displayTamperResults(data);
        showToast(`Tamper analysis: ${data.verdict}`, data.verdict === 'AUTHENTIC' ? 'success' : 'error');
    } catch (err) { showToast(err.message, 'error'); }
    finally { hideLoading(); }
}

function displayTamperResults(data) {
    const container = document.getElementById('tamper-results');
    container.classList.remove('hidden');

    const score = Math.round(data.overall_trust_score);
    const chip = document.getElementById('trust-chip');
    chip.textContent = `${score}% trust`;
    chip.className = `chip ${score >= 75 ? 'high' : score >= 50 ? 'medium' : 'low'}`;
    document.getElementById('tamper-verdict').textContent = data.verdict.replace(/_/g, ' ');
    document.getElementById('tamper-detail').textContent = data.verdict_detail;

    // Analyses
    const analyses = document.getElementById('tamper-analyses');
    analyses.innerHTML = '';
    for (const [name, info] of Object.entries(data.analyses)) {
        const sc = info.score;
        const item = document.createElement('div');
        item.className = `field-item ${sc >= 75 ? 'match' : sc >= 50 ? 'missing' : 'mismatch'}`;
        item.innerHTML = `<div class="field-label">${formatFieldName(name)}</div><div class="field-body"><div class="field-value">Score: ${Math.round(sc)}%</div><div class="field-conf">${info.description}</div></div>`;
        analyses.appendChild(item);
    }

    // Flags
    const flagsEl = document.getElementById('tamper-flags');
    flagsEl.innerHTML = '';
    if (data.flags && data.flags.length > 0) {
        for (const flag of data.flags) {
            const f = document.createElement('div');
            f.className = 'flag-item';
            f.innerHTML = `${escapeHtml(flag)}`;
            flagsEl.appendChild(f);
        }
    }
}

// ==================== FACE MATCH ====================

async function matchFaces() {
    const docFile = selectedFiles['face-doc'];
    const selfieFile = selectedFiles['face-selfie'];
    if (!docFile || !selfieFile) return;
    showLoading('Comparing faces…');
    try {
        const formData = new FormData();
        formData.append('document', docFile);
        formData.append('selfie', selfieFile);
        const res = await fetch(`${API}/api/face-match`, { method: 'POST', headers: getAuthHeaders(), body: formData });
        if (!res.ok) throw new Error((await res.json()).detail || 'Matching failed');
        const data = await res.json();
        displayFaceResults(data);
        showToast(`Face match: ${data.verdict}`, data.verdict === 'MATCH' ? 'success' : 'error');
    } catch (err) { showToast(err.message, 'error'); }
    finally { hideLoading(); }
}

function displayFaceResults(data) {
    const container = document.getElementById('face-results');
    container.classList.remove('hidden');

    const score = Math.round(data.match_score * 100);
    const chip = document.getElementById('face-score-chip');
    chip.textContent = `${score}% match`;
    chip.className = `chip ${score >= 65 ? 'high' : score >= 45 ? 'medium' : 'low'}`;
    document.getElementById('face-verdict').textContent = data.verdict.replace(/_/g, ' ');
    document.getElementById('face-detail').textContent = data.detail;

    const methods = document.getElementById('face-methods');
    methods.innerHTML = '';
    if (data.methods) {
        for (const [name, info] of Object.entries(data.methods)) {
            // info is an object: {similarity, distance, threshold, verified} or {similarity, error}
            const sim = typeof info === 'object' ? info.similarity : info;
            const pct = Math.round((sim || 0) * 100);
            const verified = typeof info === 'object' ? info.verified : false;
            const item = document.createElement('div');
            item.className = `field-item ${verified ? 'match' : 'mismatch'}`;
            const statusText = info.error ? 'Error' : (verified ? 'Verified' : 'Not verified');
            item.innerHTML = `<div class="field-label">${formatFieldName(name)}</div><div class="field-body"><div class="field-value">${pct}% similarity</div><div class="field-conf">${statusText}${info.distance !== undefined ? ` · Distance: ${info.distance}` : ''}</div></div>`;
            methods.appendChild(item);
        }
    }
}

// ==================== VERIFY ====================

function prepareVerification() {
    showSection('verify');
    document.getElementById('verify-extraction-id').value = currentExtractionId || '';
    const container = document.getElementById('verify-fields-container');
    container.innerHTML = '';
    for (const [name, field] of Object.entries(currentFields)) {
        const div = document.createElement('div');
        div.className = 'form-field';
        div.innerHTML = `<label>${formatFieldName(name)}</label><input type="text" data-field="${name}" placeholder="Enter ${formatFieldName(name).toLowerCase()}" value="${field.value !== 'NOT_FOUND' ? escapeHtml(field.value) : ''}">`;
        container.appendChild(div);
    }
}

async function verifyData() {
    const extractionId = document.getElementById('verify-extraction-id').value;
    if (!extractionId) { showToast('Enter an extraction ID', 'error'); return; }
    const formData = {};
    document.querySelectorAll('#verify-fields-container input[data-field]').forEach(input => { if (input.value) formData[input.dataset.field] = input.value; });
    if (Object.keys(formData).length === 0) { showToast('Fill in at least one field', 'error'); return; }

    showLoading('Verifying…');
    try {
        const res = await fetch(`${API}/api/verify`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify({ extraction_id: extractionId, form_data: formData }) });
        if (!res.ok) throw new Error((await res.json()).detail || 'Verification failed');
        const data = await res.json();
        displayVerificationResults(data);
        showToast('Verification complete', 'success');
    } catch (err) { showToast(err.message, 'error'); }
    finally { hideLoading(); }
}

function displayVerificationResults(data) {
    const container = document.getElementById('verification-results');
    container.classList.remove('hidden');
    const score = Math.round(data.overall_match_score * 100);
    const chip = document.getElementById('verify-score-chip');
    chip.textContent = `${score}% match`;
    chip.className = `chip ${score >= 70 ? 'high' : score >= 40 ? 'medium' : 'low'}`;
    document.getElementById('verify-status').textContent = data.overall_status.replace(/_/g, ' ');
    document.getElementById('verify-matched').textContent = `${data.matched_fields}/${data.total_fields} matched`;

    const fieldsList = document.getElementById('verify-fields-results');
    fieldsList.innerHTML = '';
    for (const field of data.fields) {
        const sc = field.status.toLowerCase();
        const item = document.createElement('div');
        item.className = `field-item ${sc}`;
        item.innerHTML = `<div class="field-label">${formatFieldName(field.field_name)}</div><div class="field-body"><div class="field-value">Expected: ${escapeHtml(field.expected_value)}</div><div class="field-value" style="color:var(--text-secondary)">Got: ${escapeHtml(field.actual_value) || '—'}</div><div class="field-conf">Similarity: ${Math.round(field.similarity_score * 100)}%</div><span class="status-badge ${sc}">${field.status}</span></div>`;
        fieldsList.appendChild(item);
    }
}

// ==================== UTILS ====================

function formatFieldName(name) { return name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()); }
function escapeHtml(str) { if (!str) return ''; return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
function showLoading(text) { document.getElementById('loading-text').textContent = text || 'Processing…'; document.getElementById('loading-overlay').classList.remove('hidden'); }
function hideLoading() { document.getElementById('loading-overlay').classList.add('hidden'); }

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; toast.style.transform = 'translateY(10px)'; toast.style.transition = 'all 0.25s ease'; setTimeout(() => toast.remove(), 250); }, 3500);
}
