from .__init__ import mysql

def execute_query(query, one=False):
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    result = cursor.fetchone() if one else cursor.fetchall()
    cursor.close()
    mysql.connection.commit()

    return result

def clear_tables(sure=False):
    if sure:
        execute_query(
                   
        )
