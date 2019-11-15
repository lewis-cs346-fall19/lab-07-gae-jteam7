import webapp2
import MySQLdb
import passwords
import random

class MainPage(webapp2.RequestHandler):
	def get(self):
		cookie = self.request.cookies.get("cookie_name")
		conn = MySQLdb.connect(unix_socket = passwords.SQL_HOST, user = passwords.SQL_USER, passwd = passwords.SQL_PASSWD, db = "animus")
		if not cookie:
			id = "%032x" % random.getrandbits(128)
			cursor = conn.cursor()
			cursor.execute("INSERT INTO sessions(id) VALUES(%s)", (id, ))
			cursor.close()
			conn.commit()
			self.response.set_cookie("cookie_name", id, max_age = 1800)
			output = '''<html><title>Create a Username</title><body><form action="/">Create a username: <input type="text" name="username" maxlength="20"><br><input type="submit"></form>
</body></html>'''
		else:
			username = self.request.get("username")
			if username != "":
				cursor = conn.cursor()
				cursor.execute("UPDATE sessions SET username=%s WHERE id=%s", (username, cookie))
				cursor.close()
				conn.commit()
			else:
				cursor = conn.cursor()
				cursor.execute("SELECT username FROM sessions WHERE id=%s", (cookie, ))
				username = cursor.fetchall()[0]
				cursor.close()
			cursor = conn.cursor()
			cursor.execute("SELECT count FROM counts WHERE username=%s", (username, ))
			count = cursor.fetchall()
			if len(count) == 0:
				count = 0
			else:
				count = count[0][0]
			cursor.close()
			if self.request.get("increment") == "1":
				if count == 0:
					cursor = conn.cursor()
					cursor.execute("INSERT INTO counts(username, count) VALUES(%s, %s)", (username, 1))
					cursor.close()
					conn.commit()
				else:
					cursor = conn.cursor()
					cursor.execute("UPDATE counts SET count=count+1 WHERE username=%s", (username, ))
					cursor.close()
					conn.commit()
				count += 1
			output = '''<html><title>Press the Button</title><body>Current value: {}<br><form action="/"><input type="hidden" name="increment" value="1">
<input type="submit" value="Increment"></form></body></html>'''.format(count)
		self.response.headers["Content-Type"] = "text/html"
		self.response.write(output)

app = webapp2.WSGIApplication([
	("/", MainPage),
], debug = True)
