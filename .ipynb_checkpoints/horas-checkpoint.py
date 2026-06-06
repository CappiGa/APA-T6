"""
Fichero: horas.py
Alumno: Javier Eduardo Basurto

Módulo de normalización de expresiones horarias en castellano a formato HH:MM.
"""
import re

def normalizaHoras(ficText, ficNorm):
    """
    Lee el fichero de texto ficText, analiza y normaliza las expresiones
    horarias válidas al formato HH:MM, y guarda el resultado en ficNorm.
    """
    
    # Patrón unificado para detectar formatos estándar, h/m, expresiones verbales y modificadores.
    patron_maestro = (
        r'\b\d{1,2}:\d{1,2}\b|'
        r'\b\d{1,2}h(?:\d{1,2}m)?(?:\s+(?:de la mañana|del mediodía|de la tarde|de la noche|de la madrugada))?\b|'
        r'\b\d{1,2}\s+(?:en punto|y cuarto|y media|menos cuarto)(?:\s+(?:de la mañana|del mediodía|de la tarde|de la noche|de la madrugada))?\b|'
        r'\b\d{1,2}\s+(?:de la mañana|del mediodía|de la tarde|de la noche|de la madrugada)\b'
    )

    def obtener_h24_modificador(h, mod):
        """Valida y convierte la hora basándose en su modificador contextual."""
        if not (1 <= h <= 12):
            return None
        
        if mod == 'de la mañana' and (4 <= h <= 12):
            return 12 if h == 12 else h
        elif mod == 'del mediodía' and (h == 12 or 1 <= h <= 3):
            return 12 if h == 12 else h + 12
        elif mod == 'de la tarde' and (3 <= h <= 8):
            return h + 12
        elif mod == 'de la noche' and (8 <= h <= 12 or 1 <= h <= 4):
            if 8 <= h <= 11:
                return h + 12
            elif h == 12:
                return 0
            return h
        elif mod == 'de la madrugada' and (1 <= h <= 6):
            return h
        return None

    def procesar_match(match):
        cadena = match.group(0)
        
        # Formato 1: HH:MM estándar
        m1 = re.match(r'^(\d{1,2}):(\d{1,2})$', cadena)
        if m1:
            h_str, m_str = m1.groups()
            if len(m_str) != 2:  # Minutos deben tener obligatoriamente dos dígitos
                return cadena
            h, m = int(h_str), int(m_str)
            if 0 <= h <= 23 and 0 <= m <= 59:
                return f"{h:02d}:{m:02d}"
            return cadena

        # Formato 2: XhYm o Xh con modificador opcional
        m2 = re.match(r'^(\d{1,2})h(?:(\d{1,2})m)?(?:\s+(de la mañana|del mediodía|de la tarde|de la noche|de la madrugada))?$', cadena)
        if m2:
            h_str, m_str, mod = m2.groups()
            h = int(h_str)
            m = int(m_str) if m_str else 0
            if not (0 <= m <= 59):
                return cadena
            
            if mod:
                h_24 = obtener_h24_modificador(h, mod)
                if h_24 is None:
                    return cadena
                h = h_24
            else:
                if not (0 <= h <= 23):
                    return cadena
            return f"{h:02d}:{m:02d}"

        # Formato 3: Expresión verbal (en punto, y media...) con modificador opcional
        m3 = re.match(r'^(\d{1,2})\s+(en punto|y cuarto|y media|menos cuarto)(?:\s+(de la mañana|del mediodía|de la tarde|de la noche|de la madrugada))?$', cadena)
        if m3:
            h_str, verbal, mod = m3.groups()
            h = int(h_str)
            if not (1 <= h <= 12):
                return cadena
            
            # Obtener base de 24 horas antes del ajuste verbal
            if mod:
                h_24 = obtener_h24_modificador(h, mod)
                if h_24 is None:
                    return cadena
            else:
                # Por defecto sistema de 12 horas (00:00 a 11:59)
                h_24 = 0 if h == 12 else h

            # Aplicar diferencias de minutos y desfases de hora (ej: menos cuarto)
            if verbal == 'en punto':
                m = 0
                h_final = h_24
            elif verbal == 'y cuarto':
                m = 15
                h_final = h_24
            elif verbal == 'y media':
                m = 30
                h_final = h_24
            elif verbal == 'menos cuarto':
                m = 45
                h_final = (h_24 - 1) % 24
            
            return f"{h_final:02d}:{m:02d}"

        # Formato 4: Dígito simple + Modificador directo (ej: 12 de la noche)
        m4 = re.match(r'^(\d{1,2})\s+(de la mañana|del mediodía|de la tarde|de la noche|de la madrugada)$', cadena)
        if m4:
            h_str, mod = m4.groups()
            h = int(h_str)
            h_24 = obtener_h24_modificador(h, mod)
            if h_24 is not None:
                return f"{h_24:02d}:00"
            return cadena

        return cadena

    # Procesamiento síncrono línea por línea preservando la estructura del texto
    with open(ficText, 'r', encoding='utf-8') as f_entrada, open(ficNorm, 'w', encoding='utf-8') as f_salida:
        for linea in f_entrada:
            linea_normalizada = re.sub(patron_maestro, procesar_match, linea)
            f_salida.write(linea_normalizada)