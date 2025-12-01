# 📱 Arquivos PWA - IASenior

Este diretório contém os arquivos necessários para o Progressive Web App (PWA).

## Arquivos

- `manifest.json` - Manifest do PWA
- `service-worker.js` - Service Worker para cache e notificações
- `pwa-install.js` - Script para instalação do PWA
- `icon-192.png` - Ícone 192x192 (criar)
- `icon-512.png` - Ícone 512x512 (criar)

## Criar Ícones

Para criar os ícones, você pode:

1. **Usar um gerador online**: https://www.pwabuilder.com/imageGenerator
2. **Criar manualmente**: Use um editor de imagens para criar ícones 192x192 e 512x512
3. **Usar um ícone existente**: Converta uma imagem para os tamanhos necessários

O ícone deve representar o sistema de monitoramento (ex: escudo, olho, etc).

## Configuração do Streamlit

Para servir arquivos estáticos no Streamlit, você precisa configurar o servidor para servir a pasta `static/`.

### Opção 1: Usar Streamlit com arquivos estáticos

O Streamlit serve automaticamente arquivos da pasta `.streamlit/static/` ou você pode usar um servidor web adicional.

### Opção 2: Integrar no dashboard

Os arquivos já estão integrados no dashboard através de tags HTML no código.

## Testar PWA

1. Abra o dashboard no navegador
2. Abra DevTools (F12)
3. Vá em "Application" > "Service Workers"
4. Verifique se o Service Worker está registrado
5. Vá em "Application" > "Manifest"
6. Verifique se o manifest está carregado
7. Procure pelo botão "Instalar App" no navegador

## Notas

- O PWA funciona melhor em HTTPS (necessário para Service Workers em produção)
- Para desenvolvimento local, use `localhost` (aceita Service Workers)
- Notificações push requerem HTTPS e permissão do usuário

