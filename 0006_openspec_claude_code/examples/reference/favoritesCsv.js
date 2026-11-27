const fields = ['titulo', 'link', 'fonte'];

function quoteCell(value) {
  const raw = String(value ?? '');
  const safe = /^[\s\u0000-\u001f]*[=+@-]/u.test(raw) ? "'" + raw : raw;
  return '"' + safe.replaceAll('"', '""') + '"';
}

export function serializeFavorites(articles) {
  const rows = articles.map((article) => fields.map((field) => quoteCell(article[field])).join(','));
  return [fields.join(','), ...rows].join('\r\n') + '\r\n';
}
