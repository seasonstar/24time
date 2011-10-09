from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.forms import ModelForm
from settings import MEDIA_URL

from photo.models import *

def main(request):
    """Main listing."""
    albums = Album.objects.all()
    if not request.user.is_authenticated():
        albums = albums.filter(public=True)

    paginator = Paginator(albums, 10)
    try:
        page = int(request.GET.get("page", '1'))
    except ValueError:
        page = 1

    try:
        albums = paginator.page(page)
    except (InvalidPage, EmptyPage):
        albums = paginator.page(paginator.num_pages)

    for album in albums.object_list:
        album.images = album.image_set.all()[:4]

    return render_to_response("photo/list.html", dict(albums=albums, user=request.user, media_url=MEDIA_URL))

def album(request, pk, view="thumbnails"):
    """Album listing."""
    num_images = 30
    if view == "full":
        num_images = 10
    album = Album.objects.get(pk=pk)
    if not album.public and not request.user.is_authenticated():
        return HttpResponse("Error: you need to be logged in to view this album.")

    images = album.image_set.all()
    paginator = Paginator(images, num_images)
    try:
        page = int(request.GET.get("page", '1'))
    except ValueError:
        page = 1

    try:
        images = paginator.page(page)
    except (InvalidPage, EmptyPage):
        images = paginator.page(paginator.num_pages)

    return render_to_response("photo/album.html", dict(
        album=album, 
        images=images, 
        user=request.user,
        view=view,
        media_url=MEDIA_URL))

def image(request, pk):
    """image page."""
    img = Image.objects.get(pk=pk)
    return render_to_response("photo/image.html", dict(
        image=img,
        user=request.user,
        media_url=MEDIA_URL,
        ))
