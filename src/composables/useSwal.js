/**
 * composables/useSwal.js
 * Composable que envuelve SweetAlert2 con el tema dark de ParkApp.
 * 
 * Uso:
 *   const { confirmAction, showTicket, promptReserva } = useSwal()
 */
import Swal from 'sweetalert2'

// Configuración base del tema dark
const darkBase = {
  background: '#161922',
  color: '#eef0f5',
  confirmButtonColor: '#00e5b0',
  cancelButtonColor: '#374151',
  customClass: {
    popup:         'font-body rounded-xl border border-white/10',
    title:         'font-head text-t-primary',
    confirmButton: 'font-head font-bold text-base rounded-sm',
    cancelButton:  'font-body rounded-sm',
  },
}

export function useSwal() {
  /**
   * Diálogo de confirmación genérico
   * @param {string} title
   * @param {string} text
   * @param {string} confirmText
   */
  function confirmAction(title, text, confirmText = 'Confirmar') {
    return Swal.fire({
      ...darkBase,
      title,
      html: `<span style="color:#8b92a8">${text}</span>`,
      showCancelButton: true,
      confirmButtonText: confirmText,
      cancelButtonText: 'Cancelar',
    })
  }

  /**
   * Modal de ticket de reserva
   * @param {Object} reserva
   */
  function showTicket(reserva) {
    const fmt = (iso) => new Date(iso).toLocaleString('es-CO', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })

    return Swal.fire({
      ...darkBase,
      title: '<span style="font-family:Syne;font-weight:800;font-size:20px">Ticket de Reserva</span>',
      html: `
        <div style="font-family:'DM Sans';text-align:left;background:#0f1117;padding:16px;border-radius:12px;border:1px solid rgba(255,255,255,0.07)">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
            <div>
              <div style="font-size:10px;color:#4e5568;letter-spacing:.08em;margin-bottom:4px">PARQUEADERO</div>
              <div style="color:#eef0f5;font-weight:600;font-size:14px">${reserva.negocio ?? '—'}</div>
            </div>
            <div>
              <div style="font-size:10px;color:#4e5568;letter-spacing:.08em;margin-bottom:4px">PLACA</div>
              <div style="color:#00e5b0;font-weight:800;font-size:20px;font-family:Syne">${reserva.placa ?? '—'}</div>
            </div>
            <div>
              <div style="font-size:10px;color:#4e5568;letter-spacing:.08em;margin-bottom:4px">PISO / PUESTO</div>
              <div style="color:#eef0f5;font-weight:600">Piso ${reserva.piso ?? '—'} · #${reserva.numero ?? '—'}</div>
            </div>
            <div>
              <div style="font-size:10px;color:#4e5568;letter-spacing:.08em;margin-bottom:4px">ESTADO</div>
              <div style="color:#00e5b0;font-weight:600">${reserva.status ?? 'Activa'}</div>
            </div>
            <div>
              <div style="font-size:10px;color:#4e5568;letter-spacing:.08em;margin-bottom:4px">ENTRADA</div>
              <div style="color:#eef0f5;font-size:13px">${fmt(reserva.hf_inicio)}</div>
            </div>
            <div>
              <div style="font-size:10px;color:#4e5568;letter-spacing:.08em;margin-bottom:4px">SALIDA</div>
              <div style="color:#eef0f5;font-size:13px">${fmt(reserva.hf_final)}</div>
            </div>
          </div>
          <div style="margin-top:16px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.07);display:flex;justify-content:space-between;align-items:center">
            <div style="font-size:11px;color:#4e5568;letter-spacing:.06em">TOTAL PAGADO</div>
            <div style="font-family:Syne;font-weight:800;font-size:24px;color:#00e5b0">
              $${Number(reserva.valor_pagado ?? 0).toLocaleString('es-CO')}
            </div>
          </div>
        </div>
      `,
      confirmButtonText: 'Cerrar',
    })
  }

  /**
   * Formulario de reserva embebido en SweetAlert
   * @param {Object} negocio
   * @returns {Promise<{placa, tiempo} | null>}
   */
  async function promptReserva(negocio) {
    const { isConfirmed, value } = await Swal.fire({
      ...darkBase,
      title: `<span style="font-family:Syne;font-weight:800;font-size:18px">${negocio.nombre}</span>`,
      html: `
        <div style="font-family:'DM Sans';text-align:left">
          <p style="color:#8b92a8;margin-bottom:16px;font-size:13px">${negocio.direccion ?? ''}</p>

          <label style="font-size:11px;font-weight:500;color:#4e5568;letter-spacing:.08em;display:block;margin-bottom:6px">
            PLACA DEL VEHÍCULO
          </label>
          <input id="swal-placa" maxlength="7" placeholder="Ej: ABC 123"
            style="width:100%;padding:10px 14px;background:#1a1e2a;border:1px solid rgba(255,255,255,0.07);
            border-radius:8px;color:#eef0f5;font-size:15px;font-family:'DM Sans';outline:none;
            letter-spacing:2px;text-transform:uppercase;margin-bottom:14px" />

          <label style="font-size:11px;font-weight:500;color:#4e5568;letter-spacing:.08em;display:block;margin-bottom:6px">
            DURACIÓN DE LA RESERVA
          </label>
          <select id="swal-tiempo"
            style="width:100%;padding:10px 14px;background:#1a1e2a;border:1px solid rgba(255,255,255,0.07);
            border-radius:8px;color:#eef0f5;font-size:14px;font-family:'DM Sans';outline:none">
            <option value="01:00:00">1 hora</option>
            <option value="02:00:00">2 horas</option>
            <option value="04:00:00">4 horas</option>
            <option value="08:00:00">8 horas</option>
          </select>
        </div>
      `,
      showCancelButton: true,
      confirmButtonText: 'Confirmar reserva →',
      cancelButtonText: 'Cancelar',
      preConfirm: () => {
        const placa  = document.getElementById('swal-placa').value.trim().toUpperCase()
        const tiempo = document.getElementById('swal-tiempo').value
        if (!placa) { Swal.showValidationMessage('Ingresa la placa del vehículo'); return false }
        return { placa, tiempo }
      },
    })

    return isConfirmed ? value : null
  }

  return { confirmAction, showTicket, promptReserva }
}
