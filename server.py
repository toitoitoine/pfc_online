from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import database_manager as db

print("lancer connard")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pfc_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

db.initialiser_bdd()
file_d_attente = None 

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('jouer_coup')
def handle_coup(data):
    global file_d_attente
    nom = data.get('nom', 'Anonyme')
    coup = data.get('signe')
    sid = request.sid

    if file_d_attente is None:
        file_d_attente = {'nom': nom, 'signe': coup, 'sid': sid}
        emit('resultat', {'message': "En attente d'un adversaire..."})
    else:
        adv = file_d_attente
        file_d_attente = None
        
        if adv['signe'] == coup: res = 0.5
        elif (adv['signe'] == 'Pierre' and coup == 'Ciseaux') or \
             (adv['signe'] == 'Feuille' and coup == 'Pierre') or \
             (adv['signe'] == 'Ciseaux' and coup == 'Feuille'): res = 1
        else: res = 0

        elo1, elo2 = db.calculer_nouveau_elo(db.obtenir_ou_creer_joueur(adv['nom']), 
                                            db.obtenir_ou_creer_joueur(nom), res)

        emit('resultat', {'message': f"Contre {coup} ! Ton ELO: {elo1}", 'nouvel_elo': elo1}, room=adv['sid'])
        emit('resultat', {'message': f"Contre {adv['signe']} ! Ton ELO: {elo2}", 'nouvel_elo': elo2})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)