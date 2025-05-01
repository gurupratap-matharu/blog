class BaseProvider:
    """
    Abstract base class that defines the interface to search and book
    tickets for any provider.
    """

    def start_session(self):
        raise NotImplementedError("Subclass should implement.")

    def search(self):
        raise NotImplementedError("Subclass should implement.")

    def select_seats(self):
        raise NotImplementedError("Subclass should implement.")

    def get_payment_options(self):
        raise NotImplementedError("Subclass should implement.")

    def prepare_sale(self):
        raise NotImplementedError("Subclass should implement.")

    def get_price(self):
        raise NotImplementedError("Subclass should implement.")

    def confirm_sale(self):
        raise NotImplementedError("Subclass should implement.")

    def close_session(self):
        raise NotImplementedError("Subclass should implement.")

    def check_status(self):
        raise NotImplementedError("Subclass should implement.")
