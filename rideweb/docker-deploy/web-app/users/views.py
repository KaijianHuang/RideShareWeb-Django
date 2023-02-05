from django.shortcuts import render,redirect, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User
from django import forms
from .forms import UserRegForm, DriverRegForm, UserEditForm, DriverEditForm, RequestForm, SharedForm
from django.contrib.auth.decorators import login_required
from .models import Driver,Rider, RideDetail, Ride
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
import pytz
curr_time = datetime.now()
curr_time = pytz.utc.localize(curr_time)
def intro(request):
    return render(request, 'users/intro.html')

def register(request):
    if request.method == 'POST':
        form = UserRegForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your account has been created! You are now able to login!')
            return redirect('login')
        else:
            form = UserRegForm()
            return render(request, 'users/user_register.html',{'form':form})
    else:
        form = UserRegForm()
        return render(request, 'users/user_register.html',{'form':form})

@login_required
def profile(request):
    return render(request,'users/profile.html')

@login_required
def RegisterAsDriver(request):
    if request.method == 'GET':
        if len(Driver.objects.filter(user_id=request.user.id))!=0:
            return redirect('driver')
        else:
            form = DriverRegForm()
            return render(request, 'users/RegisterAsDriver.html', {'form':form})   
    else:
        form = DriverRegForm(request.POST)
        if form.is_valid():
            birth = form.cleaned_data['Birth']
            vtype = form.cleaned_data['Vtype']
            plateNum = form.cleaned_data['PlateNum']
            brand = form.cleaned_data['Brand']
            model = form.cleaned_data['Model']
            color = form.cleaned_data['Color']
            MaxP = form.cleaned_data['maxP']
            licenseNum = form.cleaned_data['LicenseNum']
            special = form.cleaned_data['Special']
            new_driver = Driver(user = request.user, Brith=birth,LicenseNum=licenseNum,Vtype=vtype,
                    Brand=brand,Model=model,PlateNum=plateNum,maxP=MaxP,Special=special, Color = color)
            new_driver.save()
            messages.success(request, f'Successfully registered as a driver!')
            return redirect('driver')
      
@login_required
def driver(request):
    current_driver = Driver.objects.filter(user_id = request.user.id)
    if len(current_driver) != 0:
        return  render(request, 'users/driverInterface.html')
    else:
        return redirect('RegisterAsDriver')

@login_required
def EditAsUser(request):
    if request.method == 'GET':
        form = UserEditForm()
        return render(request, 'users/EditAsUser.html', {'form':form})
    else:
        form = UserEditForm(request.POST)
        if form.is_valid():
            request.user.rider.phone = form.cleaned_data['phone']
            request.user.save()
            request.user.rider.save()
            messages.success(request, f'Successfully updated!')
            return redirect('profile')
        else:
            form = UserEditForm()
            return render(request, 'users/EditAsUser.html',{'form':form})

@login_required
def EditAsDriver(request):
    if request.method == 'GET':
        form = DriverEditForm()
        return render(request, 'users/EditAsDriver.html', {'form':form})
    else:
        form = DriverEditForm(request.POST)
        if form.is_valid():
            request.user.driver.Vtype = form.cleaned_data['Vtype']
            request.user.driver.PlateNum = form.cleaned_data['PlateNum']
            request.user.driver.Brand = form.cleaned_data['Brand']
            request.user.driver.Model = form.cleaned_data['Model']
            request.user.driver.Color = form.cleaned_data['Color']
            request.user.driver.maxP = form.cleaned_data['maxP']
            request.user.driver.LicenseNum = form.cleaned_data['LicenseNum']
            request.user.driver.Special = form.cleaned_data['Special']
            request.user.save()
            request.user.driver.save()
            messages.success(request, f'Successfully updated!')
            return redirect('driver')
        else:
            form = DriverEditForm()
            return render(request, 'users/EditAsDriver.html',{'form':form})

@login_required
def OwnerEditFail(request):
    return render(request, 'users/OwnerEditFail.html')

@login_required
def CreateRide(request):
    current_user = request.user
    if request.method == "GET":
        form = RequestForm()
        return render(request, 'users/CreateRide.html', {'form': form})
    else:
        form = RequestForm(request.POST)
        if form.is_valid():
            arrival_time = form.cleaned_data['arrival_time']
            party_size = form.cleaned_data['party_size']
            Vtype = form.cleaned_data['Vtype']
            if Vtype == 'Sedan':
                seats = 4
            else:
                seats = 6
            if arrival_time < curr_time or seats < party_size:
                return redirect('OwnerEditFail')
            RemainSeats = seats - party_size
            ride_detail = RideDetail(
                owner = request.user.first_name +''+ request.user.last_name,
                OwnerEmail = request.user.email,
                destination = form.cleaned_data['destination'],
                arrival_time = form.cleaned_data['arrival_time'],
                RemainSeats = seats - party_size,
                Vtype = Vtype,
                sharable = form.cleaned_data['sharable'],
                Special = form.cleaned_data['Special'],
            )
            ride_detail.save()
            ride = ride_detail.ride_set.create(user_role='Owner', party_size=party_size)
            current_user.ride_set.add(ride)
            messages.success(request, f'Successfully created!')
            return redirect('OwnerRides')
        return redirect('OwnerEditFail')
            
@login_required
def OwnerRides(request):
    user = request.user

    owner_rides = Ride.objects.filter(user_id=user.id, user_role='Owner')
    owner_open_rides = []

    for ride in owner_rides:
        ride_detail = RideDetail.objects.filter(id=ride.ride_detail_id)[0]
        if ride_detail.status == 'Open':
            owner_open_rides.append(ride_detail)


    sharer_rides = Ride.objects.filter(user_id=user.id, user_role='Sharer')
    sharer_open_rides = []

    for ride in sharer_rides:
        ride_detail = RideDetail.objects.filter(id=ride.ride_detail_id)[0]
        if ride_detail.status == 'Open':
            sharer_open_rides.append(ride_detail)

    return render(request, 'users/OwnerRides.html',{'owner_open_rides': owner_open_rides, 'sharer_open_rides':sharer_open_rides})

@login_required
def OwnerViewEdit(request, ride_detail_id):
    ride_detail = RideDetail.objects.filter(id=ride_detail_id)[0]
    ride_list = Ride.objects.filter(ride_detail_id=ride_detail_id,user_role='Sharer')
    sharers_list = []
    for ride in ride_list:
        user = User.objects.filter(pk=ride.user_id).first()
        sharers_list.append(user.first_name)
    context = {'ride': ride_detail, "sharers_list" : sharers_list, "sharers": ride_list}
    return render(request, "users/OwnerViewEdit.html", context)

@login_required
def edit_ride(request):
    if request.method == 'POST':
        data = request.POST
        ride_detail_id = data['edit_id']
        edit_ride = Ride.objects.filter(ride_detail_id=ride_detail_id, user_role='Owner')[0]
        edit_ride_detail = RideDetail.objects.filter(pk=ride_detail_id)[0]
        arrival_time = data['arrival_time']
        arrival_time = datetime.strptime(arrival_time, '%Y-%m-%dT%H:%M')
        arrival_time = pytz.utc.localize(arrival_time)
        party_size = int(data['party_size'])
        vehicle = data.get('vehicle')

        if vehicle == 'Sedan':
            seats = 4
        else:
            seats = 6
        if arrival_time < curr_time or seats < party_size:
            return HttpResponseRedirect('/owner_edit_fail/')

        edit_ride_detail.destination = data.get('destination')
        edit_ride_detail.arrival_time = arrival_time
        edit_ride_detail.RemainSeats = seats - party_size
        edit_ride_detail.Vtype = vehicle
        edit_ride_detail.sharable = data.get('sharable')
        edit_ride_detail.Special = data.get('special_request')
        edit_ride_detail.save()

        edit_ride.party_size = party_size
        edit_ride.save()
        messages.success(request, f'You have successfully edited the ride request!')
        return HttpResponseRedirect('/OwnerViewEdit/'+ride_detail_id)

@login_required
def search_ride(request):
    user = request.user
    if request.method == 'GET':
        form = SharedForm()
        return render(request, 'users/search_ride.html', {'form': form, "existRides":False})
    else:
        form = SharedForm(request.POST)
        if form.is_valid():
            destination = form.cleaned_data['destination']
            earliest_arrival = form.cleaned_data['earliest_arrival']
            latest_arrival = form.cleaned_data['latest_arrival']
            party_size = form.cleaned_data['party_size']

            share_rides = RideDetail.objects.filter(sharable=True, status="Open")
            potential_rides = share_rides.exclude(OwnerEmail=user.email)
            potential_rides = potential_rides.filter(RemainSeats__gt=party_size-1, destination = destination)
            available_rides = potential_rides

            for ride in potential_rides:
                if ride.arrival_time>latest_arrival:
                    available_rides = available_rides.exclude(id=ride.id)

                elif ride.arrival_time<earliest_arrival:
                    available_rides = available_rides.exclude(id=ride.id)

            return render(request, 'users/search_ride.html', {'form': form, 'available_rides': available_rides, "existRides":True, "size":party_size})
        else:
            messages.success(request, f'Fail to search the ride! Maybe exceeded number of passengers')
            return render(request, 'users/OwnerRides.html')

@login_required
def join_ride(request):
    user = request.user
    data = request.POST
    ride_detail_id = data['ride_detail_id']
    party_size = int(data['size'])
    ride_detail = RideDetail.objects.filter(id=ride_detail_id)[0]
    rides_in = Ride.objects.filter(user=user,ride_detail=ride_detail)
    if len(rides_in)==0:
        ride_detail.RemainSeats -= party_size
        ride_detail.save()
        ride = ride_detail.ride_set.create(user_role='Sharer', party_size=party_size)
        user.ride_set.add(ride)
        messages.success(request, f'You have successfully joined the ride!')
        return render(request, 'users/OwnerRides.html')
    else:
        messages.success(request, f'Fail to join the ride!')
        return render(request,'users/OwnerRides.html')



@login_required
def SharerViewEdit(request, ride_detail_id):
    user = request.user
    ride = Ride.objects.filter(ride_detail_id=ride_detail_id,user_id=user.id)[0]
    ride_detail = RideDetail.objects.filter(id=ride_detail_id)[0]
    ride_list = Ride.objects.filter(ride_detail_id=ride_detail_id,user_role='Sharer')
    sharers_list = []
    for ride in ride_list:
        user = User.objects.filter(pk=ride.user_id).first()
        sharers_list.append(user.first_name)
    context = {'ride': ride_detail, "sharers_list" : sharers_list,"ride_id":ride.id}
    return render(request, "users/SharerViewEdit.html", context)

@login_required
def sharer_edit_ride(request):
    if request.method == 'POST':
        data = request.POST
        ride_detail_id = data['edit_id']
        ride_id = data['ride_id']
        edit_ride = Ride.objects.filter(id=ride_id)[0]
        edit_ride_detail = RideDetail.objects.filter(pk=ride_detail_id)[0]

        party_size = int(data['party_size'])
        old_size = edit_ride.party_size
        old_remain = edit_ride_detail.RemainSeats
        if party_size - old_size - old_remain > 0:
            return HttpResponseRedirect('/OwnerEditFail/')

        remaining_seats = old_size + old_remain - party_size
        edit_ride_detail.RemainSeats = remaining_seats
        edit_ride_detail.save()

        edit_ride.party_size = party_size
        edit_ride.save()

        return HttpResponseRedirect('/SharerViewEdit/'+ride_detail_id)

#driver part
@login_required
def driver_search_ride(request):
    current_user = request.user
    driver = Driver.objects.filter(user_id = current_user.id)[0]
    ridelist = RideDetail.objects.filter(Vtype = driver.Vtype, status = 'Open')
    ridelist = ridelist.exclude(OwnerEmail = current_user.email)
    for ride in ridelist:
        if ride.Special:
            if ride.Special != driver.Special:
                ridelist = ridelist.exclude(id = ride.id)
    return render(request, 'users/driver_search_ride.html', {'ridelist':ridelist})

@login_required
def confirm_ride(request, ride_detail_id):
    current_user = request.user
    ride_detail = RideDetail.objects.filter(id=ride_detail_id)[0]
    ride_detail.status = 'Confirmed'
    ride_detail.driver = current_user.first_name
    ride_detail.save()

    ride = ride_detail.ride_set.create(user_role='Driver', party_size=1)
    current_user.ride_set.add(ride)

    email_list = []
    rides = Ride.objects.filter(ride_detail_id=ride_detail_id)
    for ride in rides:
        if ride.user_role == "Driver":
            continue
        passenger = User.objects.filter(id=ride.ride_detail_id)[0]
        email_list.append(passenger.email)

    subject = 'Your ride has been confirmed!'
    message = 'Here is the info of the ride\n'
    message += 'Destination: ' + ride_detail.destination + '\n'
    message += 'Arrival time: ' + str(ride_detail.arrival_time) + '\n'
    message += 'Driver: ' + current_user.first_name+'\n'
    message += 'Vehicle: ' + ride_detail.Vtype + '\n'
    

    from_email = settings.EMAIL_HOST_USER

    send_mail(subject, message, from_email, email_list, fail_silently=False)
    messages.success(request, f'Successfully claim the ride!')
    return render(request, 'users/drive.html')
    
def complete_ride(request,ride_detail_id):
    ride_detail = RideDetail.objects.filter(id=ride_detail_id)[0]
    ride_detail.status = 'Completed'
    ride_detail.save()
    messages.success(request, f'Successfully complete the ride!')
    return render(request, 'users/driver_search_ride.html')

def ConfirmedDriver(request):
    driver = request.user
    rides = Ride.objects.filter(user_id = driver.id ,user_role = 'Driver')
    confirmed_rides = []
    completed_rides = []

    for ride in rides:
        ride_detail = RideDetail.objects.filter(id=ride.ride_detail_id)[0]
        if ride_detail.status == 'Confirmed':
            confirmed_rides.append(ride_detail)
        elif ride_detail.status == 'Completed':
            completed_rides.append(ride_detail)

    return render(request, 'users/ConfirmedDriver.html', {'confirmed_rides': confirmed_rides, 'completed_rides': completed_rides})

def ConfirmedUser(request):
    user = request.user
    rides = Ride.objects.filter(user_id=user.id)
    rides = rides.exclude(user_role='Driver')
    confirmed_rides = []
    for ride in rides:
        ride_detail = RideDetail.objects.filter(id=ride.ride_detail_id)[0]
        if ride_detail.status == 'Confirmed':
            confirmed_rides.append(ride_detail)

    return render(request, 'users/ConfirmedUser.html',{'confirmed_rides': confirmed_rides})

def ConfirmedUserDetail(request, ride_detail_id):
    ride_detail = RideDetail.objects.filter(id=ride_detail_id)[0]
    ride_list = Ride.objects.filter(ride_detail_id=ride_detail_id, user_role='Sharer')
    sharers_list = []
    for ride in ride_list:
        user = User.objects.filter(pk=ride.user_id).first()
        sharers_list.append(user.first_name)

    ride = Ride.objects.filter(ride_detail_id=ride_detail_id, user_role='Driver')[0]
    user = User.objects.filter(pk=ride.user_id).first()
    driver_name = user.first_name+' '+user.last_name
    driver = Driver.objects.filter(user_id=ride.user_id)[0]
    context = {'ride': ride_detail, "sharers_list": sharers_list, "sharers": ride_list,"driver":driver, "driver_name":driver_name}
    return render(request, "users/ConfirmedUserDetail.html", context)
