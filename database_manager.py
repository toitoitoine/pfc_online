import sqlite3

def initialiser_bdd():
    conn = sqlite3.connect('pfc_game.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS joueurs (
            nom TEXT PRIMARY KEY,
            elo REAL DEFAULT 1200
        )
    ''')
    conn.commit()
    conn.close()

def obtenir_ou_creer_joueur(nom):
    conn = sqlite3.connect('pfc_game.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nom, elo FROM joueurs WHERE nom = ?", (nom,))
    joueur = cursor.fetchone()
    
    if joueur is None:
        cursor.execute("INSERT INTO joueurs (nom, elo) VALUES (?, ?)", (nom, 1200.0))
        conn.commit()
        joueur = (nom, 1200.0)
    
    conn.close()
    return {'nom': joueur[0], 'elo': joueur[1]}

def calculer_nouveau_elo(j1, j2, score_j1, k=32):
    probabilite_j1 = 1 / (1 + 10 ** ((j2['elo'] - j1['elo']) / 400))
    nouvel_elo_j1 = j1['elo'] + k * (score_j1 - probabilite_j1)
    nouvel_elo_j2 = j2['elo'] + k * ((1 - score_j1) - (1 - probabilite_j1))
    
    conn = sqlite3.connect('pfc_game.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE joueurs SET elo = ? WHERE nom = ?", (nouvel_elo_j1, j1['nom']))
    cursor.execute("UPDATE joueurs SET elo = ? WHERE nom = ?", (nouvel_elo_j2, j2['nom']))
    conn.commit()
    conn.close()
    
    return round(nouvel_elo_j1, 1), round(nouvel_elo_j2, 1)