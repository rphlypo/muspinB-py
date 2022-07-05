#%%
# attention, ne pas mettre d'accents
import hashlib
import pandas as pd



subject = dict()
subject['prenom'] = input('Prénom sujet : ')
subject['nom'] = input('Nom sujet : ')
subject['date'] = input('Date de naissance sous forme AAAAMMJJ :')
subject['genre'] = input('Genre (F ou H) : ')


h = hashlib.sha256()
h.update('{}{}{}{}'.format(subject['prenom'].lower(),
                            subject['nom'].lower(),
                            subject['date'],
                            subject['genre'].lower()).encode())

subject_id = h.hexdigest()[:16]
df = pd.DataFrame([subject_id])
df.to_clipboard(index=False,header=False)
# subprocess.run('xclip', '-selection "clipboard"', universal_newlines=True, input=subject_id)
print("subject id {} succesfully copied to clipboard\nuse CTRL+V to paste the id in your favourite application".format(subject_id))
