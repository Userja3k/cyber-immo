import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_manager.settings')
django.setup()

from django.db import connection

def show_migrations():
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, app, name FROM django_migrations ORDER BY id;")
        rows = cursor.fetchall()
        print("Current migrations:")
        for row in rows:
            print(row)

def delete_migration(app, name):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM django_migrations WHERE app=%s AND name=%s;", [app, name])
        print(f"Deleted migration {app}.{name}")

if __name__ == "__main__":
    print("Before cleanup:")
    show_migrations()

    # Delete core.0001_initial migration record to fix order issue
    delete_migration('core', '0001_initial')

    # Delete admin.0001_initial migration record to fix dependency order
    delete_migration('admin', '0001_initial')

    # Delete admin.0002_logentry_remove_auto_add migration record to fix dependency order
    delete_migration('admin', '0002_logentry_remove_auto_add')

    # Delete admin.0003_logentry_add_action_flag_choices migration record to fix dependency order
    delete_migration('admin', '0003_logentry_add_action_flag_choices')

    print("\nAfter cleanup:")
    show_migrations()
