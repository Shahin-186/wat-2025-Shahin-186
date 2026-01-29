// Toggle the services dropdown on click, and close when clicking outside or pressing Esc
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var dropdown = document.querySelector('.services-dropdown');
    // dropdown may be absent on very small pages; continue to init theme regardless
    // if dropdown is absent, dropdown will be null and related code will be skipped

    var button = dropdown && (dropdown.querySelector('.services-button') || dropdown.querySelector('.services-button'));
    var links = dropdown ? dropdown.querySelectorAll('.dropdown-item') : [];

    function closeDropdown() {
      if (!dropdown) return;
      dropdown.classList.remove('is-active');
      if (button && button.setAttribute) button.setAttribute('aria-expanded', 'false');
    }

    function openDropdown() {
      if (!dropdown) return;
      dropdown.classList.add('is-active');
      if (button && button.setAttribute) button.setAttribute('aria-expanded', 'true');
    }

    function trackEvent(name, payload) {
      try {
        // Push to dataLayer if available (GTM-friendly)
        if (window.dataLayer && Array.isArray(window.dataLayer)) {
          window.dataLayer.push(Object.assign({ event: name }, payload || {}));
        }
        // Fallback: send a beacon to an analytics endpoint if present
        if (navigator.sendBeacon) {
          var url = '/analytics/collect';
          var body = JSON.stringify(Object.assign({ event: name, ts: Date.now() }, payload || {}));
          navigator.sendBeacon(url, new Blob([body], { type: 'application/json' }));
        }
        // Also log for debugging
        console && console.log && console.log('analytics:', name, payload || {});
      } catch (err) {
        console && console.warn && console.warn('analytics error', err);
      }
    }

    // Dropdown-related listeners — only attach if dropdown exists
    if (dropdown) {
      // Toggle on button click
      button && button.addEventListener('click', function (e) {
        // For buttons we don't need to preventDefault for navigation, but keep behaviour consistent
        e.preventDefault && e.preventDefault();
        if (dropdown.classList.contains('is-active')) {
          closeDropdown();
        } else {
          openDropdown();
          trackEvent('services_dropdown_open', { source: 'header' });
          // move focus into first link for keyboard users
          if (links && links.length) links[0].focus();
        }
      });

      // When a dropdown link is clicked, track and close the menu (use capture to run before navigation)
      links && links.forEach(function (lnk) {
        lnk.addEventListener('click', function (ev) {
          var label = (lnk.textContent || lnk.innerText || '').trim();
          trackEvent('services_link_click', { label: label, href: lnk.getAttribute('href') });
          // Close the dropdown immediately for SPA-like UX
          closeDropdown();
          // Allow navigation to proceed normally
        }, { capture: true });
      });

      // Close when clicking outside
      document.addEventListener('click', function (e) {
        if (!dropdown.contains(e.target)) {
          closeDropdown();
        }
      });

      // Close on escape
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' || e.key === 'Esc') {
          closeDropdown();
        }
      });
    }

    // --- Theme toggle (dark / light) ---
    var themeToggle = document.getElementById('theme-toggle');
    function applyTheme(isDark) {
      try {
        if (isDark) {
          document.body.classList.add('theme-dark');
          if (themeToggle) {
            themeToggle.setAttribute('aria-pressed', 'true');
            themeToggle.innerHTML = '<i class="fas fa-sun" aria-hidden="true"></i><span class="sr-only">Switch to light mode</span>';
          }
          localStorage.setItem('theme', 'dark');
        } else {
          document.body.classList.remove('theme-dark');
          if (themeToggle) {
            themeToggle.setAttribute('aria-pressed', 'false');
            themeToggle.innerHTML = '<i class="fas fa-moon" aria-hidden="true"></i><span class="sr-only">Switch to dark mode</span>';
          }
          localStorage.setItem('theme', 'light');
        }
        // If we're on the homepage, limit featured projects in dark mode
        try {
          var projectGrid = document.querySelector('#projects .project-grid');
          if (projectGrid) {
            if (isDark) projectGrid.classList.add('limited-dark'); else projectGrid.classList.remove('limited-dark');
          }
        } catch (e) { /* ignore */ }
      } catch (err) {
        console && console.warn && console.warn('theme apply error', err);
      }
    }

    try {
      var stored = localStorage.getItem('theme');
      var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (stored === 'dark' || (stored === null && prefersDark)) {
        applyTheme(true);
      } else {
        applyTheme(false);
      }

      if (themeToggle) {
        themeToggle.addEventListener('click', function (ev) {
          ev.preventDefault && ev.preventDefault();
          var isDark = document.body.classList.toggle('theme-dark');
          applyTheme(isDark);
          trackEvent('theme_toggle', { theme: isDark ? 'dark' : 'light' });
        });
      }
    } catch (err) {
      console && console.warn && console.warn('theme init error', err);
    }
  });
})();
