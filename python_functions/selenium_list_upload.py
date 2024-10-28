def selenium_upload(directory_path):
    import os
    import pandas as pd

    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.chrome.service import Service
    import time
    from lxml import html
    import random
    import sys

    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import ElementClickInterceptedException

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--window-size=3840x2160")  # Increase the window size

    # Get df of file names
    sys.path.append('/content/drive/MyDrive/python_functions')
    from file_upload_df_from_rss import create_upload_file_df
    files_to_process_df = create_upload_file_df(directory_path, '.txt')
    upload_file_dates = files_to_process_df['date'].tolist()

    # Create JSON and Summary Lists
    csv_path = directory_path + '/CSV/'
    csv_uploaded_path = directory_path + '/CSV_Uploaded/'
    csv_files = sorted(os.listdir(csv_path))
    summary_files = [file for file in csv_files if (file.startswith('summary_') and file[9:17] in upload_file_dates)]
    json_files = [file for file in csv_files if (file.startswith('json_') and file[6:14] in upload_file_dates)]

    Letterboxd_username = "kevdawg_test"
    Letterboxd_password = "Mamiya206!"

    def create_letterboxd_list(list_csv, list_title, list_summary):
        print('Starting '+list_title)
        directory_files = sorted(os.listdir(csv_path))

        service = Service(executable_path="chromedriver")
        driver = webdriver.Chrome(options=chrome_options)

        time.sleep(random.uniform(8, 12))

        # Open the target webpage
        driver.get('https://letterboxd.com/list/new/')

        print('Got Driver')

        # Use WebDriverWait to wait for the elements to be available
        wait = WebDriverWait(driver, 15)

        # Step 1: Locate the Username input field and input "test-username"
        username_input = wait.until(EC.visibility_of_element_located((By.ID, "field-username")))
        username_input.clear()
        username_input.send_keys(Letterboxd_username)

        # Step 2: Locate the Password input field and input "test-password"
        password_input = wait.until(EC.visibility_of_element_located((By.ID, "field-password")))
        password_input.clear()
        password_input.send_keys(Letterboxd_password)

        # Step 3: Locate the "Sign In" button and click it
        sign_in_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        sign_in_button.click()

        print('Signed in')

        time.sleep(random.uniform(8, 12))

        # 4 Import CSV to check progress of uploads

        # Step 1: Find the "Name" input field and enter "Text 1"
        name_field = wait.until(EC.visibility_of_element_located((By.NAME, "name")))
        name_field.clear()
        name_field.send_keys(list_title)

        # Step 2: Find the "Description" input field and enter "Text 2"
        description_field = wait.until(EC.visibility_of_element_located((By.NAME, "notes")))
        description_field.clear()
        description_field.send_keys(list_summary)

        # Step 3: Click the "Import" button to bring up the file selector
        import_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "list-import-link")))
        import_button.click()

        time.sleep(random.uniform(3, 5))

        # Step 4: Find the file input field and upload "File 1"
        file_input = wait.until(EC.presence_of_element_located((By.ID, "upload-list")))
        file_input.send_keys(list_csv)

        time.sleep(random.uniform(3, 5))

        print('uploaded film csv')

        # Finish List Upload
        time.sleep(random.uniform(10, 15))

        # See delivered HTML to confirm successful login
        # website_html = driver.execute_script("return document.body.innerHTML")
        # file = open("selenium_test_output.html", "w")
        # file.write(website_html)
        # print('exported_website_html')

        # Step 1: Locate the element you want to click using CSS_SELECTOR
        element = driver.find_element(By.CSS_SELECTOR, ".button.-action.button-large.button-action.submit-matched-films.add-import-films-to-list.track-event")

        print('identified element')

        # Step 2: Scroll the element into view
        driver.execute_script("arguments[0].scrollIntoView();", element)

        print('scrolled to element')

        time.sleep(random.uniform(4, 5))

        # Step 4: Try to click the element
        print('attempting to click submit matched films button')

        try:
            element.click()
        except ElementClickInterceptedException:
            # Step 5: If intercepted, use JavaScript to click the element
            print('element intercepted, attempting javascript click')
            driver.execute_script("arguments[0].click();", element)

        print('clicked submit match films')

        time.sleep(random.uniform(5, 15))

        # Save List
        save_button = driver.find_element(By.ID, 'list-edit-save')
        driver.execute_script("arguments[0].click();", save_button)
        print("Save button clicked successfully.")

        # Wait for any subsequent action to complete
        time.sleep(random.uniform(3, 5))

        # Quit the driver after a short delay
        driver.quit()

        print('Completed list creation for'+list_title)

    for i in range(len(json_files)):
        # Check JSON and SUMMARY file dates match
        if summary_files[i][9:17] == json_files[i][6:14]: 
            json_df = pd.read_csv(csv_path+json_files[i])
            summary_df = pd.read_csv(csv_path+summary_files[i])
            list_title = summary_df['Episode_Title']
            list_summary = summary_df['Summary']
            json_path = csv_path+json_files[i]
            
            create_letterboxd_list(json_path, list_title, list_summary)
            os.rename(csv_path + summary_files[i], csv_uploaded_path + summary_files[i])
            os.rename(csv_path + json_files[i], csv_uploaded_path + json_files[i])