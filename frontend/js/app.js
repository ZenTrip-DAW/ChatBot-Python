// ── Preloader ──────────────────────────────────────────────────────
(() => {
  const preloader = document.getElementById('appPreloader');
  const pageContent = document.getElementById('pageContent');
  const imageToPreload = './img/silksong.avif';
  let revealed = false;

  function revealPage() {
    if (revealed) return;
    revealed = true;
    document.body.classList.remove('preloading');
    pageContent.classList.remove('page-content-hidden');
    preloader.classList.add('app-preloader-hide');
    setTimeout(() => preloader.remove(), 320);
  }

  const img = new Image();
  img.onload = revealPage;
  img.onerror = revealPage;
  img.src = imageToPreload;

  window.addEventListener('load', () => {
    if (img.complete) revealPage();
  });

  // Fallback de seguridad
  setTimeout(revealPage, 4000);
})();

// ── Gamebot Chat ───────────────────────────────────────────────────
(() => {
  const fab = document.getElementById('gamebotFab');
  const offcanvasEl = document.getElementById('gamebotChat');
  const resizeHandle = document.getElementById('gamebotResizeHandle');
  const bubble = document.getElementById('gamebotBubble');
  const bubbleClose = document.getElementById('gamebotBubbleClose');
  const chatBody = document.getElementById('chatBody');
  if (!fab || !offcanvasEl || !bubble) return;

  const bsOffcanvas = new bootstrap.Offcanvas(offcanvasEl);
  let welcomeSent = false;

  // Doble saltito de atención cada 3 segundos
  function triggerAttentionJump() {
    fab.classList.remove('gamebot-attention-jump');
    void fab.offsetWidth;
    fab.classList.add('gamebot-attention-jump');
    setTimeout(() => fab.classList.remove('gamebot-attention-jump'), 500);
  }

  setInterval(() => {
    if (fab.style.display === 'none') return;
    triggerAttentionJump();
    setTimeout(() => {
      if (fab.style.display === 'none') return;
      triggerAttentionJump();
    }, 550);
  }, 3000);

  // Redimensionado desde la esquina superior izquierda (solo escritorio)
  if (resizeHandle) {
    const desktopMedia = window.matchMedia('(min-width: 992px)');
    const MIN_WIDTH = 320;
    const MIN_HEIGHT = 380;

    function getMaxWidth() {
      return Math.max(MIN_WIDTH, window.innerWidth - 32);
    }

    function getMaxHeight() {
      return Math.max(MIN_HEIGHT, window.innerHeight - 32);
    }

    function clampSize() {
      if (!desktopMedia.matches) {
        offcanvasEl.style.width = '';
        offcanvasEl.style.height = '';
        return;
      }

      if (!offcanvasEl.style.width && !offcanvasEl.style.height) return;

      const currentWidth = parseFloat(offcanvasEl.style.width || `${offcanvasEl.getBoundingClientRect().width}`);
      const currentHeight = parseFloat(offcanvasEl.style.height || `${offcanvasEl.getBoundingClientRect().height}`);

      const nextWidth = Math.min(getMaxWidth(), Math.max(MIN_WIDTH, currentWidth));
      const nextHeight = Math.min(getMaxHeight(), Math.max(MIN_HEIGHT, currentHeight));

      offcanvasEl.style.width = `${Math.round(nextWidth)}px`;
      offcanvasEl.style.height = `${Math.round(nextHeight)}px`;
    }

    function startResize(pointerDownEvent) {
      if (!desktopMedia.matches) return;

      pointerDownEvent.preventDefault();

      const startX = pointerDownEvent.clientX;
      const startY = pointerDownEvent.clientY;
      const startRect = offcanvasEl.getBoundingClientRect();

      offcanvasEl.style.width = `${Math.round(startRect.width)}px`;
      offcanvasEl.style.height = `${Math.round(startRect.height)}px`;

      function handlePointerMove(moveEvent) {
        const dx = moveEvent.clientX - startX;
        const dy = moveEvent.clientY - startY;

        const nextWidth = Math.min(getMaxWidth(), Math.max(MIN_WIDTH, startRect.width - dx));
        const nextHeight = Math.min(getMaxHeight(), Math.max(MIN_HEIGHT, startRect.height - dy));

        offcanvasEl.style.width = `${Math.round(nextWidth)}px`;
        offcanvasEl.style.height = `${Math.round(nextHeight)}px`;
      }

      function stopResize() {
        window.removeEventListener('pointermove', handlePointerMove);
        window.removeEventListener('pointerup', stopResize);
        window.removeEventListener('pointercancel', stopResize);
      }

      window.addEventListener('pointermove', handlePointerMove);
      window.addEventListener('pointerup', stopResize);
      window.addEventListener('pointercancel', stopResize);
    }

    resizeHandle.addEventListener('pointerdown', startResize);
    window.addEventListener('resize', clampSize);

    if (desktopMedia.addEventListener) {
      desktopMedia.addEventListener('change', clampSize);
    } else if (desktopMedia.addListener) {
      desktopMedia.addListener(clampSize);
    }
  }

  function addBotMessage(text, paginacion = null) {
    const msg = document.createElement('div');
    msg.className = 'gamebot-msg-bot d-flex align-items-end gap-2 mb-2';

    const escapeHtml = (value) => (value || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    const downloadMatch = (text || '').match(/\/api\/chat\/historial\/txt\?token=[A-Za-z0-9-]+/);
    const downloadUrl = downloadMatch ? downloadMatch[0] : null;
    const textWithoutDownloadUrl = downloadUrl
      ? (text || '').replace(downloadUrl, '').replace(/\n{3,}/g, '\n\n')
      : (text || '');

    const textFormatted = escapeHtml(textWithoutDownloadUrl)
      .replace(/\n/g, '<br>');

    msg.innerHTML = `
      <img src="./img/Gamebot_rosa.png" class="gamebot-msg-avatar" alt="Gamebot">
      <div class="gamebot-msg-bubble">
        <div class="gamebot-msg-text">${textFormatted}</div>
        ${downloadUrl ? `
          <div class="gamebot-download-wrap mt-2">
            <button type="button" class="btn btn-sm gamebot-download-btn" data-download-url="${downloadUrl}">
              <i class="bi bi-download me-1"></i> Descargar TXT
            </button>
          </div>
        ` : ''}
        ${paginacion && paginacion.activo ? `
          <div class="gamebot-pagination-wrap mt-2">
            <button type="button" class="btn btn-sm gamebot-pagination-btn" title="Mostrar más resultados">
              <i class="bi bi-chevron-down me-1"></i> Más
            </button>
          </div>
        ` : ''}
      </div>`;

    const downloadBtn = msg.querySelector('.gamebot-download-btn');
    if (downloadBtn) {
      downloadBtn.addEventListener('click', async () => {
        const url = downloadBtn.getAttribute('data-download-url');
        if (!url) return;

        const originalText = downloadBtn.innerHTML;
        downloadBtn.disabled = true;
        downloadBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>Descargando...';

        try {
          const response = await fetch(url);
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
          }

          const blob = await response.blob();
          const objectUrl = URL.createObjectURL(blob);
          const fileNameMatch = response.headers.get('content-disposition')?.match(/filename="?([^";]+)"?/i);
          const fileName = fileNameMatch ? fileNameMatch[1] : 'historial.txt';

          const link = document.createElement('a');
          link.href = objectUrl;
          link.download = fileName;
          document.body.appendChild(link);
          link.click();
          link.remove();
          URL.revokeObjectURL(objectUrl);
        } catch (error) {
          console.error('Error descargando historial:', error);
          alert('No se pudo descargar el historial.');
        } finally {
          downloadBtn.disabled = false;
          downloadBtn.innerHTML = originalText;
        }
      });
    }

    const paginationBtn = msg.querySelector('.gamebot-pagination-btn');
    if (paginationBtn && paginacion && paginacion.activo) {
      paginationBtn.addEventListener('click', () => {
        // Usar el offset_siguiente para la siguiente request
        if (lastSearch) {
          lastSearch.offset = paginacion.offset_siguiente;
          sendMessageWithOffset(lastSearch);
        }
      });
    }

    chatBody.appendChild(msg);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  function hideBubble() {
    bubble.classList.remove('gamebot-bubble-show');
    bubble.classList.add('gamebot-bubble-hide');
    setTimeout(() => { bubble.style.display = 'none'; bubble.classList.remove('gamebot-bubble-hide'); }, 300);
  }

  // Mostrar burbuja después de 4 segundos
  const bubbleTimer = setTimeout(() => {
    bubble.style.display = 'flex';
    bubble.classList.add('gamebot-bubble-show');
  }, 4000);

  // Clic en la burbuja → abre el Gamebot
  bubble.addEventListener('click', () => {
    hideBubble();
    bsOffcanvas.show();
  });

  // Cerrar burbuja al pulsar la X (sin abrir el chat)
  bubbleClose.addEventListener('click', (e) => {
    e.stopPropagation();
    hideBubble();
  });

  // Al abrir el chat: ocultar burbuja y mostrar mensaje de bienvenida una sola vez
  offcanvasEl.addEventListener('show.bs.offcanvas', () => {
    clearTimeout(bubbleTimer);
    hideBubble();
    fab.style.display = 'none';
  });

  offcanvasEl.addEventListener('shown.bs.offcanvas', () => {
    if (!welcomeSent) {
      welcomeSent = true;
      setTimeout(() => addBotMessage(
        '¡Hola! 👋 Bienvenido a la tienda de videojuegos.\n\n'
        + 'Soy tu asistente chatbot. Puedo ayudarte a:\n\n'
        + '🎮 Buscar un juego específico\n'
        + '   • "God of War"\n'
        + '   • "¿Cuánto cuesta Fortnite?"\n\n'
        + '💰 Mostrar precios y ofertas\n'
        + '   • "Juegos baratos"\n'
        + '   • "Juegos gratis"\n\n'
        + '🖥️  Listar por plataforma (PS5, Xbox, Switch, PC)\n'
        + '   • "Tienes juegos de PS5?"\n'
        + '   • "Juegos para PC"\n\n'
        + '🏷️  Listar por género (RPG, Acción, Horror, Estrategia...)\n'
        + '   • "Juegos de RPG"\n'
        + '   • "Juegos de horror"\n\n'
        + '¿En qué puedo ayudarte?'
      ), 400);
    }
  });

  offcanvasEl.addEventListener('hidden.bs.offcanvas', () => {
    fab.style.display = '';
  });

  // ── Envío de mensajes ──────────────────────────────────────────────
  const userInput = document.getElementById('userInput');
  const sendBtn   = document.getElementById('sendMsg');
  let sessionToken = localStorage.getItem('gamebot_token') || null;
  let lastSearch = null; // Guardar búsqueda anterior para paginación

  function addUserMessage(text) {
    const msg = document.createElement('div');
    msg.className = 'd-flex justify-content-end mb-2';
    msg.innerHTML = `<div class="gamebot-msg-user">${text}</div>`;
    chatBody.appendChild(msg);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  function addTypingIndicator() {
    const el = document.createElement('div');
    el.className = 'gamebot-msg-bot d-flex align-items-end gap-2 mb-2';
    el.id = 'typingIndicator';
    el.innerHTML = `
      <img src="./img/Gamebot_rosa.png" class="gamebot-msg-avatar" alt="Gamebot">
      <div class="gamebot-msg-bubble">...</div>`;
    chatBody.appendChild(el);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  function removeTypingIndicator() {
    const el = document.getElementById('typingIndicator');
    if (el) el.remove();
  }

  // ── Descargar conversación ──────────────────────────────────────────────
  let interaccionesReales = 0;

  function registrarInteraccionReal() {
    interaccionesReales++;
    document.getElementById('downloadChat')?.classList.remove('d-none');
  }

  function hayConversacion() {
    return interaccionesReales > 0;
  }

  function doDownload() {
    if (!hayConversacion()) {
      alert('No hay conversación para descargar. Escríbeme algo primero.');
      return;
    }
    try {
      const lines = [
        'Conversación con Gamebot',
        'Fecha: ' + new Date().toLocaleString('es-ES'),
        '═'.repeat(60),
        ''
      ];

      document.querySelectorAll('#chatBody > div').forEach(msgDiv => {
        if (msgDiv.id === 'typingIndicator') return;
        const isBot = msgDiv.classList.contains('gamebot-msg-bot');
        const isUser = !!msgDiv.querySelector('.gamebot-msg-user');
        if (isBot) {
          const t = msgDiv.querySelector('.gamebot-msg-text')?.textContent.trim();
          if (t) { lines.push('Gamebot: ' + t); lines.push(''); }
        } else if (isUser) {
          const t = msgDiv.querySelector('.gamebot-msg-user')?.textContent.trim();
          if (t) { lines.push('Tú: ' + t); lines.push(''); }
        }
      });

      lines.push('═'.repeat(60));
      const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'conversacion_gamebot_' + new Date().toISOString().slice(0, 10) + '.txt';
      a.style.display = 'none';
      document.body.appendChild(a);
      a.click();
      setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, 200);
    } catch (e) {
      alert('No se pudo descargar la conversación: ' + e.message);
    }
  }

  document.getElementById('downloadChat')?.addEventListener('click', doDownload);

  function addDownloadBotMessage() {
    const msg = document.createElement('div');
    msg.className = 'gamebot-msg-bot d-flex align-items-end gap-2 mb-2';
    msg.innerHTML = `
      <img src="./img/Gamebot_rosa.png" class="gamebot-msg-avatar" alt="Gamebot">
      <div class="gamebot-msg-bubble">
        <div class="gamebot-msg-text">Aquí tienes tu conversación:</div>
        <div class="gamebot-download-wrap mt-2">
          <button type="button" class="btn btn-sm gamebot-download-btn">
            <i class="bi bi-download me-1"></i> Descargar TXT
          </button>
        </div>
      </div>`;
    msg.querySelector('.gamebot-download-btn').addEventListener('click', doDownload);
    chatBody.appendChild(msg);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  const DOWNLOAD_TRIGGERS = [
    'descargar', 'descarga', 'descargr',           // correcto
    'descragar', 'descagar', 'descarag', 'descargat', // errores tipográficos comunes
    'guardar', 'exportar', 'bajar', 'salvar', 'grabar', 'obtener', 'conseguir',
  ];
  const DOWNLOAD_CONTEXT = ['chat', 'conversacion', 'historial', 'mensajes', 'charla'];

  async function sendMessageWithOffset(searchData) {
    // Enviar request con offset (para botón "+")
    addTypingIndicator();

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          mensaje: searchData.mensaje,
          offset: searchData.offset,
          token: sessionToken
        })
      });
      const data = await res.json();
      sessionToken = data.token;
      localStorage.setItem('gamebot_token', sessionToken);
      removeTypingIndicator();
      addBotMessage(data.respuesta, data.paginacion);
      // Actualizar búsqueda anterior con los datos de la respuesta
      if (data.paginacion) {
        lastSearch = { ...searchData, ...data.paginacion };
      }
    } catch (e) {
      removeTypingIndicator();
      addBotMessage('Lo siento, ha ocurrido un error. Inténtalo de nuevo.');
    }
  }

  async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    const norm = text.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    // Detect download request: trigger word (including typos via regex) + context word
    const hasDownloadTrigger = DOWNLOAD_TRIGGERS.some(t => norm.includes(t))
      || /desc[a-z]*g[a-z]*r/.test(norm);  // catches descragar, descrgr, etc.
    const isDownloadRequest = hasDownloadTrigger
      && (DOWNLOAD_CONTEXT.some(ctx => norm.includes(ctx))
          || norm.trim().split(/\s+/).length <= 2);

    userInput.value = '';
    addUserMessage(text);

    if (isDownloadRequest) {
      if (!hayConversacion()) {
        setTimeout(() => addBotMessage('Todavía no hay conversación para descargar. ¡Pregúntame algo primero!'), 300);
      } else {
        setTimeout(addDownloadBotMessage, 300);
      }
      return;
    }

    registrarInteraccionReal();

    addTypingIndicator();

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ mensaje: text, offset: 0, token: sessionToken })
      });
      const data = await res.json();
      sessionToken = data.token;
      localStorage.setItem('gamebot_token', sessionToken);
      removeTypingIndicator();
      addBotMessage(data.respuesta, data.paginacion);
      // Guardar búsqueda anterior para paginación
      lastSearch = { mensaje: text, offset: 0 };
      if (data.paginacion) {
        lastSearch = { ...lastSearch, ...data.paginacion };
      }
    } catch (e) {
      removeTypingIndicator();
      addBotMessage('Lo siento, ha ocurrido un error. Inténtalo de nuevo.');
    }
  }

  sendBtn.addEventListener('click', sendMessage);
  userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendMessage();
  });

  // Scroll to bottom button (mostrar cuando scrollea hacia arriba)
  const scrollToBottomBtn = document.getElementById('scrollToBottomBtn');

  function updateScrollButtonVisibility() {
    const isAtBottom = chatBody.scrollTop >= chatBody.scrollHeight - chatBody.clientHeight - 50;
    if (isAtBottom) {
      scrollToBottomBtn.classList.add('d-none');
    } else {
      scrollToBottomBtn.classList.remove('d-none');
    }
  }

  chatBody.addEventListener('scroll', updateScrollButtonVisibility);

  scrollToBottomBtn.addEventListener('click', () => {
    chatBody.scrollTo({
      top: chatBody.scrollHeight,
      behavior: 'smooth'
    });
  });

})();
