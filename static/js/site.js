document.addEventListener('DOMContentLoaded', () => { const search = document.querySelector('[data-autofocus-search]'); if (search && !search.value) search.focus({preventScroll:true}); });
