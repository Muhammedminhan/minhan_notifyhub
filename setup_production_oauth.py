#!/usr/bin/env python
"""
Setup OAuth2 Application in Production Database

This script should be run on your production server (Cloud Run instance)
to create the OAuth application with the exact same credentials you gave
to the frontend team.

Usage:
    python setup_production_oauth.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reminder_app.settings')
django.setup()

from oauth2_provider.models import Application
from django.contrib.auth import get_user_model

# The credentials you already gave to the frontend team
FRONTEND_CLIENT_ID = "N2xGLLGM8zDEiHeFei4gCk1pYMtTns4xJT9ad2gh"
FRONTEND_CLIENT_SECRET = "CrFKIrRygPpt1WLQvTZ60K2_LJdz7oeKyyH58HRvz7KXhURIHbMfoA"

def setup_production_oauth():
    print("🔧 Setting Up OAuth2 Application in Production")
    print("=" * 70)
    
    User = get_user_model()
    
    # Get the first superuser or create a system user
    user = User.objects.filter(is_superuser=True).first()
    
    if not user:
        print("⚠️  No superuser found. Creating system user...")
        user = User.objects.create_user(
            username='system',
            email='system@notifyhub.local',
            password='system_password_change_me',
            is_superuser=True,
            is_staff=True
        )
        print(f"✓ Created system user: {user.username}")
    else:
        print(f"✓ Using existing user: {user.username}")
    
    # Check if the application already exists
    app = Application.objects.filter(client_id=FRONTEND_CLIENT_ID).first()
    
    if app:
        print(f"\n⚠️  OAuth application already exists!")
        print(f"   Name: {app.name}")
        print(f"   Client ID: {app.client_id}")
        print(f"   Client Type: {app.client_type}")
        print(f"\n   Do you want to update it? (y/N): ", end='')
        
        # In production, auto-confirm
        if os.environ.get('AUTO_CONFIRM', 'false').lower() == 'true':
            response = 'y'
            print('y (auto-confirmed)')
        else:
            response = input()
        
        if response.lower() != 'y':
            print("\n❌ Cancelled")
            return
        
        # Update existing app
        app.name = "NotifyHub Frontend"
        app.client_type = Application.CLIENT_PUBLIC  # Public client for SPA
        app.authorization_grant_type = Application.GRANT_PASSWORD
        app.client_secret = FRONTEND_CLIENT_SECRET  # Will be hashed automatically
        app.user = user
        app.skip_authorization = True
        app.save()
        
        print("\n✅ OAuth application updated successfully!")
    else:
        # Create new application with the exact credentials
        app = Application.objects.create(
            name="NotifyHub Frontend",
            client_id=FRONTEND_CLIENT_ID,
            client_secret=FRONTEND_CLIENT_SECRET,  # Will be hashed automatically
            client_type=Application.CLIENT_PUBLIC,  # Public client for SPA
            authorization_grant_type=Application.GRANT_PASSWORD,
            user=user,
            skip_authorization=True,
        )
        print(f"\n✅ OAuth application created successfully!")
    
    print("\n" + "=" * 70)
    print("📋 Application Details:")
    print("=" * 70)
    print(f"\nName: {app.name}")
    print(f"Client ID: {app.client_id}")
    print(f"Client Secret (raw): {FRONTEND_CLIENT_SECRET}")
    print(f"Client Type: {app.client_type}")
    print(f"Grant Type: {app.authorization_grant_type}")
    print(f"Skip Authorization: {app.skip_authorization}")
    
    print("\n" + "=" * 70)
    print("✅ PRODUCTION SETUP COMPLETE!")
    print("=" * 70)
    
    print("\n📝 The frontend team can now use:")
    print(f"\n   Client ID: {FRONTEND_CLIENT_ID}")
    print(f"   Client Secret: {FRONTEND_CLIENT_SECRET}")
    print(f"\n   (No changes needed - these are the same credentials you already gave them)")
    
    # Test the setup
    print("\n" + "=" * 70)
    print("🧪 Testing OAuth Configuration...")
    print("=" * 70)
    
    # Verify the app can be retrieved
    test_app = Application.objects.filter(client_id=FRONTEND_CLIENT_ID).first()
    if test_app:
        print(f"\n✓ Application found in database")
        print(f"✓ Client ID matches: {test_app.client_id == FRONTEND_CLIENT_ID}")
        
        # Verify the secret is stored correctly
        from django.contrib.auth.hashers import check_password
        secret_valid = check_password(FRONTEND_CLIENT_SECRET, test_app.client_secret)
        print(f"✓ Client Secret validation: {'PASS' if secret_valid else 'FAIL'}")
        
        if secret_valid:
            print("\n✅ All tests passed! OAuth is ready to use.")
        else:
            print("\n⚠️  Warning: Secret validation failed. You may need to regenerate.")
    else:
        print("\n❌ Error: Application not found after creation!")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    try:
        setup_production_oauth()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
