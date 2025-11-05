// Basic UI interactions: navbar mobile toggle and sidebar submenu toggles

document.addEventListener('DOMContentLoaded', () => {
	// Mobile navbar toggle
	const toggleBtn = document.getElementById('menu-toggle');
	const navMenu = document.getElementById('nav-menu');
	if (toggleBtn && navMenu) {
		toggleBtn.addEventListener('click', () => {
			const isOpen = navMenu.classList.toggle('open');
			toggleBtn.setAttribute('aria-expanded', String(isOpen));
		});
	}

	// Sidebar submenu toggles
	document.querySelectorAll('.submenu-toggle').forEach(btn => {
		btn.addEventListener('click', () => {
			const next = btn.parentElement?.querySelector('.submenu');
			if (!next) return;
			const hidden = next.hasAttribute('hidden');
			if (hidden) next.removeAttribute('hidden'); else next.setAttribute('hidden', '');
			btn.setAttribute('aria-expanded', String(hidden));
		});
	});
});