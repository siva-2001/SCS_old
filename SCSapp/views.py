from django.shortcuts import render, redirect, get_object_or_404
from .models import Competition, Match, MatchEvent, VolleyballTeam, Player
from .forms import CreateCompetitionsForm, RegistrVolleybolTeamForm, RegistrPlayerForm, MatchEditForm, SignUpUser
from django.contrib.auth.forms import  AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
#from django.db.models.functions.datetime import datetime
from django.forms import formset_factory
from django.core.paginator import Paginator
import pytz
from datetime import timedelta, datetime
from .func import convertDTPickerStrToDateTime, checkCompetitionStart


def signUpUserView(request):
    userAuth = request.user.is_authenticated
    form = SignUpUser()
    if request.method == 'GET':
        return render(request, 'signUpUser.html', {'form':form})
    else:
        if request.POST['password1'] == request.POST['password2'] and len(request.POST["email"]):
            try:

                user = User.objects.create_user(username=request.POST['username'], email=request.POST['email'],
                    first_name=request.POST['first_name'], last_name=request.POST['last_name'])
                user.set_password(request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('homePage')
            except:
                return render(request, 'signUpUser.html', {'form':form, "userAuth":userAuth,
                    'error':'Имя пользователя занято. Выберите другое'})
        else:
            return render(request, 'signUpUser.html', {'form':form,
                'error':'Пароли не совпадают или не введён e-mail', "userAuth":userAuth})


def logInUserView(request):
    userAuth = request.user.is_authenticated
    if request.method == "GET":
        return render(request, 'logInUser.html', {'form':AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return redirect('homePage')
        else:
            return render(request, 'logInUser.html', {"form":AuthenticationForm(), "userAuth":userAuth,
                                                      "error":'Данные введены неверно'})


@login_required
def logoutUser(request):
    logout(request)
    return redirect('homePage')

def compHomePageView(request):
    checkCompetitionStart()
    userAuth = request.user.is_authenticated
    announcedCompetitions = Competition.objects.all().filter(status=Competition.ANNOUNSED)
    currentCompetitions = Competition.objects.all().filter(status=Competition.CURRENT)
    pastCompetitions = Competition.objects.all().filter(status=Competition.PAST)
    if(len(pastCompetitions) > 3):
        pastCompListIsLong = True
        pastCompetitions = pastCompetitions[:3]
    else:
        pastCompListIsLong = False

    # обрезать в html
    #
    for comp in announcedCompetitions:
        if len(comp.discription) > 150:
            comp.discription = comp.discription[:130] + "..."
    for comp in currentCompetitions:
        if len(comp.discription) > 100:
            comp.discription = comp.discription[:80] + "..."
    for comp in pastCompetitions:
        if len(comp.discription) > 100:
            comp.discription = comp.discription[:80] + "..."
    #
    #
    return render(request, 'homePage.html', {'announcedCompetitions': announcedCompetitions,
        'currentCompetitions': currentCompetitions,'pastCompetitions': pastCompetitions,
        'pastCompListIsLong':pastCompListIsLong, "userAuth": userAuth,
        "userIsJudge": request.user.has_perm('SCS.control_competition')})


def pastCompetitionsView(request):
    userAuth = request.user.is_authenticated
    pastCompetitions = Competition.objects.all().filter(status=Competition.PAST)
    for comp in pastCompetitions:
        if len(comp.discription) > 200:
            comp.discription = comp.discription[:180] + "..."
    pageLen = 5
    if len(pastCompetitions) > pageLen:
        paginator = Paginator(pastCompetitions, pageLen)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        pageList = paginator.get_elided_page_range(number=page_number)
        return render(request, 'pastCompPage.html', {'page_obj': page_obj, 'pageList':pageList, 'paginator':True,
            "userIsJudge": request.user.has_perm('SCS.control_competition'), "userAuth":userAuth})
    else:
            return render(request, 'pastCompPage.html', {'page_obj':pastCompetitions, 'paginator': False, 'pageList':[],
            "userAuth":userAuth, "userIsJudge": request.user.has_perm('SCS.control_competition')})


@login_required
def createCompetitionsView(request):
    userAuth = request.user.is_authenticated
    if request.user.has_perm('SCS.control_competition'):
        if request.method == "GET":
            return render(request, 'createCompetitions.html', {'form':CreateCompetitionsForm()})
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




def competitionView(request, comp_id):
    checkCompetitionStart()

    userAuth = request.user.is_authenticated
    competition = get_object_or_404(Competition, pk=comp_id)
    compForm = CreateCompetitionsForm(instance=competition)
    matches = Match.objects.all().filter(competition=competition).order_by('status_isCompleted', 'matchDateTime')
    teamForm = [RegistrVolleybolTeamForm()]
    PlayerFormSet = formset_factory(RegistrPlayerForm, extra=6)
    #playerFormSet = PlayerFormSet()
    teamForm.append(PlayerFormSet)
    MatchFormSet = formset_factory(MatchEditForm)

    if competition.status == Competition.ANNOUNSED:                                             #    ЗАЯВКА НА УЧАСТИЕ
        if userAuth:
            if not request.user.has_perm('SCS.control_competition'):
                if len(VolleyballTeam.objects.all().filter(competition=competition).filter(user=request.user)) == 0:
                    requestData = {"userIsJudge": False, "competition": competition, "userAuth":userAuth,
                                   "teamForm": teamForm, "unableToCreateTeam": False}
                else:
                    requestData = {"userIsJudge": False, "competition": competition, "unableToCreateTeam": True,
                                   "userAuth": userAuth, 'teamFormAns':"Ваша заявка на участие принята"}
            else:
                requestData = {"userIsJudge":True, "competition":competition, "compForm":compForm,
                               "unableToCreateTeam": True, "userAuth":userAuth, }
        else:
            requestData = {"userIsJudge": False, "competition": competition, "unableToCreateTeam": True, "userAuth":userAuth}
    else:
        matchRunNow = False                                                                     #       ТЕКУЩИЙ МАТЧ
        now = pytz.UTC.localize(datetime.now())
        currentMatchData = []
        for match in matches:
            if match.matchDateTime:
                if not match.status_isCompleted and match.matchDateTime < now:
                    currentMatchData.append([match.firstTeam.name, match.secondTeam.name])
                    currentMatchData.append([match.firstTeamScore, match.secondTeamScore])
                    currentMatchData.append(MatchEvent.objects.all().filter(match=match))
                    matchRunNow = True
                    break

        matchFormSetInitData, matchesEvents = list(), list()                    #     ТУРНИРНАЯ СЕТКА
        nextMDT = None
        if len(matches): nextMDT = matches[0].matchDateTime
        for match in matches:
            matchFormInitData = {
                'name':match.name,
                'place':match.place,
                'matchDateTime':match.matchDateTime,
                'firstTeamScore':match.firstTeamScore,
                'secondTeamScore':match.secondTeamScore
            }
            matchFormSetInitData.append(matchFormInitData)
            matchesEvents.append(MatchEvent.objects.all().filter(match=match))
            if match.matchDateTime and nextMDT:
                if match.matchDateTime > now and match.matchDateTime < nextMDT:
                    nextMDT = match.matchDateTime
        if nextMDT:
            nextMatchDateTime = nextMDT.strftime("%Y:%m:%d %H:%M")
        else: nextMatchDateTime = "Дата неизвестна"

        matchFormSet = MatchFormSet(initial=matchFormSetInitData)
        indexes = [i for i in range(0, len(matches))]
        matchesData = list(zip(matches, matchesEvents, matchFormSet, indexes))

        requestData = {
            "userIsJudge":request.user.has_perm('SCS.control_competition'),
            "matchesData":matchesData, "competition":competition, "compForm":compForm, 'matchFormSet':matchFormSet,
            "currentMatchData":currentMatchData, "matchRunNow":matchRunNow, "unableToCreateTeam": True,
            'now':now+timedelta(hours=2), "userAuth":userAuth, 'nextMatchDateTime':nextMatchDateTime
        }


    if request.method == "GET":
        return render(request, "competition.html", requestData)
    else:
        try:
            if request.POST['formType'] == 'compEditForm':
                competition.name=request.POST['name']
                competition.discription = request.POST['discription']
                competition.organizerName = request.POST['organizerName']
                if competition.status == Competition.ANNOUNSED:
                    competition.theNumberOfTeamsRequiredToStartTheCompetition = \
                        request.POST['theNumberOfTeamsRequiredToStartTheCompetition']
                    if not request.POST['lastTimeForApplications'] == competition.getLastTimeForApplicationStr():
                        newCompDataTime = convertDTPickerStrToDateTime(request.POST['lastTimeForApplications'])
                        competition.lastTimeForApplications = newCompDataTime
                competition.save()


            elif request.POST['formType'] == "matchEditForm":
                match = matches.get(id=int(request.POST['id']))
                for i, m in enumerate(matches):
                    if m == match:
                        index = i
                match.name = request.POST['form-' + str(index) + '-name']
                match.place = request.POST['form-' + str(index) + '-place']
                match.matchDateTime = \
                    convertDTPickerStrToDateTime(request.POST['form-' + str(index) + '-matchDateTime'])
                if match.secondTeam and match.firstTeam:
                    match.firstTeamScore = int(request.POST['form-' + str(index) + '-firstTeamScore'])
                    match.secondTeamScore = int(request.POST['form-' + str(index) + '-secondTeamScore'])
                match.save()
                if (not match.firstTeamScore == 0 or not match.secondTeamScore == 0):
                    competition.updateStanding(match.id)


            elif request.POST['formType'] == "teamRegistrForm":
                #playerFormSet = PlayerFormSet(request.POST)                                <---------------------->
                teamForm = RegistrVolleybolTeamForm(request.POST)
                team = teamForm.save(commit=False)
                team.registratedTime = pytz.UTC.localize(datetime.now())
                team.competition=competition
                team.user = request.user
                team.save()

                teamPlayers = []
                for playerNum in range(6):
                    strName = 'form-' + str(playerNum) + '-name'
                    strSurename = 'form-' + str(playerNum) + '-surename'
                    strPatronymic = 'form-' + str(playerNum) + '-patronymic'
                    strAge = 'form-' + str(playerNum) + '-age'
                    player = Player(
                        name = request.POST[strName],
                        surename = request.POST[strSurename],
                        patronymic = request.POST[strPatronymic],
                        age = int(request.POST[strAge]),
                    )
                    teamPlayers.append(player)
                if len(teamPlayers) >= 6:
                    print('team was saved')
                    team.save()
                    for player in teamPlayers:
                        player.save()
                        player.team.add(team)
                else:
                    raise Exception("teamLineUpEx")
            return redirect(competition)


        except Exception as e:
            print("Exept:", e)
            if request.POST['formType'] == "teamRegistrForm":
                requestData = {"userIsJudge": False, "competition": competition, "error":"Неверно введены данные команды",
                                "teamForm": teamForm, "unableToCreateTeam": False, "userAuth":userAuth}
            else:
                if competition.status == Competition.ANNOUNSED:
                    requestData = {"userIsJudge": True, "competition": competition, "compForm": compForm,
                                   "unableToCreateTeam": True, "userAuth":userAuth,
                                   "error":"Ошибка обновления данных соревнования",}
                else:
                    requestData = {
                        "userIsJudge": request.user.has_perm('SCS.control_competition'),
                        "matchesData": matchesData, 'matchFormSet': matchFormSet, "competition": competition,
                        "compForm": compForm, "error":"Неверно введены данные соревнования/матчей",
                        "currentMatchData": currentMatchData, "matchRunNow": matchRunNow,
                        "unableToCreateTeam": True, "userAuth":userAuth, 'nextMatchDateTime':nextMatchDateTime
                    }
            return render(request, "competition.html", requestData)


