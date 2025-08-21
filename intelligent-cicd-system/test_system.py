#!/usr/bin/env python3
"""
🧪 Test Script for Intelligent CI/CD System
Tests all components to ensure they work correctly
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        from auth_manager import AuthenticationManager
        print("✅ AuthenticationManager imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AuthenticationManager: {e}")
        return False
    
    try:
        from project_analyzer import ProjectAnalyzer
        print("✅ ProjectAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ProjectAnalyzer: {e}")
        return False
    
    try:
        from infrastructure_manager import InfrastructureManager
        print("✅ InfrastructureManager imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import InfrastructureManager: {e}")
        return False
    
    try:
        from secrets_manager import SecretsManager
        print("✅ SecretsManager imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SecretsManager: {e}")
        return False
    
    try:
        from pipeline_generator import PipelineGenerator
        print("✅ PipelineGenerator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PipelineGenerator: {e}")
        return False
    
    try:
        from monitoring_dashboard import MonitoringDashboard
        print("✅ MonitoringDashboard imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import MonitoringDashboard: {e}")
        return False
    
    return True

def test_authentication_manager():
    """Test AuthenticationManager functionality"""
    print("\n🔐 Testing AuthenticationManager...")
    
    try:
        from auth_manager import AuthenticationManager
        
        auth_manager = AuthenticationManager()
        
        # Test basic functionality
        gcp_auth = auth_manager.is_gcp_authenticated()
        github_auth = auth_manager.is_github_authenticated()
        
        print(f"✅ GCP Authentication Status: {gcp_auth}")
        print(f"✅ GitHub Authentication Status: {github_auth}")
        
        # Test permissions validation
        permissions = auth_manager.validate_permissions()
        print(f"✅ Permissions Validation: {permissions}")
        
        return True
        
    except Exception as e:
        print(f"❌ AuthenticationManager test failed: {e}")
        return False

def test_project_analyzer():
    """Test ProjectAnalyzer functionality"""
    print("\n🔍 Testing ProjectAnalyzer...")
    
    try:
        from project_analyzer import ProjectAnalyzer
        
        analyzer = ProjectAnalyzer()
        
        # Test project analysis
        analysis = analyzer.analyze_project()
        
        print(f"✅ Project Type: {analysis.get('project_type', 'Unknown')}")
        print(f"✅ Files Found: {len(analysis.get('files', {}).get('source_files', []))}")
        print(f"✅ Dependencies: {len(analysis.get('dependencies', {}).get('python_packages', []))}")
        print(f"✅ Recommendations: {len(analysis.get('recommendations', []))}")
        
        # Test project summary
        summary = analyzer.get_project_summary()
        print(f"✅ Project Summary: {summary}")
        
        return True
        
    except Exception as e:
        print(f"❌ ProjectAnalyzer test failed: {e}")
        return False

def test_infrastructure_manager():
    """Test InfrastructureManager functionality"""
    print("\n🏗️ Testing InfrastructureManager...")
    
    try:
        from infrastructure_manager import InfrastructureManager
        
        infra_manager = InfrastructureManager()
        
        # Test infrastructure summary
        summary = infra_manager.get_infrastructure_summary()
        print(f"✅ Infrastructure Summary: {summary}")
        
        # Test validation
        validation = infra_manager.validate_setup()
        print(f"✅ Setup Validation: {validation}")
        
        return True
        
    except Exception as e:
        print(f"❌ InfrastructureManager test failed: {e}")
        return False

def test_secrets_manager():
    """Test SecretsManager functionality"""
    print("\n🔑 Testing SecretsManager...")
    
    try:
        from secrets_manager import SecretsManager
        
        secrets_manager = SecretsManager()
        
        # Test secrets summary
        summary = secrets_manager.get_secrets_summary()
        print(f"✅ Secrets Summary: {summary}")
        
        return True
        
    except Exception as e:
        print(f"❌ SecretsManager test failed: {e}")
        return False

def test_pipeline_generator():
    """Test PipelineGenerator functionality"""
    print("\n📝 Testing PipelineGenerator...")
    
    try:
        from pipeline_generator import PipelineGenerator
        
        pipeline_gen = PipelineGenerator()
        
        # Test pipeline summary
        summary = pipeline_gen.get_pipeline_summary()
        print(f"✅ Pipeline Summary: {summary}")
        
        # Test validation
        validation = pipeline_gen.validate_pipeline()
        print(f"✅ Pipeline Validation: {validation}")
        
        return True
        
    except Exception as e:
        print(f"❌ PipelineGenerator test failed: {e}")
        return False

def test_monitoring_dashboard():
    """Test MonitoringDashboard functionality"""
    print("\n📊 Testing MonitoringDashboard...")
    
    try:
        from monitoring_dashboard import MonitoringDashboard
        
        dashboard = MonitoringDashboard()
        
        # Test pipeline status
        status = dashboard.get_pipeline_status()
        print(f"✅ Pipeline Status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ MonitoringDashboard test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Intelligent CI/CD System - Component Tests")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Authentication Manager", test_authentication_manager),
        ("Project Analyzer", test_project_analyzer),
        ("Infrastructure Manager", test_infrastructure_manager),
        ("Secrets Manager", test_secrets_manager),
        ("Pipeline Generator", test_pipeline_generator),
        ("Monitoring Dashboard", test_monitoring_dashboard)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"⚠️ {test_name} test had issues")
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
