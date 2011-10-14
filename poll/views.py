from django.shortcuts import render_to_response, get_object_or_404
from poll.models import Poll, Choice
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse

def index(request):
    latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
    return render_to_response('poll/index.html',{
        'latest_poll_list':latest_poll_list
        })

def detail(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    return render_to_response('poll/detail.html',{'poll':p},
            context_instance=RequestContext(request))

def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except(KeyError, Choice.DoesNotExist):
        return render_to_response('poll/detail.html',{
            'poll':p,
            'error_message':"You didn't select a choice.",
            },context_instance=RequestContext(request))
    else:
        selected_choice.vote +=1
        selected_choice.save()
        return HttpResponseRedirect(reverse('poll.views.results',
            args=(p.id,)))

def results(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    return render_to_response('poll/results.html', {
        'poll':p})
