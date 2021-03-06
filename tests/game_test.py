from nekoyume.models import Move, User
from nekoyume.game import get_unconfirmed_move

def test_login(fx_test_client):
    rv = fx_test_client.post('/login', data={
        'private_key': 'test'
    }, follow_redirects=False)

    assert rv.status == '302 FOUND'


def test_new_character_creation(fx_test_client, fx_session):
    fx_test_client.post('/login', data={
        'private_key': 'test'
    }, follow_redirects=True)

    assert fx_session.query(Move).filter_by(
        user=User('test').address,
        name='create_novice'
    ).first()


def test_move(fx_test_client, fx_session, fx_user):
    rv = fx_test_client.post('/login', data={
        'private_key': 'test'
    }, follow_redirects=True)
    rv = fx_test_client.post('/new')
    fx_user.create_block(fx_session.query(Move).filter_by(block_id=None))

    rv = fx_test_client.get('/')
    assert rv.status == '200 OK'
    assert fx_user.address.encode() in rv.data

    rv = fx_test_client.post('/session_moves', data={
        'name': 'hack_and_slash'
    }, follow_redirects=True)
    assert rv.status == '200 OK'
    fx_user.create_block(fx_session.query(Move).filter_by(block_id=None))

    rv = fx_test_client.post('/session_moves', data={
        'name': 'sleep'
    }, follow_redirects=True)
    assert rv.status == '200 OK'
    fx_user.create_block(fx_session.query(Move).filter_by(block_id=None))

    rv = fx_test_client.post('/session_moves', data={
        'name': 'say',
        'content': 'hi!',
    }, follow_redirects=True)
    assert rv.status == '200 OK'
    fx_user.create_block(fx_session.query(Move).filter_by(block_id=None))


def test_logout(fx_test_client, fx_session, fx_user):
    rv = fx_test_client.post('/login', data={
        'private_key': 'test'
    }, follow_redirects=True)

    rv = fx_test_client.get('/logout')
    rv = fx_test_client.get('/')
    assert rv.status == '302 FOUND'


def test_get_unconfirmed_move(fx_session, fx_user, fx_novice_status):
    assert not get_unconfirmed_move(fx_user.address)
    move = fx_user.create_novice(fx_novice_status)
    assert get_unconfirmed_move(fx_user.address)
    # invalid move should not be recognized as unconfirmed move
    move.id = ('00000000000000000000000000000000'
               '00000000000000000000000000000000')
    assert not get_unconfirmed_move(fx_user.address)
