from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
import jwt
import datetime
import statistics
from db_config import DB_CONFIG


app = Flask(__name__)
bcrypt = Bcrypt(app)
ma = Marshmallow(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONFIG
CORS(app)
db = SQLAlchemy(app)
SECRET_KEY = "b'|\xe7\xbfU3`\xc4\xec\xa7\xa9zf:}\xb5\xc7\xb9\x139^3@Dv'"


from model.user import User, user_schema
from model.transaction import Transaction, transaction_schema, transactions_schema
from model.listing import Listing, listing_schema, listings_schema
from model.graphpoint import GraphPoint, graph_schema


def create_token(user_id):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=4),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm='HS256'
    )


def extract_auth_token(authenticated_request):
    auth_header = authenticated_request.headers.get('Authorization')
    if auth_header:
        return auth_header.split(" ")[1]
    else:
        return None


def decode_token(token):
    payload = jwt.decode(token, SECRET_KEY, 'HS256')
    return payload['sub']


@app.route('/user', methods=['POST'])
def user():
    _json = request.json
    user_name = _json['user_name']
    password = _json['password']
    new_user = User(user_name, password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify(user_schema.dump(new_user))


@app.route('/authentication', methods=['POST'])
def authentication():
    _json = request.json
    user_name = _json['user_name']
    password = _json['password']
    if (user_name == None or password == None):
        abort(400)
    else:
        userFilter = User.query.filter_by(user_name=user_name).first()
        if userFilter == None:
            abort(403)
        elif (bcrypt.check_password_hash(userFilter.hashed_password, password)):
            newToken = create_token(userFilter.id)
            return jsonify({"token": newToken})
        else:
            abort(403)


@app.route('/transaction', methods=['POST', 'GET'])
def transaction():
    if request.method == 'POST':
        _json = request.json
        usd_amount = _json['usd_amount']
        lbp_amount = _json['lbp_amount']
        usd_to_lbp = _json['usd_to_lbp']
        isToken = extract_auth_token(request)

        if isToken:
            try:
                user_id = decode_token(isToken)
                new_transaction = Transaction(usd_amount, lbp_amount, usd_to_lbp, user_id)
            except jwt.ExpiredSignatureError:
                abort(403)
            except jwt.InvalidTokenError:
                abort(403)
        else:
            new_transaction = Transaction(usd_amount, lbp_amount, usd_to_lbp, None)

        db.session.add(new_transaction)
        db.session.commit()

        return jsonify(transaction_schema.dump(new_transaction))

    elif request.method == 'GET':
        isToken = extract_auth_token(request)
        if isToken:
            try:
                user_id = decode_token(isToken)
                transactionFilter = Transaction.query.filter_by(user_id=user_id).all()
                return jsonify(transactions_schema.dump(transactionFilter))
            except jwt.ExpiredSignatureError:
                abort(403)
            except jwt.InvalidTokenError:
                abort(403)
        else:
            abort(403)


@app.route('/listing', methods=['POST', 'GET'])
def listing():
    if request.method == 'POST':
        _json = request.json
        id = _json['id']
        user2_phone = _json['user2_phone']
        listingFilter = Listing.query.filter_by(id=id).first()
        listingFilter.user2_phone = user2_phone
        db.session.commit()
        return jsonify(listing_schema.dump(listingFilter))

    elif request.method == 'GET':
        allListings = Listing.query.all()
        return jsonify(listings_schema.dump(allListings))


@app.route('/userListing', methods=['POST', 'GET', 'DELETE'])
def userListing():
    if request.method == 'POST':
        isToken = extract_auth_token(request)
        if isToken:
            try:
                user_id = decode_token(isToken)
                _json = request.json
                ad_amount = _json['ad_amount']
                ad_type = _json['ad_type']
                ask_amount = _json['ask_amount']

                new_listing = Listing(user_id, None, ad_amount, ad_type, ask_amount)
                db.session.add(new_listing)
                db.session.commit()
                return jsonify(listing_schema.dump(new_listing))
            except jwt.ExpiredSignatureError:
                abort(403)
            except jwt.InvalidTokenError:
                abort(403)
        else:
            abort(403)

    elif request.method == 'GET':
        isToken = extract_auth_token(request)
        if isToken:
            try:
                user_id = decode_token(isToken)
                listingFilter = Listing.query.filter_by(user_id=user_id).all()
                return jsonify(listings_schema.dump(listingFilter))
            except jwt.ExpiredSignatureError:
                abort(403)
            except jwt.InvalidTokenError:
                abort(403)
        else:
            abort(403)

    elif request.method == 'DELETE':
        isToken = extract_auth_token(request)
        if isToken:
            try:
                user_id = decode_token(isToken)
                _json = request.json
                id = _json['id']
                Listing.query.filter_by(id=id).delete()
                db.session.commit()
                listingFilter = Listing.query.filter_by(user_id=user_id).all()
                return jsonify(listings_schema.dump(listingFilter))
            except jwt.ExpiredSignatureError:
                abort(403)
            except jwt.InvalidTokenError:
                abort(403)
        else:
            abort(403)


@app.route('/buyGraph', methods=['GET'])
def buyGraph():
    buyTransactions = db.session.query(Transaction).filter(Transaction.usd_to_lbp == False).group_by(Transaction.added_date).all()
    buyPoints = []
    for i in buyTransactions:
        newPoint = GraphPoint(i.added_date, (i.lbp_amount / i.usd_amount))
        buyPoints.append(newPoint)

    return jsonify(graph_schema.dump(buyPoints))


@app.route('/sellGraph', methods=['GET'])
def sellGraph():
    sellTransactions = db.session.query(Transaction).filter(Transaction.usd_to_lbp == True).group_by(Transaction.added_date).all()
    sellPoints = []
    for i in sellTransactions:
        newPoint = GraphPoint(i.added_date, (i.lbp_amount / i.usd_amount))
        sellPoints.append(newPoint)

    return jsonify(graph_schema.dump(sellPoints))


@app.route('/exchangeRate', methods=['GET'])
def exchangeRate():
    THREE_DAY_START_DATE = datetime.datetime.now() - datetime.timedelta(hours=72)
    SEVEN_DAY_START_DATE = datetime.datetime.now() - datetime.timedelta(days=7)
    DAY_AGO = datetime.datetime.now() - datetime.timedelta(hours=24)
    TREND_START_TIME = datetime.datetime.now() - datetime.timedelta(hours=6)
    NOW = datetime.datetime.now()

    ThreeDayBuyFilter = Transaction.query.filter(Transaction.added_datetime.between(THREE_DAY_START_DATE, NOW), Transaction.usd_to_lbp == False).all()
    ThreeDayBuyTransactions = []
    for row in ThreeDayBuyFilter:
        ThreeDayBuyTransactions.append(row.lbp_amount / row.usd_amount)

    if not ThreeDayBuyTransactions:
        THREE_DAY_BUY_AVG = None
    else:
        THREE_DAY_BUY_AVG = sum(ThreeDayBuyTransactions) / len(ThreeDayBuyTransactions)

    ThreeDaySellFilter = Transaction.query.filter(Transaction.added_datetime.between(THREE_DAY_START_DATE, NOW),
                                          Transaction.usd_to_lbp == True).all()
    ThreeDaySellTransactions = []
    for block in ThreeDaySellFilter:
        ThreeDaySellTransactions.append(block.lbp_amount / block.usd_amount)

    if not ThreeDaySellTransactions:
        THREE_DAY_SELL_AVG = None
    else:
        THREE_DAY_SELL_AVG = sum(ThreeDaySellTransactions) / len(ThreeDaySellTransactions)

    SevenDayBuyFilter = Transaction.query.filter(Transaction.added_datetime.between(SEVEN_DAY_START_DATE, NOW),
                                               Transaction.usd_to_lbp == False).all()
    SevenDayBuyTransactions = []
    for row in SevenDayBuyFilter:
        SevenDayBuyTransactions.append(row.lbp_amount / row.usd_amount)

    if not SevenDayBuyTransactions:
        SEVEN_DAY_BUY_AVG = None
        BUY_ST_DEV = None
    else:
        SEVEN_DAY_BUY_AVG = sum(SevenDayBuyTransactions) / len(SevenDayBuyTransactions)
        BUY_ST_DEV = statistics.stdev(SevenDayBuyTransactions)

    SevenDaySellFilter = Transaction.query.filter(Transaction.added_datetime.between(SEVEN_DAY_START_DATE, NOW),
                                                Transaction.usd_to_lbp == True).all()
    SevenDaySellTransactions = []
    for row in SevenDaySellFilter:
        SevenDaySellTransactions.append(row.lbp_amount / row.usd_amount)

    if not SevenDaySellTransactions:
        SEVEN_DAY_SELL_AVG = None
        SELL_ST_DEV = None
    else:
        SEVEN_DAY_SELL_AVG = sum(SevenDaySellTransactions) / len(SevenDaySellTransactions)
        SELL_ST_DEV = statistics.stdev(SevenDaySellTransactions)

    allTransactions = Transaction.query.all()
    ALL_TIME_USD_VOLUME = 0
    ALL_TIME_LBP_VOLUME = 0
    for row in allTransactions:
        ALL_TIME_USD_VOLUME += row.usd_amount
        ALL_TIME_LBP_VOLUME += row.lbp_amount

    pastDayTransactions = Transaction.query.filter(Transaction.added_datetime.between(DAY_AGO, NOW)).all()
    LAST_DAY_USD_VOLUME = 0
    LAST_DAY_LBP_VOLUME = 0
    for row in pastDayTransactions:
        LAST_DAY_USD_VOLUME += row.usd_amount
        LAST_DAY_LBP_VOLUME += row.lbp_amount

    BuyTrendFilter = Transaction.query.filter(Transaction.added_datetime.between(TREND_START_TIME, NOW),
                                               Transaction.usd_to_lbp == False).all()
    if (BuyTrendFilter[-1].lbp_amount / BuyTrendFilter[-1].usd_amount) - (BuyTrendFilter[0].lbp_amount / BuyTrendFilter[0].usd_amount) >= 0:
        BUY_TREND = True
    else:
        BUY_TREND = False

    SellTrendFilter = Transaction.query.filter(Transaction.added_datetime.between(TREND_START_TIME, NOW),
                                              Transaction.usd_to_lbp == True).all()
    if (SellTrendFilter[-1].lbp_amount / SellTrendFilter[-1].usd_amount) - (SellTrendFilter[0].lbp_amount / SellTrendFilter[0].usd_amount) >= 0:
        SELL_TREND = True
    else:
        SELL_TREND = False

    return jsonify({
        "usd_to_lbp": THREE_DAY_SELL_AVG,
        "lbp_to_usd": THREE_DAY_BUY_AVG,
        "7day_usd_to_lbp": SEVEN_DAY_SELL_AVG,
        "7day_lbp_to_usd": SEVEN_DAY_BUY_AVG,
        "all_time_usd_volume": ALL_TIME_USD_VOLUME,
        "all_time_lbp_volume": ALL_TIME_LBP_VOLUME,
        "last_day_usd_volume": LAST_DAY_USD_VOLUME,
        "last_day_lbp_volume": LAST_DAY_LBP_VOLUME,
        "lbp_to_usd_trend": BUY_TREND,
        "usd_to_lbp_trend": SELL_TREND,
        "lbp_to_usd_stdev": BUY_ST_DEV,
        "usd_to_lbp_stdev": SELL_ST_DEV
    })
