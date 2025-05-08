document.addEventListener("DOMContentLoaded", function() {
    // Handle form submissions with AJAX
    const youtubeForm = document.getElementById('youtube-form');
    const pinterestForm = document.getElementById('pinterest-form');
    
    youtubeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        submitDownloadForm(this, 'YouTube Audio');
    });
    
    pinterestForm.addEventListener('submit', function(e) {
        e.preventDefault();
        submitDownloadForm(this, 'Pinterest Video');
    });
    
    function submitDownloadForm(form, type) {
        // Disable the submit button
        const submitBtn = form.querySelector('.download-btn');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loader"></span> Processing...';
        
        const formData = new FormData(form);
        const url = form.getAttribute('action');
        const downloadId = Date.now().toString();
        
        // Show download status section
        const downloadStatus = document.getElementById('download-status');
        downloadStatus.style.display = 'block';
        
        // Add a new download item
        const downloadsContainer = document.getElementById('downloads-container');
        const downloadItem = document.createElement('div');
        downloadItem.id = `download-${downloadId}`;
        downloadItem.className = 'download-item status-pending';
        
        const mediaURL = formData.get('url');
        const displayURL = mediaURL.length > 40 ? mediaURL.substring(0, 40) + '...' : mediaURL;
        
        downloadItem.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <div class="d-flex align-items-center">
                        <span class="loader"></span>
                        <strong>${type}</strong>
                    </div>
                    <div class="mt-1" style="color: var(--gray-dark);">${displayURL}</div>
                </div>
                <span id="status-${downloadId}" class="badge bg-warning">Processing</span>
            </div>
        `;
        
        downloadsContainer.prepend(downloadItem);
        
        // Submit the form via AJAX
        fetch(url, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Re-enable the submit button
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-download me-2"></i>Download';
            
            if (data.success) {
                // Update UI for successful download
                downloadItem.className = 'download-item status-complete';
                downloadItem.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <div class="d-flex align-items-center">
                                <i class="fas fa-check-circle me-2 text-success"></i>
                                <strong>${type}</strong>
                            </div>
                            <div class="mt-1">${data.filename}</div>
                        </div>
                        <div>
                            <span class="badge bg-success me-2">Complete</span>
                            <a href="${data.download_url}" class="btn btn-sm btn-primary">
                                <i class="fas fa-download"></i>
                            </a>
                        </div>
                    </div>
                `;
                
                // Clear the form
                form.reset();
            } else {
                // Update UI for failed download
                downloadItem.className = 'download-item status-error';
                downloadItem.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <div class="d-flex align-items-center">
                                <i class="fas fa-exclamation-circle me-2 text-danger"></i>
                                <strong>${type}</strong>
                            </div>
                            <div class="mt-1" style="color: var(--gray-dark);">${displayURL}</div>
                            <div class="mt-1 text-danger">${data.error}</div>
                        </div>
                        <span class="badge bg-danger">Failed</span>
                    </div>
                `;
            }
        })
        .catch(error => {
            // Re-enable the submit button
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-download me-2"></i>Download';
            
            // Update UI for error
            downloadItem.className = 'download-item status-error';
            downloadItem.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <div class="d-flex align-items-center">
                            <i class="fas fa-exclamation-circle me-2 text-danger"></i>
                            <strong>${type}</strong>
                        </div>
                        <div class="mt-1" style="color: var(--gray-dark);">${displayURL}</div>
                        <div class="mt-1 text-danger">An error occurred during download.</div>
                    </div>
                    <span class="badge bg-danger">Failed</span>
                </div>
            `;
        });
    }
});