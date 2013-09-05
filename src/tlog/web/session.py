from tlog import utils
from tlog.base.user import User
from tlog import models
from tlog.decorators import new_session
from datetime import datetime, timedelta

class Session(object):
    '''
    Session handler for the web interface.
    '''

    @classmethod
    def new(cls, user_id, expire_days=30):
        '''
        Creats a session for a user, which expires in `days` days.
        Returns a random generated session key, use this to find the session again.

        :param user_id: int
        :param days: int - default: 30
        :return: str
        '''
        with new_session() as session:
            ws = utils.random_key()
            s = models.Web_session(
                session=ws,
                user_id=user_id,
                expires=datetime.utcnow()+timedelta(days=expire_days),
            )
            session.add(s)
            session.commit()
            return ws

    @classmethod
    def delete(cls, session_id):
        '''
        Removes a user's session from the database.

        :param session_id: str
        :returns: boolean
        '''
        with new_session() as session:
            session.query(
                models.Web_session,
            ).filter(
                models.Web_session.session==session_id,
            ).delete()
            session.commit()
            return True

    @classmethod
    def get(cls, session_id):
        '''
        Retrives a user by its session.

        :param session: str
        :returns: tlog.base.user.User
        '''
        with new_session() as session:
            query = session.query(
                models.Web_session,
            ).filter(
                models.Web_session.session==session_id,
                models.Web_session.expires>=datetime.utcnow(),
            ).first()
            if not query: 
                return None
            return User.get(id_=query.user_id)