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
            data.formats.filter(f => f.acodec !== 'none' && f.vcodec === 'none').forEach(format => {
                const option = document.createElement('option');
                option.value = format.format_id;
                let label = ` ${format.ext} - ${format.acodec} (${format.abr}kbps)`;
                if (format.language) {
                    label += ` - ${format.language}`;
                }
                option.textContent = label;
                formatList.appendChild(option);
            });

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
            progressText.textContent = 'Pobieranie i konwersja pliku...';
            downloadButton.disabled = true;

            try {
                const response = await fetch('/download', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ 
                        url: currentUrl, 
                        format_id: selectedFormatValue,
                        convert_to_mp3: convertToMp3
                    })
                });

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
                    progressText.textContent = 'Błąd podczas pobierania pliku.';
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

