from Layout.data_structures import AppDependencies
from ui.Sales.services.DataService import DataService

def _build_data_service(deps: AppDependencies, can_edit_price: bool) -> DataService:
    return DataService(
        deps.products_db,
        deps.customers_db,
        deps.stock_movements_db,
        deps.sales_db,
        deps.sale_items_db,
        deps.settings,
        can_edit_price,
    )