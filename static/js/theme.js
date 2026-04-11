(function () {
    // Immediate execution prevents flickering
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
})();

document.addEventListener("DOMContentLoaded", () => {
    // Only render theme switch on settings pages
    const isSettingsPage = document.body.classList.contains('settings-page') || document.body.classList.contains('admin-settings-page');
    if (!isSettingsPage) {
        return;
    }

    const mount = document.getElementById('theme-toggle-root');
    if (mount) {

        let wrapper = document.createElement("div");
        wrapper.className = "theme-switch-wrapper";
        wrapper.style.cssText = "display:flex;align-items:center;justify-content:flex-end;margin-bottom:12px;";

        let label = document.createElement("label");
        label.className = "theme-switch";

        let checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.id = "theme-checkbox";

        let slider = document.createElement("span");
        slider.className = "theme-slider";

        // Doodle SVGs for Sun and Moon
        const sunSVG = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f39c12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`;
        const moonSVG = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f1c40f" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;

        let iconSpan = document.createElement("span");
        iconSpan.className = "slider-icon";

        slider.appendChild(iconSpan);
        label.appendChild(checkbox);
        label.appendChild(slider);
        wrapper.appendChild(label);

        // Sync initial state
        if (document.documentElement.getAttribute('data-theme') === 'dark') {
            checkbox.checked = true;
            iconSpan.innerHTML = moonSVG;
        } else {
            checkbox.checked = false;
            iconSpan.innerHTML = sunSVG;
        }

        mount.appendChild(wrapper);

        // Connect Logic
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                iconSpan.innerHTML = moonSVG;
            } else {
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('theme', 'light');
                iconSpan.innerHTML = sunSVG;
            }
        });
    }
});
