/* Sfondo del sito (body::before).
 *
 * Prima scelta: l'immagine remota impostata in css/style.css.
 * Se non carica, o se al suo posto arriva qualcosa di diverso da quello che ci
 * aspettiamo (e' la difesa anti-hotlink piu' comune: ti servono un'altra
 * immagine invece di dare errore), passiamo alla nostra foto locale.
 *
 * Nota: l'immagine remota non e' nostra. Se un giorno vuoi togliere la
 * dipendenza, basta cambiare il background-image in css/style.css mettendo
 * /assets/watermark-coach2.jpg e questo file diventa inutile.
 */
(function () {
    'use strict';

    var REMOTE = 'https://www.bjjee.com/wp-content/uploads/2023/12/gordon-ryan-guard-pass-.jpeg';
    var LOCAL = "url('/assets/watermark-coach2.jpg')";

    // Sotto questa larghezza assumiamo che non sia la foto vera ma un
    // segnaposto (banner "no hotlinking", pixel di tracciamento, ecc.).
    var LARGHEZZA_MINIMA = 500;

    // Se il server non risponde entro questo tempo, non restiamo senza sfondo.
    var TIMEOUT_MS = 4000;

    var risolto = false;

    function usaLocale() {
        if (risolto) return;
        risolto = true;
        document.documentElement.style.setProperty('--wm', LOCAL);
    }

    function tieniRemota() {
        if (risolto) return;
        risolto = true; // il CSS punta gia' alla remota: non tocchiamo nulla
    }

    var probe = new Image();

    probe.onload = function () {
        if (probe.naturalWidth >= LARGHEZZA_MINIMA) {
            tieniRemota();
        } else {
            usaLocale();
        }
    };

    probe.onerror = usaLocale;

    window.setTimeout(usaLocale, TIMEOUT_MS);

    probe.src = REMOTE;
})();
