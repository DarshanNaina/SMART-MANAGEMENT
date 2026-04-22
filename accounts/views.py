import random
from datetime import timedelta
from smtplib import SMTPException

from django.contrib import messages
from django.contrib.auth import login, logout
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils import timezone

from django.conf import settings

from .decorators import role_required
from .forms import LoginWithPasswordForm, OTPForm, RegisterForm, SecretKeyForm
from .models import CustomUser, OTPVerification, StudentProfile, TeacherProfile

OTP_RATE_LIMIT_WINDOW_MINUTES = 10
OTP_RATE_LIMIT_MAX_ATTEMPTS = 3
OTP_RESEND_COOLDOWN_SECONDS = 60


def _generate_otp():
    return f"{random.randint(100000, 999999)}"


def _send_otp_email(user, otp_code, purpose_label):
    subject = f"SAMS {purpose_label} OTP"
    message = (
        f"Hello {user.get_full_name() or user.username},\n\n"
        f"Your OTP for {purpose_label.lower()} is: {otp_code}\n"
        "This OTP is valid for 10 minutes.\n\n"
        "If you did not request this, please ignore this email."
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def _otp_rate_limit_state(user, purpose):
    now = timezone.now()
    window_start = now - timedelta(minutes=OTP_RATE_LIMIT_WINDOW_MINUTES)
    recent_otps = OTPVerification.objects.filter(
        user=user,
        purpose=purpose,
        created_at__gte=window_start,
    ).order_by("-created_at")
    last_otp = recent_otps.first()
    cooldown_remaining = 0
    if last_otp:
        next_allowed_at = last_otp.created_at + timedelta(seconds=OTP_RESEND_COOLDOWN_SECONDS)
        cooldown_remaining = max(0, int((next_allowed_at - now).total_seconds()))
    return {
        "count_in_window": recent_otps.count(),
        "cooldown_remaining_seconds": cooldown_remaining,
    }


def _create_and_send_otp(user, purpose, purpose_label):
    state = _otp_rate_limit_state(user, purpose)
    if state["count_in_window"] >= OTP_RATE_LIMIT_MAX_ATTEMPTS:
        return False, (
            f"Too many OTP requests. Please wait {OTP_RATE_LIMIT_WINDOW_MINUTES} minutes before trying again."
        )
    if state["cooldown_remaining_seconds"] > 0:
        return False, f"Please wait {state['cooldown_remaining_seconds']} seconds before requesting another OTP."

    otp_code = _generate_otp()
    OTPVerification.objects.create(
        user=user,
        purpose=purpose,
        code=otp_code,
        expires_at=OTPVerification.get_expiry_time(),
    )
    try:
        _send_otp_email(user, otp_code, purpose_label)
    except (SMTPException, OSError, ValueError) as exc:
        return False, f"Unable to send OTP email right now. Check email SMTP settings. ({exc})"
    return True, "OTP sent to your email."


def _get_register_template(role):
    if role == "TEACHER":
        return "teacher/register.html"
    elif role == "ADMIN":
        return "admin_panel/register.html"
    else:
        return "accounts/register.html"


def secret_key_verification_view(request):
    flow = request.session.get('secret_key_flow')
    if not flow:
        return redirect('accounts:register')

    form = SecretKeyForm(request.POST or None, expected_key=settings.SECRET_ACCESS_KEY)
    if request.method == "POST" and form.is_valid():
        if flow == 'registration':
            user_id = request.session.get('pending_registration_user_id')
            if user_id:
                user = CustomUser.objects.filter(id=user_id).first()
                if user:
                    sent, message = _create_and_send_otp(user, OTPVerification.Purpose.REGISTRATION, "Registration")
                    if sent:
                        request.session.pop('secret_key_flow', None)
                        messages.info(request, message)
                        return redirect("accounts:verify_registration_otp")
                    else:
                        user.delete()
                        request.session.pop('pending_registration_user_id', None)
                        request.session.pop('secret_key_flow', None)
                        messages.error(request, message)
                        return redirect('accounts:register')
        elif flow == 'login':
            user_id = request.session.get('pending_login_user_id')
            if user_id:
                user = CustomUser.objects.filter(id=user_id).first()
                if user:
                    sent, message = _create_and_send_otp(user, OTPVerification.Purpose.LOGIN, "Login")
                    if sent:
                        request.session.pop('secret_key_flow', None)
                        messages.info(request, message)
                        return redirect("accounts:verify_login_otp")
                    else:
                        request.session.pop('pending_login_user_id', None)
                        request.session.pop('secret_key_flow', None)
                        messages.error(request, message)
                        return redirect('accounts:login')
    return render(request, "accounts/secret_key.html", {"form": form})


def register_view(request, role=None):
    # Default to STUDENT if no role is specified via URL
    default_role = role or CustomUser.Role.STUDENT
    initial = {"role": default_role}
    form = RegisterForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        # Use role from form if provided, otherwise use URL parameter or default to STUDENT
        user.role = form.cleaned_data.get("role") or default_role
        user.set_password(form.cleaned_data["password1"])
        user.is_active = False
        user.save()
        if user.role == CustomUser.Role.STUDENT:
            StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    "roll_number": f"S-{user.id:05d}",
                    "parent_email": form.cleaned_data["parent_email"],
                    "academic_class": form.cleaned_data["academic_class"],
                },
            )
        elif user.role == CustomUser.Role.TEACHER:
            TeacherProfile.objects.get_or_create(
                user=user,
                defaults={"employee_id": f"T-{user.id:05d}"},
            )
        # For ADMIN/TEACHER, require secret key verification
        if user.role in [CustomUser.Role.ADMIN, CustomUser.Role.TEACHER]:
            request.session['pending_registration_user_id'] = user.id
            request.session['secret_key_flow'] = 'registration'
            return redirect('accounts:secret_key_verification')
        # For STUDENT, proceed directly to OTP
        sent, message = _create_and_send_otp(user, OTPVerification.Purpose.REGISTRATION, "Registration")
        if not sent:
            user.delete()
            messages.error(request, message)
            template = _get_register_template(role)
            return render(request, template, {"form": form})
        request.session["pending_registration_user_id"] = user.id
        messages.info(request, message)
        return redirect("accounts:verify_registration_otp")
    template = _get_register_template(role)
    return render(request, template, {"form": form})


def verify_registration_otp_view(request):
    user_id = request.session.get("pending_registration_user_id")
    if not user_id:
        return redirect("accounts:register")
    user = CustomUser.objects.filter(id=user_id).first()
    if not user:
        return redirect("accounts:register")

    form = OTPForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        otp = OTPVerification.objects.filter(
            user=user,
            purpose=OTPVerification.Purpose.REGISTRATION,
            code=form.cleaned_data["code"],
        ).first()
        if not otp or not otp.is_valid():
            messages.error(request, "Invalid or expired OTP.")
        else:
            otp.is_used = True
            otp.save(update_fields=["is_used"])
            user.is_active = True
            user.save(update_fields=["is_active"])
            request.session.pop("pending_registration_user_id", None)
            messages.success(request, "Registration verified. Please login.")
            return redirect("accounts:login")
    return render(
        request,
        "accounts/verify_otp.html",
        {"form": form, "flow": "registration", "resend_url_name": "accounts:resend_registration_otp"},
    )


def login_view(request):
    form = LoginWithPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.cleaned_data["user"]
        if not user.email:
            messages.error(request, "No email is linked to this account. Contact admin.")
            return render(request, "accounts/login.html", {"form": form})
        # For ADMIN/TEACHER, require secret key verification
        if user.role in [CustomUser.Role.ADMIN, CustomUser.Role.TEACHER]:
            request.session['pending_login_user_id'] = user.id
            request.session['secret_key_flow'] = 'login'
            return redirect('accounts:secret_key_verification')
        # For STUDENT, proceed directly to OTP
        sent, message = _create_and_send_otp(user, OTPVerification.Purpose.LOGIN, "Login")
        if not sent:
            messages.error(request, message)
            return render(request, "accounts/login.html", {"form": form})
        request.session["pending_login_user_id"] = user.id
        messages.info(request, message)
        return redirect("accounts:verify_login_otp")
    return render(request, "accounts/login.html", {"form": form})


def verify_login_otp_view(request):
    user_id = request.session.get("pending_login_user_id")
    if not user_id:
        return redirect("accounts:login")
    user = CustomUser.objects.filter(id=user_id).first()
    if not user:
        return redirect("accounts:login")

    form = OTPForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        otp = OTPVerification.objects.filter(
            user=user,
            purpose=OTPVerification.Purpose.LOGIN,
            code=form.cleaned_data["code"],
        ).first()
        if not otp or not otp.is_valid():
            messages.error(request, "Invalid or expired OTP.")
        else:
            otp.is_used = True
            otp.save(update_fields=["is_used"])
            request.session.pop("pending_login_user_id", None)
            login(request, user)
            messages.success(request, "Login verified successfully.")
            return redirect("accounts:redirect_dashboard")
    return render(
        request,
        "accounts/verify_otp.html",
        {"form": form, "flow": "login", "resend_url_name": "accounts:resend_login_otp"},
    )


def resend_registration_otp_view(request):
    user_id = request.session.get("pending_registration_user_id")
    if not user_id:
        return redirect("accounts:register")
    user = CustomUser.objects.filter(id=user_id, is_active=False).first()
    if not user:
        return redirect("accounts:register")

    sent, message = _create_and_send_otp(user, OTPVerification.Purpose.REGISTRATION, "Registration")
    if sent:
        messages.success(request, "A new registration OTP has been sent.")
    else:
        messages.error(request, message)
    return redirect("accounts:verify_registration_otp")


def resend_login_otp_view(request):
    user_id = request.session.get("pending_login_user_id")
    if not user_id:
        return redirect("accounts:login")
    user = CustomUser.objects.filter(id=user_id, is_active=True).first()
    if not user:
        return redirect("accounts:login")

    sent, message = _create_and_send_otp(user, OTPVerification.Purpose.LOGIN, "Login")
    if sent:
        messages.success(request, "A new login OTP has been sent.")
    else:
        messages.error(request, message)
    return redirect("accounts:verify_login_otp")


def user_logout_view(request):
    logout(request)
    return redirect("accounts:login")


def redirect_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")

    if request.user.role == CustomUser.Role.ADMIN:
        return redirect("admin_panel:dashboard")
    if request.user.role == CustomUser.Role.TEACHER:
        return redirect("teacher:dashboard")
    return redirect("student:dashboard")


def home(request):
    return render(request, "accounts/home.html")
