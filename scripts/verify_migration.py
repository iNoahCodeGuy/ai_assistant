#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify Supabase migrations and test API endpoints.
Run this after applying database migrations.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_header(text):
    print("\n" + "="*60)
    print(text)
    print("="*60 + "\n")

def print_success(text):
    print(Colors.GREEN + "✓" + Colors.NC + " " + text)

def print_error(text):
    print(Colors.RED + "✗" + Colors.NC + " " + text)

def print_warning(text):
    print(Colors.YELLOW + "⚠" + Colors.NC + " " + text)

def check_env_vars():
    """Check if required environment variables are set."""
    print_header("Step 1: Checking Environment Variables")
    
    required_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY']
    all_present = True
    
    for var in required_vars:
        if os.getenv(var):
            print_success("{} is set".format(var))
        else:
            print_error("{} is NOT set".format(var))
            all_present = False
    
    return all_present

def check_table_exists(table_name):
    """Check if a table exists in Supabase."""
    supabase_url = os.getenv('SUPABASE_URL')
    api_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    url = "{}/rest/v1/{}?limit=0".format(supabase_url, table_name)
    headers = {
        'apikey': api_key,
        'Authorization': 'Bearer {}'.format(api_key)
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print_error("Error checking {}: {}".format(table_name, str(e)))
        return False

def check_tables():
    """Check if all required tables exist."""
    print_header("Step 2: Checking Database Tables")
    
    tables = {
        'kb_chunks': 'Migration 001',
        'messages': 'Migration 001',
        'retrieval_logs': 'Migration 001',
        'links': 'Migration 001',
        'feedback': 'Migration 001',
        'confessions': 'Migration 002',
        'sms_logs': 'Migration 002'
    }
    
    missing_tables = []
    
    for table, migration in tables.items():
        if check_table_exists(table):
            print_success("{} exists ({})".format(table, migration))
        else:
            print_error("{} MISSING (need {})".format(table, migration))
            missing_tables.append((table, migration))
    
    return missing_tables

def test_api_endpoint(name, url, data):
    """Test an API endpoint."""
    try:
        response = requests.post(
            url,
            headers={'Content-Type': 'application/json'},
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                if json_response.get('success'):
                    print_success("{} - Working".format(name))
                    return True
                else:
                    print_warning("{} - Returned success=false".format(name))
                    print("  Response: {}".format(json.dumps(json_response, indent=2)))
                    return False
            except:
                print_success("{} - OK (HTTP 200)".format(name))
                return True
        else:
            print_error("{} - HTTP {}".format(name, response.status_code))
            print("  Response: {}".format(response.text[:200]))
            return False
            
    except Exception as e:
        print_error("{} - Exception: {}".format(name, str(e)))
        return False

def test_endpoints():
    """Test all API endpoints."""
    print_header("Step 3: Testing API Endpoints")
    
    base_url = "https://noahsaiassistant.vercel.app"
    
    endpoints = [
        {
            'name': '/api/chat',
            'url': base_url + '/api/chat',
            'data': {'query': 'test', 'role': 'Just looking around'}
        },
        {
            'name': '/api/confess',
            'url': base_url + '/api/confess',
            'data': {'message': 'Test confession from verification', 'is_anonymous': True}
        },
        {
            'name': '/api/feedback',
            'url': base_url + '/api/feedback',
            'data': {'message_id': 'test', 'rating': 5, 'comment': 'Test', 'contact_requested': False}
        }
    ]
    
    results = []
    for endpoint in endpoints:
        success = test_api_endpoint(endpoint['name'], endpoint['url'], endpoint['data'])
        results.append((endpoint['name'], success))
    
    return results

def main():
    """Main verification flow."""
    print_header("Supabase Migration Verification")
    
    # Step 1: Check environment variables
    if not check_env_vars():
        print_error("\nMissing environment variables. Please check your .env file.")
        return 1
    
    # Step 2: Check tables
    missing_tables = check_tables()
    
    if missing_tables:
        print_warning("\nMissing tables detected!")
        print("\nTo fix, run these migrations in Supabase SQL Editor:")
        print("  https://app.supabase.com → Your Project → SQL Editor\n")
        
        migrations_needed = set([migration for _, migration in missing_tables])
        for migration in sorted(migrations_needed):
            if migration == 'Migration 001':
                print("  1. supabase/migrations/001_initial_schema.sql")
            elif migration == 'Migration 002':
                print("  2. supabase/migrations/002_add_confessions_and_sms.sql")
        
        print("\nAfter running migrations, run this script again to verify.")
        return 1
    
    # Step 3: Test API endpoints
    results = test_endpoints()
    
    # Summary
    print_header("Verification Summary")
    
    all_passing = all([success for _, success in results])
    
    if all_passing:
        print_success("All checks passed! Your deployment is ready.")
        return 0
    else:
        print_warning("Some endpoints are failing. Check the output above for details.")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nVerification cancelled by user.")
        sys.exit(130)
