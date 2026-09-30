"""
================================================================================
CONTEXT PROCESSORS - PROYECTO ARRIENDO DE MAQUINARIA
Inyecta variables globales en todas las plantillas HTML del sistema.
================================================================================
"""

def datos_alumno_footer(request):
    """
    Inyecta los datos de identificación del estudiante y de la evaluación
    para garantizar el cumplimiento estricto del pie de página (footer)
    en todas las vistas del frontend.
    """
    return {
        'ALUMNO_NOMBRE': 'Gabriel Michibel',
        'ALUMNO_SECCION': 'Sección IEC-N4-C1',
        'ALUMNO_ANIO': 'Año 2026',
        'PROYECTO_NOMBRE': 'Proyecto 6: Arriendo de Maquinaria de Construcción',
        'FOOTER_TEXTO': 'Gabriel Michibel | Sección IEC-N4-C1 | Año 2026',
    }
