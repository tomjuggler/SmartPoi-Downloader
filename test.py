import unittest
import random
import string
from app import generate_project

class TestGenerateProject(unittest.TestCase):

    def test_generate_project(self):
        # Generate random data_pin and clock_pin
        data_pin = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
        clock_pin = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))

        # Call generate_project with random data
        with unittest.mock.patch('app.request') as mock_request:
            mock_request.form = {'data_pin': data_pin, 'clock_pin': clock_pin}
            response = generate_project()

        # Check that the response is a zip file
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/zip')

        # Check that the zip file contains the expected files
        zip_file = zipfile.ZipFile(response.get_data())
        self.assertIn('SmartPoi-Firmware/main/main.ino', zip_file.namelist())

        # Check that the main.ino file contains the expected values
        with zip_file.open('SmartPoi-Firmware/main/main.ino') as f:
            lines = f.readlines()
            self.assertIn(f'#define DATA_PIN {data_pin}'.encode(), lines)
            self.assertIn(f'#define CLOCK_PIN {clock_pin}'.encode(), lines)

if __name__ == '__main__':
    unittest.main()
