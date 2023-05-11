from searchScripts.buscarPersona.emailPhone.intelexapi import intelx as intel

def phonebooksearch(target):
    intelx = intel("8134168d-053b-4042-adbe-19ab981d82aa")
    search = intelx.phonebooksearch(target)
    for record in search['records']:
        print(f"Found media type {record['media']} in {record['bucket']}")
    return search