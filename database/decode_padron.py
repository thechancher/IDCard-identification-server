database_in = open("PADRON_COMPLETO.txt", "r")
database_out = open("database.json", "w+")

database_out.write('{"__collections__":{"padron":{')
for person in database_in:
    data = person.split(",")
    database_out.write('"' + data[0] + '":{')
    database_out.write('"CODE":"' + data[1] + '",')
    database_out.write('"DATE":"' + data[3] + '",')
    database_out.write('"NAME":"' + data[5].strip() + '",')
    database_out.write('"LAST1":"' + data[6].strip() + '",')
    database_out.write('"LAST2":"' + data[7].strip() + '",')
    database_out.write('"__collections__":{}')

    database_out.write("},")

database_in.close()

database_out.seek(0, 2)
position = database_out.tell() - 1
database_out.seek(position)
database_out.write(" ")

database_out.write("}}}")
database_out.close()
