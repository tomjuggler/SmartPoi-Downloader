import unittest
import random
import string
import zipfile
import re
from app import generate_project, app
from unittest.mock import patch
from io import BytesIO

class TestGenerateProject(unittest.TestCase):

    def test_generate_project(self):
        # Generate random data_pin and clock_pin
        data_pin = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
        clock_pin = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
        num_pixels = random.randint(1, 100)
        ap_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        ap_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        led_type = random.choice(['WS2812', 'APA102'])

        # Create a request context
        with app.test_request_context():
            # Call generate_project with random data
            with patch('app.request') as mock_request:
                mock_request.form = {'data_pin': data_pin, 'clock_pin': clock_pin, 'num_pixels': str(num_pixels), 'ap_name': ap_name, 'ap_pass': ap_pass, 'led_type': led_type}
                response = generate_project()

            # Set the response object to not be in direct passthrough mode
            response.direct_passthrough = False

            # Check that the response is a zip file
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.mimetype, 'application/zip')

            # Check that the zip file contains the expected files
            zip_file = zipfile.ZipFile(BytesIO(response.get_data()))
            try:
                self.assertIn('main/main.ino', zip_file.namelist())

                # Check that the main.ino file contains the expected values
                with zip_file.open('main/main.ino') as f:
                    lines = [line.decode('utf-8').strip() for line in f.readlines()]
                    self.assertIn(f'#define DATA_PIN {data_pin}', lines)
                    self.assertIn(f'#define CLOCK_PIN {clock_pin}', lines)
                    self.assertIn(f'#define NUM_LEDS {num_pixels + 1}', lines)
                    self.assertIn(f'#define NUM_PX {num_pixels}', lines)
                    self.assertIn(f'const int maxPX = {num_pixels * 180};', lines)
                    self.assertIn(f'char apName[] = "{ap_name}";', lines)
                    self.assertIn(f'char apPass[] = "{ap_pass}";', lines)
                    self.assertIn('boolean auxillary = false;', lines)
                    # Regex for matching APA102 line, either commented or uncommented
                    if led_type == 'APA102':
                        # Match '#define LED_APA102' with optional leading/trailing spaces and comment
                        matched = [line for line in lines if re.search(r'^\s*#define\s+LED_APA102\b.*', line)]
                        print(f"Matching lines for APA102: {matched}")  # Debugging print
                        self.assertTrue(matched, "Expected '#define LED_APA102' not found")
                    else:
                        # Match '//#define LED_APA102' with optional leading/trailing spaces and comment
                        matched = [line for line in lines if re.search(r'^\s*//\s*#define\s+LED_APA102\b.*', line)]
                        print(f"Matching lines for commented version: {matched}")  # Debugging print
                        self.assertTrue(matched, "Expected '//#define LED_APA102' not found")



                # Check that the initalize.ino file contains the expected values - todo: remove old code block here:
                # with zip_file.open('main/initalize.ino') as f:
                #     lines = [line.decode('utf-8').strip() for line in f.readlines()]
                #     if led_type == 'APA102':
                #         self.assertIn(f'LEDS.addLeds<APA102, DATA_PIN, CLOCK_PIN, BGR>(leds, NUM_LEDS);'.strip(), [line.strip() for line in lines])
                #     else:
                #         self.assertIn(f'LEDS.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);'.strip(), [line.strip() for line in lines])
            finally:
                zip_file.close()

if __name__ == '__main__':
    unittest.main()
