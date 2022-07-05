#%%
# attention, ne pas mettre d'accents
import hashlib

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
print(h.hexdigest())
