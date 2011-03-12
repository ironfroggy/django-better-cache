from django import template
from django.shortcuts import render_to_response


def test(request):
    ctx = template.RequestContext(request, request.GET)

    return render_to_response("test.html", ctx)
