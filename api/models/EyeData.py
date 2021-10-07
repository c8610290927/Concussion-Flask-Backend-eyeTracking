from api.utils.database import db, ma

class EyeTrackingData(db.Model):
    __tablename__ = 'EyeTrackingRawData'
    uid = db.Column(db.BIGINT, primary_key=True, nullable=False)
    gameid = db.Column(db.String(100), nullable=False)
    sessionid = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    time_stamp = db.Column(db.Float, nullable=False)
    position_x = db.Column(db.Float, nullable=False)
    position_y = db.Column(db.Float, nullable=False)
    position_z = db.Column(db.Float, nullable=False)
    openness_left = db.Column(db.Float, nullable=False)
    openness_right = db.Column(db.Float, nullable=False)

    def __init__(self, gameid, sessionid, username, time_stamp, position_x, position_y, position_z, openness_left, openness_right):
        self.gameid = gameid
        self.sessionid = sessionid
        self.username = username
        self.time_stamp = time_stamp
        self.position_x = position_x
        self.position_y = position_y
        self.position_z = position_z
        self.openness_left = openness_left
        self.openness_right = openness_right

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return '<Post %r data>' % self.username

class EyeTrackingDataSchema(ma.SQLAlchemyAutoSchema):
    """
    SQLAlchemySchema automatically generates fields
    """

    class Meta:
        model = EyeTrackingData
        sqla_session = db.session
        load_instance = True


