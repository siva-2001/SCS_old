from django.shortcuts import render
from SCSapp.models.Competition import Competition
from django.core.paginator import Paginator

def compHomePageView(request):
    pastCompetitions = Competition.objects.all().filter(status=Competition.PAST)
    if(len(pastCompetitions) > 3):
        pastCompListIsLong = True
        pastCompetitions = pastCompetitions[:3]
    else:
        pastCompListIsLong = False
    data = {
        'announcedCompetitions':Competition.objects.all().filter(status=Competition.ANNOUNSED),
        'currentCompetitions':Competition.objects.all().filter(status=Competition.CURRENT),
        'userAuth': request.user.is_authenticated,
        'pastCompetitions':pastCompetitions,
        'currentCompListIsLong': pastCompListIsLong,
        'userIsJudge':request.user.has_perm("SCS.control_competition")
    }
    return render(request, 'homePage.html', data)

def pastCompetitionsView(request):
    pageLen = 5
    data = {
        'userAuth':request.user.is_authenticated,
        "userIsJudge": request.user.has_perm('SCS.control_competition')
    }
    pastCompetitions = Competition.objects.all().filter(status=Competition.PAST)
    if len(pastCompetitions) > pageLen:
        paginator = Paginator(pastCompetitions, pageLen)
        page_number = request.GET.get('page', 1)
        data['page_obj'] = paginator.get_page(page_number)
        data['pageList'] = paginator.get_elided_page_range(number=page_number)
        data['paginator'] = True
    else:
        data['page_obj'] = pastCompetitions
        data['pageList'] = []
        data['paginator'] = False
    return render(request, 'pastCompPage.html', data)
