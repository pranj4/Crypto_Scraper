from playwright.sync_api import sync_playwright
import time
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",headless=False)  ## (CAN USE BRAVE FOR MORE SMOOTH OPENING)
        page = browser.new_page()
        page.goto('https://coinmarketcap.com/')
        page.wait_for_load_state('networkidle')

        page.wait_for_selector('div.cmc-body-wrapper table tbody tr')

        # Scrolling down
        for _ in range(3):
            page.mouse.wheel(0, 5000)
            page.wait_for_timeout(10000)

        # Extracting data
        trs_xpath = 'div.cmc-body-wrapper table tbody tr'
        tr_elements = page.locator(trs_xpath).all()

        # Creating a list to store coin dictionaries
        coin_list = []

        # Extracting information for each coin
        for tr in tr_elements:
            coin_data = {}
            # Using locators to find td elements within each tr
            td_elements = tr.locator('td').all()

            coin_data['id'] = td_elements[1].all_text_contents()
            coin_data['Name_Symbol'] = td_elements[2].all_text_contents()
            coin_data['Price_in_USD'] = td_elements[3].inner_text().replace('$','').replace(',','')
            #coin_data['Circulating_Supply'] = td_elements[9].all_text_contents()
            #coin_data['Market_Cap_USD'] = td_elements[7].inner_text(timeout=5000).replace('$','')
            #coin_data['Volume(24hr)'] = td_elements[8].all_inner_texts()


            # Appending coin dictionary to coin_list
            coin_list.append(coin_data)

            time.sleep(1)

        print("Number of coins scraped:", len(coin_list))

        list_of_tuples = [tuple(dict.values()) for dict in coin_list]

        # Generate a unique table name based on current timestamp
        table_name = f"coin_data_{datetime.now().strftime('%Y%m%d')}"

        # Connect to PostgreSQL database
        conn = psycopg2.connect(host='localhost', database='crypto_scraper_data', user='postgres',
                                password='iamgame25...')
        cursor = conn.cursor()

        # Create a new table with the unique table name
        create_table_query = f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id VARCHAR(5),
                Name_Symbol TEXT,
                Price_in_USD NUMERIC(15,3)
            )
        '''
        cursor.execute(create_table_query)

        # Insert the scraped data into the new table
        execute_values(cursor, f"INSERT INTO {table_name} (id, Name_Symbol, Price_in_USD) VALUES %s", list_of_tuples)

        print(f"Data added to {table_name} table successfully")

        conn.commit()

        conn.close()


        for el in coin_list:
            print(el)




            browser.close()


# Calling the main function and printing the result
if __name__ == "__main__":
    main()


