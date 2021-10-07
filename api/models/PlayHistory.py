from api.utils.database import db, ma

class PlayHistory(db.Model):
    __tablename__ = 'PlayHistory'
    username = db.Column(db.String(100), primary_key=True, nullable=False)
    gameid = db.Column(db.String(100), primary_key=True, nullable=False)
    sessionid = db.Column(db.String(100), primary_key=True, nullable=False)

    def __init__(self, gameid, sessionid, username):
        self.gameid = gameid
        self.sessionid = sessionid
        self.username = username

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return '<Post %r data>' % self.username


class PlayHistorySchema(ma.SQLAlchemyAutoSchema):
    """
    SQLAlchemySchema automatically generates fields
    """

    class Meta:
        model = PlayHistory
        sqla_session = db.session
        load_instance = True
