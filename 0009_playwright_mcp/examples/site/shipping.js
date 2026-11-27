const form = document.querySelector('form');
const status = document.querySelector('[role="status"]');

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const postalCode = new FormData(form).get('postal-code').trim();
  const isValid = /^\d{5}-?\d{3}$/.test(postalCode);
  status.textContent = isValid ? 'Frete simulado: R$ 12,00' : 'Informe um CEP com 8 dígitos.';
});
