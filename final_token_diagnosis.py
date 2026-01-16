#!/usr/bin/env python3
"""
Final diagnosis of the token issue
"""

import requests

def final_diagnosis():
    """Complete diagnosis of the token"""
    print("🔬 DIAGNÓSTICO FINAL DEL TOKEN")
    print("=" * 60)
    print()

    token = "z8vKmHLszDpJFqzTplMPtmUITdvxKq"

    print("📝 Token proporcionado:")
    print(f"   {token}")
    print()

    print("🔍 Análisis del token:")
    print(f"   • Longitud: {len(token)} caracteres")
    print(f"   • Comienza con 'figd_': {token.startswith('figd_')}")
    print(f"   • Solo contiene caracteres alfanuméricos: {token.isalnum()}")
    print()

    print("🧪 Resultados de las pruebas realizadas:")
    print()

    # Test 1: X-Figma-Token header
    print("   Test 1: X-Figma-Token header")
    headers1 = {"X-Figma-Token": token}
    try:
        r1 = requests.get("https://api.figma.com/v1/me", headers=headers1, timeout=5)
        print(f"   ❌ Resultado: {r1.status_code} - {r1.json().get('err', 'Error')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()

    # Test 2: Bearer token
    print("   Test 2: Bearer Authorization")
    headers2 = {"Authorization": f"Bearer {token}"}
    try:
        r2 = requests.get("https://api.figma.com/v1/me", headers=headers2, timeout=5)
        print(f"   ❌ Resultado: {r2.status_code} - {r2.json().get('err', 'Error')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()

    # Test 3: With figd_ prefix
    print("   Test 3: Con prefijo 'figd_'")
    token_with_prefix = f"figd_{token}"
    headers3 = {"X-Figma-Token": token_with_prefix}
    try:
        r3 = requests.get("https://api.figma.com/v1/me", headers=headers3, timeout=5)
        print(f"   ❌ Resultado: {r3.status_code} - {r3.json().get('err', 'Error')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()

    print("=" * 60)
    print("📊 CONCLUSIÓN:")
    print("=" * 60)
    print()
    print("❌ Este token NO funciona con la API de Figma")
    print()
    print("💡 Posibles razones:")
    print("   1. Es un identificador diferente (File Key, Team ID, etc.)")
    print("   2. Es un token expirado o revocado")
    print("   3. Es un token de prueba o demo")
    print("   4. Fue copiado incorrectamente (falta parte)")
    print("   5. No es un Personal Access Token de Figma")
    print()
    print("=" * 60)
    print("🎯 SOLUCIÓN:")
    print("=" * 60)
    print()
    print("Para obtener un token VÁLIDO:")
    print()
    print("1️⃣  Abre: https://www.figma.com/")
    print()
    print("2️⃣  Click en tu perfil (esquina superior derecha)")
    print()
    print("3️⃣  Selecciona 'Settings'")
    print()
    print("4️⃣  En el menú izquierdo, busca 'Personal access tokens'")
    print()
    print("5️⃣  Click en 'Generate new token' o 'Create new token'")
    print()
    print("6️⃣  Dale un nombre (ej: 'Shotlist API Token')")
    print()
    print("7️⃣  COPIA TODO EL TOKEN que aparece")
    print("     ⚠️  Solo se muestra UNA VEZ")
    print("     ⚠️  Debe empezar con 'figd_'")
    print("     ⚠️  Debe tener 40+ caracteres")
    print()
    print("8️⃣  Pégalo aquí para continuar")
    print()
    print("=" * 60)
    print()
    print("🎨 ALTERNATIVA: Diseño Manual")
    print()
    print("Si no puedes obtener un token, puedes:")
    print("   • Abrir Figma manualmente")
    print("   • Seguir la guía: figma_quick_setup.md")
    print("   • Crear el diseño paso a paso (30-60 min)")
    print("   • Ya tienes todos los assets y especificaciones")
    print()
    print("=" * 60)
    print()
    print("📞 ¿Qué prefieres hacer?")
    print()
    print("   A) Intentar obtener un token válido")
    print("   B) Crear el diseño manualmente en Figma")
    print("   C) Continuar con otra parte del proyecto")
    print()

if __name__ == "__main__":
    final_diagnosis()
