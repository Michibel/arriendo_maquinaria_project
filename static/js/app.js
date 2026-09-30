/**
 * ============================================================================
 * PROYECTO 6: ARRIENDO DE MAQUINARIA DE CONSTRUCCIÓN (RENTING / SERVICIOS)
 * MÓDULO FRONTEND: CLIENTE ES6 Y GESTIÓN DE ESTADO (app.js)
 * Autor: Gabriel Michibel | Sección: IEC-N4-C1 | Año: 2026
 * ============================================================================
 * Este archivo implementa:
 * 1. Gestión transparente de tokens JWT (Storage, Inyección de Bearer Header)
 * 2. Control de estado de sesión y reactividad del Navbar según rol RBAC
 * 3. Cliente HTTP Fetch con interceptores de autenticación y refresco
 * 4. Sistema de feedback visual en tiempo real (Bootstrap 5 Toasts)
 * 5. Cálculo dinámico de tarifas, días de uso y garantías para arriendos
 * 6. Actualización reactiva del contador del Carro Persistente
 * ============================================================================
 */

// Claves de almacenamiento local (localStorage)
const STORAGE_ACCESS_TOKEN = 'rentamaq_access_token';
const STORAGE_REFRESH_TOKEN = 'rentamaq_refresh_token';
const STORAGE_USER_DATA = 'rentamaq_user_data';
const STORAGE_GUEST_CART = 'rentamaq_guest_cart';

// ============================================================================
// BLOQUE 1: UTILIDADES DE AUTENTICACIÓN Y ALMACENAMIENTO (JWT & RBAC)
// ============================================================================
const Auth = {
  getAccessToken() {
    return localStorage.getItem(STORAGE_ACCESS_TOKEN);
  },

  getRefreshToken() {
    return localStorage.getItem(STORAGE_REFRESH_TOKEN);
  },

  getUser() {
    try {
      const data = localStorage.getItem(STORAGE_USER_DATA);
      return data ? JSON.parse(data) : null;
    } catch (e) {
      return null;
    }
  },

  setAuth(tokens, usuario) {
    if (tokens.access) localStorage.setItem(STORAGE_ACCESS_TOKEN, tokens.access);
    if (tokens.refresh) localStorage.setItem(STORAGE_REFRESH_TOKEN, tokens.refresh);
    if (usuario) localStorage.setItem(STORAGE_USER_DATA, JSON.stringify(usuario));
    this.syncNavbarUI();
  },

  clearAuth() {
    localStorage.removeItem(STORAGE_ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_REFRESH_TOKEN);
    localStorage.removeItem(STORAGE_USER_DATA);
    this.syncNavbarUI();
  },

  isAuthenticated() {
    return !!this.getAccessToken();
  },

  isEjecutivo() {
    const user = this.getUser();
    return user && (user.rol === 'EJECUTIVO_ARRIENDOS' || user.es_ejecutivo);
  },

  isConstructora() {
    const user = this.getUser();
    return user && (user.rol === 'EMPRESA_CONSTRUCTORA' || user.es_constructora);
  },

  /**
   * Sincroniza dinámicamente la interfaz del Navbar según el estado de la sesión
   */
  syncNavbarUI() {
    const user = this.getUser();
    const guestNav = document.getElementById('nav-guest-zone');
    const userNav = document.getElementById('nav-user-zone');
    const userNameSpan = document.getElementById('nav-user-name');
    const userRoleBadge = document.getElementById('nav-user-role');
    const panelEjecutivoLink = document.getElementById('nav-link-panel');
    const misContratosLink = document.getElementById('nav-link-contratos');
    const cartNav = document.getElementById('nav-link-carro');

    if (cartNav) {
      cartNav.style.display = 'block';
    }

    if (user && this.isAuthenticated()) {
      if (guestNav) guestNav.classList.add('d-none');
      if (userNav) userNav.classList.remove('d-none');
      if (userNameSpan) userNameSpan.textContent = user.nombre_completo || user.username;
      
      if (userRoleBadge) {
        userRoleBadge.textContent = user.rol_display || user.rol;
        userRoleBadge.className = user.es_ejecutivo 
          ? 'badge bg-warning text-dark me-2' 
          : 'badge bg-info text-dark me-2';
      }

      if (panelEjecutivoLink) {
        panelEjecutivoLink.style.display = this.isEjecutivo() ? 'block' : 'none';
      }
      if (misContratosLink) {
        misContratosLink.style.display = 'block';
      }
    } else {
      if (guestNav) guestNav.classList.remove('d-none');
      if (userNav) userNav.classList.add('d-none');
      if (panelEjecutivoLink) panelEjecutivoLink.style.display = 'none';
      if (misContratosLink) misContratosLink.style.display = 'none';
    }

    Cart.syncCounter();
  }
};

// ============================================================================
// BLOQUE 2: CLIENTE HTTP CON BEARER TOKEN AUTOMÁTICO
// ============================================================================
async function apiFetch(endpoint, options = {}) {
  const url = endpoint.startsWith('http') ? endpoint : `/api${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  const token = Auth.getAccessToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, { ...options, headers });

  // Manejo de token expirado o no autorizado
  if (response.status === 401) {
    console.warn("Token JWT expirado o no autorizado.");
    // Si no estamos en la página de login, limpiar y actualizar UI
    if (!window.location.pathname.includes('/login/')) {
      Auth.clearAuth();
    }
  }

  return response;
}

// ============================================================================
// BLOQUE 3: SISTEMA DE TOASTS VISUALES
// ============================================================================
function showToast(mensaje, tipo = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const bgClass = {
    success: 'bg-success text-white',
    danger: 'bg-danger text-white',
    warning: 'bg-warning text-dark',
    info: 'bg-info text-dark'
  }[tipo] || 'bg-dark text-white';

  const toastId = 'toast_' + Date.now();
  const html = `
    <div id="${toastId}" class="toast align-items-center ${bgClass} border-0 shadow-lg" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body fw-bold">
          ${mensaje}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;

  container.insertAdjacentHTML('beforeend', html);
  const element = document.getElementById(toastId);
  const toast = new bootstrap.Toast(element, { delay: 4000 });
  toast.show();
  element.addEventListener('hidden.bs.toast', () => element.remove());
}

// ============================================================================
// BLOQUE 4: FORMATEADORES DE MONEDA Y FECHAS
// ============================================================================
function formatCLP(valor) {
  const numero = Number(valor) || 0;
  return '$' + Math.round(numero).toLocaleString('es-CL');
}

function formatDate(fechaStr) {
  if (!fechaStr) return '';
  const parts = fechaStr.split('-');
  if (parts.length === 3) {
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
  }
  return fechaStr;
}

// ============================================================================
// BLOQUE 5: GESTOR DEL CARRO DE ARRIENDO (Cart Manager)
// ============================================================================
const Cart = {
  getGuestCart() {
    try {
      const data = localStorage.getItem(STORAGE_GUEST_CART);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      return [];
    }
  },

  setGuestCart(items) {
    localStorage.setItem(STORAGE_GUEST_CART, JSON.stringify(items));
    this.syncCounter();
  },

  clearGuestCart() {
    localStorage.removeItem(STORAGE_GUEST_CART);
    this.syncCounter();
  },

  async syncCounter() {
    const badge = document.getElementById('cart-counter-badge');
    if (!badge) return;

    if (Auth.isAuthenticated()) {
      try {
        const resp = await apiFetch('/carro-arriendo/');
        if (resp.ok) {
          const data = await resp.json();
          badge.textContent = data.total_items || 0;
        }
      } catch (e) {
        console.error("Error sincronizando contador del carro:", e);
      }
    } else {
      const items = this.getGuestCart();
      badge.textContent = items.length;
    }
  },

  async addItem(maquinariaId, fechaInicio, fechaFin, maquinariaObj = null) {
    if (Auth.isAuthenticated()) {
      try {
        const resp = await apiFetch('/carro-arriendo/', {
          method: 'POST',
          body: JSON.stringify({
            maquinaria_id: maquinariaId,
            fecha_inicio: fechaInicio,
            fecha_fin: fechaFin
          })
        });

        const data = await resp.json();

        if (resp.ok) {
          showToast(data.mensaje || "Equipo agregado al carro persistente.", "success");
          this.syncCounter();
          return true;
        } else {
          const errorMsg = data.error || data.detail || (data.maquinaria_id ? data.maquinaria_id[0] : null) || "No se pudo agregar al carro.";
          showToast(errorMsg, "danger");
          return false;
        }
      } catch (e) {
        showToast("Error de conexión al agregar al carro.", "danger");
        return false;
      }
    } else {
      // MODO INVITADO: Carro TEMPORAL no persistente
      let items = this.getGuestCart();
      const fIni = new Date(fechaInicio);
      const fFin = new Date(fechaFin);
      const dias = Math.max(1, Math.ceil((fFin - fIni) / (1000 * 60 * 60 * 24)));
      const tarifa = Number(maquinariaObj ? maquinariaObj.tarifa_diaria : 0);
      const garantia = Number(maquinariaObj ? maquinariaObj.garantia_fija : 0);
      const subtotalTarifas = tarifa * dias;
      const costoCalculado = subtotalTarifas + garantia;

      const idxExistente = items.findIndex(it => it.maquinaria_id === maquinariaId);
      if (idxExistente >= 0) {
        items[idxExistente].fecha_inicio = fechaInicio;
        items[idxExistente].fecha_fin = fechaFin;
        items[idxExistente].dias_uso = dias;
        items[idxExistente].costo_calculado = costoCalculado;
        showToast(`Arriendo de '${maquinariaObj ? maquinariaObj.nombre : 'Equipo'}' actualizado en tu carro temporal.`, "info");
      } else {
        items.push({
          id: Date.now(), // ID temporal local
          maquinaria_id: maquinariaId,
          maquinaria: maquinariaObj || { id: maquinariaId, nombre: 'Maquinaria', tarifa_diaria: tarifa, garantia_fija: garantia },
          fecha_inicio: fechaInicio,
          fecha_fin: fechaFin,
          dias_uso: dias,
          costo_calculado: costoCalculado
        });
        showToast(`'${maquinariaObj ? maquinariaObj.nombre : 'Equipo'}' agregado a tu carro temporal de invitado.`, "success");
      }

      this.setGuestCart(items);
      return true;
    }
  },

  async removeItem(itemId) {
    if (Auth.isAuthenticated()) {
      try {
        const resp = await apiFetch(`/carro-arriendo/${itemId}/`, {
          method: 'DELETE'
        });
        if (resp.ok) {
          showToast("Equipo eliminado del carro.", "info");
          this.syncCounter();
          return true;
        } else {
          showToast("No se pudo eliminar el ítem.", "danger");
          return false;
        }
      } catch (e) {
        showToast("Error de conexión al eliminar del carro.", "danger");
        return false;
      }
    } else {
      let items = this.getGuestCart();
      items = items.filter(it => it.id !== itemId);
      this.setGuestCart(items);
      showToast("Equipo eliminado del carro temporal.", "info");
      return true;
    }
  }
};

// ============================================================================
// BLOQUE 6: INICIALIZACIÓN GLOBAL AL CARGAR EL DOM
// ============================================================================
document.addEventListener('DOMContentLoaded', () => {
  // Sincronizar estado visual de autenticación
  Auth.syncNavbarUI();

  // Configurar botón global de logout si existe
  const btnLogout = document.getElementById('btn-logout');
  if (btnLogout) {
    btnLogout.addEventListener('click', (e) => {
      e.preventDefault();
      Auth.clearAuth();
      showToast("Has cerrado sesión correctamente.", "info");
      setTimeout(() => {
        window.location.href = '/';
      }, 800);
    });
  }
});
