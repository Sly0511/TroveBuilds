from flet import ResponsiveRow, DataTable, DataColumn, DataRow, DataCell, Text
from models.objects import Controller


class MarketplaceController(Controller):
    def setup_controls(self):
        self.page = ResponsiveRow()
        self.listings = DataTable(
            columns=[
                DataColumn(Text("ID")),
                DataColumn(Text("Item")),
                DataColumn(Text("Price")),
                DataColumn(Text("Fee")),
                DataColumn(Text("Tax")),
                DataColumn(Text("Profit")),
            ]
        )

    def setup_events(self):
        ...