import os

# Make sure that database connections created in the code connect to the test
# database:
os.environ['APP_ENV'] = 'test'

# Show full assertion messages:
# Taken from https://stackoverflow.com/a/61345284
if 'unittest.util' in __import__('sys').modules:
    # Show full diff in self.assertEqual.
    __import__('sys').modules['unittest.util']._MAX_LENGTH = 999999999
