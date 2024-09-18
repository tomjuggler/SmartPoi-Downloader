import unittest
import random
import string
import zipfile
from app import generate_project, app
from unittest.mock import patch
from io import BytesIO

class TestGenerateProject(unittest.TestCase):

    def test_generate_project(self):
        # Generate random data_pin and clock_pin
        data_pin = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
        clock_pin = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))

        # Create a request context
        with app.test_request_context():
            # Call generate_project with random data
            with patch('app.request') as mock_request:
                mock_request.form = {'data_pin': data_pin, 'clock_pin': clock_pin}
                response = generate_project()

            # Set the response object to not be in direct passthrough mode
            response.direct_passthrough = False

            # Check that the response is a zip file
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.mimetype, 'application/zip')

            # Check that the zip file contains the expected files
            zip_file = zipfile.ZipFile(BytesIO(response.get_data()))
            self.assertIn('main/main.ino', zip_file.namelist())

            # Check that the main.ino file contains the expected values
            with zip_file.open('main/main.ino') as f:
                lines = f.readlines()
                self.assertIn(f'#define DATA_PIN {data_pin}'.encode(), lines)
                self.assertIn(f'#define CLOCK_PIN {clock_pin}'.encode(), lines)

if __name__ == '__main__':
    unittest.main()
