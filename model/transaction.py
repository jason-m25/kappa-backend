from app import db, ma, datetime


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usd_amount = db.Column(db.Float, nullable=True)
    lbp_amount = db.Column(db.Float, nullable=True)
    usd_to_lbp = db.Column(db.Boolean)
    added_datetime = db.Column(db.DateTime)
    added_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __init__(self, usd_amount, lbp_amount, usd_to_lbp, user_id):
        super(Transaction, self).__init__(usd_amount=usd_amount,
                                          lbp_amount=lbp_amount,
                                          usd_to_lbp=usd_to_lbp,
                                          user_id=user_id,
                                          added_datetime=datetime.datetime.now(),
                                          added_date=datetime.date.today())


class TransactionSchema(ma.Schema):
    class Meta:
        fields = ("id", "usd_amount", "lbp_amount", "usd_to_lbp", "added_datetime", "user_id")
        model = Transaction


transaction_schema = TransactionSchema()
transactions_schema = TransactionSchema(many=True)
