from flask import jsonify, g
from app import db, app
from app.models import Doctor
from app.auth import basic_auth, token_auth

@app.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = g.current_user.get_token()
    id = g.current_user.id
    db.session.commit()
    return jsonify({
        'code': 200,
        'id': id,
        'token': token,
        'im_token': g.current_user.im_token,
        'name': g.current_user.name})

@app.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    g.current_user.revoke_token()
    db.session.commit()
    return '', 204