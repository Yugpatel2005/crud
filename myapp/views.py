import razorpay
from django.conf import settings
from django.shortcuts import render , redirect
from .models import *
from django.contrib import messages
# Create your views here.

def loginpage(request):
    return render(request,"login.html")

def registerpage(request):
    return render(request,"register.html")

def showproductspage(request):
    # fetch products from model
    fetchproducts = product.objects.all()
    fetchcategory = category.objects.all()
    context = {
        "products":fetchproducts,
        "category":fetchcategory
    }
    return render(request,"showproducts.html",context)

def singleproductpage(request,id):
    print(id)

    # fetch product details based on id
    fetchdata = product.objects.get(id=id)
    context = {
        "data":fetchdata
    }

    return render(request,"singleproducts.html",context)

def categoryviseproduct(request,id):
    # fetch product by selected category

    fetchproducts = product.objects.filter(catid=id)
    fetchcategory = category.objects.all()
    context = {
        "products":fetchproducts,
        "category":fetchcategory
    }

    return render(request,"categoryviseproduct.html",context)


def fetchregisterdata(request):

    # code to fetch data into variable

    uname = request.POST.get("name")
    uemail = request.POST.get("email")
    uphone = request.POST.get("phone")
    upassword = request.POST.get("password")
    uaddress = request.POST.get("address")
    ugender = request.POST.get("gender")
    urole = request.POST.get("role")

    udp = request.FILES["dp"]
    print(uname)

    # query to insert data into model
    insertquery = registermodel(name=uname,email=uemail,phone=uphone,password=upassword,address=uaddress,gender=ugender,role=urole,profilepicture=udp)
    insertquery.save()

    return render(request,"login.html")

def fetchlogindata(request):
    # code to fetch data into variable

    useremail = request.POST.get("email")
    userpassword = request.POST.get("password")

    print(useremail)
    print(userpassword)

    # query to check data into model
    # select * from registermodel where email=useremail and password=userpassword
    # django query

    try:
        userdata = registermodel.objects.get(email=useremail,password=userpassword)
        print("success")
        print(userdata)

        #session starts

        request.session["log_id"] = userdata.id
        request.session["log_name"] = userdata.name
        request.session["log_email"] = userdata.email
        request.session["log_role"] = userdata.role

        # print session variable
        print("session name",request.session["log_name"])

    except:
        print("failure")
        userdata = None


    if userdata is not None:
        return redirect("/")
    else:
        print("Invalid email or password")
        messages.error(request,"Invalid Email or Password")

    return render(request,"login.html")

def logout(request):
    try:
        del request.session["log_id"]
        del request.session["log_name"]
        del request.session["log_email"]
        del request.session["log_role"]
    except:
        pass
    return redirect("/")

def addproductpage(request):
    # FETCH CATEGORY DATA FROM MODEL
    fetchcatdata = category.objects.all()
    print(fetchcatdata)

    context = {
        "catdata":fetchcatdata
    }

    return render(request,"addproduct.html",context)

def insertproductdata(request):
    # form to variable
    name = request.POST.get("pname")
    catid = request.POST.get("pcat")
    price = request.POST.get("pprice")
    desc = request.POST.get("pdesc")
    image = request.FILES["pimage"]
    status = request.POST.get("pstatus")

    # fetch sellerid from session
    sellerid = request.session["log_id"]

    # insert query
    insertquery = product(name=name,catid=category(id=catid),pimage=image,price=price,description=desc,status=status,sellerid=registermodel(id=sellerid))
    insertquery.save()
    messages.success(request,"Product Added Successfully!!")
    return render(request,"addproduct.html")


def manageproduct(request):
    # fetch sellerid from session
    sellerid__loggedin = request.session["log_id"]
    # fetch added product by seller
    fetchdata = product.objects.filter(sellerid=sellerid__loggedin)
    context = {
        "data":fetchdata
    }

    return render(request,"manageproduct.html",context)

def insertintocart(request):
    userid = request.session["log_id"]
    pid = request.POST.get("pid")
    price = request.POST.get("price")
    quantity = request.POST.get("quantity")
    totalamount = int(quantity) * float(price)

    insertquery = cart(userid=registermodel(id=userid),productid=product(id=pid),
                       quantity=quantity,totalamount=totalamount,orderid=0,orderstatus=1)
    insertquery.save()
    messages.success(request,"Product Added to Cart")
    return redirect("/")

def showcart(request):
    userid__loggedin = request.session["log_id"]
    fetchdata = cart.objects.filter(userid=userid__loggedin,orderstatus=1)
    total = sum(item.totalamount for item in fetchdata)

    context = {
        "data":fetchdata,
        "total":total
    }
    return render(request,"cart.html",context)

def deleteitem(request,id):
    print(id)
    # delete from cart where id=id
    cart.objects.get(id=id).delete()
    messages.success(request,"Item Removed")
    return redirect("/showcart")

def increase(request,id):
    fetchdata = cart.objects.get(id=id)
    fetchdata.quantity += 1
    fetchdata.totalamount += fetchdata.productid.price
    fetchdata.save()
    return redirect("/showcart")

def decrease(request,id):
    fetchdata = cart.objects.get(id=id)

    if fetchdata.quantity == 1:
        fetchdata.delete()
    else:
        fetchdata.quantity -= 1
        fetchdata.totalamount -= fetchdata.productid.price
        fetchdata.save()
    return redirect("/showcart")

def placeorder(request):
    userid = request.session["log_id"]
    finaltotal = request.POST.get("total")
    phone = request.POST.get("phone")
    address = request.POST.get("address")
    payment = request.POST.get("payment")

    if payment=="Cash on Delivery":
        storedata = ordermodel(userid=registermodel(id=userid),finaltotal=finaltotal,phone=phone,
                               address=address,paymode=payment)
        storedata.save()
        print("Order Placed")

        lastid = storedata.id
        # update status in cart model
        fetchdata = cart.objects.filter(userid=userid, orderstatus=1)

        for i in fetchdata:
            i.orderstatus = 0
            i.orderid = lastid
            i.save()

        print("Status updated in Cart")

        return redirect("/")
    else:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
        order_amount = int(float(finaltotal) * 100)  # Razorpay needs amount in paise
        razorpay_order = client.order.create({
            "amount": order_amount,
            "currency": "INR",
            "receipt": f"order_rcptid_{userid}",
            "payment_capture": "1",
        })

        storedata = ordermodel(
            userid=registermodel(id=userid),
            finaltotal=finaltotal,
            phone=phone,
            address=address,
            paymode="Online",
            razorpay_order_id=razorpay_order['id'],
        )
        storedata.save()

        lastid = storedata.id

        # Update Cart Items
        cart_items = cart.objects.filter(userid=userid, orderstatus=1)
        for item in cart_items:
            item.orderstatus = 0
            item.orderid = lastid
            item.save()

        return render(request, "payment.html", {
            "razorpay_order_id": razorpay_order['id'],
            "amount": order_amount,
            "key": settings.RAZORPAY_KEY_ID,
            "currency": "INR",
        })

    return redirect("/")


def payment_success(request):
  return render(request, "showproducts.html")

def forgotpage(request):
    return render(request,"forgotpage.html")

def forgotpassword(request):
    if request.method == 'POST':
        username = request.POST['email']
        try:
            user = registermodel.objects.get(email=username)

        except registermodel.DoesNotExist:
            user = None
        #if user exist then only below condition will run otherwise it will give error as described in else condition.
        if user is not None:
            #################### Password Generation ##########################
            import random
            letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                       't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                       'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
            numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

            nr_letters = 6
            nr_symbols = 1
            nr_numbers = 3
            password_list = []

            for char in range(1, nr_letters + 1):
                password_list.append(random.choice(letters))

            for char in range(1, nr_symbols + 1):
                password_list += random.choice(symbols)

            for char in range(1, nr_numbers + 1):
                password_list += random.choice(numbers)

            print(password_list)
            random.shuffle(password_list)
            print(password_list)

            password = ""  #we will get final password in this var.
            for char in password_list:
                password += char

            ##############################################################


            msg = "hello here it is your new password  "+password   #this variable will be passed as message in mail

            ############ code for sending mail ########################

            from django.core.mail import send_mail

            send_mail(
                'Your New Password',
                msg,
                'krushanuinfolabz@gmail.com',
                [username],
                fail_silently=False,
            )

            #now update the password in model
            cuser = registermodel.objects.get(email=username)
            cuser.password = password
            cuser.save(update_fields=['password'])

            print('Mail sent')
            messages.info(request, 'mail is sent')
            return redirect("/")

        else:
            messages.info(request, 'This account does not exist')
    return redirect("/")

def changepass(request):
    return render(request,"changepass.html")

def updatepass(request):
    userid = request.session["log_id"]
    npass = request.POST.get("npass")
    opass = request.POST.get("opass")
    cpass = request.POST.get("cpass")

    fetchdata = registermodel.objects.get(id=userid)
    originalpass = fetchdata.password

    if opass==originalpass:
        if npass==cpass:
            fetchdata.password = npass
            fetchdata.save()
            return redirect("/logout")
        else:
            messages.error(request,"password and confirm pass should be same")
    else:
        messages.error(request,"Wrong Old Password")



    return redirect("/changepass")

def yourorders(request):
    userid = request.session["log_id"]
    fetchdata = ordermodel.objects.filter(userid=userid)
    context = {
        "data":fetchdata
    }
    return render(request,"yourorders.html",context)

def yourorderdetails(request,id):
    fetchdata = cart.objects.filter(orderid=id)
    context = {
        "data":fetchdata
    }
    return render(request,"yourorderdetail.html",context)