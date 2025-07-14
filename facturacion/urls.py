from django.urls import path
from facturacion.views.emitir_comprobante import EmitirComprobanteView, EmitirComprobantePorTipoView

urlpatterns = [
    # Ruta general por defecto (venta gravada)
    path('emitir/', EmitirComprobanteView.as_view(), name='emitir_comprobante'),

    # Rutas específicas por tipo de operación
    path('emitir/ventaExonerada/', EmitirComprobantePorTipoView.as_view(), {'tipo_operacion': 'ventaExonerada'}, name='emitir_exonerada'),
    path('emitir/ventaConPercepcion/', EmitirComprobantePorTipoView.as_view(), {'tipo_operacion': 'ventaConPercepcion'}, name='emitir_percepcion'),
    path('emitir/transferenciaGratuita/', EmitirComprobantePorTipoView.as_view(), {'tipo_operacion': 'transferenciaGratuita'}, name='emitir_gratuita'),
    path('emitir/ventaConBonificaciones/', EmitirComprobantePorTipoView.as_view(), {'tipo_operacion': 'ventaConBonificaciones'}, name='emitir_bonificaciones'),
    path('emitir/ventaCredito/', EmitirComprobantePorTipoView.as_view(), {'tipo_operacion': 'ventaCredito'}, name='emitir_credito'),
]
