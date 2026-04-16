from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import HttpResponseBadRequest
from .models import BestSeller, Book, User, Admin, Order
from .forms import BookForm, RegisterForm, LoginForm,ContactForm
import razorpay


def home(request):
    bestbook = BestSeller.objects.all()
    return render(request, "home.html", {"bestbook": bestbook})


def about(request):
    return render(request, "about.html")


def books(request):
    books = Book.objects.all()
    return render(request, "books.html", {"books": books})


def login_view(request):
    msg = ""

    if request.method == "POST":
        form = LoginForm(request.POST)
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username, password=password)

            request.session["username"] = user.username
            request.session["email"] = user.email

            if Admin.objects.filter(admin=user.email).exists():
                request.session["admin"] = True
                response = redirect("home")
            else:
                request.session["admin"] = False
                response = redirect("home")

            response.set_cookie("username", user.username)
            return response

        except User.DoesNotExist:
            msg = "Invalid username or password"
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form, "msg": msg})


def register(request):
    msg = ""

    if request.method == "POST":
        form = RegisterForm(request.POST)
        email = request.POST.get("email")

        if User.objects.filter(email=email).exists():
            msg = "Email already exists"
        elif form.is_valid():
            form.save()
            return redirect("login")
        else:
            msg = "Please enter valid details."
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form, "msg": msg})

def contact_page(request):

    if request.method == "POST":
        form = ContactForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("contact")

    else:
        form = ContactForm()

    return render(request,"contact.html",{"form":form})


def logout_view(request):
    request.session.flush()
    response = redirect("login")
    response.delete_cookie("username")
    return response


def addbook(request):
    if not request.session.get("admin"):
        return redirect("home")

    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("books")
    else:
        form = BookForm()

    return render(request, "addbook.html", {"form": form})


def updatebook(request, id):
    if not request.session.get("admin"):
        return redirect("home")

    book = get_object_or_404(Book, id=id)

    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect("books")
    else:
        form = BookForm(instance=book)

    return render(request, "update_book.html", {"form": form, "book": book})


def deletebook(request, id):
    if not request.session.get("admin"):
        return redirect("home")

    book = get_object_or_404(Book, id=id)

    if request.method == "POST":
        book.delete()
        return redirect("booktable")

    return render(request, "delete_book.html", {"book": book})


def cart(request):
    cart_data = request.session.get("cart", {})
    book_ids = cart_data.keys()
    books = Book.objects.filter(id__in=book_ids)

    items = []
    total = 0

    for book in books:
        qty = cart_data.get(str(book.id), 0)
        subtotal = float(book.price) * qty
        total += subtotal

        items.append({
            "book": book,
            "qty": qty,
            "subtotal": subtotal
        })

    return render(request, "cart.html", {"items": items, "total": total})


def add_to_cart(request, book_id):
    cart_data = request.session.get("cart", {})
    key = str(book_id)

    cart_data[key] = cart_data.get(key, 0) + 1
    request.session["cart"] = cart_data
    request.session.modified = True

    return redirect("cart")


def remove_from_cart(request, book_id):
    cart_data = request.session.get("cart", {})
    key = str(book_id)

    if key in cart_data:
        cart_data[key] -= 1
        if cart_data[key] <= 0:
            del cart_data[key]

    request.session["cart"] = cart_data
    request.session.modified = True

    return redirect("cart")


def clear_cart(request):
    request.session["cart"] = {}
    request.session.modified = True
    return redirect("cart")


def booktable(request):
    if not request.session.get("admin"):
        return redirect("home")

    books = Book.objects.all()
    return render(request, "booktable.html", {"books": books})


def admin1(request):
    if not request.session.get("admin"):
        return redirect("home")

    return render(request, "admin.html")


def search_view(request):
    query = request.GET.get("q", "").strip()

    if query:
        books = Book.objects.filter(title__icontains=query)
    else:
        books = Book.objects.all()

    return render(request, "search.html", {"books": books, "query": query})


def cart_payment(request):
    if not request.session.get("username"):
        return redirect("login")

    cart_data = request.session.get("cart", {})

    if not cart_data:
        return render(request, "payment_failed.html", {"msg": "Your cart is empty"})

    book_ids = cart_data.keys()
    books = Book.objects.filter(id__in=book_ids)

    items = []
    total = 0

    for book in books:
        qty = int(cart_data.get(str(book.id), 0))

        if qty <= 0:
            continue

        if book.stock < qty:
            return render(request, "payment_failed.html", {
                "msg": f"Not enough stock for {book.title}"
            })

        subtotal = float(book.price) * qty
        total += subtotal

        items.append({
            "book": book,
            "qty": qty,
            "subtotal": subtotal
        })

    if total <= 0:
        return render(request, "payment_failed.html", {"msg": "Invalid cart total"})

    amount = int(total * 100)  # paise

    try:
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        order = Order.objects.create(
            user_name=request.session.get("username"),
            user_email=request.session.get("email"),
            amount=amount,
            status="PENDING"
        )

        razorpay_order = client.order.create(data={
            "amount": amount,
            "currency": "INR",
            "receipt": f"order_{order.id}"
        })

        order.razorpay_order_id = razorpay_order["id"]
        order.save()

        context = {
            "items": items,
            "total": total,
            "amount": amount,
            "order": order,
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "razorpay_order_id": razorpay_order["id"],
        }
        return render(request, "cart_payment.html", context)

    except razorpay.errors.BadRequestError as e:
        return render(request, "payment_failed.html", {
            "msg": f"Razorpay error: {str(e)}"
        })

    except Exception as e:
        return render(request, "payment_failed.html", {
            "msg": f"Something went wrong: {str(e)}"
        })



def payment_success(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request")

    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_signature = request.POST.get("razorpay_signature")

    if not razorpay_order_id or not razorpay_payment_id or not razorpay_signature:
        return HttpResponseBadRequest("Missing payment details")

    try:
        order = Order.objects.get(razorpay_order_id=razorpay_order_id)
    except Order.DoesNotExist:
        return HttpResponseBadRequest("Order not found")

    try:
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        }

        client.utility.verify_payment_signature(params_dict)

        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_signature = razorpay_signature
        order.status = "PAID"
        order.save()

        cart_data = request.session.get("cart", {})
        book_ids = cart_data.keys()
        books = Book.objects.filter(id__in=book_ids)

        for book in books:
            qty = int(cart_data.get(str(book.id), 0))
            if qty > 0 and book.stock >= qty:
                book.stock -= qty
                book.save()

        request.session["cart"] = {}
        request.session.modified = True

        return render(request, "payment_success.html", {"order": order})

    except razorpay.errors.SignatureVerificationError:
        order.status = "FAILED"
        order.save()
        return render(request, "payment_failed.html", {
            "order": order,
            "msg": "Payment signature verification failed"
        })

    except Exception as e:
        order.status = "FAILED"
        order.save()
        return render(request, "payment_failed.html", {
            "order": order,
            "msg": f"Payment failed: {str(e)}"
        })