// GitHub Pages redirect — fallback por si alguien llega directo via github.io
if (location.hostname.includes('github.io')) {
    location.replace('https://descubrir.digitalaccessibility.cl/');
}

// GA4 stub — encola eventos antes de que cargue el script real
window.dataLayer = window.dataLayer || [];
window.gtag = function() { dataLayer.push(arguments); };

// GA4 diferido — carga solo tras la primera interaccion del usuario
var _gaLoaded = false;
function _loadGA4() {
    if (_gaLoaded) return;
    _gaLoaded = true;
    var s = document.createElement('script');
    s.src = 'https://www.googletagmanager.com/gtag/js?id=G-9S47BNHFHZ';
    s.async = true;
    document.head.appendChild(s);
    s.onload = function() {
        gtag('js', new Date());
        gtag('config', 'G-9S47BNHFHZ');
    };
}
['click', 'touchstart', 'scroll', 'keydown'].forEach(function(ev) {
    document.addEventListener(ev, _loadGA4, { once: true, passive: true });
});

// YouTube facade — carga el iframe solo al hacer clic
document.querySelectorAll('.video-facade').forEach(function(btn) {
    btn.addEventListener('click', function() {
        var iframe = document.createElement('iframe');
        iframe.src = 'https://www.youtube-nocookie.com/embed/' + btn.dataset.embed + '?autoplay=1&rel=0';
        iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
        iframe.allowFullscreen = true;
        iframe.title = btn.getAttribute('aria-label').replace('Reproducir: ', '').replace(' (YouTube)', '');
        btn.replaceWith(iframe);
    });
});

// FAQ tracking
document.querySelectorAll('.faq details').forEach(function(detail) {
    detail.addEventListener('toggle', function() {
        if (this.open) {
            gtag('event', 'faq_open', {
                question: this.querySelector('summary').textContent.trim()
            });
        }
    });
});

// Link tracking — reemplaza los onclick inline eliminados del HTML
document.querySelectorAll('[data-ga-event]').forEach(function(el) {
    el.addEventListener('click', function() {
        gtag('event', el.dataset.gaEvent, { location: el.dataset.gaLocation });
    });
});
