import pymysql
import pickle
import os


def build_data():
    data = []
    for id, title in fetch_data():
        title = title.decode('utf8')
        data.append((id, title))
    print('build data successfully...')
    file_path = './output/page_title.pkl'
    if not os.path.exists(file_path):
        os.system(r"touch {}".format(file_path))
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)
    print('save data successfully...')


def fetch_data():
    db = pymysql.connect(host='10.176.34.89',
                         user='root',
                         passwd='123456',
                         db='wikipedia',
                         port=3306,
                         charset='utf8')
    cursor = db.cursor(pymysql.cursors.SSCursor)
    sql = 'SELECT page_id, page_title FROM page'
    cursor.execute(sql)
    record = cursor.fetchone()
    while record is not None:
        yield record
        record = cursor.fetchone()
    cursor.close()
    db.close()


if __name__ == '__main__':
    build_data()
