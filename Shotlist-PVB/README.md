# 🎨 Rebranding: Shotlist → PVB Estudio Creativo

## Resumen de Cambios

Este paquete contiene todos los archivos actualizados para el rebranding de **Shotlist** a **PVB Estudio Creativo**.

---

## 📋 Checklist de Cambios Realizados

### ✅ Identidad de Marca
| Elemento | Antes | Después |
|----------|-------|---------|
| **Nombre** | SHOTLIST | PVB ESTUDIO CREATIVO |
| **Logo texto** | SL●SHOTLIST | PVB●ESTUDIO CREATIVO |
| **Tagline** | Campañas Que Funcionan | Excelencia Visual Sin Perder el Alma |
| **Title HTML** | SHOTLIST - Campañas Que Funcionan | PVB Estudio Creativo - Excelencia Visual Sin Perder el Alma |

### ✅ Paleta de Colores
| Variable CSS | Antes (Rojo) | Después (Charcoal) |
|--------------|--------------|---------------------|
| `--color-dark` | #000000 | **#1A1A1A** (Charcoal Black) |
| `--color-mid` | #808080 | **#6B6B6B** (Slate Gray) |
| `--color-light` | #F5F5F5 | **#F5F5F5** (Soft White) |
| `--primary` | #FF0000 | **#1A1A1A** |
| `--primary-dark` | #CC0000 | **#000000** |

### ✅ Información de Contacto
| Campo | Antes | Después |
|-------|-------|---------|
| **Email** | shotlistmkt@gmail.com | **info@panchovial.com** |
| **Teléfono** | +56 9 8557 8030 | **+56 9 4432 8662** |
| **WhatsApp** | 56985578030 | **56944328662** |

### ✅ Textos Actualizados
- Hero Section: "PVB ESTUDIO CREA CAMPAÑAS QUE FUNCIONAN"
- About Section: Actualizado para reflejar fotografía fine art + marketing digital
- Footer copyright: "© 2025 PVB ESTUDIO CREATIVO"
- WhatsApp widget: Nombre actualizado a "PVB ESTUDIO"

---

## 🚀 Instrucciones de Implementación en Cursor

### Paso 1: Backup (Recomendado)
```bash
cd /Users/franciscovialbrown/Documents/GitHub/Shotlist
git add .
git commit -m "Backup before rebranding"
```

### Paso 2: Reemplazar Archivos
Copia estos archivos al directorio del proyecto:

1. **index.html** → Reemplaza `/Users/franciscovialbrown/Documents/GitHub/Shotlist/index.html`
2. **styles.css** → Reemplaza `/Users/franciscovialbrown/Documents/GitHub/Shotlist/styles.css`

### Paso 3: Verificar otros archivos que puedan contener referencias
Busca y reemplaza en estos archivos si existen:
- `dashboard.html` - Actualizar logo y referencias
- `settings.html` - Actualizar logo y referencias
- `login.html` - Actualizar logo y referencias
- `api_server.py` - Verificar si hay referencias al nombre
- Cualquier archivo `.js` que contenga "SHOTLIST" o "shotlist"

### Paso 4: Comandos de búsqueda útiles en Cursor
```bash
# Buscar todas las referencias a Shotlist
grep -r "SHOTLIST" --include="*.html" --include="*.js" --include="*.css" --include="*.py"
grep -r "shotlist" --include="*.html" --include="*.js" --include="*.css" --include="*.py"

# Buscar el email antiguo
grep -r "shotlistmkt@gmail.com" .

# Buscar el teléfono antiguo
grep -r "8557 8030" .
grep -r "85578030" .
```

### Paso 5: Commit y Push
```bash
git add .
git commit -m "Rebranding: Shotlist → PVB Estudio Creativo"
git push origin main
```

---

## 🌐 Configuración DNS (GoDaddy → GitHub Pages)

Una vez que el código esté actualizado, necesitarás configurar los DNS en GoDaddy:

### Registros DNS Requeridos

| Tipo | Nombre | Valor | TTL |
|------|--------|-------|-----|
| A | @ | 185.199.108.153 | 600 |
| A | @ | 185.199.109.153 | 600 |
| A | @ | 185.199.110.153 | 600 |
| A | @ | 185.199.111.153 | 600 |
| CNAME | www | panchovial-max.github.io | 600 |

### En GitHub (Settings > Pages)
1. Ve a tu repositorio en GitHub
2. Settings > Pages
3. En "Custom domain" escribe: `panchovial.com`
4. Marca "Enforce HTTPS"

---

## 📁 Archivos Incluidos

```
pvb-estudio-creativo/
├── index.html          # Página principal actualizada
├── styles.css          # Estilos con nueva paleta de colores
└── README.md           # Este archivo
```

---

## 🎨 Vista Previa de la Nueva Paleta

```
┌─────────────────────────────────────────┐
│  CHARCOAL BLACK (#1A1A1A)               │
│  ████████████████████████████████████   │
│  Uso: Textos, botones, fondos oscuros   │
├─────────────────────────────────────────┤
│  SLATE GRAY (#6B6B6B)                   │
│  ████████████████████████████████████   │
│  Uso: Textos secundarios, bordes        │
├─────────────────────────────────────────┤
│  SOFT WHITE (#F5F5F5)                   │
│  ████████████████████████████████████   │
│  Uso: Fondos claros, cards              │
└─────────────────────────────────────────┘
```

---

## ⚠️ Notas Importantes

1. **Video de fondo**: El archivo `hero-video.mp4` no se modificó. Considera actualizarlo con contenido de PVB Estudio.

2. **Favicon**: Necesitarás crear un nuevo favicon con el logo PVB.

3. **Open Graph / Meta tags**: Considera agregar meta tags para redes sociales:
```html
<meta property="og:title" content="PVB Estudio Creativo">
<meta property="og:description" content="Excelencia visual sin perder el alma">
<meta property="og:image" content="URL_DE_TU_IMAGEN">
```

4. **Google Analytics**: Si tienes tracking, asegúrate de actualizar el ID.

---

## 📞 Contacto

**PVB Estudio Creativo**
- Email: info@panchovial.com
- Teléfono: +56 9 4432 8662
- Web: panchovial.com

---

*Generado por Claude - Enero 2025*
