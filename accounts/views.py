from django.shortcuts import render, redirect
from django.contrib import messages, auth
from .forms import RegistrationForm
from .models import Account
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from carts.views import _cart_id
from carts.models import Cart, CartItem
import requests # I will use it, don't fret

# Verification Email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# Create your views here.
def register(request):
    # Handling the POST request when getting the submission of the form
    if request.method == "POST":
        form = RegistrationForm(request.POST)# will contain all the field values
        
        # If user passes the form submission, he may go on to create his user
        if form.is_valid():
            # You have to use cleaned_data[index] to fetch data from the POST request method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0] # < - - - basically you are splitting the email at the first
                                           #         instance of '@' sign

            # making a user object from our accounts.models.MyAccountManager to create a user, function
            user = Account.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                phone_number=phone_number,
                email=email,
                password=password,
                username=username
            )
            user.save()

            # user activation
            current_site = get_current_site(request)
            mail_subject = "Please activate your account"
            message = render_to_string("accounts/account_verification_email.html", {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)), # we are encodin user's id, so no one can see it,
                'token': default_token_generator.make_token(user) # this is the library with make/check/delete_token functions,
            })
            to_email =email #email address of the user
            send_email = EmailMessage(mail_subject, message, to=[to_email,])
            send_email.send()

            # We have implemented Django Messages which you can find in 'messages django documentation'
            # messages.success is built in for a message after successfully completing something
            # whereas error is built in to give a message of something that went wrong
            
            #messages.success(request, 'Thank you for registering with us!\nWe have sent you a verification email to activate your user!')
            
            # After successful registration, the user is redirected to the login page,
            # and the URL will look like this:
            return redirect('/accounts/login/?command=verification&email=' + email)


    # Importing and rendering our form from forms.py where we can style our fields
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    } 
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == "POST":
        email = request.POST['email']# this name is nothing but the name of it in html file section for email
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        if user != None:
            # Making sure user's items save after he logins that way cart is not reset
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))# import it from carts.views import _cart_id
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)# cart contains session id
# Getting the Product variations by id above
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
# Getting the cart items from the user to access his product variation list, we just wanna see if it exists or not
                    cart_item = CartItem.objects.filter(user=user)
                    ex_variation_list = []
                    item_id = []
                    for i in cart_item:
                        existing_variation = i.variations.all()
                        ex_variation_list.append(list(existing_variation))
                        item_id.append(i.id)
# Now we have to see the product variation inside our existing variation list, if we find a match then we need to add it
                    for pr in product_variation:
                        if pr in ex_variation_list:
                            index = ex_variation_list.index(pr)
                            item_variation_id = item_id[index]
                            item = CartItem.objects.get(id=item_variation_id)
                            item.quantity += 1
                            item.user = user # we are assigning the item to the user
                            item.save()
                        # if doesn't find a match just adds a new variation
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()


            except:
                pass
            #logging in below
            auth.login(request, user)
            messages.success(request, "You have successfully logged in!😎")
            # using the request library we will redirect the user to the next page from where he logged in, cart - - > checkout, store - - > dashboard, etc.
            # old code just sent to the dashboard when logged in: return redirect('dashboard')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                # query - - >next=/cart/checkout/
                # params - - - > {'next': '/cart/checkout/'}
                # after we have the value of the keys = and & we need to redirect the user to those values, cart/checkout
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, "Credentials Do Not Match!🤡\nPlease Try Again or Register below")
            return redirect('login')
    return render(request, 'accounts/login.html')


@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.error(request, "You are Currently Logged Out!")
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        # will give us the primary key of the user
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user != None and default_token_generator.check_token(user, token):# this will check the token
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations, your account is activated!")
        return redirect('login')
    else:
        messages.error(request, "Invalid Activation Link1😑")
        return redirect('register')


@login_required(login_url = 'login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

def forgot_password(request):
    if request.method == "POST":
        email = request.POST['email']
        if Account.objects.filter(email=email).exists(): # returns boolean value True/False
            user = Account.objects.get(email__exact=email) # exact is case sensitive while iexact is not

            # sending an email to the user
            current_site = get_current_site(request)
            mail_subject = 'RESET your PASSWORD, or no entry😬!'
            message = render_to_string('accounts/forgot_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email,])
            send_email.send()
            # unless my app goes public email won't actually be sent to other users, it will be printed in the terminal, because of the 2022 Google Security Update
            # In order to permit sending emails, you need to paste in your address of the app, but mine is a web-development server, so yeah...
            messages.success(request, "The email for you to reset your damn password has been sent🤡!")
            #return redirect('login')
            return redirect('/accounts/login/?command=password&email=' + email)

        else:
            messages.error(request, 'Account with this email does not exist😑😑😑')
            return redirect('forgot_password')
    return render(request, 'accounts/forgotpassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user != None and default_token_generator.check_token(user, token): # in order to know whether this request is safe or not
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password!')
        return redirect('reset_password')
    else:
        messages.error(request, 'Expired Reset Password Link')
        return redirect('login')
    
def reset_password(request):
    if request.method == "POST":
        password = request.POST['password'] # name of your Create Password in html file form Submission
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            # we need to get user's sessiond id in order to be able to access his profile and change password
            # that session he plugs in @ resetpassword_validate function above, 
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)# got the user
            user.set_password(password)
            # have to use set_password thingy, the in-built function that's why
            user.save()
            messages.success(request, 'Password Reset has been a success!😪😎🤗')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match!🤬😡🤬')
            return redirect('reset_password')
    else:
        return render(request, 'accounts/reset_password.html')
