import json
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def scrape_tags():
    # Set up the WebDriver
    driver = webdriver.Chrome()  # You can use other drivers like Firefox too
    
    # Create a list to store all tag data
    tag_data_list = []
    
    try:
        # Open the main page with the tag list
        driver.get("https://ranobes.top/tags/events/")
        
        # Wait for the page to load and tag list to appear
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".tag_list")))
        
        # Get all tag links
        tag_links = driver.find_elements(By.CSS_SELECTOR, ".tag_list .clouds_xsmall a")
        total_links = len(tag_links)
        print(f"Found {total_links} tags to process")
        
        # Store the original window handle
        main_window = driver.current_window_handle
        
        # Process each link
        for i in range(total_links):
            # We need to find the elements again after returning to the page
            tag_links = driver.find_elements(By.CSS_SELECTOR, ".tag_list .clouds_xsmall a")
            
            # Skip if we've somehow gone beyond the available links
            if i >= len(tag_links):
                print(f"Skipping index {i} - out of range")
                continue
            
            # Get the tag name before clicking
            tag_name = tag_links[i].text
            
            print(f"Processing tag {i+1}/{total_links}: {tag_name}")
            
            # Open link in new tab by holding CTRL and clicking
            # Since this doesn't work reliably, we'll use JavaScript to open a new tab
            driver.execute_script(f"window.open('{tag_links[i].get_attribute('href')}', '_blank');")
            
            # Switch to the new tab (it will be the last window handle)
            new_window = [window for window in driver.window_handles if window != main_window][0]
            driver.switch_to.window(new_window)
            
            try:
                # Use a shorter timeout for finding the description
                short_wait = WebDriverWait(driver, 2)  # Reduced timeout to 2 seconds
                
                # Wait for the tag description to load with shorter timeout
                short_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".cat_block")))
                
                # Extract the title and description
                tag_title = driver.find_element(By.CSS_SELECTOR, ".cat_block h3.title").text
                tag_description = driver.find_element(By.CSS_SELECTOR, ".cat_block").text
                
                # Clean up the description (remove the title part)
                tag_description = tag_description.replace(tag_title, "").strip()
                
                # Add to our data list
                tag_data_list.append({
                    "name": tag_name,
                    "description": tag_description if tag_description else None
                })
            except TimeoutException:
                print(f"No description found for {tag_name}")
                # If there's no description element, add the tag with a null description
                tag_data_list.append({
                    "name": tag_name,
                    "description": None
                })
            except Exception as e:
                print(f"Error processing {tag_name}: {str(e)}")
                # If there's any other error, add the tag with a null description
                tag_data_list.append({
                    "name": tag_name,
                    "description": None
                })
            
            # Close the current tab and switch back to the main page
            driver.close()
            driver.switch_to.window(main_window)
            
            # Add a small delay to avoid being blocked
            time.sleep(0.5)  # Reduced from 1 second to 0.5 seconds
        
        # Save all data to a JSON file
        with open('tag_descriptions.json', 'w', encoding='utf-8') as json_file:
            json.dump(tag_data_list, json_file, ensure_ascii=False, indent=4)
        
        print("Scraping completed. Results saved in tag_descriptions.json")
    
    finally:
        # Make sure to close the browser when done
        driver.quit()

if __name__ == "__main__":
    scrape_tags()