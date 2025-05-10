document.addEventListener('DOMContentLoaded', function() {
    // YouTube form submission
    const youtubeForm = document.getElementById('youtube-form');
    if (youtubeForm) {
        youtubeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleDownloadForm(this, 'audio');
        });
    }
    
    // Pinterest form submission
    const pinterestForm = document.getElementById('pinterest-form');
    if (pinterestForm) {
        pinterestForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleDownloadForm(this, 'video');
        });
    }
    
    function handleDownloadForm(form, type) {
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        
        // Get the download status container and make it visible
        const downloadStatus = document.getElementById('download-status');
        downloadStatus.style.display = 'block';
        
        // Add a new download item to the status container
        const downloadsContainer = document.getElementById('downloads-container');
        const downloadId = 'download-' + Date.now();
        const downloadItem = document.createElement('div');
        downloadItem.id = downloadId;
        downloadItem.className = 'download-item mb-3 p-3 border rounded';
        downloadItem.innerHTML = `
            <div class="download-item-header d-flex justify-content-between mb-2">
                <span class="download-item-title">${type === 'audio' ? 'YouTube Audio' : 'Pinterest Video'}</span>
                <span class="download-item-status">Processing...</span>
            </div>
            <div class="progress mb-2">
                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                     role="progressbar" style="width: 100%"></div>
            </div>
        `;
        downloadsContainer.appendChild(downloadItem);
        
        // Prepare form data
        const formData = new FormData(form);
        
        // Send AJAX request
        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Update the download item status
            const statusElem = downloadItem.querySelector('.download-item-status');
            const progressBar = downloadItem.querySelector('.progress-bar');
            
            if (data.success) {
                // Update UI to show success
                statusElem.textContent = 'Completed';
                statusElem.className = 'download-item-status text-success';
                progressBar.classList.remove('progress-bar-animated');
                progressBar.style.width = '100%';
                
                // Create download button
                const downloadBtn = document.createElement('a');
                downloadBtn.href = data.download_url;
                downloadBtn.className = 'btn btn-sm btn-success mt-2';
                downloadBtn.innerHTML = '<i class="fas fa-download me-1"></i>Download Now';
                downloadItem.appendChild(downloadBtn);
                
                // Automatically trigger download
                window.location.href = data.download_url;
                
                // Reset form
                form.reset();
            } else {
                // Update UI to show error
                statusElem.textContent = 'Failed: ' + (data.error || 'Unknown error');
                statusElem.className = 'download-item-status text-danger';
                progressBar.classList.remove('progress-bar-animated', 'progress-bar-striped');
                progressBar.classList.add('bg-danger');
                progressBar.style.width = '100%';
            }
            
            // Re-enable the submit button
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        })
        .catch(error => {
            // Update UI to show error
            const statusElem = downloadItem.querySelector('.download-item-status');
            statusElem.textContent = 'Error: ' + error.message;
            statusElem.className = 'download-item-status text-danger';
            
            const progressBar = downloadItem.querySelector('.progress-bar');
            progressBar.classList.remove('progress-bar-animated', 'progress-bar-striped');
            progressBar.classList.add('bg-danger');
            progressBar.style.width = '100%';
            
            // Re-enable the submit button
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        });
    }
});