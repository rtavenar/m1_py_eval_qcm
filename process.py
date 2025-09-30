import os
import csv
from datetime import datetime

data_dir = "data"
deadlines_path = os.path.join(data_dir, "deadlines.csv")
resultats_par_fichier = {}

# Lecture des deadlines
deadlines = {}
with open(deadlines_path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        # On convertit la deadline en datetime
        deadlines[row['NOM_FICHIER']] = datetime.strptime(row['DEADLINE'], "%d/%m/%Y %H:%M")

for filename in os.listdir(data_dir):
    if filename.endswith("notes.csv") and filename in deadlines:
        filepath = os.path.join(data_dir, filename)
        deadline = deadlines[filename]
        resultats = {}
        with open(filepath, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            # Colonnes utiles
            col_statut = header.index("Statut")
            col_termine = header.index("Terminé")
            for i, col in enumerate(header):
                if col.startswith("Note/"):
                    col_note = i
                    note_max = float(col.split("/")[1].replace('"', '').replace(',', '.'))
                    break
            # Parcourir les lignes
            for row in reader:
                if row[0] == 'Moyenne globale':
                    break
                statut = row[col_statut]
                if statut != "Terminée":
                    continue
                date_fin_str = row[col_termine].strip()
                # Remplacement des mois français par anglais
                mois_fr_en = {
                    "janvier": "January", "février": "February", "mars": "March", "avril": "April",
                    "mai": "May", "juin": "June", "juillet": "July", "août": "August",
                    "septembre": "September", "octobre": "October", "novembre": "November", "décembre": "December"
                }
                for fr, en in mois_fr_en.items():
                    if fr in date_fin_str:
                        date_fin_str = date_fin_str.replace(fr, en)
                        break
                try:
                    date_fin = datetime.strptime(date_fin_str, "%d %B %Y  %H:%M")
                except Exception:
                    print(f"Impossible de parser la date {date_fin_str} dans la ligne {row}")
                    continue
                if date_fin > deadline:
                    continue
                num_etudiant = row[2]
                try:
                    note = float(row[col_note].replace(',', '.'))
                except ValueError:
                    continue
                if num_etudiant not in resultats:
                    resultats[num_etudiant] = []
                resultats[num_etudiant].append(note == note_max)
        # Pour chaque étudiant, ne retenir qu'une seule réponse : 
        # True si au moins une tentative a la note max, False sinon
        resultats_par_fichier[filename] = {num: any(notes) for num, notes in resultats.items()}

# Inverser la structure : pour chaque numéro étudiant, le nb de True
etudiants = {}
for fichier, res in resultats_par_fichier.items():
    for num, val in res.items():
        etudiants[num] = etudiants.get(num, 0) + int(val)

# Écrire dans le fichier de sortie la liste des étudiants qui ont le point de bonus
# Pour avoir le point de bonus, il faut être dans les clous dans au moins
# n - 2 QCM, n étant le nombre total de QCM (on accorde de la flexibilité sur les 
# deux premiers QCM)
with open("output/list_etu.csv", "w") as fp:
    fp.write(f"NUMETU;NOMBRE_QCM_VALIDES\n")
    for num, vals in etudiants.items():
        if vals >= len(deadlines) - 2:
            fp.write(f"{num};{vals}\n")