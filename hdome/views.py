from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.shortcuts import render_to_response
#from subform.models import Owner
from django.contrib.auth import logout
from django.http import HttpResponseRedirect

from django.http import HttpResponse
from django.template import RequestContext, loader


from django.contrib.auth import authenticate, login

def my_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/')



def home(request):
    
    #owner_list = Owner.objects.all()
    #template = loader.get_template('subform/home.html')
    #context = { 'owner_list': owner_list }
    return render( request, 'home.html', { 'home_active' : True } )

def logout_page(request):
    """
    Log users out and re-direct them to the main page.
    """
    logout(request)
    return HttpResponseRedirect('/')
