from django.shortcuts import render, redirect, get_object_or_404

from SCSapp.models.Competition import Competition
from SCSapp.models.Match import Match
from SCSapp.models.VolleyballTeam import VolleyballTeam
from SCSapp.models.Player import Player



from SCSapp.forms import CreateCompetitionsForm, RegistrVolleybolTeamForm, RegistrPlayerForm, MatchEditForm
from django.forms import formset_factory
import pytz
from datetime import timedelta, datetime
from SCSapp.func import convertDTPickerStrToDateTime

def competitionView(request, comp_id):

    #------------------------------------------------------------------------------------------------------------------
    #       Отображение страницы соревнования
    #           Извлечение общих данных
    #------------------------------------------------------------------------------------------------------------------

    userAuth = request.user.is_authenticated
    competition = get_object_or_404(Competition, pk=comp_id)
    compForm = CreateCompetitionsForm(instance=competition)
    matches = Match.objects.all().filter(competition=competition).order_by('status_isCompleted', 'matchDateTime')
    MatchFormSet = formset_factory(MatchEditForm)
    now = pytz.UTC.localize(datetime.now())

    requestData = {
        'userIsJudge':request.user.has_perm('SCS.control_competition'),
        'userAuth':request.user.is_authenticated,
        'competition':competition,
        'unableToCreateTeam':True,
    }
    if request.user.has_perm('SCS.control_competition'): requestData['compForm'] = compForm

    #------------------------------------------------------------------------------------------------------------------
    #       Извлечение данных для анонсированного соревнования
    #------------------------------------------------------------------------------------------------------------------
    if competition.status == Competition.ANNOUNSED:
        if userAuth and not request.user.has_perm('SCS.control_competition'):
            if len(VolleyballTeam.objects.all().filter(competition=competition).filter(user=request.user)) == 0:
                requestData['teamForm'] = [RegistrVolleybolTeamForm(), formset_factory(RegistrPlayerForm, extra=6)]
                requestData["unableToCreateTeam"] = False
            else:
                requestData['teamFormAns'] = "Ваша заявка на участие принята"

    # ------------------------------------------------------------------------------------------------------------------
    #       Извлечение данных текущего/прошедшего соревнования
    # ------------------------------------------------------------------------------------------------------------------
    else:
        requestData['now'] = now + timedelta(hours=2)

        #   Match form set init data
        matchFormSetInitData = list()
        nextMDT = None
        if len(matches): nextMDT = matches[0].matchDateTime
        for match in matches:
            matchFormSetInitData.append({
                'name':match.name,
                'place':match.place,
                'matchDateTime':match.matchDateTime,
                'firstTeamScore':match.firstTeamScore,
                'secondTeamScore':match.secondTeamScore
            })
            if match.matchDateTime and nextMDT:
                if match.matchDateTime > now and match.matchDateTime < nextMDT:
                    nextMDT = match.matchDateTime

        #   Match Form Set
        matchFormSet = MatchFormSet(initial=matchFormSetInitData)
        indexes = [i for i in range(0, len(matches))]
        requestData['matchesData'] = list(zip(matches, matchFormSet, indexes))
        for matchForm, ind in zip(matchFormSet, indexes):
            matchForm.fields['matchDateTime'].widget.attrs.update({
                'id': 'id_datetimepicker_' + str(ind)
            })
        requestData['matchFormSet'] = matchFormSet

        #   Next match datetime string
        if nextMDT:
            nextMatchDateTime = nextMDT.strftime("%Y:%m:%d %H:%M")
        else: nextMatchDateTime = "Дата неизвестна"
        requestData['nextMatchDateTime'] = nextMatchDateTime



    if request.method == "GET":
        return render(request, "competition.html", requestData)
    else:
        try:
            # ----------------------------------------------------------------------------------------------------------
            #       Обработка формы редактирования соревнования
            # ----------------------------------------------------------------------------------------------------------
            if request.POST['formType'] == 'compEditForm':
                competition.name=request.POST['name']
                competition.discription = request.POST['discription']
                competition.organizerName = request.POST['organizerName']
                if competition.status == Competition.ANNOUNSED:
                    competition.theNumberOfTeamsRequiredToStartTheCompetition = \
                        request.POST['theNumberOfTeamsRequiredToStartTheCompetition']
                    newCompDataTime = convertDTPickerStrToDateTime(request.POST['lastTimeForApplications'])
                    competition.lastTimeForApplications = newCompDataTime
                competition.save()

            # ----------------------------------------------------------------------------------------------------------
            #       Обработка формы редактирования матча
            # ----------------------------------------------------------------------------------------------------------
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
                if not(int(request.POST['form-' + str(index) + '-firstTeamScore']) == 0 and
                       int(request.POST['form-' + str(index) + '-secondTeamScore']) == 0):
                    match.status_isCompleted = True
                    match.save()
                    competition.updateStanding(match.id)
                match.save()

            # ------------------------------------------------------------------------------------------------------------------
            #       Обработка формы регистрации новой команды
            # ------------------------------------------------------------------------------------------------------------------
            elif request.POST['formType'] == "teamRegistrForm":
                #playerFormSet = PlayerFormSet(request.POST)                                <---------------------->
                teamForm = RegistrVolleybolTeamForm(request.POST)
                team = teamForm.save(commit=False)
                team.registratedTime = now
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
                requestData["error"] = "Неверно введены данные команды"
            else:
                if competition.status == Competition.ANNOUNSED:
                    requestData["error"] = "Ошибка обновления данных соревнования"
                else:
                    requestData["error"] = "Неверно введены данные соревнования/матчей"

            return render(request, "competition.html", requestData)


