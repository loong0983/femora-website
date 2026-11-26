/* FEMORA — skrip laman */
(function () {
  'use strict';

  // Menu mudah alih
  var suis = document.querySelector('.nav-suis');
  var nav = document.getElementById('nav');
  if (suis && nav) {
    suis.addEventListener('click', function () {
      var buka = nav.classList.toggle('buka');
      suis.setAttribute('aria-expanded', buka ? 'true' : 'false');
    });
  }

  // Borang tempahan -> mesej WhatsApp
  var borang = document.getElementById('borang-tempah');
  if (!borang) return;

  var nombor = borang.getAttribute('data-whatsapp') || '';
  var jenama = borang.getAttribute('data-jenama') || 'FEMORA';
  var sedia = document.getElementById('sedia');
  var pratonton = document.getElementById('mesej-pratonton');
  var pautan = document.getElementById('pautan-whatsapp');

  // Pra-pilih pakej daripada pautan (#pakej-2)
  var m = /^#pakej-(\d+)$/.exec(location.hash || '');
  if (m) {
    var r = borang.querySelector('input[name="pakej"][value="' + m[1] + '"]');
    if (r) r.checked = true;
  }

  function nilai(nama) {
    var el = borang.elements[nama];
    return el ? String(el.value || '').trim() : '';
  }

  function semak() {
    var sah = true;
    var pertama = null;
    borang.querySelectorAll('.medan[data-wajib]').forEach(function (medan) {
      var el = medan.querySelector('input, select, textarea');
      var v = String(el.value || '').trim();
      var ok = v.length > 0;
      if (ok && el.name === 'poskod') ok = /^\d{5}$/.test(v);
      if (ok && el.name === 'telefon') ok = /^[0-9+\-\s]{9,15}$/.test(v);
      medan.classList.toggle('tak-sah', !ok);
      el.setAttribute('aria-invalid', ok ? 'false' : 'true');
      if (!ok) { sah = false; if (!pertama) pertama = el; }
    });
    if (pertama) pertama.focus();
    return sah;
  }

  borang.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!semak()) return;

    var pilih = borang.querySelector('input[name="pakej"]:checked');
    var namaPakej = pilih ? pilih.getAttribute('data-nama') : '';
    var harga = pilih ? pilih.getAttribute('data-harga') : '';

    var baris = [
      'Salam, saya nak tempah ' + jenama + '.',
      '',
      'Pakej: ' + namaPakej + (harga ? ' (' + harga + ')' : ''),
      'Nama: ' + nilai('nama'),
      'No. telefon: ' + nilai('telefon'),
      'Alamat: ' + nilai('alamat'),
      'Poskod: ' + nilai('poskod'),
      'Negeri: ' + nilai('negeri')
    ];
    var bayar = nilai('bayaran');
    if (bayar) baris.push('Cara bayar: ' + bayar);
    var catatan = nilai('catatan');
    if (catatan) baris.push('Catatan: ' + catatan);

    var mesej = baris.join('\n');
    var url = 'https://wa.me/' + nombor.replace(/\D/g, '') + '?text=' + encodeURIComponent(mesej);

    pratonton.textContent = mesej;
    pautan.setAttribute('href', url);
    sedia.classList.add('tunjuk');
    sedia.scrollIntoView({ behavior: 'smooth', block: 'center' });

    if (typeof window.fbq === 'function') { try { window.fbq('track', 'Lead'); } catch (err) {} }

    var w = null;
    try { w = window.open(url, '_blank', 'noopener'); } catch (err) {}
    if (!w) pautan.focus();
  });
})();
