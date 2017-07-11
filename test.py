import dbf
with dbf.Table("result.dbf") as db:
    dbf.export(db, "test.csv" ,header=True)
