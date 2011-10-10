from string import join
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.forms import ModelForm
from collections import defaultdict
from settings import MEDIA_URL
from django.db.models import Q
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

    # add list of tags as string and list of album objects to each image object
    for img in images.object_list:
        tags = [x[1] for x in img.tags.values_list()]
        img.tag_lst = join(tags, ', ')
        img.album_lst = [x[1] for x in img.albums.values_list()]

    d = dict(
        album=album, 
        images=images, 
        user=request.user,
        view=view,
        albums=Album.objects.all(),
        media_url=MEDIA_URL,
        )
    d.update(csrf(request))

    return render_to_response("photo/album.html", d) 

def image(request, pk):
    """image page."""
    img = Image.objects.get(pk=pk)
    return render_to_response("photo/image.html", dict(
        image=img,
        user=request.user,
        media_url=MEDIA_URL,
        backurl=request.META["HTTP_REFERER"]
        ))

def update(request):
    """Update image title, rating, tags, albums."""
    p = request.POST
    images = defaultdict(dict)

    # create dictionary of properties for each image
    for k, v in p.items():
        if k.startswith("title") or k.startswith("rating") or k.startswith("tags"):
            k, pk = k.split('-')
            images[pk][k] = v
        elif k.startswith("album"):
            pk = k.split('-')[1]
            images[pk]["albums"] = p.getlist(k)

    # process properties, assign to image objects and save
    for k, d in images.items():
        image = Image.objects.get(pk=k)
        image.title = d["title"]
        image.rating = int(d["rating"])

        # tags - assign or create if a new tag!
        tags = d["tags"].split(', ')
        lst = []
        for t in tags:
            if t: lst.append(Tag.objects.get_or_create(tag=t)[0])
        image.tags = lst

        if "albums" in d:
            image.albums = d["albums"]
        image.save()

    return HttpResponseRedirect(request.META["HTTP_REFERER"])

@login_required
def search(request):
    """Search, filter, sort images."""
    try: page = int(request.GET.get("page", '1'))
    except ValueError: page = 1

    p = request.POST
    images = defaultdict(dict)

    # init parameters
    parameters = {}
    keys = ("title filename rating_from rating_to width_from width_to height_from height_to tags view"
        " user sort asc_desc").split()
    for k in keys:
        parameters[k] = ''
    parameters["album"] = []

    # create dictionary of properties for each image and a dict of search/filter parameters
    for k, v in p.items():
        if k == "album":
            parameters[k] = [int(x) for x in p.getlist(k)]
        elif k == "user":
            if v != "all": v = int(v)
            parameters[k] = v
        elif k in parameters:
            parameters[k] = v
        elif k.startswith("title") or k.startswith("rating") or k.startswith("tags"):
            k, pk = k.split('-')
            images[pk][k] = v
        elif k.startswith("album"):
            pk = k.split('-')[1]
            images[pk]["albums"] = p.getlist(k)

    # save or restore parameters from session
    if page != 1 and "parameters" in request.session:
        parameters = request.session["parameters"]
    else:
        request.session["parameters"] = parameters

    results = update_and_filter(request, images, parameters)

    # make paginator
    paginator = Paginator(results, 20)
    try:
        results = paginator.page(page)
    except (InvalidPage, EmptyPage):
        request = paginator.page(paginator.num_pages)

    # add list of tags as string and list of album names to each image object
    for img in results.object_list:
        tags = [x[1] for x in img.tags.values_list()]
        img.tag_lst = join(tags, ', ')
        img.album_lst = [x[1] for x in img.albums.values_list()]

    d = dict(results=results, user=request.user, albums=Album.objects.all(), prm=parameters,
             users=User.objects.all(), media_url=MEDIA_URL)
    d.update(csrf(request))
    return render_to_response("photo/search.html", d)

def update_and_filter(request, images, p):
    """Update image data if changed, filter results through parameters and return results list"""
    # process properties, assign to image objects and save
    for k, d in images.items():
        image = Image.objects.get(pk=k)
        image.title  = d["title"]
        image.rating = int(d["rating"])
        
        # tags - assign or create if a new tag!
        tags = d["tags"].split(', ')
        lst = []
        for t in tags:
            if t:
                lst.append(Tag.objects.get_or_create(tag=t)[0])
        image.tags = lst

        if "albums" in d:
            image.albums = d["albums"]
        image.save()


    # sort and filter results by parameters
    order = "created"
    if p["sort"]: order = p["sort"]
    if p["asc_desc"] == "desc": order = '-' + order

    results = Image.objects.all().order_by(order)
    if p["title"]:
        results = results.filter(title__icontains=p["title"])
    if p["filename"]:
           results = results.filter(image__icontains=p["filename"])
    if p["rating_from"]:
           results = results.filter(rating__gte=int(p["rating_from"]))
    if p["rating_to"]:
           results = results.filter(rating__lte=int(p["rating_to"]))
    if p["width_from"]:
           results = results.filter(width__gte=int(p["width_from"]))
    if p["width_to"]:
           results = results.filter(width__lte=int(p["width_to"]))
    if p["height_from"]:
           results = results.filter(height__gte=int(p["height_from"]))
    if p["height_to"]:
           results = results.filter(height__lte=int(p["height_to"]))
    if p["user"] and p["user"] != "all" : 
        results = results.filter(user__pk=int(p["user"]))
    if p["tags"]:
        tags = p["tags"].split(', ')
        lst = []
        for t in tags:
            if t:
                results = results.filter(tags=Tag.objects.get(tag=t))

    if p["album"]:
        lst = p["album"]
        or_query = Q(albums=lst[0])
        for album in lst[1:]:
            or_query = or_query | Q(albums=album)
        results = results.filter(or_query).distinct()
    return results



