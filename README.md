# Download the registers

Be sure stay in the "database" path. To download the registers and prepare the format, execute:

```
python download_padron.py
```

# Upload the registers

To update the database with the registers previously obtained. Prepare the environment with:

```
npm install -g node-firestore-import-export 
```

For more information read the [documentation](https://www.npmjs.com/package/node-firestore-import-export?activeTab=readme)

Then, execute the command to upload the registers to th database:

```
firestore-import -a key.json -b database.json
```

For more information read the [documentation](https://firebase.google.com/docs/firestore/manage-data/export-import)
