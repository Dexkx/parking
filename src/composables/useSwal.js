import Swal from 'sweetalert2'

const darkBase = {
  background: '#161922',
  color: '#eef0f5',
  confirmButtonColor: '#00e5b0',
  cancelButtonColor: '#374151',
}

export function useSwal() {
  function confirmAction(title, text, confirmText = 'Confirmar') {
    return Swal.fire({
      ...darkBase,
      title: `<span style="font-family:Syne;font-weight:800;font-size:18px">${title}</span>`,
      html: `<span style="color:#8b92a8;font-size:14px">${text}</span>`,
      showCancelButton: true,
      confirmButtonText: confirmText,
      cancelButtonText: 'Cancelar',
    })
  }

  function showTicket(reserva) {
    const fmt = (iso) => new Date(iso).toLocaleString('es-CO', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })
    return Swal.fire({
      ...darkBase,
      title: '<span style="font-family:Syne;font-weight:800;font-size:18px">Ticket de Reserva</span>',
      html: `
        <div style="font-family:'DM Sans';text-align:left;background:#0f1117;padding:16px;border-radius:12px;border:1px solid rgba(255,255,255,0.07)">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
            <div><div style="font-size:10px;color:#4e5568;letter-spacing:.08em;margin-bottom:4px">PARQUEADERO</div>
              <div style="color:#eef0f5;font-weight:600;font-size:13px">${reserva.negocio ?? '—'}</div></div>
            <div><div style="font-size:10px;color:#4e5568;letter-spacing:.08em;margin-bottom:4px">PLACA</div>
              <div style="color:#00e5b0;font-weight:800;font-size:20px;font-family:Syne">${reserva.placa ?? '—'}</div></div>
            <div><div style="font-size:10px;color:#4e5568;letter-spacing:.08em;margin-bottom:4px">PISO / PUESTO</div>
              <div style="color:#eef0f5;font-weight:600">Piso ${reserva.piso ?? '—'} · #${reserva.numero ?? '—'}</div></div>
            <div><div style="font-size:10px;color:#4e5568;letter-spacing:.08em;margin-bottom:4px">ESTADO</div>
              <div style="color:#00e5b0;font-weight:600">${reserva.status ?? 'Activa'}</div></div>
            <div><div style="font-size:10px;color:#4e5568;letter-spacing:.08em;margin-bottom:4px">ENTRADA</div>
              <div style="color:#eef0f5;font-size:13px">${fmt(reserva.hf_inicio)}</div></div>
            <div><div style="font-size:10px;color:#4e5568;letter-spacing:.08em;margin-bottom:4px">SALIDA</div>
              <div style="color:#eef0f5;font-size:13px">${fmt(reserva.hf_final)}</div></div>
          </div>
          <div style="margin-top:16px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.07);display:flex;justify-content:space-between;align-items:center">
            <div style="font-size:11px;color:#4e5568;letter-spacing:.06em">TOTAL PAGADO</div>
            <div style="font-family:Syne;font-weight:800;font-size:22px;color:#00e5b0">
              $${Number(reserva.valor_pagado ?? 0).toLocaleString('es-CO')}
            </div>
          </div>
        </div>`,
      confirmButtonText: 'Cerrar',
    })
  }

  return { confirmAction, showTicket }
}
