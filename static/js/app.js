document.addEventListener('DOMContentLoaded', () => {
  AOS.init({ duration: 700, once: true, easing: 'ease-out-cubic' });

  const loader = document.getElementById('page-loader');
  if (loader) {
    setTimeout(() => loader.classList.add('hide'), 500);
  }

  // Mobile-specific enhancements
  const isMobile = window.innerWidth <= 768;

  if (isMobile) {
    // Add touch feedback for buttons
    document.querySelectorAll('.btn, .nav-link, .stat-card').forEach(element => {
      element.addEventListener('touchstart', () => {
        element.style.transform = 'scale(0.98)';
      });

      element.addEventListener('touchend', () => {
        setTimeout(() => {
          element.style.transform = '';
        }, 150);
      });
    });

    // Improve scrolling on mobile
    document.body.style.webkitOverflowScrolling = 'touch';

    // Prevent zoom on input focus for iOS
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
      input.addEventListener('focus', () => {
        input.setAttribute('autocomplete', 'off');
        input.setAttribute('autocorrect', 'off');
        input.setAttribute('autocapitalize', 'off');
        input.setAttribute('spellcheck', 'false');
      });
    });
  }

  // Theme Toggle Functionality
  const themeToggle = document.getElementById('theme-toggle');
  const html = document.documentElement;

  // Load saved theme
  const savedTheme = localStorage.getItem('theme') || 'light';
  html.setAttribute('data-theme', savedTheme);

  if (themeToggle) {
    // Update toggle icon based on current theme
    updateThemeIcon(savedTheme);

    themeToggle.addEventListener('click', () => {
      const currentTheme = html.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

      html.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      updateThemeIcon(newTheme);
    });
  }

  function updateThemeIcon(theme) {
    const icon = themeToggle.querySelector('.toggle-icon');
    const text = themeToggle.querySelector('.toggle-text');
    if (icon) {
      icon.className = theme === 'dark' ? 'fas fa-sun toggle-icon' : 'fas fa-moon toggle-icon';
    }
    if (text) {
      text.textContent = theme === 'dark' ? 'Light' : 'Dark';
    }
  }

  if (window.dashboardChartData) {
    const canvas = document.getElementById('adminAnalyticsChart');
    if (canvas) {
      new Chart(canvas, {
        type: 'bar',
        data: {
          labels: window.dashboardChartData.labels,
          datasets: [{
            label: 'Percentage',
            data: window.dashboardChartData.values,
            borderRadius: 8,
            backgroundColor: ['#5b6cff', '#8b5cf6']
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true, max: 100 } }
        }
      });
    }
  }
});
