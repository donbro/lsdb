#!/Users/donb/projects/VENV/mysql-connector-python/bin/python
# encoding: utf-8



import mysql.connector
from mysql.connector import errorcode


def main():
    
    config = {
    'user': 'scott',
    'password': 'tiger',
    'host': '127.0.0.1',
    'database': 'testt',
    'raise_on_warnings': True
    }
	
	try:
	    cnx = mysql.connector.connect(**config)
		
		print cnx
	
	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("Something is wrong your username or password")
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			print("Database %r does not exist.", config.database)
		else:
			print(err)
	else:
		cnx.close()
	
    
    # try:
    #     db = mysql.connector.connect(unix_socket='/tmp/mysql.sock', user='root', password='')
    # except mysql.connector.errors.InterfaceError, e:
    #     print e
    #     sys.exit(1)

#    console = MySQLConsole(db)
    # myconnpy_version = "%s-%s" % (
    #     '.'.join(map(str,mysql.connector.__version__[0:3])),
    #     mysql.connector.__version__[3])
	
	print "Your MySQL connection ID is %d." % (db.get_server_threadid())
	print "Server version: %s" % (db.get_server_info())
	# print "MySQL Connector/Python v%s" % (myconnpy_version)
	print


if __name__ == '__main__':
	main()

