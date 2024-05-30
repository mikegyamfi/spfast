import json
from datetime import datetime
from time import sleep

import pandas as pd
from decouple import config
from django.contrib.auth.models import Group, Permission
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
import requests
from tablib import Dataset

from . import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . import helper, models
from .forms import UploadFileForm
from .models import CustomUser
from .resource import CustomUserResource


# Create your views here.
def home(request):
    return render(request, "layouts/index.html")


def services(request):
    return render(request, "layouts/services.html")


@login_required(login_url='login')
def pay_with_wallet(request):
    if request.method == "POST":
        admin = models.AdminInfo.objects.filter().first().phone_number
        user = models.CustomUser.objects.get(id=request.user.id)
        phone_number = request.POST.get("phone")
        amount = request.POST.get("amount")
        reference = request.POST.get("reference")
        if user.wallet is None:
            return JsonResponse(
                {'status': f'Your wallet balance is low. Contact the admin to recharge. Admin Contact Info: 0{admin}'})
        elif user.wallet <= 0 or user.wallet < float(amount):
            return JsonResponse(
                {'status': f'Your wallet balance is low. Contact the admin to recharge. Admin Contact Info: 0{admin}'})
        print(phone_number)
        print(amount)
        print(reference)
        bundle = models.IshareBundlePrice.objects.get(
            price=float(amount)).bundle_volume if user.status == "User" else models.AgentIshareBundlePrice.objects.get(
            price=float(amount)).bundle_volume
        send_bundle_response = helper.send_bundle(phone_number, bundle, reference)
        try:
            data = send_bundle_response.json()
            print(data)
        except Exception as e:
            print(e)
            return JsonResponse({'status': f'Something went wrong'})

        sms_headers = {
            'Authorization': 'Bearer 1436|gac9vHmxr2q5TSvYMSaT5qkfPJ8x6M8S2WNJtLur',
            'Content-Type': 'application/json'
        }

        sms_url = 'https://webapp.usmsgh.com/api/sms/send'
        if send_bundle_response.status_code == 200:
            if data["status"] == "Success":
                new_transaction = models.IShareBundleTransaction.objects.create(
                    user=request.user,
                    bundle_number=phone_number,
                    offer=f"{bundle}MB",
                    reference=reference,
                    transaction_status="Completed"
                )
                new_transaction.save()
                user.wallet -= float(amount)
                user.save()
                receiver_message = f"Your bundle purchase has been completed successfully. {bundle}MB has been credited to you by {request.user.phone}.\nReference: {reference}\n"
                sms_message = f"Hello @{request.user.username}. Your bundle purchase has been completed successfully. {bundle}MB has been credited to {phone_number}.\nReference: {reference}\nCurrent Wallet Balance: {user.wallet}\nThank You.\n\n"

                num_without_0 = phone_number[1:]
                print(num_without_0)
                receiver_body = {
                    'recipient': f"233{num_without_0}",
                    'sender_id': 'SPFASTGH',
                    'message': receiver_message
                }

                response = requests.request('POST', url=sms_url, params=receiver_body, headers=sms_headers)
                print(response.text)

                sms_body = {
                    'recipient': f"233{request.user.phone}",
                    'sender_id': 'SPFASTGH',
                    'message': sms_message
                }

                try:
                    response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)

                    print(response.text)
                    return JsonResponse({'status': 'Transaction Completed Successfully', 'icon': 'success'})
                except:
                    return JsonResponse({'status': 'Transaction Completed Successfully', 'icon': 'success'})
            else:
                new_transaction = models.IShareBundleTransaction.objects.create(
                    user=request.user,
                    bundle_number=phone_number,
                    offer=f"{bundle}MB",
                    reference=reference,
                    transaction_status="Failed"
                )
                new_transaction.save()
                return JsonResponse({'status': 'Something went wrong'})
        else:
            new_transaction = models.IShareBundleTransaction.objects.create(
                user=request.user,
                bundle_number=phone_number,
                offer=f"{bundle}MB",
                reference=reference,
                transaction_status="Failed"
            )
            new_transaction.save()
            return JsonResponse({'status': 'Something went wrong'})
    return redirect('airtel-tigo')


@login_required(login_url='login')
def airtel_tigo(request):
    if models.AdminInfo.objects.filter().first().at_active:
        user = models.CustomUser.objects.get(id=request.user.id)
        status = user.status
        form = forms.IShareBundleForm(status)
        reference = helper.ref_generator()
        user_email = request.user.email
        if request.method == "POST":
            form = forms.IShareBundleForm(data=request.POST, status=status)
            payment_reference = request.POST.get("reference")
            amount_paid = request.POST.get("amount")
            new_payment = models.Payment.objects.create(
                user=request.user,
                reference=payment_reference,
                amount=amount_paid,
                transaction_date=datetime.now(),
                transaction_status="Completed"
            )
            new_payment.save()
            print("payment saved")
            print("form valid")
            phone_number = request.POST.get("phone")
            offer = request.POST.get("amount")
            print(offer)
            bundle = models.IshareBundlePrice.objects.get(
                price=float(
                    offer)).bundle_volume if user.status == "User" else models.AgentIshareBundlePrice.objects.get(
                price=float(offer)).bundle_volume
            new_transaction = models.IShareBundleTransaction.objects.create(
                user=request.user,
                bundle_number=phone_number,
                offer=f"{bundle}MB",
                reference=payment_reference,
                transaction_status="Pending"
            )
            print("created")
            new_transaction.save()

            print("===========================")
            print(phone_number)
            print(bundle)
            print("--------------------")
            # send_bundle_response = helper.send_bundle(request.user, phone_number, bundle, payment_reference)
            # print("********************")
            # data = send_bundle_response.json()
            #
            # print(data)
            return JsonResponse({'status': 'Transaction Completed Successfully', 'icon': 'success'})
        user = models.CustomUser.objects.get(id=request.user.id)
        context = {"form": form, "ref": reference, "email": user_email,
                   "wallet": 0 if user.wallet is None else user.wallet}
        return render(request, "layouts/services/at.html", context=context)
    else:
        messages.info(request, "Service is currently Unavailable")
        return redirect('home')


@login_required(login_url='login')
def mtn_pay_with_wallet(request):
    if request.method == "POST":
        user = models.CustomUser.objects.get(id=request.user.id)
        phone_number = request.POST.get("phone")
        amount = request.POST.get("amount")
        reference = request.POST.get("reference")
        print(phone_number)
        print(amount)
        print(reference)
        if user.wallet is None:
            return JsonResponse(
                {'status': f'Your wallet balance is low. Contact the admin to recharge.'})
        elif user.wallet <= 0 or user.wallet < float(amount):
            return JsonResponse(
                {'status': f'Your wallet balance is low. Contact the admin to recharge.'})
        bundle = models.MTNBundlePrice.objects.get(
            price=float(amount)).bundle_volume if user.status == "User" else models.AgentMTNBundlePrice.objects.get(
            price=float(amount)).bundle_volume
        print(bundle)
        new_mtn_transaction = models.MTNTransaction.objects.create(
            user=request.user,
            bundle_number=phone_number,
            offer=bundle,
            reference=reference,
        )
        new_mtn_transaction.save()
        user.wallet -= float(amount)
        user.save()
        return JsonResponse({'status': "Your transaction will be completed shortly", 'icon': 'success'})
    return redirect('mtn')


@login_required(login_url='login')
def mtn(request):
    if models.AdminInfo.objects.filter().first().mtn_active:
        user = models.CustomUser.objects.get(id=request.user.id)
        status = user.status
        form = forms.MTNForm(status)
        reference = helper.ref_generator()
        user_email = request.user.email

        if request.method == "POST":
            payment_reference = request.POST.get("reference")
            amount_paid = request.POST.get("amount")
            new_payment = models.Payment.objects.create(
                user=request.user,
                reference=payment_reference,
                amount=amount_paid,
                transaction_date=datetime.now(),
                transaction_status="Pending"
            )
            new_payment.save()
            phone_number = request.POST.get("phone")
            offer = request.POST.get("amount")

            bundle = models.MTNBundlePrice.objects.get(
                price=float(offer)).bundle_volume if user.status == "User" else models.AgentMTNBundlePrice.objects.get(
                price=float(offer)).bundle_volume

            print(phone_number)
            new_mtn_transaction = models.MTNTransaction.objects.create(
                user=request.user,
                bundle_number=phone_number,
                offer=f"{bundle}MB",
                reference=payment_reference,
            )
            new_mtn_transaction.save()
            return JsonResponse({'status': "Your transaction will be completed shortly", 'icon': 'success'})
        user = models.CustomUser.objects.get(id=request.user.id)
        phone_num = user.phone
        mtn_dict = {}

        if user.status == "Agent":
            mtn_offer = models.AgentMTNBundlePrice.objects.all()
        else:
            mtn_offer = models.MTNBundlePrice.objects.all()
        for offer in mtn_offer:
            mtn_dict[str(offer)] = offer.bundle_volume
        context = {'form': form, 'phone_num': phone_num, 'mtn_dict': json.dumps(mtn_dict),
                   "ref": reference, "email": user_email, "wallet": 0 if user.wallet is None else user.wallet}
        return render(request, "layouts/services/mtn.html", context=context)
    else:
        messages.info(request, "Service is currently Unavailable")
        return redirect('home')


@login_required(login_url='login')
def history(request):
    user_transactions = models.IShareBundleTransaction.objects.filter(user=request.user).order_by(
        'transaction_date').reverse()
    header = "AirtelTigo Transactions"
    net = "tigo"
    context = {'txns': user_transactions, "header": header, "net": net}
    return render(request, "layouts/history.html", context=context)


@login_required(login_url='login')
def mtn_history(request):
    user_transactions = models.MTNTransaction.objects.filter(user=request.user).order_by('transaction_date').reverse()
    header = "MTN Transactions"
    net = "mtn"
    context = {'txns': user_transactions, "header": header, "net": net}
    return render(request, "layouts/history.html", context=context)


def verify_transaction(request, reference):
    if request.method == "GET":
        response = helper.verify_paystack_transaction(reference)
        data = response.json()
        try:
            status = data["data"]["status"]
            amount = data["data"]["amount"]
            api_reference = data["data"]["reference"]
            date = data["data"]["paid_at"]
            real_amount = float(amount) / 100
            print(status)
            print(real_amount)
            print(api_reference)
            print(reference)
            print(date)
        except:
            status = data["status"]
        return JsonResponse({'status': status})


@login_required(login_url='login')
def admin_mtn_history(request):
    if request.user.is_staff and request.user.is_superuser:
        all_txns = models.MTNTransaction.objects.filter().order_by('-transaction_date')
        context = {'txns': all_txns}
        return render(request, "layouts/services/mtn_admin.html", context=context)


@login_required(login_url='login')
def admin_at_history(request):
    if request.user.is_staff and request.user.is_superuser:
        all_txns = models.IShareBundleTransaction.objects.filter().order_by('-transaction_date')
        context = {'txns': all_txns}
        return render(request, "layouts/services/at_admin.html", context=context)


@login_required(login_url='login')
def mark_as_sent(request, pk):
    if request.user.is_staff and request.user.is_superuser:
        txn = models.MTNTransaction.objects.filter(id=pk).first()
        print(txn)
        txn.transaction_status = "Completed"
        txn.save()
        sms_headers = {
            'Authorization': 'Bearer 1436|gac9vHmxr2q5TSvYMSaT5qkfPJ8x6M8S2WNJtLur',
            'Content-Type': 'application/json'
        }

        sms_url = 'https://webapp.usmsgh.com/api/sms/send'
        sms_message = f"Your account has been credited with {txn.offer}.\nTransaction Reference: {txn.reference}"

        sms_body = {
            'recipient': f"233{txn.bundle_number}",
            'sender_id': 'SPFASTGH',
            'message': sms_message
        }
        try:
            response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)
            print(response.text)
        except:
            messages.success(request, f"Transaction Completed")
            return redirect('mtn_admin')
        messages.success(request, f"Transaction Completed")
        return redirect('mtn_admin')


@login_required(login_url='login')
def at_mark_as_sent(request, pk):
    if request.user.is_staff and request.user.is_superuser:
        txn = models.IShareBundleTransaction.objects.filter(id=pk).first()
        print(txn)
        txn.transaction_status = "Completed"
        txn.save()
        sms_headers = {
            'Authorization': 'Bearer 1436|gac9vHmxr2q5TSvYMSaT5qkfPJ8x6M8S2WNJtLur',
            'Content-Type': 'application/json'
        }

        sms_url = 'https://webapp.usmsgh.com/api/sms/send'
        sms_message = f"Your account has been credited with {txn.offer}.\nTransaction Reference: {txn.reference}"

        sms_body = {
            'recipient': f"233{txn.bundle_number}",
            'sender_id': 'SPFASTGH',
            'message': sms_message
        }
        # response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)
        # print(response.text)
        messages.success(request, f"Transaction Completed")
        return redirect('at_admin')


@login_required(login_url='login')
def credit_user(request):
    user = models.CustomUser.objects.get(id=request.user.id)
    if request.user.is_superuser:
        form = forms.CreditUserForm()
        if request.method == "POST":
            form = forms.CreditUserForm(request.POST)
            if form.is_valid():
                user = form.cleaned_data["user"]
                amount = form.cleaned_data["amount"]
                print(user)
                print(amount)
                user_needed = models.CustomUser.objects.get(username=user)
                if user_needed.wallet is None:
                    user_needed.wallet = amount
                else:
                    user_needed.wallet += float(amount)
                user_needed.save()
                print(user_needed.username)
                messages.success(request, "Crediting Successful")
                return redirect('credit_user')
        context = {'form': form}
        return render(request, "layouts/services/credit.html", context=context)
    else:
        messages.success(request, "Access Denied")
        return redirect('home')


@login_required(login_url='login')
def topup_info(request):
    if request.method == "POST":
        admin = models.AdminInfo.objects.filter().first().phone_number
        user = models.CustomUser.objects.get(id=request.user.id)
        amount = request.POST.get("amount")
        if float(amount) < 10:
            messages.info(request, "Minimum amount is GHS 10")
            return redirect('topup-info')
        print(amount)
        reference = helper.top_up_ref_generator()
        new_topup_request = models.TopUpRequest.objects.create(
            user=request.user,
            amount=amount,
            reference=reference,
        )
        new_topup_request.save()

        sms_headers = {
            'Authorization': 'Bearer 1436|gac9vHmxr2q5TSvYMSaT5qkfPJ8x6M8S2WNJtLur',
            'Content-Type': 'application/json'
        }

        sms_url = 'https://webapp.usmsgh.com/api/sms/send'
        sms_message = f"A top up request has been placed.\nGHS{amount} for {user}.\nReference: {reference}"

        sms_body = {
            'recipient': f"233{admin}",
            'sender_id': 'SPFASTGH',
            'message': sms_message
        }
        # response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)
        # print(response.text)
        messages.success(request,
                         f"Your Request has been sent successfully. Kindly go on to pay to {admin} and use the reference stated as reference. Reference: {reference}")
        return redirect("request_successful", reference)
    return render(request, "layouts/topup-info.html")


@login_required(login_url='login')
def request_successful(request, reference):
    admin = models.AdminInfo.objects.filter().first()
    context = {
        "name": admin.name,
        "number": f"0{admin.momo_number}",
        "channel": admin.payment_channel,
        "reference": reference
    }
    return render(request, "layouts/services/request_successful.html", context=context)


def topup_list(request):
    if request.user.is_superuser:
        topup_requests = models.TopUpRequest.objects.all().order_by('date').reverse()
        context = {
            'requests': topup_requests,
        }
        return render(request, "layouts/services/topup_list.html", context=context)
    else:
        messages.error(request, "Access Denied")
        return redirect('home')


@login_required(login_url='login')
def credit_user_from_list(request, reference):
    if request.user.is_superuser:
        crediting = models.TopUpRequest.objects.filter(reference=reference).first()
        user = crediting.user
        custom_user = models.CustomUser.objects.get(username=user.username)
        if crediting.status:
            return redirect('topup_list')
        amount = crediting.amount
        print(user)
        print(user.phone)
        print(amount)
        custom_user.wallet += amount
        custom_user.save()
        crediting.status = True
        crediting.credited_at = datetime.now()
        crediting.save()
        sms_headers = {
            'Authorization': 'Bearer 1436|gac9vHmxr2q5TSvYMSaT5qkfPJ8x6M8S2WNJtLur',
            'Content-Type': 'application/json'
        }

        sms_url = 'https://webapp.usmsgh.com/api/sms/send'
        sms_message = f"Hello,\nYour wallet has been topped up with GHS{amount}.\nReference: {reference}.\nThank you"

        sms_body = {
            'recipient': f"233{custom_user.phone}",
            'sender_id': 'SPFASTGH',
            'message': sms_message
        }
        try:
            response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)
            print(response.text)
        except:
            messages.success(request, f"{user} has been credited with {amount}")
            return redirect('topup_list')
        messages.success(request, f"{user} has been credited with {amount}")
        return redirect('topup_list')


@login_required(login_url='login')
def at_mark_completed(request, pk, status):
    if request.user.is_superuser:
        txn = models.IShareBundleTransaction.objects.get(id=pk)
        if txn:
            if status == "WIP":
                txn.transaction_status = "WIP"
                txn.save()
                messages.success(request, f"Transaction in progress")
            elif status == "Initiated":
                txn.transaction_status = "Initiated"
                txn.save()
                messages.success(request, f"Transaction Initiated")
            elif status == "Completed":
                txn.transaction_status = "Completed"
                txn.save()
                # sms_headers = {
                #     'Authorization': 'Bearer 1436|gac9vHmxr2q5TSvYMSaT5qkfPJ8x6M8S2WNJtLur',
                #     'Content-Type': 'application/json'
                # }
                #
                # sms_url = 'https://webapp.usmsgh.com/api/sms/send'
                # sms_message = f"Hello,\nYour wallet has been topped up with GHS{amount}.\nReference: {reference}.\nThank you"
                #
                # sms_body = {
                #     'recipient': f"233{custom_user.phone}",
                #     'sender_id': 'SPFASTGH',
                #     'message': sms_message
                # }
                # response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)
                # print(response.text)
                messages.success(request, f"Transaction Completed")
        return redirect('at_admin')


@login_required(login_url='login')
def mtn_mark_completed(request, pk, status):
    if request.user.is_superuser:
        txn = models.MTNTransaction.objects.get(id=pk)
        if txn:
            if status == "WIP":
                txn.transaction_status = "WIP"
                txn.save()
                messages.success(request, f"Transaction in progress")
            elif status == "Initiated":
                txn.transaction_status = "Initiated"
                txn.save()
                messages.success(request, f"Transaction Initiated")
            elif status == "Completed":
                txn.transaction_status = "Completed"
                txn.save()
                sms_headers = {
                    'Authorization': 'Bearer 1436|gac9vHmxr2q5TSvYMSaT5qkfPJ8x6M8S2WNJtLur',
                    'Content-Type': 'application/json'
                }

                sms_url = 'https://webapp.usmsgh.com/api/sms/send'
                sms_message = f"Your account has been credited with {txn.offer}.\nTransaction Reference: {txn.reference}"

                sms_body = {
                    'recipient': f"233{txn.bundle_number}",
                    'sender_id': 'SPFASTGH',
                    'message': sms_message
                }
                response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)
                print(response.text)
                # sms_headers = {
                #     'Authorization': 'Bearer 1436|gac9vHmxr2q5TSvYMSaT5qkfPJ8x6M8S2WNJtLur',
                #     'Content-Type': 'application/json'
                # }
                #
                # sms_url = 'https://webapp.usmsgh.com/api/sms/send'
                # sms_message = f"Hello,\nYour wallet has been topped up with GHS{amount}.\nReference: {reference}.\nThank you"
                #
                # sms_body = {
                #     'recipient': f"233{custom_user.phone}",
                #     'sender_id': 'SPFASTGH',
                #     'message': sms_message
                # }
                # response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)
                # print(response.text)
                messages.success(request, f"Transaction Completed")
        return redirect('mtn_admin')

# def populate_custom_users_from_excel(request):
#     # Read the Excel file using pandas
#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             excel_file = request.FILES['file']
#
#             # Process the uploaded Excel file
#             df = pd.read_excel(excel_file)
#             counter = 0
#             # Iterate through rows to create CustomUser instances
#             for index, row in df.iterrows():
#                 print(counter)
#                 # Create a CustomUser instance for each row
#                 custom_user = CustomUser.objects.create(
#                     first_name=row['first_name'],
#                     last_name=row['last_name'],
#                     username=str(row['username']),
#                     email=row['email'],
#                     phone=row['phone'],
#                     wallet=float(row['wallet']),
#                     status=str(row['status']),
#                     password1=row['password1'],
#                     password2=row['password2'],
#                     is_superuser=row['is_superuser'],
#                     is_staff=row['is_staff'],
#                     is_active=row['is_active'],
#                     password=row['password']
#                 )
#
#                 custom_user.save()
#
#                 # group_names = row['groups'].split(',')  # Assuming groups are comma-separated
#                 # groups = Group.objects.filter(name__in=group_names)
#                 # custom_user.groups.set(groups)
#                 #
#                 # if row['user_permissions']:
#                 #     permission_ids = [int(pid) for pid in row['user_permissions'].split(',')]
#                 #     permissions = Permission.objects.filter(id__in=permission_ids)
#                 #     custom_user.user_permissions.set(permissions)
#                 print("killed")
#                 counter = counter+1
#             messages.success(request, 'All done')
#     else:
#         form = UploadFileForm()
#     return render(request, 'layouts/import_users.html', {'form': form})


# def delete_custom_users(request):
#     CustomUser.objects.all().delete()
#     return HttpResponseRedirect('Done')


# def send_change_sms(request):
#     sms_headers = {
#         'Authorization': 'Bearer 1334|wroIm5YnQD6hlZzd8POtLDXxl4vQodCZNorATYGX',
#         'Content-Type': 'application/json'
#     }
#
#     sms_url = 'https://webapp.usmsgh.com/api/sms/send'
#
#     all_users = CustomUser.objects.all()
#     counter = 0
#
#     for user in all_users:
#         sleep(1)
#         sms_message = f"Hello {user.username},\nGH Bay has changed its website to https://www.ghbays.com\nYou do not need to create a new account for this. Just log in and start transacting\nAll wallet balance are intact."
#
#         sms_body = {
#             'recipient': f"233{user.phone}",
#             'sender_id': 'GH BAY',
#             'message': sms_message
#         }
#
#         response = requests.request('POST', url=sms_url, params=sms_body, headers=sms_headers)
#         print(response.text)
#         counter = counter+1
#         print(counter)
#         print("killed")
#     messages.success(request, "ALL DONE")
#     return redirect('home')
