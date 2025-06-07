#!/usr/bin/env python3
"""
UI Tests for Edit Prompt Functionality
======================================

Tests for the Edit Prompt modal and custom prompt JavaScript functionality.
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


class TestEditPromptFunctionality:
    """Test Edit Prompt modal and custom prompt JavaScript functionality"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for tests"""
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920,1080")
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

    def test_edit_prompt_button_exists(self):
        """Test that Edit Prompt button exists in form lines"""
        self.skip_if_server_not_running()
        driver = webdriver.Chrome(options=self.options)

        try:
            # Load tagging management page
            driver.get(f"{self.base_url}/tagging-management")

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for JavaScript to load
            time.sleep(2)

            # Check that Edit Prompt button exists
            button_info = driver.execute_script(
                """
                var editBtn = document.querySelector('.edit-prompt-btn');
                if (editBtn) {
                    var style = window.getComputedStyle(editBtn);
                    return {
                        exists: true,
                        text: editBtn.textContent.trim(),
                        backgroundColor: style.backgroundColor,
                        onclick: editBtn.getAttribute('onclick'),
                        dataLineId: editBtn.getAttribute('data-line-id')
                    };
                }
                return { exists: false };
            """
            )

            assert button_info["exists"], "Edit Prompt button should exist"
            assert (
                "📝 Edit Prompt" in button_info["text"]
            ), "Button should have correct text"
            assert (
                "editPrompt(1)" in button_info["onclick"]
            ), "Button should have correct onclick handler"
            assert (
                button_info["dataLineId"] == "1"
            ), "Button should have correct data-line-id"

        finally:
            driver.quit()

    def test_edit_prompt_modal_functions_exist(self):
        """Test that Edit Prompt JavaScript functions exist"""
        self.skip_if_server_not_running()
        driver = webdriver.Chrome(options=self.options)

        try:
            # Load tagging management page
            driver.get(f"{self.base_url}/tagging-management")

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for JavaScript to load
            time.sleep(2)

            # Check that all required JavaScript functions are defined
            required_functions = [
                "editPrompt",
                "hideEditPromptModal",
                "saveCustomPrompt",
                "resetToDefaultPrompt",
                "testCustomPrompt",
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

    def test_edit_prompt_modal_elements_exist(self):
        """Test that Edit Prompt modal HTML elements exist"""
        self.skip_if_server_not_running()
        driver = webdriver.Chrome(options=self.options)

        try:
            # Load tagging management page
            driver.get(f"{self.base_url}/tagging-management")

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for JavaScript to load
            time.sleep(2)

            # Check that modal and its elements exist
            modal_elements = driver.execute_script(
                """
                return {
                    modal: !!document.getElementById('editPromptModal'),
                    promptTextarea: !!document.getElementById('customPrompt'),
                    saveButton: !!document.querySelector('.modal-btn.primary'),
                    resetButton: !!document.querySelector('.modal-btn.secondary'),
                    testButton: !!document.querySelector('.modal-btn.secondary:last-child'),
                    errorDiv: !!document.getElementById('editPromptError'),
                    resultDiv: !!document.getElementById('promptTestResult'),
                    closeButton: !!document.querySelector('#editPromptModal .close-btn')
                };
            """
            )

            assert modal_elements["modal"], "Edit Prompt modal should exist"
            assert modal_elements["promptTextarea"], "Prompt textarea should exist"
            assert modal_elements["saveButton"], "Save button should exist"
            assert modal_elements["resetButton"], "Reset button should exist"
            assert modal_elements["testButton"], "Test button should exist"
            assert modal_elements["errorDiv"], "Error div should exist"
            assert modal_elements["resultDiv"], "Result div should exist"
            assert modal_elements["closeButton"], "Close button should exist"

        finally:
            driver.quit()

    def test_edit_prompt_modal_show_hide(self):
        """Test that Edit Prompt modal can be shown and hidden"""
        self.skip_if_server_not_running()
        driver = webdriver.Chrome(options=self.options)

        try:
            # Load tagging management page
            driver.get(f"{self.base_url}/tagging-management")

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for JavaScript to load
            time.sleep(2)  # Test showing modal
            show_result = driver.execute_script(
                """
                var modal = document.getElementById('editPromptModal');
                var initialDisplay = window.getComputedStyle(modal).display;
                
                // Set narrative first (required for validation)
                var narrativeField = document.getElementById('narrative1');
                if (narrativeField) {
                    narrativeField.value = 'Test narrative for modal display';
                }

                // Call editPrompt function
                if (typeof editPrompt === 'function') {
                    editPrompt(1);
                    var afterShowDisplay = window.getComputedStyle(modal).display;

                    return {
                        initialDisplay: initialDisplay,
                        afterShowDisplay: afterShowDisplay,
                        modalTitle: document.querySelector('#editPromptModal .modal-header h3').textContent
                    };
                }
                return null;
            """
            )

            assert show_result is not None, "editPrompt function should be available"
            assert (
                show_result["initialDisplay"] == "none"
            ), "Modal should be initially hidden"
            assert (
                show_result["afterShowDisplay"] == "block"
            ), "Modal should be visible after editPrompt call"
            assert (
                "Edit Story Prompt (Test narrative for modal display)"
                in show_result["modalTitle"]
            ), "Modal title should update with narrative"

            # Test hiding modal
            hide_result = driver.execute_script(
                """
                if (typeof hideEditPromptModal === 'function') {
                    hideEditPromptModal();
                    var afterHideDisplay = window.getComputedStyle(document.getElementById('editPromptModal')).display;
                    return { afterHideDisplay: afterHideDisplay };
                }
                return null;
            """
            )

            assert (
                hide_result is not None
            ), "hideEditPromptModal function should be available"
            assert (
                hide_result["afterHideDisplay"] == "none"
            ), "Modal should be hidden after hideEditPromptModal call"

        finally:
            driver.quit()

    def test_custom_prompts_global_storage(self):
        """Test that customPrompts global storage works correctly"""
        self.skip_if_server_not_running()
        driver = webdriver.Chrome(options=self.options)

        try:
            # Load tagging management page
            driver.get(f"{self.base_url}/tagging-management")

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for JavaScript to load
            time.sleep(2)

            # Test customPrompts storage
            storage_test = driver.execute_script(
                """
                // Test that customPrompts object exists
                var customPromptsExists = typeof customPrompts !== 'undefined';
                var isObject = typeof customPrompts === 'object';
                
                // Test storing and retrieving
                if (customPromptsExists && isObject) {
                    customPrompts['test1'] = 'Test prompt for line 1';
                    customPrompts['test2'] = 'Test prompt for line 2';
                    
                    return {
                        exists: true,
                        isObject: true,
                        canStore: customPrompts['test1'] === 'Test prompt for line 1',
                        canRetrieve: customPrompts['test2'] === 'Test prompt for line 2',
                        keys: Object.keys(customPrompts)
                    };
                }
                
                return { exists: customPromptsExists, isObject: isObject };
            """
            )

            assert storage_test["exists"], "customPrompts variable should exist"
            assert storage_test["isObject"], "customPrompts should be an object"
            assert storage_test["canStore"], "Should be able to store custom prompts"
            assert storage_test[
                "canRetrieve"
            ], "Should be able to retrieve custom prompts"

        finally:
            driver.quit()

    def test_default_prompt_constant(self):
        """Test that DEFAULT_PROMPT constant exists and is correct"""
        self.skip_if_server_not_running()
        driver = webdriver.Chrome(options=self.options)

        try:
            # Load tagging management page
            driver.get(f"{self.base_url}/tagging-management")

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for JavaScript to load
            time.sleep(2)

            # Test DEFAULT_PROMPT constant
            default_prompt_test = driver.execute_script(
                """
                return {
                    exists: typeof DEFAULT_PROMPT !== 'undefined',
                    isString: typeof DEFAULT_PROMPT === 'string',
                    hasNarrativePlaceholder: DEFAULT_PROMPT && DEFAULT_PROMPT.includes('{narrative}'),
                    length: DEFAULT_PROMPT ? DEFAULT_PROMPT.length : 0,
                    containsStoryInstructions: DEFAULT_PROMPT && DEFAULT_PROMPT.includes('Create a brief story')
                };
            """
            )

            assert default_prompt_test["exists"], "DEFAULT_PROMPT constant should exist"
            assert default_prompt_test["isString"], "DEFAULT_PROMPT should be a string"
            assert default_prompt_test[
                "hasNarrativePlaceholder"
            ], "DEFAULT_PROMPT should contain {narrative} placeholder"
            assert (
                default_prompt_test["length"] > 50
            ), "DEFAULT_PROMPT should be a substantial prompt"
            assert default_prompt_test[
                "containsStoryInstructions"
            ], "DEFAULT_PROMPT should contain story creation instructions"

        finally:
            driver.quit()

    def test_save_custom_prompt_validation(self):
        """Test that saveCustomPrompt validates input correctly"""
        self.skip_if_server_not_running()
        driver = webdriver.Chrome(options=self.options)

        try:
            # Load tagging management page
            driver.get(f"{self.base_url}/tagging-management")

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for JavaScript to load
            time.sleep(2)  # Test validation with empty prompt
            empty_validation = driver.execute_script(
                """
                // Set narrative first (required for validation)
                var narrativeField = document.getElementById('narrative1');
                if (narrativeField) {
                    narrativeField.value = 'Test narrative for validation';
                }
                
                // Open edit modal for line 1
                if (typeof editPrompt === 'function') {
                    editPrompt(1);

                    // Clear the textarea
                    document.getElementById('customPrompt').value = '';

                    // Try to save
                    if (typeof saveCustomPrompt === 'function') {
                        saveCustomPrompt();

                        var errorDiv = document.getElementById('editPromptError');
                        return {
                            errorDisplayed: errorDiv.style.display === 'block',
                            errorMessage: errorDiv.innerHTML
                        };
                    }
                }
                return null;
            """
            )

            assert (
                empty_validation is not None
            ), "Validation functions should be available"
            assert empty_validation[
                "errorDisplayed"
            ], "Error should be displayed for empty prompt"
            assert (
                "empty" in empty_validation["errorMessage"].lower()
            ), "Error should mention empty prompt"

            # Test validation without {narrative} placeholder
            placeholder_validation = driver.execute_script(
                """
                // Set prompt without placeholder
                document.getElementById('customPrompt').value = 'This is a prompt without the required placeholder';

                // Clear previous errors
                document.getElementById('editPromptError').style.display = 'none';

                // Try to save
                saveCustomPrompt();

                var errorDiv = document.getElementById('editPromptError');
                return {
                    errorDisplayed: errorDiv.style.display === 'block',
                    errorMessage: errorDiv.innerHTML
                };
            """
            )

            assert placeholder_validation[
                "errorDisplayed"
            ], "Error should be displayed for missing placeholder"
            assert (
                "narrative" in placeholder_validation["errorMessage"].lower()
            ), "Error should mention narrative placeholder"

        finally:
            driver.quit()

    def test_save_custom_prompt_success(self):
        """Test successful custom prompt saving"""
        self.skip_if_server_not_running()
        driver = webdriver.Chrome(options=self.options)

        try:
            # Load tagging management page
            driver.get(f"{self.base_url}/tagging-management")

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for JavaScript to load
            time.sleep(2)  # Test successful save
            save_result = driver.execute_script(
                """
                // Set narrative first (required for validation)
                var narrativeField = document.getElementById('narrative1');
                if (narrativeField) {
                    narrativeField.value = 'Test narrative for save success';
                }
                
                // Open edit modal for line 1
                editPrompt(1);

                // Set valid custom prompt
                var customPromptText = 'Create a custom story about: {narrative}. Make it exciting and engaging.';
                document.getElementById('customPrompt').value = customPromptText;

                // Save the prompt
                saveCustomPrompt();

                // Check results
                var errorDiv = document.getElementById('editPromptError');
                var editBtn = document.querySelector('[data-line-id="1"].edit-prompt-btn');

                return {
                    promptSaved: customPrompts['1'] === customPromptText,
                    buttonTextUpdated: editBtn.textContent.includes('Prompt Edited ✓'),
                    buttonExists: !!editBtn,
                    successDisplayed: errorDiv.style.display === 'block' && errorDiv.innerHTML.includes('success')
                };
            """
            )

            assert save_result[
                "promptSaved"
            ], "Custom prompt should be saved in storage"
            assert save_result[
                "buttonTextUpdated"
            ], "Button text should update to show edited status"
            assert save_result["buttonExists"], "Button should exist"
            assert save_result[
                "successDisplayed"
            ], "Success message should be displayed"

        finally:
            driver.quit()

    def test_reset_to_default_prompt(self):
        """Test resetting to default prompt"""
        self.skip_if_server_not_running()
        driver = webdriver.Chrome(options=self.options)

        try:
            # Load tagging management page
            driver.get(f"{self.base_url}/tagging-management")

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for JavaScript to load
            time.sleep(2)  # Test reset functionality
            reset_result = driver.execute_script(
                """
                // Set narrative first (required for validation)
                var narrativeField = document.getElementById('narrative1');
                if (narrativeField) {
                    narrativeField.value = 'Test narrative for reset function';
                }
                
                // First, set a custom prompt
                editPrompt(1);
                customPrompts['1'] = 'Custom prompt text with {narrative}';

                // Update button to show custom state
                var editBtn = document.querySelector('[data-line-id="1"].edit-prompt-btn');
                var originalBackground = editBtn.style.background;
                editBtn.textContent = '📝 Prompt Edited ✓';
                editBtn.style.background = '#357abd';
                var customBackground = editBtn.style.background;

                // Now reset to default
                resetToDefaultPrompt();

                // Check results - compare computed styles instead of inline styles
                var computedStyle = window.getComputedStyle(editBtn);
                var resetBackground = editBtn.style.background;

                return {
                    customPromptRemoved: !customPrompts.hasOwnProperty('1'),
                    buttonTextReset: editBtn.textContent === '📝 Edit Prompt',
                    buttonStyleChanged: customBackground !== resetBackground,
                    resetStyleValue: resetBackground,
                    computedBackground: computedStyle.backgroundColor,
                    textareaUpdated: document.getElementById('customPrompt').value === DEFAULT_PROMPT,
                    successDisplayed: document.getElementById('editPromptError').style.display === 'block'
                };
            """
            )

            assert reset_result[
                "customPromptRemoved"
            ], "Custom prompt should be removed from storage"
            assert reset_result[
                "buttonTextReset"
            ], "Button text should reset to default"
            assert reset_result[
                "buttonStyleChanged"
            ], "Button style should change from custom back to default"
            assert reset_result[
                "textareaUpdated"
            ], "Textarea should show default prompt"
            assert reset_result[
                "successDisplayed"
            ], "Success message should be displayed"

        finally:
            driver.quit()

    def test_prompt_duplication_on_add_new_line(self):
        """Test that custom prompts are duplicated when adding new form lines"""
        self.skip_if_server_not_running()
        driver = webdriver.Chrome(options=self.options)

        try:
            # Load tagging management page
            driver.get(f"{self.base_url}/tagging-management")

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for JavaScript to load
            time.sleep(2)

            # Test prompt duplication
            duplication_result = driver.execute_script(
                """
                // Set custom prompt for line 1
                customPrompts['1'] = 'Custom prompt for testing: {narrative}';
                
                // Add new form line from line 1
                if (typeof addNewFormLine === 'function') {
                    addNewFormLine(1);
                    
                    // Check if prompt was duplicated
                    return {
                        line1HasPrompt: customPrompts.hasOwnProperty('1'),
                        line2HasPrompt: customPrompts.hasOwnProperty('2'),
                        promptsMatch: customPrompts['1'] === customPrompts['2'],
                        line2ButtonExists: !!document.querySelector('[data-line-id="2"].edit-prompt-btn')
                    };
                }
                return null;
            """
            )

            assert (
                duplication_result is not None
            ), "addNewFormLine function should be available"
            assert duplication_result[
                "line1HasPrompt"
            ], "Line 1 should still have custom prompt"
            assert duplication_result[
                "line2HasPrompt"
            ], "Line 2 should have duplicated prompt"
            assert duplication_result[
                "promptsMatch"
            ], "Prompts should match between lines"
            assert duplication_result[
                "line2ButtonExists"
            ], "Line 2 should have edit prompt button"

        finally:
            driver.quit()

    def test_suggest_story_uses_custom_prompt(self):
        """Test that suggestStory uses custom prompts when available"""
        self.skip_if_server_not_running()
        driver = webdriver.Chrome(options=self.options)

        try:
            # Load tagging management page
            driver.get(f"{self.base_url}/tagging-management")

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for JavaScript to load
            time.sleep(2)

            # Test custom prompt usage in suggestStory
            custom_prompt_usage = driver.execute_script(
                """
                // Set up test data
                var narrativeField = document.getElementById('narrative1');
                var storyField = document.getElementById('story1');
                
                if (narrativeField && storyField) {
                    narrativeField.value = 'A mysterious package arrives';
                    customPrompts['1'] = 'Create a thrilling story about: {narrative}';
                    
                    var apiCallInfo = null;
                    
                    // Mock fetch to capture API call
                    var originalFetch = window.fetch;
                    window.fetch = function(url, options) {
                        apiCallInfo = {
                            url: url,
                            method: options.method,
                            body: options.body ? JSON.parse(options.body) : null,
                            usedCustomEndpoint: url.includes('generate-story-custom-prompt')
                        };
                        
                        return Promise.resolve({
                            ok: true,
                            json: function() {
                                return Promise.resolve({
                                    story: 'Generated story with custom prompt',
                                    metadata: { word_count: 25 }
                                });
                            }
                        });
                    };
                    
                    // Call suggestStory
                    if (typeof suggestStory === 'function') {
                        suggestStory(1);
                        
                        // Wait for async call
                        return new Promise(function(resolve) {
                            setTimeout(function() {
                                window.fetch = originalFetch;
                                resolve(apiCallInfo);
                            }, 100);
                        });
                    }
                }
                return null;
            """
            )

            # Wait for async operation
            time.sleep(0.5)

            if custom_prompt_usage is not None:
                assert custom_prompt_usage[
                    "usedCustomEndpoint"
                ], "Should use custom prompt endpoint when custom prompt exists"
                assert (
                    custom_prompt_usage["body"] is not None
                ), "Should send request body"
                assert (
                    "custom_prompt" in custom_prompt_usage["body"]
                ), "Should include custom_prompt in request"

        finally:
            driver.quit()

    def test_edit_prompt_button_in_dynamic_forms(self):
        """Test that edit prompt buttons are included in dynamically created form lines"""
        self.skip_if_server_not_running()
        driver = webdriver.Chrome(options=self.options)

        try:
            # Load tagging management page
            driver.get(f"{self.base_url}/tagging-management")

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for JavaScript to load
            time.sleep(2)

            # Test edit prompt button in dynamic forms
            dynamic_button_test = driver.execute_script(
                """
                if (typeof createFormLineHTML === 'function') {
                    var html = createFormLineHTML(3, 'Test Topic', 'Test Narrative');
                    return {
                        hasEditPromptButton: html.includes('edit-prompt-btn'),
                        hasCorrectOnClick: html.includes('editPrompt(3)'),
                        hasCorrectDataLineId: html.includes('data-line-id="3"'),
                        hasButtonText: html.includes('📝 Edit Prompt')
                    };
                }
                return null;
            """
            )

            assert (
                dynamic_button_test is not None
            ), "createFormLineHTML function should be available"
            assert dynamic_button_test[
                "hasEditPromptButton"
            ], "Should include edit prompt button"
            assert dynamic_button_test[
                "hasCorrectOnClick"
            ], "Should have correct onclick handler"
            assert dynamic_button_test[
                "hasCorrectDataLineId"
            ], "Should have correct data-line-id"
            assert dynamic_button_test[
                "hasButtonText"
            ], "Should have correct button text"

        finally:
            driver.quit()

    def test_edit_prompt_validation_requires_narrative(self):
        """Test that Edit Prompt button validates narrative exists before opening modal"""
        self.skip_if_server_not_running()
        driver = webdriver.Chrome(options=self.options)

        try:
            # Load tagging management page
            driver.get(f"{self.base_url}/tagging-management")

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait for JavaScript to load
            time.sleep(2)

            # Test validation with empty narrative
            validation_result = driver.execute_script(
                """
                // Clear the narrative field
                var narrativeField = document.getElementById('narrative1');
                var errorDiv = document.getElementById('addNarrativeError');
                var modal = document.getElementById('editPromptModal');
                
                if (narrativeField && errorDiv && modal) {
                    narrativeField.value = '';
                    
                    // Clear any existing error
                    errorDiv.style.display = 'none';
                    errorDiv.innerHTML = '';
                    
                    // Ensure modal is initially hidden
                    modal.style.display = 'none';
                    
                    // Try to open edit prompt modal
                    if (typeof editPrompt === 'function') {
                        editPrompt(1);
                    }
                    
                    return {
                        narrativeFieldExists: true,
                        errorDivExists: true,
                        modalStaysHidden: window.getComputedStyle(modal).display === 'none',
                        errorDisplayed: errorDiv.style.display === 'block',
                        errorMessage: errorDiv.innerHTML,
                        errorVisible: window.getComputedStyle(errorDiv).display !== 'none'
                    };
                }
                return { narrativeFieldExists: false, errorDivExists: false, modalExists: false };
            """
            )

            assert validation_result[
                "narrativeFieldExists"
            ], "Narrative field should exist"
            assert validation_result["errorDivExists"], "Error div should exist"
            assert validation_result[
                "modalStaysHidden"
            ], "Modal should stay hidden when narrative is empty"
            assert validation_result[
                "errorDisplayed"
            ], "Error should be displayed for empty narrative"
            assert (
                "narrative" in validation_result["errorMessage"].lower()
            ), f"Error should mention narrative, got: {validation_result['errorMessage']}"

            # Test that modal opens when narrative is present
            modal_opens_result = driver.execute_script(
                """
                // Add narrative text
                var narrativeField = document.getElementById('narrative1');
                var modal = document.getElementById('editPromptModal');
                var errorDiv = document.getElementById('addNarrativeError');
                
                if (narrativeField && modal) {
                    narrativeField.value = 'A test narrative for prompt editing';
                    
                    // Clear any previous error
                    errorDiv.style.display = 'none';
                    
                    // Ensure modal is initially hidden
                    modal.style.display = 'none';
                    
                    // Try to open edit prompt modal
                    if (typeof editPrompt === 'function') {
                        editPrompt(1);
                    }
                    
                    return {
                        modalOpens: window.getComputedStyle(modal).display === 'block',
                        errorStaysHidden: errorDiv.style.display === 'none' || errorDiv.style.display === ''
                    };
                }
                return { modalOpens: false, errorStaysHidden: false };
            """
            )

            assert modal_opens_result[
                "modalOpens"
            ], "Modal should open when narrative is present"
            assert modal_opens_result[
                "errorStaysHidden"
            ], "Error should not be displayed when narrative is present"

        finally:
            driver.quit()


if __name__ == "__main__":
    pytest.main([__file__])
