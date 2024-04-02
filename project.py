from flask import Flask, jsonify, request
import sqlite3

user_connection = sqlite3.connect("user.db")
user_cursor = user_connection.cursor()
user_cursor.execute("CREATE TABLE IF NOT EXISTS registration (name TEXT, surname TEXT)")
user_cursor.close()
user_connection.close()

message_connection = sqlite3.connect("message.db")
message_cursor = message_connection.cursor()
message_cursor.execute("CREATE TABLE IF NOT EXISTS message (from_person TEXT, to_person TEXT, content TEXT)")
message_cursor.close()
message_connection.close()

app = Flask(__name__)

@app.route('/create-user', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data["name"]
    surname = data["surname"]

    connection = sqlite3.connect("user.db")
    cursor = connection.cursor()

    cursor.execute("""INSERT INTO registration VALUES (?,?)""", (name, surname))
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify(name, surname)

def check_user(name, user_cursor):
    user_cursor.execute("""SELECT * FROM registration WHERE name = ? """, (name,))
    if not user_cursor.fetchone():
        return False
    return True

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.get_json()
    from_person = data["from_person"]
    to_person = data["to_person"]
    content = data["content"]

    user_connection = sqlite3.connect("user.db")
    user_cursor = user_connection.cursor()

    value = check_user(from_person, user_cursor)
    value_2 = check_user(to_person, user_cursor)

    if value is False and value_2 is False:
        return jsonify(False)

    message_connection = sqlite3.connect("message.db")
    message_cursor = message_connection.cursor()

    message_cursor.execute("""INSERT INTO message VALUES (?,?,?)""", (from_person, to_person, content))
    message_connection.commit()

    user_cursor.close()
    user_connection.close()

    message_cursor.close()
    message_connection.close()

    return jsonify(True)


@app.route('/check-message/<who_you_are>', methods=['GET'])
def check_message(who_you_are):
    connection = sqlite3.connect("message.db")
    cursor = connection.cursor()

    result = cursor.execute("""SELECT * FROM message WHERE to_person = ?""", (who_you_are,))
    messages = result.fetchall().copy()

    cursor.execute("""DELETE FROM message WHERE to_person = ?""", (who_you_are,))
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify(messages)


if __name__ == '__main__':
    app.run(port=None)
