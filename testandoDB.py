import sqlite3

connection = sqlite3.connect('logs.db')

cursor = connection.cursor()

# Certifique-se de que o valor da data está entre aspas, já que é um TEXT.
cursor.execute("DELETE FROM log WHERE date = '2024-12-03'")

# Não há necessidade de fetchall(), pois DELETE não retorna dados.
connection.commit()  # Não se esqueça de fazer commit para persistir a mudança!

cursor.close()
connection.close()