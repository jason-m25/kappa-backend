from app import db, ma


class GraphPoint:
    added_date = db.Date
    rate = db.Float

    def __init__(self, added_date, rate):
        self.added_date = added_date
        self.rate = rate


class GraphPointSchema(ma.Schema):
    class Meta:
        fields = ("added_date", "rate")
        model = GraphPoint


graph_point_schema = GraphPointSchema()
graph_schema = GraphPointSchema(many=True)
