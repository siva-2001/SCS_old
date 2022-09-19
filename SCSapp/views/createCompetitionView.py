from django.shortcuts import render, redirect
from SCSapp.models.Competition import Competition
from SCSapp.forms import CreateCompetitionsForm
from django.contrib.auth.decorators import login_required
from SCSapp.func import convertDTPickerStrToDateTime

@login_required
def createCompetitionsView(request):
    userAuth = request.user.is_authenticated
    if request.user.has_perm('SCS.control_competition'):
        if request.method == "GET":
            return render(request, 'createCompetitions.html', {'form':CreateCompetitionsForm(), "userAuth":userAuth,
                                                               "userIsJudge": request.user.has_perm('SCS.control_competition')})
        else:
            try:
                newCompDataTime = convertDTPickerStrToDateTime(request.POST['lastTimeForApplications'])
                newCompetition = Competition(
                    name=request.POST['name'],
                    discription=request.POST['discription'],
                    lastTimeForApplications=newCompDataTime,
                    organizer=request.user,
                    organizerName=request.POST['organizerName'],
                    status = Competition.ANNOUNSED
                )
                newCompetition.save()
                return redirect(newCompetition)
            except:
                return render(request, 'createCompetitions.html', {'form':CreateCompetitionsForm(),
                                                                   "error":"Bad data, try again", "userAuth":userAuth})
    else:
        return redirect('homePage')
        #   Ошибка доступа

