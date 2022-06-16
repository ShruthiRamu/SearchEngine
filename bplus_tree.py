import sqlite3

byte_offsets = [i for i in range(0, 25, 4)]
print(byte_offsets)
terms = ["angels", "baseball", "connect", "best", "to", "far", "cat"]

conn = sqlite3.connect("term_byteposition.db")

c = conn.cursor()
try:
    c.execute("""CREATE TABLE termBytePositions (
             term text, 
             byte_position integer
              )""")

    for term, byte in zip(terms, byte_offsets):
        # Add Term -> Start byte position
        with conn:
            c.execute("INSERT INTO termBytePositions VALUES (:term, :byte_position)",
              {'term': term, 'byte_position': byte})

except sqlite3.OperationalError:
    pass

search_term = 'connect'
c.execute("SELECT byte_position FROM termBytePositions WHERE term=:term",
          {'term': search_term})
#print("Fetching All: ", c.fetchall())
print("Fetching One: ", c.fetchone() )
