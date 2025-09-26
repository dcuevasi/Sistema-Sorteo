#!/usr/bin/env python
"""
Script simple para probar los endpoints de la API del sorteo
"""
import requests
import json

# URL base de la API
BASE_URL = "http://127.0.0.1:8000/api"

def test_contest_stats():
    """Probar endpoint de estadísticas"""
    try:
        response = requests.get(f"{BASE_URL}/stats/")
        print("=== ESTADÍSTICAS DEL CONCURSO ===")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_participant_registration():
    """Probar registro de participante"""
    data = {
        "full_name": "Juan Pérez",
        "email": "juan.perez@example.com",
        "phone": "+56912345678"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register/", json=data)
        print("\n=== REGISTRO DE PARTICIPANTE ===")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json() if response.status_code == 201 else None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_admin_login():
    """Probar login de admin"""
    data = {
        "username": "admin",
        "password": "admincts"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/admin/login/", json=data)
        print("\n=== LOGIN ADMIN ===")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Login exitoso! Token: {result.get('access_token', 'N/A')[:50]}...")
            return result.get('access_token')
        else:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_list_participants(token):
    """Probar listado de participantes (requiere auth)"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/admin/participants/", headers=headers)
        print("\n=== LISTADO DE PARTICIPANTES ===")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎯 PROBANDO API DEL SORTEO SAN VALENTÍN")
    print("=" * 50)
    
    test_contest_stats()
    
    participant_data = test_participant_registration()
    
    admin_token = test_admin_login()

    if admin_token:
        test_list_participants(admin_token)
    
    print("\n Pruebas completadas!")