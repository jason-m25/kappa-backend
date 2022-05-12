from app import db, ma, datetime


class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user2_phone = db.Column(db.Integer, nullable=True)
    ad_amount = db.Column(db.Float)
    ad_type = db.Column(db.Boolean)
    ask_amount = db.Column(db.Float)
    added_datetime = db.Column(db.DateTime)

    def __init__(self, user_id, user2_phone, ad_amount, ad_type, ask_amount):
        super(Listing, self).__init__(user_id=user_id,
                                      user2_phone=user2_phone,
                                      ad_amount=ad_amount,
                                      ad_type=ad_type,
                                      ask_amount=ask_amount,
                                      added_datetime=datetime.datetime.now())


class ListingSchema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "user2_phone", "ad_amount", "ad_type", "ask_amount", "added_datetime")
        model = Listing


listing_schema = ListingSchema()
listings_schema = ListingSchema(many=True)
