import sqlite3
import random

connection = sqlite3.connect('grades.db')
cursor = connection.cursor()

cursor.execute('select * from students where groupa = ?', ('AVT-118',))
avt = cursor.fetchall()

cursor.execute('select * from students where groupa = ?', ('AA-76',))
aa = cursor.fetchall()

'''
i = 22
for stud in aa:
	cursor.execute('insert into grades values (?, ?, 1, ?, ?)', 
		(i, stud[0], random.randint(1, 50), random.randint(50, 100)))
	i += 1
	cursor.execute('insert into grades values (?, ?, 3, ?, ?)', 
		(i, stud[0], random.randint(1, 50), random.randint(25, 100)))
	i += 1
'''

cursor.execute('select * from grades')
gr = cursor.fetchall()

print(*gr, sep='\n')
print(len(avt), len(aa))

connection.commit()
connection.close()
