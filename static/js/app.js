(() => {
    const $ = (sel, ctx = document) => ctx.querySelector(sel);
    const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

    // Theme toggle with smooth transition
    const themeBtn = $('#themeToggle');
    if (themeBtn) {
        const setTheme = (theme) => {
            document.documentElement.dataset.theme = theme;
            localStorage.setItem('theme', theme);
            themeBtn.textContent = theme === 'dark' ? '☀️' : '🌙';
        };

        themeBtn.addEventListener('click', () => {
            const current = document.documentElement.dataset.theme || 'dark';
            const next = current === 'dark' ? 'light' : 'dark';
            setTheme(next);
        });

        // Set initial button icon
        const currentTheme = document.documentElement.dataset.theme || 'dark';
        themeBtn.textContent = currentTheme === 'dark' ? '☀️' : '🌙';
    }

    // Enhanced dropzone with visual feedback
    const dropzone = $('#dropzone');
    const fileInput = $('#resume');
    const fileName = $('#fileName');

    if (dropzone && fileInput) {
        const openPicker = () => fileInput.click();

        dropzone.addEventListener('click', openPicker);

        dropzone.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openPicker();
            }
        });

        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dropzone--active');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dropzone--active');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dropzone--active');
            const file = e.dataTransfer.files?.[0];
            if (file) {
                fileInput.files = e.dataTransfer.files;
                fileName.textContent = file.name;
            }
        });

        fileInput.addEventListener('change', () => {
            const file = fileInput.files?.[0];
            if (file) {
                fileName.textContent = file.name;
            } else {
                fileName.textContent = '';
            }
        });
    }

    // Loading overlay with smooth transitions
    const form = $('#analyzeForm');
    const loading = $('#appLoading');
    const submitBtn = $('#submitBtn');

    if (form && loading) {
        form.addEventListener('submit', () => {
            loading.setAttribute('aria-hidden', 'false');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Analyzing...';
            }
        });
    }

    // Copy JSON with visual feedback
    const copyBtn = $('#copyJsonBtn');
    const downloadBtn = $('#downloadJsonBtn');

    const getJsonData = (el) => {
        try {
            const jsonData = JSON.parse(el?.dataset?.json || '{}');
            return JSON.stringify(jsonData, null, 2);
        } catch {
            return el?.dataset?.json || '{}';
        }
    };

    if (copyBtn) {
        copyBtn.addEventListener('click', async () => {
            const text = getJsonData(copyBtn);
            try {
                await navigator.clipboard.writeText(text);
                const originalText = copyBtn.textContent;
                copyBtn.textContent = '✓ Copied!';
                copyBtn.style.background = 'var(--accent)';
                copyBtn.style.color = 'white';
                copyBtn.style.borderColor = 'var(--accent)';

                setTimeout(() => {
                    copyBtn.textContent = originalText;
                    copyBtn.style.background = '';
                    copyBtn.style.color = '';
                    copyBtn.style.borderColor = '';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        });
    }

    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            const text = getJsonData(downloadBtn);
            const blob = new Blob([text], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'resume-analysis.json';
            document.body.appendChild(a);
            a.click();
            requestAnimationFrame(() => {
                URL.revokeObjectURL(url);
                a.remove();
            });

            // Visual feedback
            const originalText = downloadBtn.textContent;
            downloadBtn.textContent = '✓ Downloaded!';
            setTimeout(() => {
                downloadBtn.textContent = originalText;
            }, 2000);
        });
    }

    // Initialize circular progress with animation
    const progressEl = $('.progress');
    if (progressEl) {
        const value = Math.max(0, Math.min(100, parseInt(progressEl.getAttribute('data-value') || '0')));
        
        // Animate from 0 to target value
        let current = 0;
        const duration = 1500;
        const startTime = Date.now();

        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function for smooth animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            current = Math.floor(value * easeOutQuart);
            
            progressEl.style.setProperty('--value', current);

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                progressEl.style.setProperty('--value', value);
            }
        };

        // Start animation after a brief delay
        setTimeout(() => {
            requestAnimationFrame(animate);
        }, 300);
    }

    // Add smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';
})();