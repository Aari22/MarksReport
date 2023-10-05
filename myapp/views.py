from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from .models import subjectmark
from .models import customuser
import random
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from django.db.models import Sum
import calendar


dropdown_subjects = None

from django.shortcuts import render

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            custom_user = customuser(username=username, password=make_password(password))
            custom_user.save()
            registration_message = f"Registration successful. Your user ID is: {custom_user.pk}"
            messages.success(request, registration_message)
            return render(request, 'myapp/login.html', {'registration_message': registration_message})

        messages.warning(request, "Username and password are required.")

    return render(request, 'myapp/register.html')

def user_login(request):
    if request.method == 'POST':
        user_id = request.POST['user_id']
        password = request.POST['password']

        try:
            user = customuser.objects.get(id=user_id)
        except customuser.DoesNotExist:
            user = None

        if user and check_password(password, user.password):
            request.session['user_id'] = user.id  # Set the user_id in the session
            request.session['username'] = user.username
            request.session['login_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            login_message = f"Login successful. Welcome, {user.username}!"
            messages.success(request, login_message)

            return redirect('subject_details')

        messages.warning(request, "Invalid username or password.")
        return render(request, 'myapp/login.html', {'wrong_password': True})  # Pass an additional context variable

    return render(request, 'myapp/login.html')
def subject_details(request):
    if request.method == 'POST':
        selected_subject = request.POST.get('subject')
        total_marks_str = request.POST.get('total_marks')
        marks_obtained_str = request.POST.get('marks_obtained')
        score_date_str = request.POST.get('score_date')

        if selected_subject == "All":
            messages.warning(request, "Cannot enter marks for ALL")
            return redirect('subject_details')

        if selected_subject and total_marks_str and marks_obtained_str:
            try:
                total_marks = float(total_marks_str)
                marks_obtained = float(marks_obtained_str)
                selected_date = datetime.datetime.strptime(score_date_str, "%Y-%m-%d").date()

            except ValueError:
                messages.warning(request, "Invalid marks value. Please enter valid numerical values")
                return redirect('subject_details')

            if total_marks <= 0:
                messages.warning(request, "Total Marks cannot be 0")
                return redirect('subject_details')

            if marks_obtained > total_marks:
                messages.warning(request, "Marks obtained cannot be greater than Total Marks")
                return redirect('subject_details')

            if marks_obtained < 0:
                messages.warning(request, "Marks obtained cannot be negative")
                return redirect('subject_details')

            percentage = (marks_obtained / total_marks) * 100

            print("User ID:", request.session.get('user_id'))  # Add this line to print the user ID

            user_id = request.session.get('user_id')
            user = customuser.objects.get(id=user_id)
            subjectmark.objects.create(user_id=user, subject=selected_subject, marks_obtained=marks_obtained,
                                       total_marks=total_marks, score_date=selected_date, percentage=percentage)

            messages.success(request, "Marks entered in the database.")
            return redirect('subject_details')

        messages.warning(request, "Please fill all the fields.")
        return redirect('subject_details')

    subjects = ["All", "Maths", "Science", "English"]
    return render(request, 'myapp/subject_details.html', {'subjects': subjects})


def generate_report1(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        selected_subject = request.POST.get('subject')

        if selected_subject == "All":
            result = subjectmark.objects.filter(user_id=user_id).order_by('score_date').values_list('score_date', 'percentage')
        else:
            result = subjectmark.objects.filter(user_id=user_id, subject=selected_subject).order_by('score_date').values_list('score_date', 'percentage')

        print(f"Selected Subject: {selected_subject}")
        print(f"Result: {result}")

        if result:
            score_dates = []
            percentage = []

            for row in result:
                score_dates.append(row[0].strftime("%Y-%m-%d"))
                percentage.append(row[1])

            average_marks = sum(percentage) / len(percentage)

            fig, ax = plt.subplots()
            ax.plot(score_dates, percentage)
            ax.set_xlabel("Score Date")
            ax.set_ylabel("Percentage")
            ax.set_title("Student marks")
            ax.text(len(score_dates) - 1, max(percentage), f"Average: {average_marks:.2f}", ha='right', va='bottom')
            plt.xticks(rotation=20, ha='right')

            graph_file_path = f'myapp/static/myapp/report1_{selected_subject}.png'
            plt.savefig(graph_file_path)
            plt.close(fig)

            return render(request, 'myapp/report1.html', {'graph_file_path': f'/static/myapp/report1_{selected_subject}.png'})

        else:
            messages.info(request, "No Data Available")
            return redirect('subject_details')
    else:
        return redirect('subject_details')

def generate_report2(request):
    user_id = request.session.get('user_id')
    selected_subject = request.POST.get('subject')

    if selected_subject == "All":
        result = subjectmark.objects.filter(user_id=user_id).values('score_date', 'subject', 'marks_obtained', 'total_marks').annotate(marks_obtained_sum=Sum('marks_obtained'), total_marks_sum=Sum('total_marks'))
    else:
        result = subjectmark.objects.filter(user_id=user_id, subject=selected_subject).values('score_date', 'subject', 'marks_obtained', 'total_marks').annotate(marks_obtained_sum=Sum('marks_obtained'), total_marks_sum=Sum('total_marks'))

    if result:
        month_names = [calendar.month_name[i] for i in range(1, 13)]
        x = np.arange(len(month_names))
        width = 0.35

        math_marks = [0] * 12
        english_marks = [0] * 12
        science_marks = [0] * 12

        for row in result:
            month_index = row['score_date'].month - 1
            if row['subject'] == "Maths":
                math_marks[month_index] = row['marks_obtained_sum'] / row['total_marks_sum']
            elif row['subject'] == "English":
                english_marks[month_index] = row['marks_obtained_sum'] / row['total_marks_sum']
            elif row['subject'] == "Science":
                science_marks[month_index] = row['marks_obtained_sum'] / row['total_marks_sum']

        plt.bar(x-width, math_marks, width=width, label='Math')
        plt.bar(x, english_marks, width=width, label='English')
        plt.bar(x+width, science_marks, width=width, label='Science')

        plt.xlabel('Months')
        plt.ylabel('Marks')
        plt.title('Monthly Average Marks')

        if selected_subject == "All":
            plt.xticks(x, month_names, rotation=35)
            plt.legend()
        else:
            plt.xticks(x, month_names, rotation=35)

        graph_file_path = f'myapp/static/myapp/report2.png'
        plt.savefig(graph_file_path)
        plt.close()

        return render(request, 'myapp/report2.html', {'graph_file_path': '/static/myapp/report2.png'})
    else:
        messages.info(request, "No Data Available")
        return redirect('subject_details')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from .models import subjectmark
from .models import customuser
import random
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from django.db.models import Sum
import calendar


dropdown_subjects = None

from django.shortcuts import render

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            custom_user = customuser(username=username, password=make_password(password))
            custom_user.save()
            registration_message = f"Registration successful. Your user ID is: {custom_user.pk}"
            messages.success(request, registration_message)
            return render(request, 'myapp/login.html', {'registration_message': registration_message})

        messages.warning(request, "Username and password are required.")

    return render(request, 'myapp/register.html')

def user_login(request):
    if request.method == 'POST':
        user_id = request.POST['user_id']
        password = request.POST['password']

        try:
            user = customuser.objects.get(id=user_id)
        except customuser.DoesNotExist:
            user = None

        if user and check_password(password, user.password):
            request.session['user_id'] = user.id  # Set the user_id in the session
            request.session['username'] = user.username
            request.session['login_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            login_message = f"Login successful. Welcome, {user.username}!"
            messages.success(request, login_message)

            return redirect('subject_details')

        messages.warning(request, "Invalid username or password.")
        return render(request, 'myapp/login.html', {'wrong_password': True})  # Pass an additional context variable

    return render(request, 'myapp/login.html')
def subject_details(request):
    if request.method == 'POST':
        selected_subject = request.POST.get('subject')
        total_marks_str = request.POST.get('total_marks')
        marks_obtained_str = request.POST.get('marks_obtained')
        score_date_str = request.POST.get('score_date')

        if selected_subject == "All":
            messages.warning(request, "Cannot enter marks for ALL")
            return redirect('subject_details')

        if selected_subject and total_marks_str and marks_obtained_str:
            try:
                total_marks = float(total_marks_str)
                marks_obtained = float(marks_obtained_str)
                selected_date = datetime.datetime.strptime(score_date_str, "%Y-%m-%d").date()

            except ValueError:
                messages.warning(request, "Invalid marks value. Please enter valid numerical values")
                return redirect('subject_details')

            if total_marks <= 0:
                messages.warning(request, "Total Marks cannot be 0")
                return redirect('subject_details')

            if marks_obtained > total_marks:
                messages.warning(request, "Marks obtained cannot be greater than Total Marks")
                return redirect('subject_details')

            if marks_obtained < 0:
                messages.warning(request, "Marks obtained cannot be negative")
                return redirect('subject_details')

            percentage = (marks_obtained / total_marks) * 100

            print("User ID:", request.session.get('user_id'))  # Add this line to print the user ID

            user_id = request.session.get('user_id')
            user = customuser.objects.get(id=user_id)
            subjectmark.objects.create(user_id=user, subject=selected_subject, marks_obtained=marks_obtained,
                                       total_marks=total_marks, score_date=selected_date, percentage=percentage)

            messages.success(request, "Marks entered in the database.")
            return redirect('subject_details')

        messages.warning(request, "Please fill all the fields.")
        return redirect('subject_details')

    subjects = ["All", "Maths", "Science", "English"]
    return render(request, 'myapp/subject_details.html', {'subjects': subjects})


def generate_report1(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        selected_subject = request.POST.get('subject')

        if selected_subject == "All":
            result = subjectmark.objects.filter(user_id=user_id).order_by('score_date').values_list('score_date', 'percentage')
        else:
            result = subjectmark.objects.filter(user_id=user_id, subject=selected_subject).order_by('score_date').values_list('score_date', 'percentage')

        print(f"Selected Subject: {selected_subject}")
        print(f"Result: {result}")

        if result:
            score_dates = []
            percentage = []

            for row in result:
                score_dates.append(row[0].strftime("%Y-%m-%d"))
                percentage.append(row[1])

            average_marks = sum(percentage) / len(percentage)

            fig, ax = plt.subplots()
            ax.plot(score_dates, percentage)
            ax.set_xlabel("Score Date")
            ax.set_ylabel("Percentage")
            ax.set_title("Student marks")
            ax.text(len(score_dates) - 1, max(percentage), f"Average: {average_marks:.2f}", ha='right', va='bottom')
            plt.xticks(rotation=20, ha='right')

            graph_file_path = f'myapp/static/myapp/report1_{selected_subject}.png'
            plt.savefig(graph_file_path)
            plt.close(fig)

            return render(request, 'myapp/report1.html', {'graph_file_path': f'/static/myapp/report1_{selected_subject}.png'})

        else:
            messages.info(request, "No Data Available")
            return redirect('subject_details')
    else:
        return redirect('subject_details')

def generate_report2(request):
    user_id = request.session.get('user_id')
    selected_subject = request.POST.get('subject')

    if selected_subject == "All":
        result = subjectmark.objects.filter(user_id=user_id).values('score_date', 'subject', 'marks_obtained', 'total_marks').annotate(marks_obtained_sum=Sum('marks_obtained'), total_marks_sum=Sum('total_marks'))
    else:
        result = subjectmark.objects.filter(user_id=user_id, subject=selected_subject).values('score_date', 'subject', 'marks_obtained', 'total_marks').annotate(marks_obtained_sum=Sum('marks_obtained'), total_marks_sum=Sum('total_marks'))

    if result:
        month_names = [calendar.month_name[i] for i in range(1, 13)]
        x = np.arange(len(month_names))
        width = 0.35

        math_marks = [0] * 12
        english_marks = [0] * 12
        science_marks = [0] * 12

        for row in result:
            month_index = row['score_date'].month - 1
            if row['subject'] == "Maths":
                math_marks[month_index] = row['marks_obtained_sum'] / row['total_marks_sum']
            elif row['subject'] == "English":
                english_marks[month_index] = row['marks_obtained_sum'] / row['total_marks_sum']
            elif row['subject'] == "Science":
                science_marks[month_index] = row['marks_obtained_sum'] / row['total_marks_sum']

        plt.bar(x-width, math_marks, width=width, label='Math')
        plt.bar(x, english_marks, width=width, label='English')
        plt.bar(x+width, science_marks, width=width, label='Science')

        plt.xlabel('Months')
        plt.ylabel('Marks')
        plt.title('Monthly Average Marks')

        if selected_subject == "All":
            plt.xticks(x, month_names, rotation=35)
            plt.legend()
        else:
            plt.xticks(x, month_names, rotation=35)

        graph_file_path = f'myapp/static/myapp/report2.png'
        plt.savefig(graph_file_path)
        plt.close()

        return render(request, 'myapp/report2.html', {'graph_file_path': '/static/myapp/report2.png'})
    else:
        messages.info(request, "No Data Available")
        return redirect('subject_details')


def list_entries(request):
    # Assuming the user is authenticated, get their ID
    user_id = request.session.get('user_id')

    # Get the user's entries
    user_entries = subjectmark.objects.filter(user_id=user_id)

    return render(request, 'myapp/list_entries.html', {'user_entries': user_entries})

def logout(request):
    del request.session['user_id']
    del request.session['username']
    del request.session['login_time']
    messages.success(request, "Logout successful!")
    return redirect('login')
