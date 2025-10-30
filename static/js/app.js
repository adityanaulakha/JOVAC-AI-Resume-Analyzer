(() => {
	const $ = (sel, ctx=document) => ctx.querySelector(sel);
	const $$ = (sel, ctx=document) => Array.from(ctx.querySelectorAll(sel));

	// Theme toggle
	const themeBtn = $('#themeToggle');
	if (themeBtn) {
		themeBtn.addEventListener('click', () => {
			const cur = document.documentElement.dataset.theme || 'dark';
			const next = cur === 'dark' ? 'light' : 'dark';
			document.documentElement.dataset.theme = next;
			localStorage.setItem('theme', next);
		});
	}

	// Dropzone
	const dropzone = $('#dropzone');
	const fileInput = $('#resume');
	const fileName = $('#fileName');
	if (dropzone && fileInput) {
		const openPicker = () => fileInput.click();
		dropzone.addEventListener('click', openPicker);
		dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openPicker(); }});
		dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('dropzone--active'); });
		dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dropzone--active'));
		dropzone.addEventListener('drop', (e) => {
			e.preventDefault();
			dropzone.classList.remove('dropzone--active');
			const f = e.dataTransfer.files && e.dataTransfer.files[0];
			if (f) {
				fileInput.files = e.dataTransfer.files;
				fileName.textContent = f.name;
			}
		});
		fileInput.addEventListener('change', () => {
			const f = fileInput.files && fileInput.files[0];
			fileName.textContent = f ? f.name : '';
		});
	}

	// Loading overlay on submit
	const form = $('#analyzeForm');
	const loading = $('#appLoading');
	const submitBtn = $('#submitBtn');
	if (form && loading) {
		form.addEventListener('submit', () => {
			loading.setAttribute('aria-hidden', 'false');
			submitBtn && (submitBtn.disabled = true);
		});
	}

	// Copy/Download JSON on results page
	const copyBtn = $('#copyJsonBtn');
	const downloadBtn = $('#downloadJsonBtn');
	const getJsonData = (el) => {
		try { return JSON.stringify(JSON.parse(el?.dataset?.json || '{}'), null, 2); } catch { return el?.dataset?.json || '{}'; }
	};
	if (copyBtn) {
		copyBtn.addEventListener('click', async () => {
			const text = getJsonData(copyBtn);
			try { await navigator.clipboard.writeText(text); copyBtn.textContent = 'Copied!'; setTimeout(()=>copyBtn.textContent='Copy JSON',1200); } catch {}
		});
	}
	if (downloadBtn) {
		downloadBtn.addEventListener('click', () => {
			const text = getJsonData(downloadBtn);
			const blob = new Blob([text], { type: 'application/json' });
			const url = URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url; a.download = 'analysis.json';
			document.body.appendChild(a); a.click();
			requestAnimationFrame(() => { URL.revokeObjectURL(url); a.remove(); });
		});
	}
})();