# Generated manually to fix foreign key reference to correct user table
#
# Problem: The valuation_valuation table had a foreign key constraint
# pointing to auth_user instead of account_user (the custom User model).
# This happens when migrations are run before AUTH_USER_MODEL is properly set.
#
# Solution: Drop old constraint and recreate with correct table reference.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('valuation', '0002_alter_valuation_managers_and_more'),
        ('account', '0001_initial'),  # Ensure account migrations are applied first
    ]

    operations = [
        migrations.RunSQL(
            # Drop the old foreign key constraint that points to auth_user
            sql="""
                ALTER TABLE valuation_valuation
                DROP CONSTRAINT IF EXISTS valuation_valuation_user_id_73bf7fa7_fk_auth_user_id;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            # Add new foreign key constraint pointing to account_user
            sql="""
                ALTER TABLE valuation_valuation
                ADD CONSTRAINT valuation_valuation_user_id_fk_account_user
                FOREIGN KEY (user_id)
                REFERENCES account_user(id)
                ON DELETE CASCADE
                DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
                ALTER TABLE valuation_valuation
                DROP CONSTRAINT IF EXISTS valuation_valuation_user_id_fk_account_user;
            """,
        ),
        # Also fix the Like model's user foreign key
        migrations.RunSQL(
            sql="""
                ALTER TABLE valuation_like
                DROP CONSTRAINT IF EXISTS valuation_like_user_id_fk;
                
                ALTER TABLE valuation_like
                DROP CONSTRAINT IF EXISTS valuation_like_user_id_73bf7fa7_fk_auth_user_id;
                
                ALTER TABLE valuation_like
                DROP CONSTRAINT IF EXISTS valuation_like_user_id_e1a64bd6_fk_auth_user_id;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="""
                ALTER TABLE valuation_like
                ADD CONSTRAINT valuation_like_user_id_fk_account_user
                FOREIGN KEY (user_id)
                REFERENCES account_user(id)
                ON DELETE CASCADE
                DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
                ALTER TABLE valuation_like
                DROP CONSTRAINT IF EXISTS valuation_like_user_id_fk_account_user;
            """,
        ),
    ]
