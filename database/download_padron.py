import requests  # pip install requests
import zipfile
import os
import difflib
from tqdm import tqdm  # pip install tqdm
import sqlite3
import time
import datetime

# capture init time
start_time = time.time()
now = datetime.datetime.now()
print("Time begin: ", now)

# constants
padron_folder_new = "padron_new"
diff_filename = padron_folder_new + "/" + "diff.txt"
diff_add_filename = padron_folder_new + "/" + "diff_add.txt"
diff_sub_filename = padron_folder_new + "/" + "diff_sub.txt"
diff_del_filename = padron_folder_new + "/" + "diff_del.txt"

padron_folder_old = "padron"
padron_filename = "PADRON_COMPLETO.txt"
padron_dir_old = padron_folder_old + "/" + padron_filename
padron_dir_new = padron_folder_new + "/" + padron_filename

padron_filename_zip = "padron.zip"
padron_dir_zip = padron_folder_new + "/" + padron_filename_zip

db_add = padron_folder_new + "/" + "db_add.db"
db_sub = padron_folder_new + "/" + "db_sub.db"

url = "https://www.tse.go.cr/zip/padron/padron_completo.zip"

# create directories
if not os.path.exists(padron_folder_old):
    print("Folder: <", padron_folder_old, "> doesn't exist")
    exit(0)

if not os.path.exists(padron_folder_new):
    os.makedirs(padron_folder_new)

if os.path.exists(db_add):
    os.remove(db_add)

if os.path.exists(db_sub):
    os.remove(db_sub)

# download file
response = requests.get(url, allow_redirects=True, stream=True)
padron_size = int(response.headers.get("content-length", 0))
print("downloading... [1/8]")
with open(padron_dir_zip, "wb") as target:
    with tqdm(total=padron_size, unit="B", unit_scale=True) as progress_bar:
        for data in response.iter_content(chunk_size=4096):
            target.write(data)
            progress_bar.update(len(data))

# unzip file
print("unzipping... [2/8]")
with zipfile.ZipFile(padron_dir_zip, "r") as zip_ref:
    zip_ref.extractall(padron_folder_new)

# check difference
print("open files... [3/8]")
with open(padron_dir_old, "r") as f1, open(padron_dir_new, "r") as f2:
    content_1 = f1.readlines()
    content_2 = f2.readlines()

# calculate diff
print("calculate difference between files... [4/8]")
diff_add = difflib.ndiff(content_1, content_2)
diff_sub = difflib.ndiff(content_1, content_2)
diff_add = [line[2:] for line in diff_add if line.startswith("+ ")]
diff_sub = [line[2:] for line in diff_sub if line.startswith("- ")]

# save diff
print("saving differences... [5/8]")
with open(diff_add_filename, "w") as diff_add_file:
    diff_add_file.writelines(diff_add)

with open(diff_sub_filename, "w") as diff_sub_file:
    diff_sub_file.writelines(diff_sub)

# build "db_sub" and its table
print("preparing databases for check the deleted registers... [6/8]")
connection_sub = sqlite3.connect(db_sub)
cursor1 = connection_sub.cursor()
cursor1.execute(
    "CREATE TABLE IF NOT EXISTS data (att1 TEXT, att2 TEXT, att3 TEXT, att4 TEXT, att5 TEXT, att6 TEXT, att7 TEXT, att8 TEXT)"
)

# read "diff_sub_filename" and save registers to the DB
with open(diff_sub_filename, "r") as file:
    lines = file.readlines()
    for line in lines:
        attributes = line.strip().split(",")
        cursor1.execute("INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?, ?)", attributes)

# database checkpoint
connection_sub.commit()
connection_sub.close()

# build "db_add" and its table
connection_add = sqlite3.connect(db_add)
cursor2 = connection_add.cursor()
cursor2.execute(
    "CREATE TABLE IF NOT EXISTS data (att1 TEXT, att2 TEXT, att3 TEXT, att4 TEXT, att5 TEXT, att6 TEXT, att7 TEXT, att8 TEXT)"
)

# read "diff_add_filename" and save registers to the DB
with open(diff_add_filename, "r") as file:
    lines = file.readlines()
    for line in lines:
        attributes = line.strip().split(",")
        cursor2.execute("INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?, ?)", attributes)

# database checkpoint
connection_add.commit()
connection_add.close()

# prepare variables for connections
register_deleted = []
connection_sub = sqlite3.connect(db_sub)
cursor1 = connection_sub.cursor()
connection_add = sqlite3.connect(db_add)
cursor2 = connection_add.cursor()

# Get records from the first database that are not found in the second database
print("search registers... [7/8]")
cursor1.execute("SELECT * FROM data")
register_sub = cursor1.fetchall()
# for register in register_sub:
for register in tqdm(register_sub, desc="searching deleted register", unit="file"):
    cursor2.execute("SELECT * FROM data WHERE att1=?", (register[0],))
    if cursor2.fetchone() is None:
        register_deleted.append(register)

# save the registers
print("save the registers... [8/8]")
with open(diff_del_filename, "w") as file:
    for register in register_deleted:
        line = ",".join(register) + "\n"
        file.write(line)

# check the final time
execution_time = time.time() - start_time
hours = int(execution_time // 3600)
minutes = int((execution_time % 3600) // 60)
seconds = int(execution_time % 60)
execution_time = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
now = datetime.datetime.now()
print("Time end: ", now)
print("Total time: {}".format(execution_time))
