import datetime
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.conf import settings
from mini_factory import utils, models


def control_mode(request):
        
    return render(
                    request,
                    "mini_factory/control_mode.html",
                    {
                    }
    )


def data_table(request):
    (new_state, new_detect) = utils.StateManager.load_state()

    detect_blue = False
    detected_red = False
    detected_white = False

    if new_detect != {}:
        detected_blue = new_detect["Detected Blue"]
        detected_red = new_detect["Detected Red"]
        detected_white = new_detect["Detected White"]
    else:
        detect_blue = False
        detected_red = False
        detected_white = False

    return render(
                    request,
                    "mini_factory/data_table.html",
                    {
                        "new_state": new_state,
                        "detected_blue": detected_blue,
                        "detected_red": detected_red,
                        "detected_white": detected_white
                    }
    )
