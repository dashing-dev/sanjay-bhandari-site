(function () {
  var toggle = document.getElementById('navToggle');
  var list = document.getElementById('navList');
  if (toggle && list) {
    toggle.addEventListener('click', function () {
      var open = list.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  var chips = document.querySelectorAll('.filter-chip');
  var rows = document.querySelectorAll('#workList .work-row');
  if (chips.length && rows.length) {
    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        chips.forEach(function (c) { c.classList.remove('is-active'); });
        chip.classList.add('is-active');
        var tag = chip.getAttribute('data-tag');
        rows.forEach(function (row) {
          var tags = (row.getAttribute('data-tags') || '').split(',');
          row.style.display = (tag === 'all' || tags.indexOf(tag) !== -1) ? '' : 'none';
        });
      });
    });
  }
})();
