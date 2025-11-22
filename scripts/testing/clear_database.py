"""
Clear all telemetry and anomaly data from the database.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../", "../")))

from app.db import SessionLocal
from app.models import TelemetryEvent, AnomalyRecord

def main():
    print("=" * 80)
    print("CLEARING DATABASE")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        # Count before deletion
        telemetry_count = db.query(TelemetryEvent).count()
        anomaly_count = db.query(AnomalyRecord).count()
        
        print(f"\n📊 Current Database State:")
        print(f"   Telemetry Events: {telemetry_count}")
        print(f"   Anomaly Records: {anomaly_count}")
        
        if telemetry_count == 0 and anomaly_count == 0:
            print("\n✅ Database is already empty!")
            return
        
        # Delete all records
        print(f"\n🗑️  Deleting all records...")
        db.query(AnomalyRecord).delete()
        db.query(TelemetryEvent).delete()
        db.commit()
        
        # Verify deletion
        telemetry_count_after = db.query(TelemetryEvent).count()
        anomaly_count_after = db.query(AnomalyRecord).count()
        
        print(f"\n✅ Database Cleared Successfully!")
        print(f"   Telemetry Events: {telemetry_count_after}")
        print(f"   Anomaly Records: {anomaly_count_after}")
        
        print("\n💡 Next Steps:")
        print("   1. Run: python scripts/testing/generate_realtime_data.py")
        print("   2. Wait 5 minutes for Celery Beat to trigger detection")
        print("   3. Run: python scripts/testing/verify_anomalies.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
