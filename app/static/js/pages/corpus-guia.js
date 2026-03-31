/**
 * Corpus Guía page scripts
 * Handles copy functionality for CQL prompt code block
 */
(function() {
  'use strict';

  function initCopyButton() {
    const copyBtn = document.getElementById('copy-cql-prompt');
    const promptText = document.getElementById('cql-prompt-text');
    
    if (!copyBtn || !promptText) {
      return;
    }
    
    copyBtn.addEventListener('click', function() {
      const textToCopy = (promptText.innerText || promptText.textContent || '').trim();
      if (!textToCopy) return;
      
      navigator.clipboard.writeText(textToCopy).then(function() {
        const icon = copyBtn.querySelector('.material-symbols-rounded');
        if (icon) icon.textContent = 'check';
        copyBtn.classList.add('md3-code-block__copy--success', 'is-success');
        setTimeout(function() {
          if (icon) icon.textContent = 'content_copy';
          copyBtn.classList.remove('md3-code-block__copy--success', 'is-success');
        }, 2000);
      }).catch(function(err) {
        const icon = copyBtn.querySelector('.material-symbols-rounded');
        if (icon) icon.textContent = 'error';
        copyBtn.classList.add('is-error');
        setTimeout(function() {
          if (icon) icon.textContent = 'content_copy';
          copyBtn.classList.remove('is-error');
        }, 2000);
        console.error('Copy failed:', err);
      });
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCopyButton);
  } else {
    initCopyButton();
  }
})();
