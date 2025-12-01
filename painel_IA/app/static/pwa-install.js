// Script para instalação do PWA
// Adicionar ao dashboard para permitir instalação

// Registrar Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/service-worker.js')
      .then((registration) => {
        console.log('Service Worker registrado:', registration);
      })
      .catch((error) => {
        console.error('Erro ao registrar Service Worker:', error);
      });
  });
}

// Detectar se pode instalar
let deferredPrompt;
const installButton = document.getElementById('install-pwa-button');

window.addEventListener('beforeinstallprompt', (e) => {
  // Prevenir prompt automático
  e.preventDefault();
  deferredPrompt = e;
  
  // Mostrar botão de instalação
  if (installButton) {
    installButton.style.display = 'block';
  }
});

// Instalar PWA
if (installButton) {
  installButton.addEventListener('click', async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      console.log('Resultado da instalação:', outcome);
      deferredPrompt = null;
      installButton.style.display = 'none';
    }
  });
}

// Detectar se já está instalado
window.addEventListener('appinstalled', () => {
  console.log('PWA instalado com sucesso!');
  if (installButton) {
    installButton.style.display = 'none';
  }
});

