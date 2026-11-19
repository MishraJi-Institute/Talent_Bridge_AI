import unittest

from windows_manager import _planned_migrations


class PlannedMigrationTests(unittest.TestCase):
    def test_extracts_current_django_migrate_plan_format(self):
        output = """Planned operations:
jobs.0011_application_statuses
    Custom state/database change combination
jobs.0012_unique_interview_slots
    Create constraint unique_interview_slot_per_application on model interview
"""

        self.assertEqual(
            _planned_migrations(output),
            [
                ('jobs', '0011_application_statuses'),
                ('jobs', '0012_unique_interview_slots'),
            ],
        )

    def test_no_operations_produces_empty_migration_list(self):
        self.assertEqual(
            _planned_migrations('Planned operations:\n  No planned migration operations.'),
            [],
        )

    def test_accepts_checkbox_prefixed_plan_entries(self):
        self.assertEqual(
            _planned_migrations('[ ] jobs.0011_application_statuses'),
            [('jobs', '0011_application_statuses')],
        )


if __name__ == '__main__':
    unittest.main()
