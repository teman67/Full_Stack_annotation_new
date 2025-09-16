#!/usr/bin/env python3
"""
Debug script to test database connectivity issues
"""
import os
import socket
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

def test_dns_resolution():
    """Test DNS resolution for the hostname"""
    hostname = "db.toyattjeguduxpiwpzrl.supabase.co"
    print(f"Testing DNS resolution for: {hostname}")
    
    try:
        # Test IPv4
        ipv4_info = socket.getaddrinfo(hostname, 5432, socket.AF_INET)
        print(f"IPv4 addresses: {[info[4][0] for info in ipv4_info]}")
    except socket.gaierror as e:
        print(f"IPv4 resolution failed: {e}")
    
    try:
        # Test IPv6
        ipv6_info = socket.getaddrinfo(hostname, 5432, socket.AF_INET6)
        print(f"IPv6 addresses: {[info[4][0] for info in ipv6_info]}")
    except socket.gaierror as e:
        print(f"IPv6 resolution failed: {e}")

def test_socket_connection():
    """Test raw socket connection"""
    hostname = "db.toyattjeguduxpiwpzrl.supabase.co"
    port = 5432
    
    print(f"\nTesting socket connection to {hostname}:{port}")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((hostname, port))
        if result == 0:
            print("Socket connection successful!")
        else:
            print(f"Socket connection failed with code: {result}")
        sock.close()
    except Exception as e:
        print(f"Socket connection error: {e}")

def test_psycopg2_connection():
    """Test psycopg2 connection"""
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    print(f"\nTesting psycopg2 connection...")
    print(f"Database URL: {database_url}")
    
    try:
        # Parse URL to get components
        parsed = urlparse(database_url)
        print(f"Hostname: {parsed.hostname}")
        print(f"Port: {parsed.port}")
        print(f"Database: {parsed.path[1:]}")  # Remove leading /
        
        conn = psycopg2.connect(database_url)
        print("psycopg2 connection successful!")
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL version: {version[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"psycopg2 connection error: {e}")

def test_alternative_connection_methods():
    """Test alternative connection methods"""
    load_dotenv()
    
    # Get base connection info
    database_url = os.getenv('DATABASE_URL')
    parsed = urlparse(database_url)
    
    # Try different hostnames/approaches
    alternatives = [
        # Try with IPv6 disabled
        f"postgresql://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}/{parsed.path[1:]}?options=-c%20default_transaction_isolation=read_committed",
        # Try with SSL mode specified
        f"postgresql://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}/{parsed.path[1:]}?sslmode=require",
        # Try with connection timeout
        f"postgresql://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}/{parsed.path[1:]}?connect_timeout=10",
    ]
    
    for i, alt_url in enumerate(alternatives, 1):
        print(f"\nTesting alternative connection method {i}:")
        try:
            conn = psycopg2.connect(alt_url)
            print(f"Alternative method {i} successful!")
            conn.close()
            return alt_url
        except Exception as e:
            print(f"Alternative method {i} failed: {e}")
    
    return None

if __name__ == "__main__":
    print("=== Database Connection Debug Tool ===\n")
    
    test_dns_resolution()
    test_socket_connection()
    test_psycopg2_connection()
    
    # If basic connection fails, try alternatives
    working_url = test_alternative_connection_methods()
    if working_url:
        print(f"\n✅ Working connection string found:")
        print(f"DATABASE_URL={working_url}")
    else:
        print(f"\n❌ No working connection method found.")
        print("\nPossible solutions:")
        print("1. Check your internet connection")
        print("2. Verify Supabase project is active")
        print("3. Try connecting from Supabase dashboard")
        print("4. Check if your network/firewall blocks PostgreSQL connections")
        print("5. Try using the Supabase client library instead of direct PostgreSQL")
