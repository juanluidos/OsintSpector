from utils.Intelx.intelexapi import intelx as intel

def  phonebooksearch(target):
    intelx = intel()
    search = intelx.search(target)
    for record in search['records']:
        print(f"Found media type {record['media']} in {record['bucket']}")
    return search