from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import authenticate
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import json
import random
from .models import SalonUser
from .models import Expense
from datetime import datetime, timedelta, time
import razorpay
from razorpay.errors import SignatureVerificationError
from django.utils import timezone

from .models import AboutSalon
from .serializers import AboutSalonSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

from .models import Appointment, Service
from .serializers import AppointmentSerializer

from rest_framework.decorators import api_view

from .serializers import ServiceSerializer
from .models import Wallet, WalletTransaction, SalonUser



from django.db.models import Count, Sum, Min, Max, Q,Avg
from django.http import JsonResponse
from django.db.models import Count, Sum, Q, Min, Max
from django.db.models.functions import ExtractMonth
from django.utils import timezone
from datetime import timedelta
from .serializers import ExpenseSerializer
from .models import Inventory
from .serializers import InventorySerializer
from django.db.models import F

from .models import Review, Appointment, Service, SalonUser
from .serializers import ReviewSerializer
from django.db import transaction
from decimal import Decimal
from .models import WalletTransaction









otp_store = {}
@csrf_exempt
def send_otp(request):
    print("SEND OTP HIT")

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Only POST allowed"
        })

    try:
        data = json.loads(request.body.decode("utf-8"))
        print("DATA:", data)

        email = data.get("email")

        if not email:
            return JsonResponse({
                "success": False,
                "message": "Email missing"
            })

        # Check if account already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                "success": False,
                "message": "Account already exists"
            })

        # Generate OTP
        otp = random.randint(100000, 999999)
        otp_store[email] = otp

        print("OTP =", otp)

        subject = "Verify your BeautyCare account"

        text_content = f"Your OTP is {otp}"

        html_content = f"""
        <html>
        <body style="background:#f5f5f5;padding:30px;font-family:Arial;">

        <div style="
        max-width:500px;
        margin:auto;
        background:white;
        padding:30px;
        border-radius:15px;
        text-align:center;
        ">

        <h1 style="color:#304FFE;">BeautyCare</h1>

        <h2>Email Verification</h2>

        <p>Use the verification code below to continue.</p>

        <h1 style="
        letter-spacing:8px;
        font-size:40px;
        color:#304FFE;
        ">
        {otp}
        </h1>

        <p>This code expires in 10 minutes.</p>

        <hr>

        <p style="color:gray;">
        If you didn't request this email, simply ignore it.
        </p>

        </div>

        </body>
        </html>
        """

        message = EmailMultiAlternatives(
            subject,
            text_content,
            settings.EMAIL_HOST_USER,
            [email]
        )

        message.attach_alternative(html_content, "text/html")
        message.send()

        return JsonResponse({
            "success": True,
            "message": "OTP sent successfully"
        })

    except Exception as e:
        print("SEND OTP ERROR:", e)

        return JsonResponse({
            "success": False,
            "message": str(e)
        })

@csrf_exempt
def verify_otp(request):


    data = json.loads(request.body.decode("utf-8"))

    print("REQUEST DATA:", data)

    email = data.get("email")
    otp = data.get("otp")

    print("EMAIL =", email)
    print("OTP RECEIVED =", otp)
    print("OTP STORE =", otp_store)



    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Only POST allowed"
        })

    try:

        data = json.loads(request.body.decode("utf-8"))

        email = data.get("email")
        otp = data.get("otp")

        if not email or not otp:
            return JsonResponse({
                "status": "error",
                "message": "Email and OTP are required"
            })

        otp = int(otp)

        print("========== VERIFY OTP ==========")
        print("EMAIL :", email)
        print("OTP :", otp)
        print("OTP STORE :", otp_store)

        if email not in otp_store:
            return JsonResponse({
                "status": "failed",
                "message": "OTP not found"
            })

        if otp_store[email] != otp:
            return JsonResponse({
                "status": "failed",
                "message": "Invalid OTP"
            })

        # OTP verified
        del otp_store[email]

        return JsonResponse({
            "status": "success",
            "message": "OTP Verified Successfully"
        })

    except ValueError:
        return JsonResponse({
            "status": "error",
            "message": "OTP must be numeric"
        })

    except Exception as e:
        print(e)
        return JsonResponse({
            "status": "error",
            "message": str(e)
        })




@csrf_exempt
def create_profile(request):

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Only POST allowed"
        })

    try:

        # ==========================
        # Multipart Form Data
        # ==========================
        email = request.POST.get("email")
        full_name = request.POST.get("fullName")
        phone = request.POST.get("phone")
        age = request.POST.get("age")
        gender = request.POST.get("gender")
        password = request.POST.get("password")

        # Profile Image (Optional)
        profile_image = request.FILES.get("profile_image")

        # ==========================
        # Validation
        # ==========================
        if not email or not full_name or not phone or not age or not gender or not password:
            return JsonResponse({
                "status": "error",
                "message": "All fields are required"
            })

        # Email check
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                "status": "failed",
                "message": "Email already exists"
            })

        # Phone check
        if SalonUser.objects.filter(phone=phone).exists():
            return JsonResponse({
                "status": "failed",
                "message": "Phone number already exists"
            })

        # ==========================
        # Create Django User
        # ==========================
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        # ==========================
        # Create Salon Profile
        # ==========================
        profile = SalonUser.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            age=age,
            gender=gender,
            is_verified=True
        )

        # ==========================
        # Save Image (if selected)
        # ==========================
        if profile_image:
            profile.profile_image = profile_image
            profile.save()

        return JsonResponse({
            "status": "success",
            "message": "Profile Created Successfully",
            "imageUrl": request.build_absolute_uri(profile.profile_image.url)
            if profile.profile_image else ""
        })

    except Exception as e:

        print("CREATE PROFILE ERROR :", e)

        return JsonResponse({
            "status": "error",
            "message": str(e)
        })

@csrf_exempt
def login_user(request):
    if request.method != "POST":

        return JsonResponse({
            "status": "error",
            "message": "Only POST allowed"
        })


    try:

        data = json.loads(
            request.body.decode("utf-8")
        )


        email = data.get("email")

        password = data.get("password")



        if not email or not password:

            return JsonResponse({

                "status": "error",

                "message": "Email and Password are required"

            })




        user = authenticate(

            username=email,

            password=password

        )



        if user is None:

            return JsonResponse({

                "status": "failed",

                "message": "Invalid Email or Password"

            })





        profile = SalonUser.objects.get(
            user=user
        )





        return JsonResponse({

            "status": "success",

            "message": "Login Successful",
            
            "user_id": user.id,


            "email": user.email,


            "fullName": profile.full_name,


            "phone": profile.phone,


            "age": profile.age,


            "gender": profile.gender,


            "is_admin": profile.is_admin

        })





    except SalonUser.DoesNotExist:


        return JsonResponse({

            "status": "failed",

            "message": "Profile not found"

        })




    except Exception as e:


        print("LOGIN ERROR :", e)


        return JsonResponse({

            "status": "error",

            "message": str(e)

        })

@csrf_exempt
def get_profile(request):

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Only POST allowed"
        })

    try:

        data = json.loads(request.body.decode("utf-8"))

        email = data.get("email")

        user = User.objects.get(email=email)
        profile = SalonUser.objects.get(user=user)

        return JsonResponse({
            "status": "success",

            "email": user.email,
            "fullName": profile.full_name,
            "phone": profile.phone,
            "age": profile.age,
            "gender": profile.gender,
            "profileImage": request.build_absolute_uri(profile.profile_image.url) if profile.profile_image else ""
        })

    except Exception as e:

        return JsonResponse({
            "status": "error",
            "message": str(e)
        })





@csrf_exempt
def update_profile(request):

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Only POST allowed"
        })

    try:
        email = request.POST.get("email")
        full_name = request.POST.get("fullName")
        phone = request.POST.get("phone")
        age = request.POST.get("age")
        gender = request.POST.get("gender")

        user = User.objects.get(email=email)
        profile = SalonUser.objects.get(user=user)

        # TEXT fields update
        profile.full_name = full_name
        profile.phone = phone
        profile.age = age
        profile.gender = gender

        # IMAGE update (IMPORTANT FIX)
        if "profile_image" in request.FILES:
            profile.profile_image = request.FILES["profile_image"]

        profile.save()

        return JsonResponse({
            "status": "success",
            "message": "Profile Updated Successfully",
            "image_url": profile.profile_image.url if profile.profile_image else ""
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        })



@csrf_exempt
def forgot_password_send_otp(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Only POST allowed"
        })

    try:

        data = json.loads(request.body.decode("utf-8"))

        email = data.get("email")

        if not email:
            return JsonResponse({
                "success": False,
                "message": "Email is required"
            })

        # Check email exists
        if not User.objects.filter(email=email).exists():
            return JsonResponse({
                "success": False,
                "message": "Email not registered"
            })

        # Generate OTP
        otp = random.randint(100000, 999999)

        otp_store[email] = otp

        print("Forgot Password OTP :", otp)

        subject = "BeautyCare Password Reset OTP"

        text_content = f"Your OTP is {otp}"

        html_content = f"""
        <html>
        <body style="background:#f5f5f5;padding:30px;font-family:Arial;">

        <div style="
        max-width:500px;
        margin:auto;
        background:white;
        padding:30px;
        border-radius:15px;
        text-align:center;
        ">

        <h1 style="color:#304FFE;">
        BeautyCare
        </h1>

        <h2>Reset Password</h2>

        <p>Use the OTP below to reset your password.</p>

        <h1 style="
        letter-spacing:8px;
        font-size:40px;
        color:#304FFE;
        ">
        {otp}
        </h1>

        <p>This OTP expires in 10 minutes.</p>

        </div>

        </body>
        </html>
        """

        message = EmailMultiAlternatives(
            subject,
            text_content,
            settings.EMAIL_HOST_USER,
            [email]
        )

        message.attach_alternative(html_content, "text/html")
        message.send()

        return JsonResponse({
            "success": True,
            "message": "OTP sent successfully"
        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "message": str(e)
        })



@csrf_exempt
def reset_password(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Only POST allowed"
        })

    try:

        data = json.loads(request.body.decode("utf-8"))

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse({
                "success": False,
                "message": "Email and Password are required"
            })

        user = User.objects.get(email=email)

        user.set_password(password)
        user.save()

        return JsonResponse({
            "success": True,
            "message": "Password Updated Successfully"
        })

    except User.DoesNotExist:

        return JsonResponse({
            "success": False,
            "message": "User not found"
        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "message": str(e)
        })





@api_view(['GET'])
def get_services(request):
    services = Service.objects.all()

    serializer = ServiceSerializer(
        services,
        many=True,
        context={'request': request}
    )

    return Response(serializer.data)


@csrf_exempt
def create_appointment(request):

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Only POST allowed"
        })

    try:

        data = json.loads(request.body.decode("utf-8"))

        # ================= USER =================

        email = data.get("email")
        user = User.objects.get(email=email)

        # ================= CUSTOMER DETAILS =================

        customer_name = data.get("customer_name")
        customer_phone = data.get("customer_phone")
        customer_email = data.get("customer_email")
        notes = data.get("notes", "")
        payment_status = data.get("payment_status", "Pending")
        razorpay_order_id = data.get("razorpay_order_id", "")
        razorpay_payment_id = data.get("razorpay_payment_id", "")
        razorpay_signature = data.get("razorpay_signature", "")

        # ================= APPOINTMENT =================

        appointment_date = data.get("appointment_date")
        appointment_time = data.get("appointment_time")

        # ================= SERVICES =================

        service_ids = data.get("services", [])

        services = Service.objects.filter(id__in=service_ids)

        if not services.exists():
            return JsonResponse({
                "status": "failed",
                "message": "No services selected."
            })

        # ================= TOTAL SERVICE DURATION =================

        total_duration = 0

        for service in services:
            duration = service.duration.replace("min", "").strip()
            total_duration += int(duration)

        # Start Time


        # ================= START TIME =================

        selected_time = datetime.strptime(appointment_time,"%I:%M %p").time()

        start_time = datetime.combine(datetime.today(),selected_time)

# ================= END TIME =================

        end_time = start_time + timedelta(minutes=total_duration)

        appointment_end_time = end_time.time()



        # ================= CHECK SLOT (Temporary) =================

        # ================= CHECK OVERLAP =================

        appointments = Appointment.objects.filter(appointment_date=appointment_date).exclude(status="Cancelled")

        for booking in appointments:

            old_start = datetime.combine(datetime.today(),booking.appointment_time)

            old_end = datetime.combine(datetime.today(),booking.appointment_end_time)

            if (start_time < old_end and end_time > old_start):

                  return JsonResponse({"status": "failed","message": "This time slot overlaps with another appointment."})

        # ================= BILL =================

        total_price = 0
        total_service_charge = 0

        for service in services:
            total_price += service.price
            total_service_charge += service.service_charge

        gst = (total_price + total_service_charge) * 0.18

        grand_total = total_price + total_service_charge + gst

        # ================= CREATE APPOINTMENT =================

        appointment = Appointment.objects.create(

    user=user,

    customer_name=customer_name,
    customer_phone=customer_phone,
    customer_email=customer_email,
    notes=notes,

    appointment_date=appointment_date,
    appointment_time=start_time.time(),
    appointment_end_time=appointment_end_time,

    total_price=total_price,
    total_service_charge=total_service_charge,
    gst=gst,
    grand_total=grand_total,

    payment_status=payment_status,
    razorpay_order_id=razorpay_order_id,
    razorpay_payment_id=razorpay_payment_id,
    razorpay_signature=razorpay_signature,

    status="Pending"
)

        appointment.services.set(services)

        appointment.save()


        # ================= ⚡ यहाँ आपके ईमेल भेजने वाले मेथड का इस्तेमाल (Call) होगा =================
        send_booking_confirmation_email(
            customer_email=appointment.customer_email,
            customer_name=appointment.customer_name,
            date=appointment.appointment_date,
            time=str(appointment_time), # आपका ओरिजिनल स्ट्रिंग टाइम (जैसे 10:00 AM) पास किया है
            grand_total=appointment.grand_total
        )

        # ================= RESPONSE =================

        return JsonResponse({

            "status": "success",

            "message": "Appointment Created Successfully",

            "appointment_id": appointment.id,

            "appointment_end_time": str(appointment_end_time),

            "total_price": total_price,

            "service_charge": total_service_charge,

            "gst": gst,

            "grand_total": grand_total

        })

    except User.DoesNotExist:

        return JsonResponse({
            "status": "failed",
            "message": "User not found."
        })

    except Exception as e:

        print("CREATE APPOINTMENT ERROR :", e)

        return JsonResponse({

            "status": "error",

            "message": str(e)

        })


@csrf_exempt
def available_slots(request):

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Only POST allowed"
        })

    try:

        data = json.loads(request.body.decode("utf-8"))

        appointment_date = data.get("appointment_date")
        total_duration = int(data.get("total_duration"))

        print("\n========== AVAILABLE SLOT API ==========")
        print("Date :", appointment_date)
        print("Duration :", total_duration)

        # ================= SHOP TIMING =================

        shop_open = datetime.combine(
            datetime.today(),
            time(8, 0)
        )

        shop_close = datetime.combine(
            datetime.today(),
            time(22, 0)
        )

        slots = []

        # ================= GET BOOKINGS =================

        appointments = Appointment.objects.filter(
            appointment_date=appointment_date
        ).exclude(status="Cancelled")

        print("Total Bookings :", appointments.count())

        for booking in appointments:

            print(
                "Booking ->",
                booking.appointment_time,
                "|",
                booking.appointment_end_time,
                "|",
                booking.status
            )

        # ================= SLOT GENERATION =================

        current = shop_open

        while current + timedelta(minutes=total_duration) <= shop_close:

            current_end = current + timedelta(minutes=total_duration)

            overlap = False

            for booking in appointments:

                booking_start = datetime.combine(
                    datetime.today(),
                    booking.appointment_time
                )

                booking_end = datetime.combine(
                    datetime.today(),
                    booking.appointment_end_time
                )

                if current < booking_end and current_end > booking_start:

                    overlap = True

                    print(
                        current.strftime("%I:%M %p"),
                        "❌ Overlap with",
                        booking.appointment_time,
                        "-",
                        booking.appointment_end_time
                    )

                    break

            if not overlap:

                print(
                    current.strftime("%I:%M %p"),
                    "✅ Available"
                )

                slots.append(
                    current.strftime("%I:%M %p")
                )

            # ✅ 15 Minute Interval
            current += timedelta(minutes=15)

        print("Final Available Slots :", slots)

        return JsonResponse({
            "status": "success",
            "slots": slots
        })

    except Exception as e:

        print("AVAILABLE SLOT ERROR :", e)

        return JsonResponse({
            "status": "error",
            "message": str(e)
        })



@csrf_exempt
def create_order(request):

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Only POST allowed"
        })

    try:

        data = json.loads(request.body.decode("utf-8"))

        appointment_id = data.get("appointment_id")

        if not appointment_id:
            return JsonResponse({
                "status": "failed",
                "message": "Appointment ID is required"
            })

        appointment = Appointment.objects.get(id=appointment_id)

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        amount = int(appointment.grand_total * 100)

        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        appointment.razorpay_order_id = order["id"]
        appointment.save()

        return JsonResponse({
            "status": "success",
            "order_id": order["id"],
            "amount": amount,
            "currency": "INR"
        })

    except Appointment.DoesNotExist:

        return JsonResponse({
            "status": "failed",
            "message": "Appointment not found."
        })

    except Exception as e:

        print("CREATE ORDER ERROR :", e)

        return JsonResponse({
            "status": "error",
            "message": str(e)
        })




@csrf_exempt
def verify_payment(request):

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Only POST allowed"
        })

    try:

        data = json.loads(request.body.decode("utf-8"))

        appointment_id = data.get("appointment_id")
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")

        appointment = Appointment.objects.get(id=appointment_id)

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        })

        appointment.payment_status = "Success"
        appointment.status = "Confirmed"

        appointment.razorpay_order_id = razorpay_order_id
        appointment.razorpay_payment_id = razorpay_payment_id
        appointment.razorpay_signature = razorpay_signature

        appointment.save()

        return JsonResponse({
            "status": "success",
            "message": "Payment Verified Successfully"
        })

    except SignatureVerificationError:

        return JsonResponse({
            "status": "failed",
            "message": "Invalid Signature"
        })

    except Appointment.DoesNotExist:

        return JsonResponse({
            "status": "failed",
            "message": "Appointment Not Found"
        })

    except Exception as e:

        print(e)

        return JsonResponse({
            "status": "error",
            "message": str(e)
        })








@csrf_exempt
def my_bookings(request):

    if request.method == "GET":

        email = request.GET.get("email")


        if not email:
            return JsonResponse({
                "success": False,
                "message": "Email required"
            })



        appointments = Appointment.objects.filter(
            customer_email=email,
            appointment_date__gte=timezone.now().date()
        ).prefetch_related(
            "services"
        ).order_by(
            "appointment_date"
        )



        booking_list = []



        for appointment in appointments:


            services = []


            for service in appointment.services.all():

                services.append(
                    service.service_name
                )



            # Check Review Submitted or Not

            has_review = Review.objects.filter(
                appointment=appointment
            ).exists()



            booking_list.append({

                "id": appointment.id,


                "serviceName": ", ".join(
                    services
                ),


                "employeeName": "Not Assigned",


                "bookingDate": str(
                    appointment.appointment_date
                ),


                "bookingTime": str(
                    appointment.appointment_time
                ),


                "totalPrice": str(
                    appointment.grand_total
                ),


                "status": appointment.status,


                "has_review": has_review

            })



        return JsonResponse({

            "success": True,

            "bookings": booking_list

        })



    return JsonResponse({

        "success": False,

        "message": "Invalid Method"

    })
  

def booking_history(request):

    email = request.GET.get("email")

    if not email:
        return JsonResponse({
            "status": "error",
            "message": "Email required"
        }, status=400)


    today = timezone.now().date()


    appointments = Appointment.objects.filter(
        customer_email=email,
        appointment_date__lt=today
    ).prefetch_related(
        "services"
    ).order_by(
        "-appointment_date"
    )


    data = []


    for appointment in appointments:

        services = []

        for service in appointment.services.all():
            services.append({
                "service_name": service.service_name,
                "price": service.price
            })


        data.append({

            "id": appointment.id,

            "services": services,

            "date": appointment.appointment_date,

            "time": appointment.appointment_time,

            "total_price": appointment.total_price,

            "grand_total": appointment.grand_total,

            "payment_status": appointment.payment_status,

            "status": appointment.status,

        })


    return JsonResponse({

        "status": "success",
        "bookings": data

    })






@api_view(['GET'])
def get_about_salon(request):

    about = AboutSalon.objects.first()


    if about:

        serializer = AboutSalonSerializer(about)

        return Response(
            serializer.data
        )


    return Response(
        {
            "message":"About data not found"
        }
    )



# android reports for admin
# ==========================
# CUSTOMER REPORT
# ==========================

def customer_report(request):

    report_type = request.GET.get("type", "all")
    search = request.GET.get("search", "").strip()

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    appointments = Appointment.objects.all()


    if search:
        appointments = appointments.filter(
            Q(customer_name__icontains=search) |
            Q(customer_phone__icontains=search) |
            Q(customer_email__icontains=search)
        )


    if from_date:
        appointments = appointments.filter(
            appointment_date__gte=from_date
        )


    if to_date:
        appointments = appointments.filter(
            appointment_date__lte=to_date
        )


    customers = (
        appointments
        .values(
            "customer_name",
            "customer_phone",
            "customer_email"
        )
        .annotate(

            total_visits=Count("id"),

            total_spent=Sum(
                "grand_total"
            ),

            first_visit=Min(
                "appointment_date"
            ),

            last_visit=Max(
                "appointment_date"
            )
        )
        .order_by("-total_visits")
    )


    if report_type == "new":

        customers = customers.filter(
            total_visits=1
        )


    elif report_type == "returning":

        customers = customers.filter(
            total_visits__gte=2
        )


    data=[]


    for c in customers:

        data.append({

            "customer_name":c["customer_name"],

            "phone":c["customer_phone"],

            "email":c["customer_email"],

            "total_visits":c["total_visits"],

            "total_spent":round(
                c["total_spent"] or 0,
                2
            ),

            "first_visit":c["first_visit"],

            "last_visit":c["last_visit"],

            "customer_type":
                "New"
                if c["total_visits"]==1
                else "Returning"

        })


    return JsonResponse({

        "status":"success",

        "count":len(data),

        "data":data

    })



# ==========================
# REVENUE REPORT
# ==========================

def revenue_report(request):

    today = timezone.now().date()

    week_start = today - timedelta(
        days=today.weekday()
    )

    month_start = today.replace(
        day=1
    )

    year_start = today.replace(
        month=1,
        day=1
    )


    appointments = Appointment.objects.filter(
        payment_status="Success"
    )


    def total(qs):

        return round(
            qs.aggregate(
                total=Sum("grand_total")
            )["total"] or 0,
            2
        )


    return JsonResponse({

        "status":"success",

        "today_revenue":total(
            appointments.filter(
                appointment_date=today
            )
        ),

        "yesterday_revenue":total(
            appointments.filter(
                appointment_date=today-timedelta(days=1)
            )
        ),

        "week_revenue":total(
            appointments.filter(
                appointment_date__gte=week_start
            )
        ),

        "month_revenue":total(
            appointments.filter(
                appointment_date__gte=month_start
            )
        ),

        "year_revenue":total(
            appointments.filter(
                appointment_date__gte=year_start
            )
        ),

        "total_revenue":total(
            appointments
        ),

        "total_transactions":
            appointments.count()

    })



# ==========================
# SERVICE REPORT
# ==========================
def service_report(request):

    services = Service.objects.annotate(

        total_bookings=Count(
            "appointments",
            distinct=True
        ),

        completed_bookings=Count(
            "appointments",
            filter=Q(
                appointments__status="Completed",
                appointments__payment_status="Success"
            ),
            distinct=True
        ),

        confirmed_bookings=Count(
            "appointments",
            filter=Q(
                appointments__status="Confirmed"
            ),
            distinct=True
        ),

        cancelled_bookings=Count(
            "appointments",
            filter=Q(
                appointments__status="Cancelled"
            ),
            distinct=True
        )

    ).order_by("-total_bookings")


    data = []

    for s in services:

        # Revenue = Service Price × Completed Bookings
        total_revenue = s.price * s.completed_bookings

        data.append({

            "service_name": s.service_name,

            "price": s.price,

            "duration": s.duration,

            "total_bookings": s.total_bookings,

            "completed_bookings": s.completed_bookings,

            "confirmed_bookings": s.confirmed_bookings,

            "cancelled_bookings": s.cancelled_bookings,

            "total_revenue": round(total_revenue, 2)

        })

    return JsonResponse({

        "status": "success",

        "count": len(data),

        "data": data

    })


    return JsonResponse({

        "status":"success",

        "count":len(data),

        "data":data

    })



# ==========================
# APPOINTMENT REPORT
# ==========================

def appointment_report(request):

    today = timezone.now().date()

    appointments = Appointment.objects.all()


    return JsonResponse({

        "status":"success",

        "total":
            appointments.count(),

        "pending":
            appointments.filter(
                status="Pending"
            ).count(),

        "confirmed":
            appointments.filter(
                status="Confirmed"
            ).count(),

        "completed":
            appointments.filter(
                status="Completed"
            ).count(),

        "cancelled":
            appointments.filter(
                status="Cancelled"
            ).count(),

        "today":
            appointments.filter(
                appointment_date=today
            ).count()

    })



# ==========================
# PAYMENT REPORT
# ==========================

def payment_report(request):

    appointments = Appointment.objects.all()


    success = appointments.filter(
        payment_status="Success"
    )


    pending = appointments.filter(
        payment_status="Pending"
    )


    failed = appointments.filter(
        payment_status="Failed"
    )


    def amount(qs):

        return round(
            qs.aggregate(
                total=Sum("grand_total")
            )["total"] or 0,
            2
        )


    return JsonResponse({

        "status":"success",

        "total_transactions":
            appointments.count(),

        "success_count":
            success.count(),

        "pending_count":
            pending.count(),

        "failed_count":
            failed.count(),

        "success_amount":
            amount(success),

        "pending_amount":
            amount(pending),

        "failed_amount":
            amount(failed)

    })



# ==========================
# DASHBOARD SUMMARY
# ==========================

def dashboard_summary(request):

    today = timezone.now().date()


    return JsonResponse({

        "status":"success",

        "total_customers":
            SalonUser.objects.count(),

        "total_services":
            Service.objects.count(),

        "total_bookings":
            Appointment.objects.count(),

        "today_bookings":
            Appointment.objects.filter(
                appointment_date=today
            ).count(),

        "today_revenue":
            Appointment.objects.filter(
                appointment_date=today,
                payment_status="Success"
            ).aggregate(
                total=Sum("grand_total")
            )["total"] or 0

    })



# ==========================
# TOP CUSTOMERS
# ==========================

def top_customers(request):

    customers = Appointment.objects.values(

        "customer_name",
        "customer_phone",
        "customer_email"

    ).annotate(

        total_visit=Count("id"),

        total_spent=Sum(
            "grand_total"
        )

    ).order_by(
        "-total_spent"
    )[:10]


    return JsonResponse({

        "status":"success",

        "data":list(customers)

    })



# ==========================
# TOP SERVICES
# ==========================
from django.db.models import Count

def top_services(request):

    services = Service.objects.annotate(

        booking_count=Count(
            "appointments",
            distinct=True
        )

    ).order_by(
        "-booking_count"
    )[:10]

    data = []

    for s in services:

        completed_count = s.appointments.filter(
            status="Completed"
        ).count()

        revenue = completed_count * s.price

        data.append({

            "service_name": s.service_name,

            "booking_count": s.booking_count,

            "revenue": round(revenue, 2)

        })

    return JsonResponse({

        "status": "success",

        "data": data

    })

# ==========================
# MONTHLY REVENUE
# ==========================

def monthly_revenue(request):

    revenue = Appointment.objects.filter(
        payment_status="Success"
    ).annotate(

        month=ExtractMonth(
            "appointment_date"
        )

    ).values(
        "month"
    ).annotate(

        revenue=Sum(
            "grand_total"
        )

    ).order_by(
        "month"
    )


    return JsonResponse({

        "status":"success",

        "data":list(revenue)

    })





# Django views.py में यह फंक्शन जोड़ें
def send_booking_confirmation_email(customer_email, customer_name, date, time, grand_total):
    subject = "Booking Confirmed! 🎉 - BeautyCare"
    text_content = f"Hello {customer_name}, your appointment is confirmed for {date} at {time}."
    
    # ग्राहकों के लिए एक सुंदर HTML ईमेल टेम्पलेट
    html_content = f"""
    <html>
    <body style="background:#f5f5f5; padding:30px; font-family:Arial, sans-serif;">
        <div style="max-width:500px; margin:auto; background:white; padding:30px; border-radius:15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
            <h1 style="color:#304FFE; text-align:center;">BeautyCare</h1>
            <h2 style="text-align:center; color:#2e7d32;">Booking Confirmed! 🎉</h2>
            <p>Hello <strong>{customer_name}</strong>,</p>
            <p>Thank you for booking with us. Your appointment has been successfully booked and confirmed.</p>
            <hr style="border:none; border-top:1px solid #eee;">
            <table style="width:100%; font-size:14px; line-height:25px;">
                <tr><td><strong>Date:</strong></td><td>{date}</td></tr>
                <tr><td><strong>Time:</strong></td><td>{time}</td></tr>
                <tr><td><strong>Amount Paid:</strong></td><td style="color:#304FFE; font-weight:bold;">₹{grand_total}</td></tr>
            </table>
            <hr style="border:none; border-top:1px solid #eee;">
            <p style="text-align:center; color:gray; font-size:12px;">We look forward to serving you!</p>
        </div>
    </body>
    </html>
    """
    
    try:
        message = EmailMultiAlternatives(
            subject,
            text_content,
            settings.EMAIL_HOST_USER,
            [customer_email]
        )
        message.attach_alternative(html_content, "text/html")
        message.send()
        print(f"CONFIRMATION EMAIL SENT TO {customer_email}")
    except Exception as e:
        print("EMAIL SENDING ERROR:", str(e))







@api_view(["POST"])
def add_expense(request):

    serializer = ExpenseSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

        return Response({
            "status": "success",
            "message": "Expense Added Successfully",
            "data": serializer.data
        })

    return Response({
        "status": "failed",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def expense_list(request):

    expenses = Expense.objects.all().order_by("-expense_date", "-id")

    serializer = ExpenseSerializer(expenses, many=True)

    return Response({
        "status": "success",
        "count": expenses.count(),
        "data": serializer.data
    })







@api_view(["GET"])
def expense_summary(request):

    def total(expense_type):
        return round(
            Expense.objects.filter(
                expense_type=expense_type
            ).aggregate(
                total=Sum("amount")
            )["total"] or 0,
            2
        )

    staff_salary = total("Staff Salary")

    product_purchase = total("Product Purchase")

    electricity = total("Electricity & Utilities")

    other = total("Other Expenses")

    total_expense = (
        staff_salary
        + product_purchase
        + electricity
        + other
    )

    return Response({

        "status": "success",

        "staff_salary": staff_salary,

        "product_purchase": product_purchase,

        "electricity_utilities": electricity,

        "other_expenses": other,

        "total_expenses": total_expense

    })


@api_view(["POST"])
def delete_expense(request):

    expense_id = request.data.get("id")

    try:
        expense = Expense.objects.get(id=expense_id)
        expense.delete()

        return Response({
            "status": "success",
            "message": "Expense Deleted Successfully"
        })

    except Expense.DoesNotExist:

        return Response({
            "status": "failed",
            "message": "Expense Not Found"
        }, status=status.HTTP_404_NOT_FOUND)



@api_view(["GET"])
def profit_summary(request):

    # =========================
    # Total Income
    # =========================

    total_income = Appointment.objects.filter(
        status="Completed",
        payment_status="Success"
    ).aggregate(
        total=Sum("grand_total")
    )["total"] or 0


    # =========================
    # Total Expense
    # =========================

    total_expense = Expense.objects.aggregate(
        total=Sum("amount")
    )["total"] or 0


    # =========================
    # Profit
    # =========================

    net_profit = total_income - total_expense


    return Response({

        "status": "success",

        "total_income": total_income,

        "total_expense": total_expense,

        "net_profit": net_profit

    })


# ==========================
# INVENTORY API
# ==========================
@api_view(["POST"])
def add_inventory(request):

    product_name = request.data.get("product_name", "").strip()

    try:
        stock_quantity = int(request.data.get("stock_quantity", 0))
        minimum_stock = int(request.data.get("minimum_stock", 5))
    except (ValueError, TypeError):
        return Response({
            "status": "error",
            "message": "Invalid quantity."
        }, status=status.HTTP_400_BAD_REQUEST)

    if not product_name:
        return Response({
            "status": "error",
            "message": "Product name is required."
        }, status=status.HTTP_400_BAD_REQUEST)

    if stock_quantity <= 0:
        return Response({
            "status": "error",
            "message": "Stock quantity must be greater than zero."
        }, status=status.HTTP_400_BAD_REQUEST)

    inventory = Inventory.objects.filter(
        product_name__iexact=product_name
    ).first()

    if inventory:

        inventory.stock_quantity += stock_quantity
        inventory.minimum_stock = minimum_stock
        inventory.save()

        message = "Stock Updated Successfully"

    else:

        inventory = Inventory.objects.create(
            product_name=product_name,
            stock_quantity=stock_quantity,
            minimum_stock=minimum_stock
        )

        message = "Product Added Successfully"

    serializer = InventorySerializer(inventory)

    return Response({
        "status": "success",
        "message": message,
        "data": serializer.data
    })

    

# ==========================
# INVENTORY LIST
# ==========================

@api_view(["GET"])
def inventory_list(request):

    search = request.GET.get("search", "").strip()

    sort = request.GET.get("sort", "name")

    inventory = Inventory.objects.all()

    # --------------------------
    # Search
    # --------------------------

    if search:
        inventory = inventory.filter(
            product_name__icontains=search
        )

    # --------------------------
    # Sorting
    # --------------------------

    if sort == "name_desc":
        inventory = inventory.order_by("-product_name")

    elif sort == "stock_low":
        inventory = inventory.order_by("stock_quantity", "product_name")

    elif sort == "stock_high":
        inventory = inventory.order_by("-stock_quantity", "product_name")

    else:
        # Default: kam stock wala sabse upar
        inventory = inventory.order_by("stock_quantity", "product_name")

    serializer = InventorySerializer(
        inventory,
        many=True
    )

    return Response({

        "status": "success",

        "count": inventory.count(),

        "data": serializer.data

    })

# ==========================
# REDUCE STOCK
# ==========================

@api_view(["POST"])
def reduce_stock(request):

    product_id = request.data.get("id")
    stock_quantity = request.data.get("stock_quantity")

    # --------------------------
    # Validation
    # --------------------------

    if not product_id:
        return Response({
            "status": "error",
            "message": "Product ID is required."
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        stock_quantity = int(stock_quantity)
    except (TypeError, ValueError):
        return Response({
            "status": "error",
            "message": "Invalid stock quantity."
        }, status=status.HTTP_400_BAD_REQUEST)

    if stock_quantity <= 0:
        return Response({
            "status": "error",
            "message": "Stock quantity must be greater than zero."
        }, status=status.HTTP_400_BAD_REQUEST)

    # --------------------------
    # Product Check
    # --------------------------

    try:
        inventory = Inventory.objects.get(id=product_id)

    except Inventory.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Product not found."
        }, status=status.HTTP_404_NOT_FOUND)

    # --------------------------
    # Stock Check
    # --------------------------

    if inventory.stock_quantity < stock_quantity:

        return Response({

            "status": "error",

            "message": "Not enough stock.",

            "available_stock": inventory.stock_quantity

        }, status=status.HTTP_400_BAD_REQUEST)

    # --------------------------
    # Reduce Stock
    # --------------------------

    inventory.stock_quantity -= stock_quantity
    inventory.save()

    serializer = InventorySerializer(inventory)

    return Response({

        "status": "success",

        "message": "Stock reduced successfully.",

        "data": serializer.data

    })

# ==========================
# ADD STOCK API
# ==========================
@api_view(["POST"])
def add_stock(request):

    product_id = request.data.get("id")
    stock_quantity = request.data.get("stock_quantity")

    if not product_id:
        return Response({
            "status": "error",
            "message": "Product ID is required."
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        stock_quantity = int(stock_quantity)
    except (TypeError, ValueError):
        return Response({
            "status": "error",
            "message": "Invalid stock quantity."
        }, status=status.HTTP_400_BAD_REQUEST)

    if stock_quantity <= 0:
        return Response({
            "status": "error",
            "message": "Stock quantity must be greater than zero."
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        inventory = Inventory.objects.get(id=product_id)
    except Inventory.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Product not found."
        }, status=status.HTTP_404_NOT_FOUND)

    inventory.stock_quantity += stock_quantity
    inventory.save()

    serializer = InventorySerializer(inventory)

    return Response({
        "status": "success",
        "message": "Stock added successfully.",
        "data": serializer.data
    })

# ==========================
# DELETE INVENTORY
# ==========================

@api_view(["POST"])
def delete_inventory(request):

    product_id = request.data.get("id")

    if not product_id:
        return Response({
            "status": "error",
            "message": "Product ID is required."
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        inventory = Inventory.objects.get(id=product_id)

    except Inventory.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Product not found."
        }, status=status.HTTP_404_NOT_FOUND)

    product_name = inventory.product_name

    inventory.delete()

    return Response({
        "status": "success",
        "message": f"{product_name} deleted successfully."
    }, status=status.HTTP_200_OK)

# ==========================
# UPDATE INVENTORY
# ==========================

@api_view(["POST"])
def update_inventory(request):

    product_id = request.data.get("id")
    product_name = request.data.get("product_name", "").strip()
    minimum_stock = request.data.get("minimum_stock")

    # --------------------------
    # Validation
    # --------------------------

    if not product_id:
        return Response({
            "status": "error",
            "message": "Product ID is required."
        }, status=status.HTTP_400_BAD_REQUEST)

    if not product_name:
        return Response({
            "status": "error",
            "message": "Product name is required."
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        minimum_stock = int(minimum_stock)
    except (TypeError, ValueError):
        return Response({
            "status": "error",
            "message": "Invalid minimum stock."
        }, status=status.HTTP_400_BAD_REQUEST)

    if minimum_stock < 1:
        return Response({
            "status": "error",
            "message": "Minimum stock must be at least 1."
        }, status=status.HTTP_400_BAD_REQUEST)

    # --------------------------
    # Product Check
    # --------------------------

    try:
        inventory = Inventory.objects.get(id=product_id)

    except Inventory.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Product not found."
        }, status=status.HTTP_404_NOT_FOUND)

    # --------------------------
    # Duplicate Name Check
    # --------------------------

    duplicate = Inventory.objects.filter(
        product_name__iexact=product_name
    ).exclude(id=product_id).exists()

    if duplicate:
        return Response({
            "status": "error",
            "message": "Product name already exists."
        }, status=status.HTTP_400_BAD_REQUEST)

    # --------------------------
    # Update Product
    # --------------------------

    inventory.product_name = product_name
    inventory.minimum_stock = minimum_stock
    inventory.save()

    serializer = InventorySerializer(inventory)

    return Response({
        "status": "success",
        "message": "Product updated successfully.",
        "data": serializer.data
    })

# ==========================
# INVENTORY SUMMARY
# ==========================

@api_view(["GET"])
def inventory_summary(request):

    total_products = Inventory.objects.count()


    total_stock = Inventory.objects.aggregate(
        total=Sum("stock_quantity")
    )["total"] or 0


    low_stock = Inventory.objects.filter(
        stock_quantity__lte=F("minimum_stock")
    ).count()


    out_of_stock = Inventory.objects.filter(
        stock_quantity=0
    ).count()


    return Response({

        "status":"success",

        "total_products": total_products,

        "total_stock": total_stock,

        "low_stock": low_stock,

        "out_of_stock": out_of_stock

    })





@api_view(["POST"])
def update_appointment_status(request):

    appointment_id = request.data.get("appointment_id")
    status_value = request.data.get("status")

    if not appointment_id:
        return Response({
            "status": "error",
            "message": "Appointment ID is required."
        }, status=status.HTTP_400_BAD_REQUEST)

    if status_value not in ["Pending", "Confirmed", "Completed", "Cancelled"]:
        return Response({
            "status": "error",
            "message": "Invalid status."
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        appointment = Appointment.objects.get(id=appointment_id)

        appointment.status = status_value
        appointment.save()

        return Response({
            "status": "success",
            "message": "Appointment status updated successfully."
        })

    except Appointment.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Appointment not found."
        }, status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
def can_review(request):

    if request.method == "POST":

        data = json.loads(request.body)

        appointment_id = data.get("appointment_id")

        try:

            appointment = Appointment.objects.get(id=appointment_id)

        except Appointment.DoesNotExist:

            return JsonResponse({
                "status": "error",
                "message": "Appointment not found"
            })

        if appointment.status != "Completed":

            return JsonResponse({
                "status": "error",
                "can_review": False,
                "message": "Service not completed"
            })

        if appointment.payment_status != "Success":

            return JsonResponse({
                "status": "error",
                "can_review": False,
                "message": "Payment not completed"
            })

        if Review.objects.filter(appointment=appointment).exists():

            return JsonResponse({
                "status": "error",
                "can_review": False,
                "message": "Already reviewed"
            })

        return JsonResponse({
            "status": "success",
            "can_review": True
        })

    return JsonResponse({"status":"error"})



@csrf_exempt
def submit_review(request):

    if request.method == "POST":

        data = json.loads(request.body)

        print(data)

        appointment_id = data.get("appointment_id")
        rating = data.get("rating")
        review_text = data.get("review")


        try:

            appointment = Appointment.objects.get(
                id=appointment_id
            )


        except Appointment.DoesNotExist:

            return JsonResponse({

                "status": "error",
                "message": "Appointment not found"

            })



        # Check already reviewed

        if Review.objects.filter(
                appointment=appointment
        ).exists():

            return JsonResponse({

                "status": "error",
                "message": "Review already submitted"

            })



        # User Profile

        try:

            profile = SalonUser.objects.get(
                user=appointment.user
            )

        except SalonUser.DoesNotExist:

            return JsonResponse({

                "status": "error",
                "message": "User profile not found"

            })



        # Get Appointment Service

        service = appointment.services.first()


        if service is None:

            return JsonResponse({

                "status": "error",
                "message": "Service not found for appointment"

            })



        # Save Review

        Review.objects.create(

            appointment=appointment,

            user=profile,

            service=service,

            rating=rating,

            review=review_text

        )



        return JsonResponse({

            "status": "success",

            "message": "Review Submitted Successfully"

        })



    return JsonResponse({

        "status": "error",

        "message": "Only POST allowed"

    })

def my_reviews(request):

    email = request.GET.get("email")

    try:

        profile = SalonUser.objects.get(user__email=email)

    except SalonUser.DoesNotExist:

        return JsonResponse({

            "status":"error"

        })

    reviews = Review.objects.filter(user=profile)

    data = []

    for r in reviews:

        data.append({

            "id":r.id,
            "appointment_id":r.appointment.id,
            "rating":r.rating,
            "review":r.review,
            "date":str(r.created_at.date())

        })

    return JsonResponse({

        "status":"success",
        "data":data

    })


def service_reviews(request):

    reviews = Review.objects.all().order_by("-created_at")

    data = []

    for r in reviews:

        services = []

        for s in r.appointment.services.all():

            services.append(s.service_name)

        data.append({

            "customer":r.user.full_name,
            "rating":r.rating,
            "review":r.review,
            "services":services,
            "date":str(r.created_at.date())

        })

    return JsonResponse({

        "status":"success",
        "count":len(data),
        "data":data

    })



@api_view(["POST"])
def create_wallet_order(request):

    amount = request.data.get("amount")


    if not amount:
        return Response({
            "status":False,
            "message":"Amount required"
        })


    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )


    order = client.order.create({

        "amount": int(float(amount) * 100),

        "currency":"INR",

        "payment_capture":1

    })


    return Response({

        "status":True,

        "order_id":order["id"],

        "amount":amount,

        "currency":"INR",

        "key":settings.RAZORPAY_KEY_ID

    })


#  Wallet Apis

@api_view(["POST"])
def create_wallet_order(request):

    amount = request.data.get("amount")


    if not amount:
        return Response({
            "status":False,
            "message":"Amount required"
        })


    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )


    order = client.order.create({

        "amount": int(float(amount) * 100),

        "currency":"INR",

        "payment_capture":1

    })


    return Response({

        "status":True,

        "order_id":order["id"],

        "amount":amount,

        "currency":"INR",

        "key":settings.RAZORPAY_KEY_ID

    })






@api_view(["POST"])
@transaction.atomic
def verify_wallet_payment(request):

    user_id = request.data.get("user_id")

    razorpay_payment_id = request.data.get(
        "razorpay_payment_id"
    )

    razorpay_order_id = request.data.get(
        "razorpay_order_id"
    )

    razorpay_signature = request.data.get(
        "razorpay_signature"
    )

    amount = request.data.get("amount")

    print("========== VERIFY WALLET PAYMENT ==========")
    print("REQUEST DATA =", request.data)
    print("USER ID =", user_id)
    print("ORDER ID =", razorpay_order_id)
    print("PAYMENT ID =", razorpay_payment_id)
    print("SIGNATURE =", razorpay_signature)
    print("AMOUNT =", amount)

    try:

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        client.utility.verify_payment_signature({

            "razorpay_order_id":
                razorpay_order_id,

            "razorpay_payment_id":
                razorpay_payment_id,

            "razorpay_signature":
                razorpay_signature

        })

        print("✅ SIGNATURE VERIFIED")

        profile = SalonUser.objects.get(
            user_id=user_id
        )

        print("✅ PROFILE FOUND")

        wallet, created = Wallet.objects.get_or_create(
            user=profile
        )

        if created:
            print("✅ NEW WALLET CREATED")

        print("CURRENT BALANCE =", wallet.balance)

        amount = Decimal(str(amount))

        wallet.balance += amount

        wallet.save()

        print("✅ WALLET UPDATED")
        print("NEW BALANCE =", wallet.balance)

        WalletTransaction.objects.create(

            user=profile,

            amount=amount,

            transaction_type="CREDIT",

            payment_method="RAZORPAY",

            payment_id=razorpay_payment_id,

            reference_id=razorpay_order_id,

            description="Wallet Recharge",

            status="SUCCESS"

        )

        print("✅ TRANSACTION CREATED")

        return Response({

            "status": True,

            "message": "Wallet Recharge Successful",

            "wallet_balance": wallet.balance

        })

    except SalonUser.DoesNotExist:

        return Response({

            "status": False,

            "message": "User not found"

        })

    except Exception as e:

        print("❌ VERIFY WALLET ERROR =", str(e))

        return Response({

            "status": False,

            "message": str(e)

        })





@api_view(["POST"])
def wallet_balance(request):

    user_id = request.data.get("user_id")


    profile = SalonUser.objects.get(
        user_id=user_id
    )


    wallet, created = Wallet.objects.get_or_create(
        user=profile
    )


    return Response({

        "status":True,

        "wallet_balance":
        wallet.balance

    })




@api_view(["POST"])
def wallet_history(request):

    user_id=request.data.get("user_id")


    profile=SalonUser.objects.get(
        user_id=user_id
    )


    transactions = WalletTransaction.objects.filter(
        user=profile
    ).order_by("-created_at")




    data = []

    for t in transactions:

        data.append({

        "amount": t.amount,

        "type": t.transaction_type,

        "description": t.description,

        "date": timezone.localtime(t.created_at).strftime("%d %b %Y %I:%M %p")

    })


    return Response({

        "status":True,

        "transactions":data

    }) 



    @api_view(["POST"])
    def use_wallet_payment(request):

       user_id = request.data.get("user_id")
       amount = request.data.get("amount")
       appointment_id = request.data.get("appointment_id")


    try:

        profile = SalonUser.objects.get(
            user_id=user_id
        )


        amount = Decimal(amount)



        wallet, created = Wallet.objects.get_or_create(
    user=profile
)


        if wallet.balance < amount:

            return Response({

                "status":"failed",
                "message":"Insufficient Wallet Balance"

            })



        # Deduct wallet money

        wallet.balance -= amount
        wallet.save()



        WalletTransaction.objects.create(

          user=profile,

         amount=amount,

    transaction_type="DEBIT",

    payment_method="WALLET",

    reference_id=str(appointment_id),

    description=f"Appointment Payment #{appointment_id}",

    status="SUCCESS"

)



        return Response({

            "status":"success",

            "message":
            "Wallet Payment Successful"

        })



    except SalonUser.DoesNotExist:


        return Response({

            "status":"failed",

            "message":
            "User not found"

        })
from decimal import Decimal


@api_view(["POST"])
@transaction.atomic
def use_wallet_payment(request):

    user_id = request.data.get("user_id")
    amount = Decimal(str(request.data.get("amount")))
    appointment_id = request.data.get("appointment_id")

    try:

        profile = SalonUser.objects.get(user_id=user_id)

        wallet = Wallet.objects.get(user=profile)

        if wallet.balance < amount:
            return Response({
                "status": "failed",
                "message": "Insufficient Wallet Balance"
            })

        wallet.balance -= amount
        wallet.save()

        WalletTransaction.objects.create(
            user=profile,
            amount=amount,
            transaction_type="DEBIT",
            payment_method="WALLET",
            description=f"Appointment Payment #{appointment_id}",
            status="SUCCESS"
        )

        return Response({
            "status": "success",
            "message": "Wallet Payment Successful",
            "wallet_balance": wallet.balance
        })

    except Wallet.DoesNotExist:
        return Response({
            "status": "failed",
            "message": "Wallet not found"
        })

    except SalonUser.DoesNotExist:
        return Response({
            "status": "failed",
            "message": "User not found"
        })