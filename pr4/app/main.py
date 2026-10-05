from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from .models import (
    Book,
    BookCreate,
    BookUpdate,
    Order,
    OrderCreate,
    OrderStatusUpdate,
)
from .service import (
    BookNotFoundError,
    Bookstore,
    DuplicateBookError,
    OrderNotFoundError,
)

app = FastAPI(title="Bookstore API")

_store = Bookstore()


def get_store() -> Bookstore:
    return _store


def _register_error(exc_class, status_code):
    async def handler(request: Request, exc: Exception):
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    app.add_exception_handler(exc_class, handler)


_register_error(BookNotFoundError, 404)
_register_error(OrderNotFoundError, 404)
_register_error(DuplicateBookError, 409)
_register_error(ValueError, 400)


@app.post("/books/", response_model=Book, status_code=201)
def add_book(book: BookCreate, store: Bookstore = Depends(get_store)):
    return store.add_book(**book.model_dump())


@app.get("/books/", response_model=list[Book])
def get_books(store: Bookstore = Depends(get_store)):
    return store.get_all_books()


@app.get("/books/{isbn}", response_model=Book)
def get_book(isbn: str, store: Bookstore = Depends(get_store)):
    return store.get_book(isbn)


@app.put("/books/{isbn}", response_model=Book)
def update_book(isbn: str, update: BookUpdate, store: Bookstore = Depends(get_store)):
    return store.update_book(isbn, **update.model_dump(exclude_none=True))


@app.delete("/books/{isbn}")
def delete_book(isbn: str, store: Bookstore = Depends(get_store)):
    if not store.delete_book(isbn):
        raise BookNotFoundError(f"Книгу з ISBN {isbn} не знайдено")
    return {"message": "Book deleted successfully"}


@app.post("/orders/", response_model=Order, status_code=201)
def create_order(order: OrderCreate, store: Bookstore = Depends(get_store)):
    return store.place_order(order.customer_id, [i.model_dump() for i in order.items])


@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: int, store: Bookstore = Depends(get_store)):
    return store.get_order(order_id)


@app.put("/orders/{order_id}/status", response_model=Order)
def update_order_status(
    order_id: int, body: OrderStatusUpdate, store: Bookstore = Depends(get_store)
):
    return store.update_order_status(order_id, body.status)


@app.get("/customers/{customer_id}/orders", response_model=list[Order])
def get_customer_orders(customer_id: int, store: Bookstore = Depends(get_store)):
    return store.get_customer_orders(customer_id)