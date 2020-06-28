import redis
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST, require_GET

from actions.utils import create_action
from common.decorators import ajax_required
from .forms import ImageCreateForm
from .models import Image

# connect to redis
r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)


@login_required
def image_create(request):
    if request.method == 'POST':
        # form is sent
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # form data is valid
            cd = form.cleaned_data
            new_item = form.save(commit=False)

            # assign current user to form
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'bookmarked image', new_item)
            messages.success(request, 'Image added successfully')

            # redirect to new created item detail view
            return redirect(new_item.get_absolute_url())
    else:
        # build form with data provided via GET
        form = ImageCreateForm(data=request.GET)

    return render(request,
                  'images/image/create.html',
                  {
                      'section': 'images',
                      'form': form
                  })


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    # Increment total image views by 1
    total_views = r.incr(f'image:{image.pk}:views')
    # Increment image ranking by 1
    r.zincrby('image_ranking', 1, image.pk)
    return render(request,
                  'images/image/detail.html',
                  {
                      'image': image,
                      'section': 'images',
                      'total_views': total_views
                  })


@login_required
@require_POST
@ajax_required
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        # noinspection PyBroadException
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Exception:
            pass
    return JsonResponse({'status': 'error'})


@login_required
@require_GET
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # If request is ajax AJAX and page is out of range
            # return empty response
            return HttpResponse('')
        # If page is out of range deliver last page of result
        images = paginator.page(paginator.num_pages)
    template = 'list.html'
    if request.is_ajax():
        template = 'list_ajax.html'

    return render(request,
                  f'images/image/{template}',
                  {'section': 'images', 'images': images})


@login_required
def image_ranking(request):
    # Get image ranking dictionary
    ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    ranking_ids = [int(id) for id in ranking]
    # Get most viewed images
    most_viewed = list(Image.objects.filter(id__in=ranking_ids))
    most_viewed.sort(key=lambda x: ranking_ids.index(x.id))
    return render(request,
                  'images/image/ranking.html',
                  {
                      'section': 'images',
                      'most_viewed': most_viewed
                  })
