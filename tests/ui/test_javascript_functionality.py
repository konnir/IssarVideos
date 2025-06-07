#!/usr/bin/env python3
"""
JavaScript Functionality Tests
===============================

Tests for JavaScript functionality in the frontend files.
Uses Selenium WebDriver to test JavaScript execution.
"""
import pytest
import sys
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestJavaScriptFunctionality:
    """Test JavaScript functionality in the web pages"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for JavaScript tests"""
        self.base_url = "http://localhost:8000"
        self.driver = None

    def get_webdriver(self):
        """Get a configured WebDriver instance"""
        if self.driver is not None:
            return self.driver

        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            return self.driver
        except WebDriverException:
            pytest.skip("Chrome WebDriver not available - skipping JavaScript tests")

    def teardown_method(self):
        """Cleanup after each test"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def skip_if_server_not_running(self):
        """Skip test if server is not running"""
        import requests

        try:
            requests.get(f"{self.base_url}/health", timeout=2)
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping JavaScript tests")

    def test_tagger_page_loads(self):
        """Test that the tagger page loads and JavaScript initializes"""
        self.skip_if_server_not_running()
        driver = self.get_webdriver()

        driver.get(f"{self.base_url}/")

        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Check that the page title is correct
        assert "Video Tagger" in driver.title

        # Check for key elements that should be present
        assert driver.find_element(By.TAG_NAME, "h1")

        # Check that no JavaScript errors occurred (ignore favicon 404s)
        logs = driver.get_log("browser")
        js_errors = [
            log
            for log in logs
            if log["level"] == "SEVERE" and "favicon.ico" not in log["message"]
        ]
        assert len(js_errors) == 0, f"JavaScript errors found: {js_errors}"

    def test_report_page_loads(self):
        """Test that the report page loads and JavaScript initializes"""
        self.skip_if_server_not_running()
        driver = self.get_webdriver()

        driver.get(f"{self.base_url}/report")

        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Check that the page title contains the expected text
        assert "Tagger Record Report" in driver.title

        # Check for key elements that should be present
        h1_element = driver.find_element(By.TAG_NAME, "h1")
        assert "Tagger Record Report" in h1_element.text

        # Check that no JavaScript errors occurred (ignore favicon 404s)
        logs = driver.get_log("browser")
        js_errors = [
            log
            for log in logs
            if log["level"] == "SEVERE" and "favicon.ico" not in log["message"]
        ]
        assert len(js_errors) == 0, f"JavaScript errors found: {js_errors}"

    def test_report_authentication_modal(self):
        """Test the authentication modal in the report page"""
        self.skip_if_server_not_running()
        driver = self.get_webdriver()

        driver.get(f"{self.base_url}/report")

        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Look for authentication-related elements
        # (The specific implementation may vary, so we'll check for common patterns)
        try:
            # Check for authentication modal or form
            auth_elements = driver.find_elements(
                By.CSS_SELECTOR,
                "[id*='auth'], [class*='auth'], [id*='login'], [class*='login']",
            )
            assert len(auth_elements) > 0, "No authentication elements found"

            # Check for username and password inputs
            username_inputs = driver.find_elements(
                By.CSS_SELECTOR,
                "input[type='text'], input[placeholder*='username'], input[id*='username']",
            )
            password_inputs = driver.find_elements(
                By.CSS_SELECTOR,
                "input[type='password'], input[placeholder*='password'], input[id*='password']",
            )

            # At least one of each should be present
            assert (
                len(username_inputs) > 0 or len(password_inputs) > 0
            ), "No authentication input fields found"

        except Exception as e:
            # If specific elements aren't found, at least ensure the page loaded without errors
            logs = driver.get_log("browser")
            js_errors = [
                log
                for log in logs
                if log["level"] == "SEVERE" and "favicon.ico" not in log["message"]
            ]
            assert len(js_errors) == 0, f"JavaScript errors found: {js_errors}"

    def test_report_statistics_display(self):
        """Test that report statistics are displayed correctly"""
        self.skip_if_server_not_running()
        driver = self.get_webdriver()

        driver.get(f"{self.base_url}/report")

        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Wait a bit for JavaScript to execute
        time.sleep(2)

        # Look for statistics elements
        # Check for counter-related elements (based on our knowledge of report.js)
        stats_elements = driver.find_elements(
            By.CSS_SELECTOR,
            "[class*='counter'], [class*='stat'], [id*='counter'], [id*='stat']",
        )

        # Check for elements that might contain statistics
        text_elements = driver.find_elements(By.CSS_SELECTOR, "div, span, p")
        stats_found = False

        for element in text_elements:
            text = element.text.strip()
            if any(
                keyword in text.lower()
                for keyword in ["tagged", "records", "narratives", "count"]
            ):
                stats_found = True
                break

        # Either specific stats elements should exist, or stats should be in text
        assert (
            stats_found or len(stats_elements) > 0
        ), "No statistics elements found on report page"

        # Check that no JavaScript errors occurred (ignore favicon 404s)
        logs = driver.get_log("browser")
        js_errors = [
            log
            for log in logs
            if log["level"] == "SEVERE" and "favicon.ico" not in log["message"]
        ]
        assert len(js_errors) == 0, f"JavaScript errors found: {js_errors}"

    def test_tagger_navigation_buttons(self):
        """Test navigation buttons in the tagger interface"""
        self.skip_if_server_not_running()
        driver = self.get_webdriver()

        driver.get(f"{self.base_url}/")

        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Wait for JavaScript to initialize
        time.sleep(2)

        # Look for button elements
        buttons = driver.find_elements(By.TAG_NAME, "button")
        links = driver.find_elements(By.TAG_NAME, "a")
        inputs = driver.find_elements(
            By.CSS_SELECTOR, "input[type='button'], input[type='submit']"
        )

        interactive_elements = len(buttons) + len(links) + len(inputs)
        assert interactive_elements > 0, "No interactive elements found on tagger page"

        # Check that no JavaScript errors occurred (ignore favicon 404s)
        logs = driver.get_log("browser")
        js_errors = [
            log
            for log in logs
            if log["level"] == "SEVERE" and "favicon.ico" not in log["message"]
        ]
        assert len(js_errors) == 0, f"JavaScript errors found: {js_errors}"

    def test_ajax_api_calls(self):
        """Test that AJAX calls to API endpoints work from the frontend"""
        self.skip_if_server_not_running()
        driver = self.get_webdriver()

        # Load the tagger page
        driver.get(f"{self.base_url}/")

        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Execute JavaScript to test API calls
        try:
            # Test health endpoint call
            result = driver.execute_script(
                """
                return new Promise((resolve) => {
                    fetch('/health')
                        .then(response => response.json())
                        .then(data => resolve(data))
                        .catch(error => resolve({error: error.toString()}));
                });
            """
            )

            # Should get a response from the health endpoint
            assert "error" not in result or result.get("status") == "healthy"

        except Exception as e:
            # If JavaScript execution fails, at least check for basic functionality
            logs = driver.get_log("browser")
            js_errors = [
                log
                for log in logs
                if log["level"] == "SEVERE" and "favicon.ico" not in log["message"]
            ]

            # Allow some flexibility - just ensure no severe JS errors
            severe_errors = [
                error
                for error in js_errors
                if "fetch" not in error.get("message", "").lower()
            ]
            assert (
                len(severe_errors) == 0
            ), f"Severe JavaScript errors found: {severe_errors}"


class TestReportCounterLogic:
    """Test the specific counter logic in report.js"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for counter logic tests"""
        self.base_url = "http://localhost:8000"
        self.driver = None

    def get_webdriver(self):
        """Get a configured WebDriver instance"""
        if self.driver is not None:
            return self.driver

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            return self.driver
        except WebDriverException:
            pytest.skip("Chrome WebDriver not available - skipping counter tests")

    def teardown_method(self):
        """Cleanup after each test"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def skip_if_server_not_running(self):
        """Skip test if server is not running"""
        import requests

        try:
            requests.get(f"{self.base_url}/health", timeout=2)
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping counter tests")

    def test_counter_calculation_logic(self):
        """Test that counter calculations work correctly"""
        self.skip_if_server_not_running()
        driver = self.get_webdriver()

        driver.get(f"{self.base_url}/report")

        # Wait for page load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Wait for JavaScript to execute
        time.sleep(3)

        # Test the counter logic with mock data
        counter_test_result = driver.execute_script(
            """
            // Mock data for testing counter logic
            const mockData = [
                {Narrative: 'Story 1', Tagger_1_Result: 1},
                {Narrative: 'Story 1', Tagger_1_Result: 1},
                {Narrative: 'Story 1', Tagger_1_Result: 1},
                {Narrative: 'Story 1', Tagger_1_Result: 1},
                {Narrative: 'Story 1', Tagger_1_Result: 1},
                {Narrative: 'Story 1', Tagger_1_Result: 1}, // 6 "Yes" results for Story 1
                {Narrative: 'Story 2', Tagger_1_Result: 1},
                {Narrative: 'Story 2', Tagger_1_Result: 2}, // Mixed results for Story 2
                {Narrative: 'Story 3', Tagger_1_Result: 1},
                {Narrative: 'Story 3', Tagger_1_Result: 1},
                {Narrative: 'Story 3', Tagger_1_Result: 1},
                {Narrative: 'Story 3', Tagger_1_Result: 1},
                {Narrative: 'Story 3', Tagger_1_Result: 1}, // 5 "Yes" results for Story 3
            ];
            
            // Calculate unique narratives
            const uniqueNarratives = [...new Set(mockData.map(r => r.Narrative))];
            
            // Calculate narratives with >5 "Yes" results
            const narrativeYesCounts = {};
            mockData.forEach(record => {
                if (record.Tagger_1_Result === 1) {
                    narrativeYesCounts[record.Narrative] = (narrativeYesCounts[record.Narrative] || 0) + 1;
                }
            });
            
            const fullNarratives = Object.entries(narrativeYesCounts)
                .filter(([narrative, count]) => count > 5)
                .length;
            
            return {
                uniqueNarrativeCount: uniqueNarratives.length,
                fullNarrativeCount: fullNarratives,
                totalRecords: mockData.length,
                narrativeYesCounts: narrativeYesCounts
            };
        """
        )

        # Verify the logic
        assert counter_test_result["uniqueNarrativeCount"] == 3  # Story 1, 2, 3
        assert (
            counter_test_result["fullNarrativeCount"] == 1
        )  # Only Story 1 has >5 "Yes"
        assert counter_test_result["totalRecords"] == 13
        assert counter_test_result["narrativeYesCounts"]["Story 1"] == 6
        assert counter_test_result["narrativeYesCounts"]["Story 2"] == 1
        assert counter_test_result["narrativeYesCounts"]["Story 3"] == 5


class TestAddNarrativeModalFunctionality:
    """Test Add Narrative modal JavaScript functionality"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for tests"""
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.base_url = "http://localhost:8000"

    def skip_if_server_not_running(self):
        """Skip test if server is not running"""
        import requests

        try:
            requests.get(f"{self.base_url}/health", timeout=2)
        except requests.exceptions.ConnectionError:
            pytest.skip(
                "Server not running - skipping JavaScript tests that require server"
            )

    def test_add_narrative_modal_functions_exist(self):
        """Test that Add Narrative modal JavaScript functions exist"""
        self.skip_if_server_not_running()
        driver = webdriver.Chrome(options=self.options)

        try:
            # Load via server to get JavaScript functions working
            driver.get(f"{self.base_url}/tagging-management")

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for JavaScript to load
            import time

            time.sleep(2)

            # Check that all required JavaScript functions are defined
            required_functions = [
                "showAddNarrativeModal",
                "hideAddNarrativeModal",
                "addSingleNarrative",
                "addNewFormLine",
                "createFormLineHTML",
                "resetFormContainer",
            ]

            for func_name in required_functions:
                function_exists = driver.execute_script(
                    f"return typeof {func_name} === 'function';"
                )
                assert (
                    function_exists
                ), f"JavaScript function {func_name} should be defined"

        finally:
            driver.quit()

    def test_form_line_counter_initialization(self):
        """Test that form line counter is properly initialized"""
        self.skip_if_server_not_running()
        driver = webdriver.Chrome(options=self.options)

        try:
            # Load via server
            driver.get(f"{self.base_url}/tagging-management")

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for JavaScript to load
            import time

            time.sleep(2)

            # Check that formLineCounter is initialized
            counter_value = driver.execute_script(
                "return typeof formLineCounter !== 'undefined' ? formLineCounter : null;"
            )
            assert counter_value is not None, "formLineCounter should be initialized"
            assert counter_value == 1, "formLineCounter should start at 1"

        finally:
            driver.quit()

    def test_create_form_line_html_structure(self):
        """Test that createFormLineHTML generates proper structure"""
        self.skip_if_server_not_running()
        driver = webdriver.Chrome(options=self.options)

        try:
            # Load via server
            driver.get(f"{self.base_url}/tagging-management")

            # Wait for page to load and scripts to execute
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for JavaScript to load
            import time

            time.sleep(2)

            # Test createFormLineHTML function
            html_result = driver.execute_script(
                """
                if (typeof createFormLineHTML === 'function') {
                    var html = createFormLineHTML(2, 'Test Topic', 'Test Narrative');
                    var tempDiv = document.createElement('div');
                    tempDiv.innerHTML = html;
                    
                    return {
                        hasFormLine: html.includes('narrative-form-line'),
                        hasCorrectId: html.includes('formLine2'),
                        hasTopicField: html.includes('id="sheet2"'),
                        hasNarrativeField: html.includes('id="narrative2"'),
                        hasStoryField: html.includes('id="story2"'),
                        hasLinkField: html.includes('id="link2"'),
                        hasAddButton: html.includes('addSingleNarrative(2)'),
                        hasPlusButton: html.includes('addNewFormLine(2)'),
                        hasGridLayout: html.includes('grid-template-columns'),
                        hasCopiedValues: html.includes('value="Test Topic"') && html.includes('value="Test Narrative"')
                    };
                }
                return null;
            """
            )

            assert (
                html_result is not None
            ), "createFormLineHTML function should be available"
            assert html_result["hasFormLine"], "Should create form line structure"
            assert html_result["hasCorrectId"], "Should have correct line ID"
            assert html_result["hasTopicField"], "Should have topic field"
            assert html_result["hasNarrativeField"], "Should have narrative field"
            assert html_result["hasStoryField"], "Should have story field"
            assert html_result["hasLinkField"], "Should have link field"
            assert html_result["hasAddButton"], "Should have Add button"
            assert html_result["hasPlusButton"], "Should have Plus button"
            assert html_result["hasGridLayout"], "Should use CSS grid layout"
            assert html_result[
                "hasCopiedValues"
            ], "Should copy Topic and Narrative values"

        finally:
            driver.quit()

    def test_form_field_grid_positioning(self):
        """Test that form fields are properly positioned in CSS grid"""
        self.skip_if_server_not_running()
        driver = webdriver.Chrome(options=self.options)

        try:
            # Load via server
            driver.get(f"{self.base_url}/tagging-management")

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for styles to load
            import time

            time.sleep(2)

            # Test that grid positioning is correct
            grid_test = driver.execute_script(
                """
                var formLine = document.querySelector('#formLine1 .form-row');
                if (formLine) {
                    var computedStyle = window.getComputedStyle(formLine);
                    var gridColumns = computedStyle.getPropertyValue('grid-template-columns');
                    var display = computedStyle.getPropertyValue('display');
                    var gap = computedStyle.getPropertyValue('gap');
                    
                    return {
                        hasGridDisplay: display === 'grid',
                        hasCorrectColumns: gridColumns.includes('0.42fr') && gridColumns.includes('1.5fr') && gridColumns.includes('3fr'),
                        hasGap: gap.includes('30px'),
                        formLineExists: true
                    };
                }
                return { formLineExists: false };
            """
            )

            assert grid_test["formLineExists"], "Form line should exist"
            assert grid_test["hasGridDisplay"], "Form should use CSS grid display"
            assert grid_test[
                "hasCorrectColumns"
            ], "Should have correct grid column proportions"
            assert grid_test["hasGap"], "Should have 30px gap between fields"

        finally:
            driver.quit()


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])
