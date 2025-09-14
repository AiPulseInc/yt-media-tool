document.addEventListener('DOMContentLoaded', function() {
    const metadataForm = document.getElementById('metadataForm');
    const downloadForm = document.getElementById('downloadForm');
    const loader = document.getElementById('loader');
    const errorDiv = document.getElementById('error');
    const metadataButton = document.getElementById('metadataButton');
    const downloadLoader = document.getElementById('downloadLoader');
    const downloadStatus = document.getElementById('downloadStatus');
    const downloadButton = document.getElementById('downloadButton');
    const progressModal = document.getElementById('progressModal');
    const progressText = document.getElementById('progressText');
    let currentUrl = '';

    if (metadataForm) {
        metadataForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            currentUrl = document.getElementById('youtubeUrl').value;
            
            // UI updates
            errorDiv.style.display = 'none';
            loader.style.display = 'block';
            metadataButton.disabled = true;
            document.getElementById('metadataResult').style.display = 'none'; // Hide previous results

            const response = await fetch(`/metadata?url=${encodeURIComponent(currentUrl)}`);
            const data = await response.json();

            // UI updates
            loader.style.display = 'none';
            metadataButton.disabled = false;

            if (data.error) {
                errorDiv.textContent = `Błąd: ${data.error}`;
                errorDiv.style.display = 'block';
                return;
            }

            document.getElementById('videoTitle').textContent = data.title;
            document.getElementById('videoAuthor').textContent = data.author;
            document.getElementById('videoThumbnail').src = data.thumbnail;

            const formatList = document.getElementById('formatList');
            formatList.innerHTML = '';
            const audioFormats = (data.formats || []).filter(f => f && f.vcodec === 'none' && f.acodec && f.acodec !== 'none');

            if (audioFormats.length === 0) {
                const empty = document.createElement('option');
                empty.textContent = 'Brak dostępnych formatów audio';
                empty.disabled = true;
                empty.selected = true;
                formatList.appendChild(empty);
            } else {
                audioFormats.forEach(format => {
                    const option = document.createElement('option');
                    option.value = format.format_id || '';
                    const parts = [];
                    if (format.ext) parts.push(format.ext);
                    if (format.acodec && format.acodec !== 'none') parts.push(format.acodec);
                    if (typeof format.abr === 'number' || typeof format.abr === 'string') parts.push(`${format.abr}kbps`);
                    if (format.language) parts.push(format.language);
                    option.textContent = parts.join(' - ');
                    formatList.appendChild(option);
                });
            }

            document.getElementById('metadataResult').style.display = 'block';
            document.getElementById('metadataContainer').style.display = 'none';
        });
    }

    if (downloadForm) {
        downloadForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            const selectedFormatValue = document.getElementById('formatList').value;
            const convertToMp3 = document.getElementById('convertToMp3').checked;
            if (!selectedFormatValue) {
                alert('Wybierz format audio.');
                return;
            }

            // UI updates
            progressModal.style.display = 'block';
            progressText.textContent = 'Inicjowanie pobierania...';
            downloadButton.disabled = true;

            try {
                // Generate a task id to track server-side progress (fallback for older browsers)
                const taskId = (window.crypto && crypto.randomUUID) ? crypto.randomUUID() : (Date.now().toString(36) + Math.random().toString(36).slice(2));

                // Start polling /progress to update the modal while the stream is in-flight
                let pollTimer = setInterval(async () => {
                    try {
                        const r = await fetch(`/progress?task_id=${encodeURIComponent(taskId)}`);
                        if (!r.ok) return; // ignore until server registers task
                        const p = await r.json();
                        const stage = p.stage;
                        const detail = p.detail || '';
                        const map = {
                            initializing: 'Inicjowanie...',
                            starting_download: 'Start pobierania...',
                            downloading: 'Pobieranie strumienia audio...',
                            download_complete: `Pobieranie zakończone ${detail ? '(' + detail + ')' : ''}`,
                            converting: 'Konwertowanie do MP3...',
                            streaming: 'Przygotowywanie pliku do pobrania...',
                            completed: 'Zakończono.'
                        };
                        progressText.textContent = map[stage] || `Przetwarzanie... ${detail}`;
                        if (stage === 'error') {
                            progressText.textContent = `Błąd: ${detail}`;
                        }
                    } catch (_) { /* ignore polling errors */ }
                }, 1000);

                const response = await fetch('/download', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ 
                        url: currentUrl, 
                        format_id: selectedFormatValue,
                        convert_to_mp3: convertToMp3,
                        task_id: taskId
                    })
                });

                // Stop polling when the response completes
                clearInterval(pollTimer);

                if (response.ok) {
                    downloadStatus.textContent = 'Pobieranie zakończone. Przygotowywanie pliku...';
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = response.headers.get('Content-Disposition').split('filename=')[1].replace(/"/g, '');
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    progressText.textContent = 'Plik gotowy!';
                    setTimeout(() => { progressModal.style.display = 'none'; }, 2000);
                } else {
                    try {
                        const err = await response.json();
                        progressText.textContent = `Błąd podczas pobierania: ${err.detail || response.statusText}`;
                    } catch (e) {
                        progressText.textContent = `Błąd podczas pobierania pliku.`;
                    }
                    setTimeout(() => { progressModal.style.display = 'none'; }, 2000);
                }
            } catch (error) {
                progressText.textContent = `Wystąpił błąd: ${error.message}`;
                setTimeout(() => { progressModal.style.display = 'none'; }, 2000);
            } finally {
                downloadButton.disabled = false;
            }
        });
    }
});

