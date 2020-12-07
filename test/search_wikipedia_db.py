from pathlib import Path
import re
import json

import pymysql

def fetch_wikis():
    titles = set()
    db = pymysql.connect(host="10.176.64.33", 
                        user="root",
                        passwd="123456", 
                        db="wikipedia-test", 
                        port=3306,
                        charset='utf8'
                        )
    cursor = db.cursor(pymysql.cursors.SSCursor)
    sql = "SELECT * FROM page WHERE page_id=260 LIMIT 10"
    cursor.execute(sql)
    record = cursor.fetchone()
    while record is not None:
        page_id, page_namespace, page_title, page_restrictions, page_is_redirect, page_is_new, page_random, page_touched, page_links_updated, page_latest, page_len, page_content_model, page_lang = record
        titles.add(page_title.decode())
        print(page_title.decode())
        record = cursor.fetchone()
    cursor.close()
    db.close()
    return titles
 

if __name__ == "__main__":
    titles = fetch_wikis()
    # print(list(titles)[2000])
    # with Path("output/results.json").open("w", encoding="utf-8") as f:
    #     json.dump(results, f, indent=4)
