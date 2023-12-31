from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import Profile
from django.contrib import messages
from django.http import JsonResponse
from .models import Teacher, Student, Organization
import random
import json


def coursebase(request):
    return render(request, 'main/course_base.html')


# messages.error(request,'User not found')
# @login_required(login_url='login')

def loginUser(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.get(username=email)
        except:
            messages.error(request,'User not found')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request,'Username or password is incorrect')
    return render(request,'user/login.html',)

def logoutUser(request):
    logout(request)
    return redirect('index')

def generate_otp():
    new_otp = random.randint(100000, 999999)
    return new_otp

def registerUser(request):
    page='signup'
    if (request.user.is_authenticated):
        return redirect('index')
    else:
        if request.method == 'POST':
            if 'otp' in request.POST:
                print("here with otp")
                otp = request.POST.get('otp')
                session_otp = request.session.get('otp')
                if str(session_otp) == otp:
                    try:
                        username = request.POST.get('name')
                        email = request.POST.get('email')
                        phone = request.POST.get('phone')
                        status = request.POST.get('status')
                        pwd = request.POST.get('password')
                        cnfrm_pwd = request.POST.get('confirmpassword')
                        if pwd == cnfrm_pwd:
                            profile=Profile.objects.filter(email=email)
                            user=User.objects.filter(email=email)

                            if not user.exists():
                                user=User.objects.create_user(username=email,email=email)
                                user.set_password(pwd)
                                profile=Profile.objects.create(user=user,name=username,email=email,phone=phone, status=status)
                                # student=Student.objects.create(profile=profile)
                                user.save()
                                profile.save()
                                # student.save()
                                if status=='Student':
                                    student=Student.objects.create(profile=profile)
                                    student.save()
                                elif status=='Teacher':
                                    teacher=Teacher.objects.create(profile=profile)
                                    teacher.save()
                                elif status=='Organization':
                                    organization=Organization.objects.create(profile=profile)
                                    organization.save()
                                login(request, user)
                                return redirect('index')
                            else:
                                return render(request, 'user/register.html',{"msg": "User already exists"})
                        else:
                            return render(request, 'user/register.html',{ "msg":"Confirm Password is not equal to Password" }) 
                        
                    except Exception as e:
                        return HttpResponse(e)
                else:
                    return render(request, 'user/register.html',{"msg": "OTP is incorrect"})
            else:
                username = request.POST.get('name')
                # email = request.POST.get('email')
                phone = request.POST.get('phone')
                status = request.POST.get('status')
                pwd = request.POST.get('password')
                cnfrm_pwd = request.POST.get('confirmpassword')
                if pwd == cnfrm_pwd:
                    print("here to generate otp")
                    otp = generate_otp()
                    data = json.loads(request.body)
                    email = data.get('email')
                    request.session['otp'] = otp
                    request.session['email'] = email
                    request.session['username'] = username
                    request.session['phone'] = phone
                    request.session['status'] = status
                    request.session['password'] = pwd
                    print("email:", email)
                    print(f"the otp is {otp}")
                    try:
                        send_mail(
                            'OTP Verification',
                            f'Your OTP is {otp}',
                            'pilotlms.kgp@gmail.com',
                            [email],
                            fail_silently=False,
                        )
                        print("otp sent ig")
                    except Exception as e:
                        print("otp not sent", e)
                    # return render(request, 'user/register.html',{"status": "success"})
                    return JsonResponse({"status": "success"})
        return render(request, 'user/register.html')        


def update_profile(request):
    print(request.user)
    if request.user.is_authenticated:

        try:
            r_profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            raise ValueError("Profile does not exist for user")
        context = {
            'profile': r_profile
        }
        
        if request.method == 'POST':
            name = request.POST.get('name')
            image_profile = request.FILES.get('image_profile')
            shortBio = request.POST.get('shortBio')
            detail = request.POST.get('detail')
            github = request.POST.get('github')
            youtube = request.POST.get('youtube')
            twitter = request.POST.get('twitter')
            facebook = request.POST.get('facebook')
            instagram = request.POST.get('instagram')
            linkedin = request.POST.get('linkedin')
           
            

            try:
                r_profile = Profile.objects.get(user=request.user)
            except Profile.DoesNotExist:
                raise ValueError("Profile does not exist for user")
            r_profile.name=name    
            r_profile.image_profile=image_profile
            r_profile.shortBio=shortBio
            r_profile.github=github
            r_profile.youtube=youtube
            r_profile.twitter=twitter
            r_profile.facebook=facebook
            r_profile.instagram=instagram
            r_profile.linkedin=linkedin

            r_profile.save()
            if(r_profile.status=="Student"):
                date_of_birth = request.POST.get('date_of_birth')
                department = request.POST.get('department')
                student = Student.objects.filter(profile=r_profile)

                if student.exists():
                    student=Student.objects.get(profile=r_profile)
                else:
                    student=Student()  
                
                student.profile = r_profile
                student.department = department
                if(date_of_birth is not None ):
                    student.date_of_birth = date_of_birth
                student.save()
                return redirect('profile_detail',profile_id=r_profile.id)   



            elif(r_profile.status=="Teacher"):
                date_of_birth = request.POST.get('date_of_birth')
                department = request.POST.get('department')
                qualification = request.POST.get('qualification')
                bio = request.POST.get('bio')
                research_interests = request.POST.get('research_interests')
                teacher = Teacher.objects.filter(profile=r_profile)

                if teacher.exists():
                    teacher=Teacher.objects.get(profile=r_profile)
                else:
                    teacher=Teacher()  
                 
                teacher.profile = r_profile
                teacher.department = department
                teacher.qualification = qualification
                teacher.bio = bio
                teacher.research_interests = research_interests

                if(date_of_birth is not None ):
                    teacher.date_of_birth = date_of_birth
                teacher.save()
                return redirect('profile_detail',profile_id=r_profile.id)  
            

            elif(r_profile.status=="Organization"):
                location=request.POST.get('location',None)
                website = request.POST.get('website',None)
                founded_year = request.POST.get('founded_year',None)
                employees = request.POST.get('employees',None)
                print(employees)
                if(employees is None or employees==""):
                    employees=0
                print(employees)
                organization = Organization.objects.filter(profile=r_profile)
                if organization.exists():
                    organization=Organization.objects.get(profile=r_profile)
                else:
                    organization=Organization()  
                organization.profile = r_profile
                organization.location = location
                organization.website = website
                organization.employees = employees

                if(founded_year is not "" ):
                    organization.founded_year = founded_year
                organization.save()
                return redirect('profile_detail',profile_id=r_profile.id)   
            else:
                return HttpResponse("Something went wrong")
        return render(request, 'user/update_profile.html', context)
    else:
        return redirect('index')
    

def profile_detail(request, profile_id):
    
    profile = get_object_or_404(Profile, id=profile_id)
    
    if profile.status == 'Organization':
        organization = get_object_or_404(Organization, profile=profile)
        context = {'organization': organization,'profile': profile}
    
    elif profile.status == 'Teacher':
        teacher = get_object_or_404(Teacher, profile=profile)
        context = {'teacher': teacher,'profile': profile}
    
    else:
        student = get_object_or_404(Student, profile=profile)
        context = {'student': student,'profile': profile}
    return render(request, 'user/user_details.html', context)    


def reset_password(request):
    page = 'reset_password'
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        # email = request.POST.get('email')
        # data = json.loads(request.body)
        # email = data.get('email')
        # print('email', email)
        try:
            if 'otp' in request.POST:
                otp = request.POST.get('otp')
                print("otp", otp)
                print("otp in session", request.session['otp'])
                if otp == str(request.session['otp']):
                    password = request.POST.get('password')
                    confirm_password = request.POST.get('confirmpassword')
                    if password == confirm_password:
                        email = request.POST.get('email')
                        print("here", email)
                        user = User.objects.get(email=email)
                        user.set_password(password)
                        user.save()
                        print("success password")
                        messages.success(request, "Password reset successful")
                        return redirect('login')
                    else:
                        print("wrong pass")
                        messages.error(request, "Passwords don't match")
                        return render(request, 'user/reset_password.html', {'page': page})
                    # return JsonResponse({'status': 'success'})
                else:
                    return JsonResponse({'status': 'fail'})
            else:
                otp = generate_otp()
                data = json.loads(request.body)
                email = data.get('email')
                print('email', email)
                request.session['otp'] = otp
                request.session['email'] = email
                try:
                    send_mail(
                        'OTP Verification',
                        f'Your OTP is {otp}',
                        'pilotlms.kgp@gmail.com',
                        [email],
                        fail_silently=False,
                    )
                    print("otp sent", otp)
                    return JsonResponse({'status': 'success'})
                except Exception as e:
                    print("otp not sent", e)
                    return JsonResponse({'status': 'fail'})
        except User.DoesNotExist:
            print("user does not exist")
            messages.error(request, "User does not exist")
            return render(request, 'user/reset_password.html', {'page': page})
    return render(request, 'user/reset_password.html', {'page': page})

